
import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { GoogleGenAI, LiveServerMessage, Modality } from '@google/genai';
import Orb from './components/Orb';
import Terminal from './components/Terminal';
import Dashboard from './components/Dashboard';
import { JerryStatus, LogEntry, SystemStats, DEFAULT_STATS, BridgeCommand, BridgeResponse } from './types';
import { 
  JERRY_TOOLS, 
  JERRY_SYSTEM_INSTRUCTION, 
  encode, 
  decode, 
  decodeAudioData,
  NeuralKeyManager
} from './services/gemini';
import { BridgeAuthenticator, CommandValidator, ActivityLogger } from './services/security';
import { CommandQueue } from './services/commandQueue';
import { SystemMonitorService, SystemSnapshot } from './services/systemMonitor';
import { WorkflowEngine } from './services/workflowEngine';

const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
const BRIDGE_HOST = (import.meta as any).env?.VITE_BRIDGE_HOST || 'localhost:8765';
const BRIDGE_PROTOCOL = (import.meta as any).env?.VITE_BRIDGE_TLS === 'true' ? 'wss' : 'ws';

const debounce = <T extends (...args: any[]) => void>(fn: T, delay: number) => {
  let timer: number | undefined;
  return (...args: Parameters<T>) => {
    if (timer) window.clearTimeout(timer);
    timer = window.setTimeout(() => fn(...args), delay);
  };
};

