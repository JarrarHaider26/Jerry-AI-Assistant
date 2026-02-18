
import React, { useEffect, useRef, useState } from 'react';
import { LogEntry } from '../types';

interface TerminalProps {
  logs: LogEntry[];
}

const Terminal: React.FC<TerminalProps> = ({ logs }) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString('en-US', { hour12: false }));

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString('en-US', { hour12: false }));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const getSourceStyle = (source: LogEntry['source']) => {
    switch (source) {
      case 'JERRY': return 'text-cyan-400 glow-text-cyan';
      case 'USER': return 'text-blue-400';
      case 'BRIDGE': return 'text-emerald-400 glow-text-green';
      case 'WORKFLOW': return 'text-amber-400';
      default: return 'text-slate-500';
    }
  };

  const getTypeStyle = (type: LogEntry['type']) => {
    switch (type) {
      case 'error': return 'text-red-500 font-bold';
      case 'success': return 'text-emerald-400';
      case 'command': return 'text-amber-400 italic';
      case 'warning': return 'text-yellow-400 font-semibold';
      case 'alert': return 'text-red-400 font-bold animate-pulse';
      default: return 'text-slate-300';
    }
  };

  return (
    <div className="glass-card-dark flex-1 h-full overflow-hidden flex flex-col rounded-2xl border border-cyan-500/20 relative corner-accent">
      {/* Scan Line Effect */}
      <div className="scan-line" />
      
      {/* Terminal Header */}
      <div className="bg-black/60 px-5 py-3 flex items-center justify-between border-b border-cyan-500/20 relative">
        {/* Window Controls */}
        <div className="flex items-center gap-4">
          <div className="flex gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500/60 hover:bg-red-500 transition-colors cursor-pointer shadow-[0_0_8px_rgba(239,68,68,0.5)]"></div>
            <div className="w-3 h-3 rounded-full bg-yellow-500/60 hover:bg-yellow-500 transition-colors cursor-pointer shadow-[0_0_8px_rgba(234,179,8,0.5)]"></div>
            <div className="w-3 h-3 rounded-full bg-emerald-500/60 hover:bg-emerald-500 transition-colors cursor-pointer shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
          </div>
          <div className="h-4 w-px bg-cyan-500/20"></div>
          <span className="font-hack text-[10px] tracking-[0.2em] text-cyan-500/80 uppercase">
            sys://neural_terminal
          </span>
        </div>
        
        {/* Status Indicators */}
        <div className="flex items-center gap-4">
          <span className="font-mono text-[9px] text-slate-600">{currentTime}</span>
          <div className="flex items-center gap-2">
            <span className="font-mono text-[8px] text-emerald-500/60">SECURE</span>
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_10px_#10b981]"></div>
          </div>
        </div>
      </div>

      {/* Command Path Bar */}
      <div className="bg-black/40 px-5 py-2 border-b border-cyan-500/10 flex items-center gap-2">
        <span className="text-emerald-500 font-mono text-[10px]">root@jerry</span>
        <span className="text-slate-600 font-mono text-[10px]">:</span>
        <span className="text-blue-400 font-mono text-[10px]">~/neural_core</span>
        <span className="text-slate-600 font-mono text-[10px]">$</span>
        <span className="text-cyan-400/60 font-mono text-[10px] ml-1">stream --mode=realtime</span>
      </div>

      {/* Log Output Area */}
      <div 
        ref={scrollRef}
        className="flex-1 p-4 font-mono text-[11px] overflow-y-auto space-y-2 bg-black/30"
        style={{
          backgroundImage: 'linear-gradient(rgba(6, 182, 212, 0.02) 1px, transparent 1px)',
          backgroundSize: '100% 20px'
        }}
      >
        {logs.length === 0 && (
          <div className="flex flex-col gap-2 text-slate-600">
            <div className="flex items-center gap-2">
              <span className="text-emerald-500">$</span>
              <span className="animate-pulse">Initializing neural interface...</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-emerald-500">$</span>
              <span className="opacity-50">Awaiting voice authorization...</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-emerald-500">$</span>
              <span className="opacity-30">Say "Jerry" to establish connection</span>
            </div>
          </div>
        )}
        
        {logs.map((log, index) => (
          <div 
            key={log.id} 
            className="group flex gap-3 leading-relaxed hover:bg-cyan-500/5 px-2 py-1 -mx-2 rounded transition-colors"
            style={{ 
              animation: 'fadeIn 0.3s ease-out',
              animationDelay: `${index * 0.02}s`
            }}
          >
            {/* Timestamp */}
            <span className="text-slate-700 font-bold select-none whitespace-nowrap opacity-60 group-hover:opacity-100 transition-opacity">
              [{log.timestamp}]
            </span>
            
            {/* Source Badge */}
            <span className={`font-black select-none tracking-tight ${getSourceStyle(log.source)} min-w-[70px]`}>
              {log.source === 'JERRY' && <span className="text-cyan-600 mr-1">&gt;</span>}
              {log.source === 'USER' && <span className="text-blue-600 mr-1">&lt;</span>}
              {log.source === 'BRIDGE' && <span className="text-emerald-600 mr-1">~</span>}
              {log.source === 'WORKFLOW' && <span className="text-amber-600 mr-1">@</span>}
              {log.source === 'SYSTEM' && <span className="text-slate-600 mr-1">#</span>}
              {log.source}
            </span>
            
            {/* Message Content */}
            <span className={`flex-1 ${getTypeStyle(log.type)}`}>
              {log.type === 'command' && <span className="text-slate-600 mr-1">$</span>}
              {log.message}
            </span>
          </div>
        ))}
        
        {/* Blinking Cursor */}
        <div className="flex items-center gap-2 text-cyan-500/60 mt-2">
          <span className="text-emerald-500">$</span>
          <span className="cursor-blink">_</span>
        </div>
      </div>

      {/* Terminal Footer */}
      <div className="bg-black/60 px-5 py-2 border-t border-cyan-500/20 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span className="font-mono text-[8px] text-slate-600">ENTRIES: {logs.length}</span>
          <span className="font-mono text-[8px] text-slate-700">|</span>
          <span className="font-mono text-[8px] text-slate-600">BUFFER: 200</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex gap-1">
            {[...Array(8)].map((_, i) => (
              <div 
                key={i} 
                className="w-1 bg-cyan-500/40 rounded-full"
                style={{ 
                  height: `${4 + Math.random() * 8}px`,
                  animation: 'pulse 1s infinite alternate',
                  animationDelay: `${i * 0.1}s`
                }}
              />
            ))}
          </div>
          <span className="font-mono text-[8px] text-cyan-500/60">STREAM ACTIVE</span>
        </div>
      </div>
    </div>
  );
};

export default Terminal;