const App: React.FC = () => {
  const [status, setStatus] = useState<JerryStatus>(JerryStatus.SLEEPING);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isBridgeActive, setIsBridgeActive] = useState(false);
  const [stats, setStats] = useState<SystemStats & { security: number; neural: number; activeNode: number; totalNodes: number }>(
    { ...DEFAULT_STATS, security: 0, neural: 0, activeNode: 0, totalNodes: 0 }
  );
  const [audioLevel, setAudioLevel] = useState(0);
  const [queuedCount, setQueuedCount] = useState(0);
  const [connectionHealth, setConnectionHealth] = useState({
    lastPing: 0,
    latency: 0,
    reconnectCount: 0
  });
  
  // Core refs
  const keyManagerRef = useRef(new NeuralKeyManager(process.env.API_KEY));
  const autoReconnectAttemptsRef = useRef(0);
  const maxAutoReconnectAttempts = 5;
  const sessionRef = useRef<any>(null);
  const bridgeRef = useRef<WebSocket | null>(null);
  const audioSourcesRef = useRef<Set<AudioBufferSourceNode>>(new Set());
  const nextAudioStartTimeRef = useRef<number>(0);
  const outputAudioContextRef = useRef<AudioContext | null>(null);
  const inputAudioContextRef = useRef<AudioContext | null>(null);
  const recognitionRef = useRef<any>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);

  // New service refs
  const authRef = useRef(new BridgeAuthenticator());
  const activityLoggerRef = useRef(new ActivityLogger());
  const commandQueueRef = useRef(new CommandQueue());
  const systemMonitorRef = useRef(new SystemMonitorService());
  const workflowEngineRef = useRef(new WorkflowEngine());
  const uptimeIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const startTimeRef = useRef<number>(Date.now());
  const pendingRequestsRef = useRef<Map<string, { resolve: (data: any) => void, timer: ReturnType<typeof setTimeout> }>>(new Map());

  const addLog = useCallback((message: string, source: LogEntry['source'] = 'SYSTEM', type: LogEntry['type'] = 'info') => {
    setLogs(prev => [
      ...prev,
      {
        id: Math.random().toString(36).substr(2, 9),
        timestamp: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        source,
        message,
        type
      }
    ].slice(-200));
  }, []);

  // --- Send command to bridge ---
  const sendBridgeCommand = useCallback((command: BridgeCommand): boolean => {
    if (bridgeRef.current?.readyState === WebSocket.OPEN) {
      const reqId = Math.random().toString(36).substr(2, 12);
      const authedCommand = { ...authRef.current.wrapCommand(command), _reqId: reqId };
      bridgeRef.current.send(JSON.stringify(authedCommand));
      activityLoggerRef.current.log(command.action, command.target, 'voice', 'pending');
      return true;
    }
    return false;
  }, []);

  // --- Send command and wait for response (with timeout) ---
  const sendBridgeCommandAsync = useCallback((command: BridgeCommand, timeoutMs = 8000): Promise<any> => {
    return new Promise((resolve) => {
      if (bridgeRef.current?.readyState !== WebSocket.OPEN) {
        resolve({ status: 'error', message: 'Bridge offline' });
        return;
      }
      const reqId = Math.random().toString(36).substr(2, 12);
      const authedCommand = { ...authRef.current.wrapCommand(command), _reqId: reqId };
      const timer = setTimeout(() => {
        pendingRequestsRef.current.delete(reqId);
        resolve({ status: 'error', message: 'Request timed out' });
      }, timeoutMs);
      pendingRequestsRef.current.set(reqId, { resolve, timer });
      bridgeRef.current.send(JSON.stringify(authedCommand));
      activityLoggerRef.current.log(command.action, command.target, 'voice', 'pending');
    });
  }, []);

  const debouncedSendBridgeCommand = useMemo(
    () => debounce(sendBridgeCommand, 300),
    [sendBridgeCommand]
  );

  // Initialize stats and check for API Key
  useEffect(() => {
    const kmStats = keyManagerRef.current.getStats();
    setStats(s => ({ 
      ...s, 
      activeNode: kmStats.activeNode, 
      totalNodes: kmStats.totalNodes,
      neural: kmStats.totalNodes > 0 ? 98.4 : 0 
    }));
    
    if (kmStats.totalNodes === 0) {
      addLog(">>> CRITICAL: API_KEY not detected in environment.", 'SYSTEM', 'error');
      addLog(">>> HELP: Create a .env.local file with GEMINI_API_KEY=your_key", 'SYSTEM', 'info');
    } else {
      addLog(`Neural Link: ${kmStats.totalNodes} nodes synchronized. Active: Node-${kmStats.activeNode}.`, 'SYSTEM', 'success');
    }

    // Set up command queue bridge sender
    commandQueueRef.current.setBridgeSender((data: string) => {
      if (bridgeRef.current?.readyState === WebSocket.OPEN) {
        bridgeRef.current.send(data);
        return true;
      }
      return false;
    });

    // Set up system monitor alerts
    systemMonitorRef.current.onAlert((rule, value) => {
      const msg = rule.message.replace('{value}', value.toString());
      addLog(`ALERT: ${msg}`, 'SYSTEM', 'alert');
    });

    // Set up workflow engine logging
    workflowEngineRef.current.onLog((message, type) => {
      addLog(message, 'WORKFLOW', type as LogEntry['type']);
    });

    // Uptime counter
    uptimeIntervalRef.current = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
      const h = String(Math.floor(elapsed / 3600)).padStart(2, '0');
      const m = String(Math.floor((elapsed % 3600) / 60)).padStart(2, '0');
      const sec = String(elapsed % 60).padStart(2, '0');
      setStats(s => ({ ...s, uptime: `${h}:${m}:${sec}` }));
    }, 1000);

    return () => {
      if (uptimeIntervalRef.current) clearInterval(uptimeIntervalRef.current);
      workflowEngineRef.current.stopScheduler();
    };
  }, [addLog]);

  // Handle Python Bridge Reconnection
  useEffect(() => {
    let reconnectTimer: any;
    let reconnectDelay = 2000;
    let pingInterval: any;

    const connectBridge = () => {
      const socket = new WebSocket(`${BRIDGE_PROTOCOL}://${BRIDGE_HOST}`);
      
      socket.onopen = () => {
        setIsBridgeActive(true);
        reconnectDelay = 2000;
        addLog("Neural Bridge established. Full system control online.", 'BRIDGE', 'success');

        pingInterval = setInterval(() => {
          if (socket.readyState === WebSocket.OPEN) {
            const started = Date.now();
            setConnectionHealth(prev => ({ ...prev, lastPing: started }));
            socket.send("ping");
          }
        }, 30000);
        
        // Flush queued commands
        const queueStatus = commandQueueRef.current.getStatus();
        if (queueStatus.pending > 0) {
          addLog(`Flushing ${queueStatus.pending} queued commands...`, 'BRIDGE', 'info');
          commandQueueRef.current.flush().then(result => {
            addLog(`Queue flushed: ${result.sent} sent, ${result.failed} failed.`, 'BRIDGE', result.failed > 0 ? 'warning' : 'success');
            setQueuedCount(commandQueueRef.current.pendingCount);
          });
        }

        // Request initial system status
        sendBridgeCommand({ action: 'system_status' });

        // Set up workflow executor
        workflowEngineRef.current.setExecutor(async (cmd) => {
          return new Promise((resolve) => {
            const authed = authRef.current.wrapCommand(cmd);
            if (bridgeRef.current?.readyState === WebSocket.OPEN) {
              bridgeRef.current.send(JSON.stringify(authed));
              setTimeout(() => resolve({ status: 'success', message: `${cmd.action} executed` }), 500);
            } else {
              resolve({ status: 'error', message: 'Bridge offline' });
            }
          });
        });

        workflowEngineRef.current.startScheduler();
      };

      socket.onmessage = (event) => {
        if (event.data === "pong") {
          setConnectionHealth(prev => ({
            ...prev,
            latency: Date.now() - prev.lastPing
          }));
          return;
        }
        try {
          const data = JSON.parse(event.data);
          
          // Handle system monitor broadcasts
          if (data.type === 'system_monitor' || data.cpu || data.memory || data.disk) {
            const sysData = data;
            setStats(s => ({
              ...s,
              cpu: sysData.cpu?.percent ?? s.cpu,
              memory: sysData.memory?.percent ?? s.memory,
              disk: sysData.disk?.percent ?? s.disk,
              battery: sysData.battery?.percent ?? s.battery,
              batteryCharging: sysData.battery?.charging ?? s.batteryCharging,
              hostname: sysData.hostname || s.hostname,
              os: sysData.os || s.os,
              cpuCores: sysData.cpu?.cores ?? s.cpuCores,
              cpuFreq: sysData.cpu?.freq_current ?? s.cpuFreq,
              memoryTotal: sysData.memory?.total_gb ?? s.memoryTotal,
              memoryUsed: sysData.memory?.used_gb ?? s.memoryUsed,
              diskTotal: sysData.disk?.total_gb ?? s.diskTotal,
              diskFree: sysData.disk?.free_gb ?? s.diskFree,
              networkSent: sysData.network?.sent_mb ?? s.networkSent,
              networkRecv: sysData.network?.recv_mb ?? s.networkRecv,
              network: 'LOCAL // ENCRYPTED',
            }));
            systemMonitorRef.current.processSnapshot(data);
            return;
          }

          // Handle normal command responses
          // Check if this is a response to a pending async request
          if (data._reqId && pendingRequestsRef.current.has(data._reqId)) {
            const pending = pendingRequestsRef.current.get(data._reqId)!;
            clearTimeout(pending.timer);
            pendingRequestsRef.current.delete(data._reqId);
            pending.resolve(data);
          }
          const logType = data.status === 'success' ? 'success' : data.status === 'error' ? 'error' : 'info';
          addLog(`BRIDGE: ${data.message || 'Command acknowledged.'}`, 'BRIDGE', logType);
        } catch (e) {
          addLog(`BRIDGE: ${event.data}`, 'BRIDGE', 'info');
        }
      };

      socket.onclose = () => {
        setIsBridgeActive(false);
        addLog("Neural Bridge disconnected. Reconnecting...", 'BRIDGE', 'error');
        setConnectionHealth(prev => ({ ...prev, reconnectCount: prev.reconnectCount + 1 }));
        if (pingInterval) clearInterval(pingInterval);
        reconnectDelay = Math.min(reconnectDelay * 1.5, 15000);
        reconnectTimer = setTimeout(connectBridge, reconnectDelay);
      };

      socket.onerror = () => socket.close();
      bridgeRef.current = socket;
    };

    connectBridge();
    return () => {
      bridgeRef.current?.close();
      clearTimeout(reconnectTimer);
      if (pingInterval) clearInterval(pingInterval);
    };
  }, [addLog, sendBridgeCommand]);

  const handleToolCall = useCallback(async (toolCall: any) => {
    setStatus(JerryStatus.EXECUTING);
    addLog(`Neural Directive: ${toolCall.name.toUpperCase()}`, 'SYSTEM', 'command');
    
    let result = "Done, Sir.";

    if (toolCall.name === 'system_execution_directive') {
      const command: BridgeCommand = {
        action: toolCall.args.action,
        target: toolCall.args.target || '',
        payload: toolCall.args.payload || '',
        extra: toolCall.args.extra || ''
      };

      const validation = CommandValidator.validate(command);
      if (!validation.valid) {
        result = `Sir, I've blocked that command: ${validation.message}`;
        addLog(`BLOCKED: ${validation.message}`, 'SYSTEM', 'error');
      } else if (bridgeRef.current?.readyState === WebSocket.OPEN) {
        const authed = authRef.current.wrapCommand(command);
        bridgeRef.current.send(JSON.stringify(authed));
        addLog(`Transmitting: ${command.action} -> ${command.target || 'System'}`, 'SYSTEM', 'success');
        activityLoggerRef.current.log(command.action, command.target, 'voice', 'success');
        result = `I've executed the ${command.action} protocol for ${command.target || 'the core system'}, Sir. It should be active now.`;
      } else {
        commandQueueRef.current.enqueue(command, 
          CommandValidator.requiresConfirmation(command.action) ? 'high' : 'normal'
        );
        setQueuedCount(commandQueueRef.current.pendingCount);
        addLog(`Bridge offline. Command queued: ${command.action}`, 'SYSTEM', 'warning');
        result = "Sir, the neural bridge is offline. I've queued the command for reconnection. Please ensure the Python driver is running.";
      }
    } else if (toolCall.name === 'alarm_timer_reminder') {
      // Handle Alarms, Timers, Reminders
      const { action, time, label, alarm_id } = toolCall.args;
      if (bridgeRef.current?.readyState === WebSocket.OPEN) {
        const command: BridgeCommand = {
          action: action, // set_alarm, set_timer, set_reminder, cancel_alarm, list_alarms
          target: time || alarm_id || '',
          payload: label || ''
        };
        bridgeRef.current.send(JSON.stringify(authRef.current.wrapCommand(command)));
        addLog(`Time Protocol: ${action} - ${time || alarm_id || 'listing'}`, 'SYSTEM', 'success');
        result = `${action.replace('_', ' ')} command transmitted, Sir.`;
      } else {
        result = "Sir, I need the neural bridge for time-based operations.";
      }
    } else if (toolCall.name === 'text_to_speech') {
      // Handle TTS
      const { text, action: ttsAction, voice_id } = toolCall.args;
      if (bridgeRef.current?.readyState === WebSocket.OPEN) {
        const command: BridgeCommand = {
          action: ttsAction || 'speak',
          target: text,
          payload: voice_id?.toString() || ''
        };
        bridgeRef.current.send(JSON.stringify(authRef.current.wrapCommand(command)));
        addLog(`Voice Output: "${text?.substring(0, 40)}..."`, 'SYSTEM', 'info');
        result = `Speaking aloud, Sir.`;
      } else {
        result = "Sir, the neural bridge is needed for voice output.";
      }
    } else if (toolCall.name === 'media_control') {
      // Handle Media Control
      const { action: mediaAction, query } = toolCall.args;
      if (bridgeRef.current?.readyState === WebSocket.OPEN) {
        let command: BridgeCommand;
        
        // Map media actions to correct bridge commands
        if (mediaAction === 'play_youtube') {
          command = { action: 'play_youtube', target: query || '', payload: '' };
        } else if (mediaAction === 'play_spotify') {
          command = { action: 'play_spotify', target: query || '', payload: '' };
        } else if (mediaAction === 'open_url') {
          command = { action: 'open_url', target: query || '', payload: '' };
        } else {
          // For play, pause, next, previous, stop, mute - use "media" action with mediaAction as target
          command = { action: 'media', target: mediaAction, payload: '' };
        }
        
        bridgeRef.current.send(JSON.stringify(authRef.current.wrapCommand(command)));
        addLog(`Media: ${mediaAction} ${query ? '-> ' + query : ''}`, 'SYSTEM', 'success');
        result = `Media command executed, Sir.`;
      } else {
        result = "Sir, the neural bridge is required for media control.";
      }
    } else if (toolCall.name === 'calendar_events') {
      // Handle Calendar
      const { action: calAction, days, subject, start_time, duration, location } = toolCall.args;
      if (bridgeRef.current?.readyState === WebSocket.OPEN) {
        if (calAction === 'get_calendar' || calAction === 'list_events') {
          const command: BridgeCommand = { action: 'get_calendar', target: days?.toString() || '7' };
          bridgeRef.current.send(JSON.stringify(authRef.current.wrapCommand(command)));
          result = `Retrieving your calendar events, Sir.`;
        } else if (calAction === 'create_event') {
          const command: BridgeCommand = {
            action: 'create_event',
            target: subject || '',
            payload: start_time || '',
            extra: duration?.toString() || '60'
          };
          bridgeRef.current.send(JSON.stringify(authRef.current.wrapCommand(command)));
          result = `Creating calendar event: ${subject}, Sir.`;
        }
        addLog(`Calendar: ${calAction}`, 'SYSTEM', 'info');
      } else {
        result = "Sir, calendar access requires the neural bridge.";
      }
    } else if (toolCall.name === 'send_email') {
      // Handle Email
      const { to, subject, body } = toolCall.args;
      if (bridgeRef.current?.readyState === WebSocket.OPEN) {
        const command: BridgeCommand = {
          action: 'send_email',
          target: to,
          payload: subject,
          extra: body
        };
        bridgeRef.current.send(JSON.stringify(authRef.current.wrapCommand(command)));
        addLog(`Email: To ${to}, Subject: ${subject}`, 'SYSTEM', 'info');
        result = `Sending email to ${to}, Sir.`;
      } else {
        result = "Sir, email requires an active neural bridge connection.";
      }
    } else if (toolCall.name === 'quick_notes') {
      // Handle Notes
      const { action: noteAction, content, tags, note_id, tag_filter } = toolCall.args;
      if (bridgeRef.current?.readyState === WebSocket.OPEN) {
        const command: BridgeCommand = {
          action: noteAction, // add_note, list_notes, search_notes, delete_note
          target: content || note_id || tag_filter || '',
          payload: tags || ''
        };
        bridgeRef.current.send(JSON.stringify(authRef.current.wrapCommand(command)));
        addLog(`Notes: ${noteAction}`, 'SYSTEM', 'success');
        result = `Note operation complete, Sir.`;
      } else {
        result = "Sir, notes require the neural bridge.";
      }
    } else if (toolCall.name === 'window_management') {
      // Handle Window Management
      const { action: winAction, window_title, x, y, width, height, position } = toolCall.args;
      if (bridgeRef.current?.readyState === WebSocket.OPEN) {
        let command: BridgeCommand;
        if (winAction === 'list_windows') {
          command = { action: 'list_windows' };
        } else if (winAction === 'move_window') {
          command = { action: 'move_window', target: window_title || '', payload: `${x},${y}` };
        } else if (winAction === 'resize_window') {
          command = { action: 'resize_window', target: window_title || '', payload: `${width},${height}` };
        } else if (winAction === 'snap_window') {
          command = { action: 'snap_window', target: window_title || '', payload: position || '' };
        } else {
          command = { action: winAction, target: window_title || '' };
        }
        const response = await sendBridgeCommandAsync(command);
        if (winAction === 'list_windows' && response.windows) {
          const titles = response.windows.map((w: any) => w.title).filter(Boolean);
          addLog(`Window: ${winAction}`, 'SYSTEM', 'success');
          result = `Here are the currently open windows:\n${titles.map((t: string, i: number) => `${i + 1}. ${t}`).join('\n')}`;
        } else {
          addLog(`Window: ${winAction} ${window_title || ''}`, 'SYSTEM', 'success');
          result = response.message || `Window ${winAction} complete, Sir.`;
        }
      } else {
        result = "Sir, window management requires the neural bridge.";
      }
    } else if (toolCall.name === 'global_intel_search') {
      const query = toolCall.args.query || '';
      addLog(`Intel Scan: "${query}"`, 'SYSTEM', 'info');
      if (bridgeRef.current?.readyState === WebSocket.OPEN) {
        const command: BridgeCommand = { action: 'google_first', target: query };
        bridgeRef.current.send(JSON.stringify(authRef.current.wrapCommand(command)));
        result = `I've initiated a web search for "${query}", Sir. The results should be opening in Chrome.`;
      } else {
        result = `Sir, web search requires the neural bridge. The bridge is currently offline.`;
      }
    } else if (toolCall.name === 'execute_workflow') {
      const workflowName = toolCall.args.workflow_name;
      addLog(`Workflow Initiated: ${workflowName}`, 'WORKFLOW', 'command');
      setStatus(JerryStatus.WORKFLOW);
      
      const wfResult = await workflowEngineRef.current.executeWorkflow(workflowName);
      if (wfResult) {
        const successCount = wfResult.steps.filter(s => s.status === 'success').length;
        result = `${workflowName} workflow complete, Sir. ${successCount} of ${wfResult.steps.length} steps executed successfully.`;
      } else {
        result = `Sir, I couldn't find the workflow "${workflowName}". Available: ${workflowEngineRef.current.getWorkflowNames().join(', ')}.`;
      }
    } else if (toolCall.name === 'system_diagnostics') {
      if (bridgeRef.current?.readyState === WebSocket.OPEN) {
        const response = await sendBridgeCommandAsync({ action: 'system_status' });
        if (toolCall.args.report_type === 'network') {
          const netResp = await sendBridgeCommandAsync({ action: 'network_info' });
          result = `System status: ${response.message || 'collected'}. Network: ${netResp.message || 'collected'}`;
        } else if (toolCall.args.report_type === 'processes') {
          const procResp = await sendBridgeCommandAsync({ action: 'process', target: 'resource_hogs' });
          result = `System status: ${response.message || 'collected'}. Processes: ${procResp.message || 'collected'}`;
        } else {
          const statusReport = systemMonitorRef.current.getStatusReport();
          result = statusReport || response.message || 'System diagnostics collected, Sir.';
        }
      } else {
        result = "Sir, I need the neural bridge active for system diagnostics. Please start the Python driver.";
      }
    } else if (toolCall.name === 'extended_system_control') {
      // Handle v7.0 Extended System Control
      const { action: extAction, target: extTarget, payload: extPayload, extra: extExtra } = toolCall.args;
      if (bridgeRef.current?.readyState === WebSocket.OPEN) {
        const command: BridgeCommand = {
          action: extAction,
          target: extTarget || '',
          payload: extPayload || '',
          extra: extExtra || ''
        };
        const response = await sendBridgeCommandAsync(command);
        addLog(`Extended: ${extAction} ${extTarget ? '-> ' + extTarget : ''}`, 'SYSTEM', 'success');
        result = response.message || `${extAction.replace(/_/g, ' ')} command executed, Sir.`;
      } else {
        result = "Sir, extended control requires the neural bridge.";
      }
    } else if (toolCall.name === 'git_operations') {
      // Handle Git Operations
      const { action: gitAction, path: gitPath, message: gitMsg, url: gitUrl, destination: gitDest } = toolCall.args;
      if (bridgeRef.current?.readyState === WebSocket.OPEN) {
        let command: BridgeCommand;
        if (gitAction === 'git_clone') {
          command = { action: 'git_clone', target: gitUrl || '', payload: gitDest || '' };
        } else if (gitAction === 'git_commit') {
          command = { action: 'git_commit', target: gitPath || '.', payload: gitMsg || 'Auto-commit by Jerry' };
        } else {
          command = { action: gitAction, target: gitPath || '.' };
        }
        bridgeRef.current.send(JSON.stringify(authRef.current.wrapCommand(command)));
        addLog(`Git: ${gitAction}`, 'SYSTEM', 'success');
        result = `Git ${gitAction.replace('git_', '')} executed, Sir.`;
      } else {
        result = "Sir, git operations require the neural bridge.";
      }
    } else if (toolCall.name === 'code_execution') {
      // Handle Code Execution
      const { language, code } = toolCall.args;
      if (bridgeRef.current?.readyState === WebSocket.OPEN) {
        const command: BridgeCommand = {
          action: language === 'python' ? 'run_python' : 'run_powershell',
          target: code,
          payload: ''
        };
        const response = await sendBridgeCommandAsync(command, 15000);
        addLog(`Code Exec: ${language} (${code.substring(0, 30)}...)`, 'SYSTEM', 'info');
        result = response.message || `Code execution complete, Sir.`;
      } else {
        result = "Sir, code execution requires the neural bridge.";
      }
    } else if (toolCall.name === 'calculator_converter') {
      // Handle Calculator & Converter
      const { action: calcAction, expression, value, from_unit, to_unit } = toolCall.args;
      if (bridgeRef.current?.readyState === WebSocket.OPEN) {
        let command: BridgeCommand;
        if (calcAction === 'calculate') {
          command = { action: 'calculate', target: expression || '' };
        } else if (calcAction === 'convert_units') {
          command = { action: 'convert_units', target: value?.toString() || '0', payload: from_unit || '', extra: to_unit || '' };
        } else if (calcAction === 'convert_currency') {
          command = { action: 'convert_currency', target: value?.toString() || '0', payload: from_unit || '', extra: to_unit || '' };
        } else {
          command = { action: calcAction, target: expression || '' };
        }
        bridgeRef.current.send(JSON.stringify(authRef.current.wrapCommand(command)));
        addLog(`Calc: ${calcAction}`, 'SYSTEM', 'info');
        result = `Calculation complete, Sir.`;
      } else {
        result = "Sir, calculations require the neural bridge.";
      }
    } else if (toolCall.name === 'translator') {
      // Handle Translator
      const { text, to_language, from_language } = toolCall.args;
      if (bridgeRef.current?.readyState === WebSocket.OPEN) {
        const command: BridgeCommand = {
          action: 'translate',
          target: text || '',
          payload: to_language || 'en',
          extra: from_language || 'auto'
        };
        bridgeRef.current.send(JSON.stringify(authRef.current.wrapCommand(command)));
        addLog(`Translate: ${from_language || 'auto'} -> ${to_language}`, 'SYSTEM', 'info');
        result = `Opening translation, Sir.`;
      } else {
        result = "Sir, translation requires the neural bridge.";
      }
    } else if (toolCall.name === 'browser_automation') {
      // Handle Browser Control (keyboard + URL based, no Selenium)
      const { action: browserAction, url, text: inputText, submit, direction, amount, x, y, wait_seconds, query, keys, click_type } = toolCall.args;
      if (bridgeRef.current?.readyState === WebSocket.OPEN) {
        let command: BridgeCommand;
        
        if (browserAction === 'navigate') {
          command = { action: 'browser_navigate', target: url || '' };
        } else if (browserAction === 'type') {
          command = { action: 'browser_type', target: inputText || '', extra: submit ? 'true' : 'false' };
        } else if (browserAction === 'scroll') {
          command = { action: 'browser_scroll', target: direction || 'down', payload: amount?.toString() || '5' };
        } else if (browserAction === 'screenshot') {
          command = { action: 'browser_screenshot', target: '' };
        } else if (browserAction === 'get_text') {
          command = { action: 'browser_get_text', target: '' };
        } else if (browserAction === 'close' || browserAction === 'close_tab') {
          command = { action: 'close_tab', target: '' };
        } else if (browserAction === 'youtube_play') {
          command = { action: 'youtube_play', target: query || inputText || '' };
        } else if (browserAction === 'spotify_play') {
          command = { action: 'spotify_play', target: query || inputText || '' };
        } else if (browserAction === 'google_first') {
          command = { action: 'google_first', target: query || inputText || '' };
        } else if (browserAction === 'click_position') {
          command = { action: 'click_position', target: x?.toString() || '0', payload: y?.toString() || '0', extra: click_type || 'single' };
        } else if (browserAction === 'wait_click') {
          command = { action: 'wait_click', target: wait_seconds?.toString() || '1', payload: x?.toString() || '0', extra: y?.toString() || '0' };
        } else if (browserAction === 'browser_keys') {
          command = { action: 'browser_keys', target: keys || '' };
        } else if (browserAction === 'new_tab') {
          command = { action: 'new_tab', target: url || '' };
        } else if (browserAction === 'switch_tab') {
          command = { action: 'switch_tab', target: direction || 'next' };
        } else if (browserAction === 'back') {
          command = { action: 'browser_back', target: '' };
        } else if (browserAction === 'forward') {
          command = { action: 'browser_forward', target: '' };
        } else if (browserAction === 'refresh') {
          command = { action: 'browser_refresh', target: '' };
        } else if (browserAction === 'zoom') {
          command = { action: 'browser_zoom', target: direction || 'in' };
        } else if (browserAction === 'fullscreen') {
          command = { action: 'browser_fullscreen', target: '' };
        } else if (browserAction === 'find') {
          command = { action: 'browser_find', target: inputText || query || '' };
        } else {
          command = { action: browserAction, target: query || inputText || url || '' };
        }
        
        bridgeRef.current.send(JSON.stringify(authRef.current.wrapCommand(command)));
        addLog(`Browser: ${browserAction} ${query || inputText || url || ''}`, 'SYSTEM', 'success');
        result = `Browser ${browserAction.replace(/_/g, ' ')} executed, Sir.`;
      } else {
        result = "Sir, browser control requires the neural bridge.";
      }
    }

    // SCREEN READER & OCR (MODULE 14C)
    else if (toolCall.name === 'screen_reader') {
      const { action, text, paragraph_number, copy_what, identifier, click_type } = toolCall.args;
      if (bridgeRef.current?.readyState === WebSocket.OPEN) {
        let command: any = { action: 'ocr_screen' };
        
        if (action === 'read_screen') {
          command = { action: 'ocr_screen' };
        } else if (action === 'read_window') {
          command = { action: 'ocr_window' };
        } else if (action === 'find_text') {
          command = { action: 'find_text', target: text || '' };
        } else if (action === 'click_text') {
          command = { action: 'click_screen_text', target: text || '', payload: click_type || 'single' };
        } else if (action === 'click_button') {
          command = { action: 'click_button', target: text || '', payload: click_type || 'single' };
        } else if (action === 'get_paragraph') {
          command = { action: 'get_paragraph', target: paragraph_number?.toString() || '1' };
        } else if (action === 'copy_text') {
          command = { action: 'copy_screen_text', target: copy_what || 'all', payload: text || '', extra: paragraph_number?.toString() || '1' };
        } else if (action === 'find_element') {
          command = { action: 'find_element', target: identifier || '' };
        } else if (action === 'list_elements') {
          command = { action: 'list_screen_elements' };
        }
        
        bridgeRef.current.send(JSON.stringify(authRef.current.wrapCommand(command)));
        addLog(`Screen Reader: ${action} ${text || identifier || ''}`, 'SYSTEM', 'success');
        result = `Screen reader ${action?.replace(/_/g, ' ')} executed, Sir.`;
      } else {
        result = "Sir, screen reader requires the neural bridge.";
      }
    }

    if (sessionRef.current) {
      sessionRef.current.sendToolResponse({
        functionResponses: {
          id: toolCall.id,
          name: toolCall.name,
          response: { result },
        }
      });
    }
  }, [addLog, sendBridgeCommand]);

  const startLiveSession = useCallback(async () => {
    if (sessionRef.current) return;
    
    const maxRetries = keyManagerRef.current.getStats().totalNodes;
    let retryCount = 0;

    const attemptConnection = async (): Promise<boolean> => {
      // Smart key selection with cooldown awareness
      const { key: activeKey, waitMs } = keyManagerRef.current.getAvailableKeyOrWaitTime();
      
      if (!activeKey) {
        addLog("Authorization Failed: Missing Neural Key.", 'SYSTEM', 'error');
        return false;
      }

      // If all keys are in cooldown, wait for the shortest one
      if (waitMs > 0) {
        const waitSec = Math.ceil(waitMs / 1000);
        addLog(`All nodes in cooldown. Waiting ${waitSec}s for recovery...`, 'SYSTEM', 'warning');
        await new Promise(resolve => setTimeout(resolve, waitMs));
      }

      const keyStats = keyManagerRef.current.getStats();
      addLog(`Neural Node-${keyStats.activeNode} initializing... (${keyStats.healthyNodes}/${keyStats.totalNodes} healthy)`, 'SYSTEM', 'info');

      if (recognitionRef.current) try { recognitionRef.current.stop(); } catch (e) {}

      try {
        // Close previous AudioContexts to prevent leaks on retry
        if (outputAudioContextRef.current) try { outputAudioContextRef.current.close(); } catch (e) {}
        if (inputAudioContextRef.current) try { inputAudioContextRef.current.close(); } catch (e) {}
        if (mediaStreamRef.current) { mediaStreamRef.current.getTracks().forEach(t => t.stop()); mediaStreamRef.current = null; }

        const outCtx = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });
        const inCtx = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
        outputAudioContextRef.current = outCtx;
        inputAudioContextRef.current = inCtx;

        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaStreamRef.current = stream;
        const ai = new GoogleGenAI({ apiKey: activeKey });
        
        console.log('Attempting Gemini Live connection with key:', activeKey.substring(0, 10) + '...');
        const sessionPromise = ai.live.connect({
          model: 'gemini-2.5-flash-native-audio-preview-12-2025',
          callbacks: {
            onopen: () => {
              console.log('Gemini Live session OPENED successfully');
              // Mark key as successful on connection
              keyManagerRef.current.markSuccess();
              // Reset auto-reconnect counter on successful connection
              autoReconnectAttemptsRef.current = 0;
              addLog(`Node-${keyStats.activeNode} synchronized. Awaiting your command, Sir.`, 'JERRY', 'success');
              setStatus(JerryStatus.LISTENING);
              const source = inCtx.createMediaStreamSource(stream);
              const scriptProcessor = inCtx.createScriptProcessor(4096, 1, 1);
              
              // Noise gate settings
              const NOISE_GATE_THRESHOLD = 0.015; // Minimum audio level to send (adjust 0.01-0.05)
              let silenceFrames = 0;
              const MAX_SILENCE_FRAMES = 10; // Send a few silent frames after speech ends
              
              scriptProcessor.onaudioprocess = (e) => {
                if (!sessionRef.current) return; // Guard: don't send if session closed
                const inputData = e.inputBuffer.getChannelData(0);
                let sum = 0;
                for (let i = 0; i < inputData.length; i++) sum += inputData[i] * inputData[i];
                const rmsLevel = Math.sqrt(sum / inputData.length);
                setAudioLevel(rmsLevel);
                
                // Noise gate: only send audio above threshold
                const isSpeech = rmsLevel > NOISE_GATE_THRESHOLD;
                
                if (isSpeech) {
                  silenceFrames = 0; // Reset silence counter
                } else {
                  silenceFrames++;
                  // After MAX_SILENCE_FRAMES of silence, stop sending
                  if (silenceFrames > MAX_SILENCE_FRAMES) return;
                }
                
                const int16 = new Int16Array(inputData.length);
                for (let i = 0; i < inputData.length; i++) int16[i] = inputData[i] * 32768;
                try {
                  sessionRef.current.sendRealtimeInput({ media: { data: encode(new Uint8Array(int16.buffer)), mimeType: 'audio/pcm;rate=16000' } });
                } catch (e) { /* Session may have closed */ }
              };
              source.connect(scriptProcessor);
              scriptProcessor.connect(inCtx.destination);
            },
            onmessage: async (msg: LiveServerMessage) => {
              console.log('Gemini message:', msg); // Debug logging
              if (msg.toolCall) msg.toolCall.functionCalls.forEach(handleToolCall);
              if (msg.serverContent?.modelTurn) {
                const part = msg.serverContent.modelTurn.parts[0];
                if (part?.inlineData?.data) {
                  setStatus(JerryStatus.SPEAKING);
                  const data = part.inlineData.data;
                  nextAudioStartTimeRef.current = Math.max(nextAudioStartTimeRef.current, outCtx.currentTime);
                  const buffer = await decodeAudioData(decode(data), outCtx, 24000, 1);
                  const source = outCtx.createBufferSource();
                  source.buffer = buffer;
                  source.connect(outCtx.destination);
                  source.start(nextAudioStartTimeRef.current);
                  nextAudioStartTimeRef.current += buffer.duration;
                  audioSourcesRef.current.add(source);
                  source.onended = () => {
                    audioSourcesRef.current.delete(source);
                    if (audioSourcesRef.current.size === 0) setStatus(JerryStatus.LISTENING);
                  };
                }
              }
              if (msg.serverContent?.outputTranscription) addLog(msg.serverContent.outputTranscription.text, 'JERRY');
              if (msg.serverContent?.inputTranscription) {
                addLog(msg.serverContent.inputTranscription.text, 'USER');
                setStatus(JerryStatus.THINKING);
              }
            },
            onerror: (err: any) => {
              console.error('Gemini error:', err); // Debug logging
              const errorMsg = err.message || err.toString() || 'Unknown protocol error';
              const lowerError = errorMsg.toLowerCase();
              // More specific rate limit detection to avoid false positives
              const isRateLimit = (lowerError.includes('quota') && lowerError.includes('exceeded')) || 
                                lowerError.includes('resource_exhausted') ||
                                lowerError.includes('rate limit') ||
                                lowerError.includes('rate-limit') ||
                                lowerError.includes('ratelimit') ||
                                lowerError.includes('429') ||
                                (lowerError.includes('too many') && lowerError.includes('request'));
              
              if (isRateLimit && retryCount < maxRetries - 1) {
                const cooldownInfo = keyManagerRef.current.getStats();
                addLog(`Node-${keyStats.activeNode} quota exceeded (${cooldownInfo.healthyNodes} nodes healthy). Rotating...`, 'SYSTEM', 'error');
                keyManagerRef.current.rotate(); // This now marks failure and applies cooldown
                retryCount++;
                sessionRef.current = null;
                const newStats = keyManagerRef.current.getStats();
                setStats(s => ({ ...s, activeNode: newStats.activeNode }));
                // Smart delay based on cooldown status
                const { waitMs } = keyManagerRef.current.getAvailableKeyOrWaitTime();
                const delay = waitMs > 0 ? waitMs : 1500;
                setTimeout(() => attemptConnection(), delay);
              } else {
                addLog(`Neural Drift Detected: ${errorMsg}`, 'SYSTEM', 'error');
                if (retryCount >= maxRetries - 1) {
                  addLog(`All ${maxRetries} API keys exhausted. Please add new keys or wait for quota reset.`, 'SYSTEM', 'error');
                }
                setStatus(JerryStatus.SLEEPING);
                sessionRef.current = null;
              }
            },
            onclose: (event: any) => {
              console.log('Gemini Live session CLOSED:', event);
              const code = event?.code || 0;
              const reason = event?.reason || event?.code || 'No reason provided';
              const reasonStr = typeof reason === 'string' ? reason : String(reason);
              console.log('Close code:', code, 'reason:', reasonStr);
              
              // Normal close (code 1000) - handle FIRST before quota check
              const isNormalClose = code === 1000 || reasonStr === '1000';
              
              // Check if closed due to quota/rate limit - SPECIFIC phrases only
              // Generic words like "exceeded" or "limit" alone can cause false positives
              const lowerReason = reasonStr.toLowerCase();
              const isQuotaError = (lowerReason.includes('quota') && lowerReason.includes('exceeded')) || 
                                   lowerReason.includes('resource_exhausted') ||
                                   lowerReason.includes('rate limit') ||
                                   lowerReason.includes('rate-limit') ||
                                   lowerReason.includes('ratelimit') ||
                                   lowerReason.includes('429') ||
                                   (lowerReason.includes('too many') && lowerReason.includes('request'));
              
              // Only treat as quota error if NOT a normal close AND matches quota patterns
              if (!isNormalClose && isQuotaError && retryCount < maxRetries - 1) {
                const cooldownInfo = keyManagerRef.current.getStats();
                addLog(`Node-${keyStats.activeNode} quota exceeded (${cooldownInfo.healthyNodes} healthy). Rotating...`, 'SYSTEM', 'warning');
                keyManagerRef.current.rotate(); // Marks failure + applies cooldown
                retryCount++;
                sessionRef.current = null;
                const newStats = keyManagerRef.current.getStats();
                setStats(s => ({ ...s, activeNode: newStats.activeNode }));
                // Clean up before retry
                if (mediaStreamRef.current) { mediaStreamRef.current.getTracks().forEach(t => t.stop()); mediaStreamRef.current = null; }
                // Smart delay based on cooldown
                const { waitMs } = keyManagerRef.current.getAvailableKeyOrWaitTime();
                const delay = waitMs > 0 ? waitMs : 2000;
                setTimeout(() => attemptConnection(), delay);
                return;
              }
              
              // Transient/recoverable errors that should trigger auto-reconnect
              const isTransientError = reasonStr.toLowerCase().includes('operation is not') ||
                                       reasonStr.toLowerCase().includes('not implemented') ||
                                       reasonStr.toLowerCase().includes('not supported') ||
                                       reasonStr.toLowerCase().includes('not enabled') ||
                                       reasonStr.toLowerCase().includes('internal') ||
                                       reasonStr.toLowerCase().includes('temporary') ||
                                       reasonStr.toLowerCase().includes('unavailable');
              
              if (isNormalClose || isTransientError) {
                const isIdle = isNormalClose && !isTransientError;
                
                if (autoReconnectAttemptsRef.current >= maxAutoReconnectAttempts) {
                  addLog(`Max auto-reconnect attempts reached. Say 'Jerry' to re-sync.`, 'SYSTEM', 'warning');
                  autoReconnectAttemptsRef.current = 0;
                  setStatus(JerryStatus.SLEEPING);
                  sessionRef.current = null;
                  if (mediaStreamRef.current) { mediaStreamRef.current.getTracks().forEach(t => t.stop()); mediaStreamRef.current = null; }
                  if (recognitionRef.current) try { recognitionRef.current.start(); } catch (e) {}
                  return;
                }
                
                autoReconnectAttemptsRef.current++;
                const attempt = autoReconnectAttemptsRef.current;
                
                // Exponential backoff: 1.5s, 3s, 6s, 12s, 24s
                const backoffDelay = isIdle ? 1500 : Math.min(1500 * Math.pow(2, attempt - 1), 30000);
                const delaySec = (backoffDelay / 1000).toFixed(1);
                
                addLog(`${isIdle ? 'Session idle timeout' : 'Transient error detected'}. Auto-reconnecting in ${delaySec}s (attempt ${attempt}/${maxAutoReconnectAttempts})...`, 'SYSTEM', 'info');
                sessionRef.current = null;
                setStatus(JerryStatus.SLEEPING);
                
                // Clean up streams before reconnect
                if (mediaStreamRef.current) { mediaStreamRef.current.getTracks().forEach(t => t.stop()); mediaStreamRef.current = null; }
                
                // Auto-reconnect with backoff
                setTimeout(() => {
                  retryCount = 0; // Reset retry count for fresh session
                  attemptConnection();
                }, backoffDelay);
                return;
              }
              
              // Reset auto-reconnect counter on other close types
              autoReconnectAttemptsRef.current = 0;
              
              addLog(`Session closed: ${reasonStr}. Say 'Jerry' to re-sync.`, 'SYSTEM', 'warning');
              setStatus(JerryStatus.SLEEPING);
              sessionRef.current = null;
              // Stop microphone stream
              if (mediaStreamRef.current) { mediaStreamRef.current.getTracks().forEach(t => t.stop()); mediaStreamRef.current = null; }
              if (recognitionRef.current) try { recognitionRef.current.start(); } catch (e) {}
            }
          },
          config: {
            responseModalities: [Modality.AUDIO],
            systemInstruction: JERRY_SYSTEM_INSTRUCTION,
            tools: [{ functionDeclarations: JERRY_TOOLS }],
            speechConfig: { voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Charon' } } }
          }
        });
        sessionRef.current = await sessionPromise;
        return true;
      } catch (err: any) {
        const errorMsg = err.message || 'Unknown error';
        const lowerError = errorMsg.toLowerCase();
        // More specific rate limit detection
        const isRateLimit = (lowerError.includes('quota') && lowerError.includes('exceeded')) || 
                          lowerError.includes('resource_exhausted') ||
                          lowerError.includes('rate limit') ||
                          lowerError.includes('rate-limit') ||
                          lowerError.includes('ratelimit') ||
                          lowerError.includes('429') ||
                          (lowerError.includes('too many') && lowerError.includes('request'));

        if (isRateLimit && retryCount < maxRetries - 1) {
          const cooldownInfo = keyManagerRef.current.getStats();
          addLog(`Node-${keyStats.activeNode} quota exceeded (${cooldownInfo.healthyNodes} healthy). Rotating...`, 'SYSTEM', 'error');
          keyManagerRef.current.rotate(); // Marks failure + applies cooldown
          retryCount++;
          // Smart delay based on cooldown
          const { waitMs } = keyManagerRef.current.getAvailableKeyOrWaitTime();
          const delay = waitMs > 0 ? waitMs : 1000;
          await new Promise(resolve => setTimeout(resolve, delay));
          return attemptConnection();
        } else {
          addLog(`Handshake Failed: ${errorMsg}`, 'SYSTEM', 'error');
          if (retryCount >= maxRetries - 1) {
            addLog(`All ${maxRetries} nodes exhausted. Cooldowns will reset in 60s.`, 'SYSTEM', 'warning');
          }
          setStatus(JerryStatus.SLEEPING);
          return false;
        }
      }
    };

    await attemptConnection();
  }, [addLog, handleToolCall]);

  // Continuous Wake-Word Detection
  useEffect(() => {
    if (!SpeechRecognition) return;
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.lang = 'en-US';
    recognition.onresult = (e: any) => {
      const text = e.results[e.results.length - 1][0].transcript.toLowerCase();
      if (text.includes('jerry')) {
        addLog(`Voice Signature Verified. Initializing Jerry...`, 'SYSTEM', 'success');
        startLiveSession();
      }
    };
    recognition.onend = () => { 
      if (status === JerryStatus.SLEEPING) {
        try { recognition.start(); } catch (e) {}
      }
    };
    recognitionRef.current = recognition;
    recognition.start();
    return () => { try { recognition.stop(); } catch (e) {} };
  }, [status, startLiveSession, addLog]);

  // --- Cleanup AudioContext & MediaStream on unmount ---
  useEffect(() => {
    return () => {
      if (outputAudioContextRef.current) {
        try { outputAudioContextRef.current.close(); } catch (e) {}
        outputAudioContextRef.current = null;
      }
      if (inputAudioContextRef.current) {
        try { inputAudioContextRef.current.close(); } catch (e) {}
        inputAudioContextRef.current = null;
      }
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(t => t.stop());
        mediaStreamRef.current = null;
      }
      audioSourcesRef.current.forEach(src => { try { src.stop(); } catch (e) {} });
      audioSourcesRef.current.clear();
    };
  }, []);

  // --- Periodic Bridge Stats Polling ---
  useEffect(() => {
    if (!isBridgeActive) return;
    const interval = setInterval(() => {
      if (bridgeRef.current?.readyState === WebSocket.OPEN) {
        debouncedSendBridgeCommand({ action: 'system_status' });
      }
    }, 10000);
    return () => clearInterval(interval);
  }, [isBridgeActive, debouncedSendBridgeCommand]);

  const runPredictiveAction = useCallback((action: string, goal?: string) => {
    if (bridgeRef.current?.readyState !== WebSocket.OPEN) {
      addLog('Predictive tools require the neural bridge.', 'SYSTEM', 'warning');
      return;
    }
    const command: BridgeCommand = { action, target: goal || '' };
    sendBridgeCommand(command);
    addLog(`Predictive: ${action}${goal ? ' -> ' + goal : ''}`, 'SYSTEM', 'info');
  }, [addLog, sendBridgeCommand]);

  return (
    <div className="relative min-h-screen w-full flex flex-col items-stretch lg:items-center justify-center p-3 sm:p-4 lg:p-6 text-slate-200 overflow-x-hidden overflow-y-auto lg:overflow-hidden select-none font-inter">
      {/* Ambient Corner Glows */}
      <div className="fixed top-0 left-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-[150px] pointer-events-none" />
      <div className="fixed bottom-0 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-[150px] pointer-events-none" />
      
      <div className="relative z-10 w-full max-w-[1800px] min-h-0 md:min-h-[88vh] lg:h-[96vh] flex flex-col md:flex-row gap-3 sm:gap-4">
        
        {/* Left Panel: Branding & Stats */}
        <div className="w-full md:w-72 lg:w-80 flex flex-col gap-3 sm:gap-4">
          {/* Logo Header */}
          <div className="glass-card-dark p-4 sm:p-6 rounded-2xl border-l-4 border-cyan-500 shadow-2xl relative overflow-hidden holo-card">
            <div className="absolute top-0 right-0 w-20 h-20 bg-cyan-500/10 rounded-bl-full" />
            <div className="relative z-10">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-3 h-3 rounded-full bg-cyan-500 shadow-[0_0_15px_#06b6d4] animate-pulse" />
                <span className="font-hack text-[9px] tracking-[0.3em] text-cyan-500/60 uppercase">System Online</span>
              </div>
              <h1 className="font-orbitron text-4xl sm:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 tracking-tight uppercase leading-none glitch-text">
                JERRY
              </h1>
              <p className="text-[9px] text-slate-600 font-hack mt-2 tracking-[0.3em] sm:tracking-[0.5em] uppercase">
                Neural Command v7.0
              </p>
            </div>
          </div>

          {/* Dashboard Stats */}
          <div className="flex-1 overflow-visible md:overflow-hidden">
            <Dashboard stats={{...stats, security: isBridgeActive ? 100 : 20}} queuedCount={queuedCount} />
          </div>

          {/* Bridge Control Panel */}
          <div className="glass-card-dark p-5 rounded-2xl relative overflow-hidden">
            {/* Status Header */}
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center gap-3">
                <span className="text-cyan-500 text-sm">â—†</span>
                <span className="font-hack text-[10px] tracking-[0.3em] text-slate-500 uppercase">Bridge</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-[8px] text-slate-600">{isBridgeActive ? 'LINKED' : 'OFFLINE'}</span>
                <div className={`w-3 h-3 rounded-full transition-all duration-500 ${
                  isBridgeActive 
                    ? 'bg-emerald-500 shadow-[0_0_20px_#10b981]' 
                    : 'bg-red-500 shadow-[0_0_20px_#ef4444] animate-pulse'
                }`} />
              </div>
            </div>
            
            {/* Queue Indicator */}
            {queuedCount > 0 && (
              <div className="mb-4 p-2 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
                <span className="font-mono text-[10px] text-amber-400">{queuedCount} commands pending</span>
              </div>
            )}

            <div className="mb-4 flex items-center justify-between text-[9px] font-mono text-slate-600">
              <span>LATENCY: {connectionHealth.latency}ms</span>
              <span>RECONNECTS: {connectionHealth.reconnectCount}</span>
            </div>

            <div className="mb-4 grid grid-cols-2 gap-2">
              <button
                onClick={() => runPredictiveAction('predict_next')}
                className="px-3 py-2 text-[9px] font-mono uppercase tracking-wider rounded-lg border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
              >
                Predict Next
              </button>
              <button
                onClick={() => runPredictiveAction('detect_routines')}
                className="px-3 py-2 text-[9px] font-mono uppercase tracking-wider rounded-lg border border-purple-500/30 text-purple-400 hover:bg-purple-500/10"
              >
                Routines
              </button>
              <button
                onClick={() => runPredictiveAction('suggest_automation')}
                className="px-3 py-2 text-[9px] font-mono uppercase tracking-wider rounded-lg border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10"
              >
                Suggest
              </button>
              <button
                onClick={() => {
                  const goal = window.prompt('Describe the goal for the agent:');
                  if (goal) runPredictiveAction('agent_execute', goal);
                }}
                className="px-3 py-2 text-[9px] font-mono uppercase tracking-wider rounded-lg border border-amber-500/30 text-amber-400 hover:bg-amber-500/10"
              >
                Agent Goal
              </button>
            </div>

            {/* Action Button */}
            <button 
              onClick={() => status === JerryStatus.SLEEPING ? startLiveSession() : sessionRef.current?.close()}
              className={`w-full py-4 sm:py-6 font-orbitron text-[10px] sm:text-[12px] font-black tracking-[0.2em] sm:tracking-[0.6em] rounded-xl transition-all duration-300 border-2 relative overflow-hidden group ${
                status === JerryStatus.SLEEPING 
                  ? 'border-cyan-500/40 text-cyan-400 hover:bg-cyan-500/10 hover:border-cyan-400 hover:shadow-[0_0_30px_rgba(6,182,212,0.3)]' 
                  : 'border-red-500/40 text-red-400 hover:bg-red-500/10 hover:border-red-400 hover:shadow-[0_0_30px_rgba(239,68,68,0.3)]'
              }`}
            >
              <span className="relative z-10">{status === JerryStatus.SLEEPING ? '[ SYNC ]' : '[ HALT ]'}</span>
              <div className={`absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity ${
                status === JerryStatus.SLEEPING ? 'bg-gradient-to-r from-cyan-500/5 via-cyan-500/10 to-cyan-500/5' : 'bg-gradient-to-r from-red-500/5 via-red-500/10 to-red-500/5'
              }`} />
            </button>
            
            <p className="mt-4 text-[8px] text-center text-slate-700 font-mono uppercase tracking-[0.3em]">
              {isBridgeActive ? 'â— Bridge Active' : 'â—‹ Run: py jerry_bridge.py'}
            </p>
          </div>
        </div>

        {/* Center: Neural Core Orb */}
        <div className="flex-1 min-h-[40vh] sm:min-h-[45vh] md:min-h-0 glass-card-dark rounded-3xl flex flex-col items-center justify-center relative overflow-hidden border border-white/5 shadow-[inset_0_0_200px_rgba(0,0,0,0.95)]">
          {/* Corner Tech Accents */}
          <div className="absolute top-4 left-4 flex items-center gap-2">
            <div className="w-8 h-px bg-gradient-to-r from-cyan-500/50 to-transparent" />
            <span className="font-mono text-[8px] text-cyan-500/40">CORE::ACTIVE</span>
          </div>
          <div className="absolute top-4 right-4 flex items-center gap-2">
            <span className="font-mono text-[8px] text-cyan-500/40">v7.0</span>
            <div className="w-8 h-px bg-gradient-to-l from-cyan-500/50 to-transparent" />
          </div>
          <div className="absolute bottom-4 left-4 flex items-center gap-2">
            <div className="w-4 h-4 border border-cyan-500/30 rounded-sm" />
            <span className="font-mono text-[7px] text-slate-600">NEURAL_INTERFACE</span>
          </div>
          <div className="absolute bottom-4 right-4 flex items-center gap-2">
            <span className="font-mono text-[7px] text-slate-600">LATENCY: &lt;50ms</span>
            <div className="w-4 h-4 border border-cyan-500/30 rounded-sm" />
          </div>
          
          {/* The Orb */}
          <Orb status={status} audioLevel={audioLevel} />
          
          {/* Error Overlay */}
          {stats.totalNodes === 0 && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/80 backdrop-blur-md z-50">
              <div className="glass-card-dark p-8 rounded-2xl border border-red-500/30 text-center max-w-sm">
                <div className="w-14 h-14 rounded-full bg-red-500/10 border-2 border-red-500/50 flex items-center justify-center mx-auto mb-4">
                  <span className="font-bold text-red-500 text-2xl">!</span>
                </div>
                <h2 className="font-orbitron text-lg font-bold text-red-400 mb-3 tracking-wider">CONFIG ERROR</h2>
                <p className="text-slate-500 text-xs mb-4 font-mono">Missing API configuration. Please verify your environment file.</p>
                <div className="bg-black/60 p-3 rounded-lg font-mono text-[10px] text-emerald-400 border border-emerald-500/20">
                  GEMINI_API_KEY=your_key
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Panel: Terminal */}
        <div className="w-full md:w-[420px] min-h-[35vh] sm:min-h-[40vh] md:min-h-0 flex flex-col">
          <Terminal logs={logs} />
        </div>
      </div>
      
      {/* Bottom Status Bar */}
      <div className="fixed bottom-0 left-0 w-full h-1.5 bg-black/80 overflow-hidden z-50">
        <div 
          className={`h-full transition-all duration-75 relative ${
            status === JerryStatus.THINKING ? 'bg-gradient-to-r from-purple-600 to-purple-400' : 
            status === JerryStatus.EXECUTING ? 'bg-gradient-to-r from-orange-600 to-orange-400' :
            status === JerryStatus.WORKFLOW ? 'bg-gradient-to-r from-amber-600 to-amber-400' :
            status === JerryStatus.SPEAKING ? 'bg-gradient-to-r from-emerald-600 to-emerald-400' :
            'bg-gradient-to-r from-cyan-600 to-cyan-400'
          }`} 
          style={{ 
            width: `${Math.max(2, Math.min(100, audioLevel * 2500))}%`,
            boxShadow: status !== JerryStatus.SLEEPING ? '0 0 20px currentColor' : 'none'
          }}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-[holoShine_1s_linear_infinite]" />
        </div>
      </div>
    </div>
  );
};

export default App;
