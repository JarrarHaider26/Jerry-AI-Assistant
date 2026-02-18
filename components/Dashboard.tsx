
import React from 'react';
import { SystemStats } from '../types';

interface DashboardProps {
  stats: SystemStats & { 
    security: number; 
    neural: number; 
    activeNode?: number; 
    totalNodes?: number;
  };
  queuedCount?: number;
}

const Dashboard: React.FC<DashboardProps> = ({ stats, queuedCount = 0 }) => {
  return (
    <div className="flex flex-col gap-3 h-full">
      {/* Primary Stats Grid - 2x2 */}
      <div className="grid grid-cols-2 gap-2">
        <CyberStatBox 
          label="CPU" 
          value={`${(stats.cpu || 0).toFixed(1)}%`} 
          progress={stats.cpu || 0} 
          icon="◈"
          color="cyan"
          warning={stats.cpu > 80}
        />
        <CyberStatBox 
          label="RAM" 
          value={`${(stats.memory || 0).toFixed(1)}%`} 
          progress={stats.memory || 0} 
          icon="▣"
          color="purple"
          warning={stats.memory > 85}
        />
        <CyberStatBox 
          label="DISK" 
          value={`${(stats.disk || 0).toFixed(1)}%`} 
          progress={stats.disk || 0} 
          icon="◉"
          color={stats.disk > 90 ? "red" : "emerald"}
          warning={stats.disk > 90}
        />
        <CyberStatBox 
          label="NEURAL" 
          value={`${(stats.neural || 0).toFixed(1)}%`} 
          progress={stats.neural || 0} 
          icon="⬡"
          color="blue"
        />
      </div>

      {/* Battery & Security Row */}
      <div className="grid grid-cols-2 gap-2">
        <CyberStatBox 
          label="POWER" 
          value={stats.battery !== null && stats.battery !== undefined ? `${stats.battery}%` : 'N/A'} 
          progress={stats.battery || 0} 
          icon={stats.batteryCharging ? '⚡' : '◆'}
          color={stats.battery !== null && stats.battery < 20 ? "red" : "yellow"}
          warning={stats.battery !== null && stats.battery < 20}
        />
        <CyberStatBox 
          label="SECURE" 
          value={`${stats.security}%`} 
          progress={stats.security} 
          icon="◇"
          color={stats.security > 90 ? "emerald" : "red"}
        />
      </div>
      
      {/* API Node Cluster */}
      <div className="glass-card-dark p-3 rounded-xl border border-purple-500/30 relative overflow-hidden holo-card">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/5 to-transparent" />
        
        <div className="relative z-10">
          <div className="flex justify-between items-center mb-3">
            <div className="flex items-center gap-2">
              <span className="text-purple-400 text-xs">⬢</span>
              <span className="font-hack text-[9px] tracking-[0.2em] text-slate-500 uppercase">API Cluster</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse shadow-[0_0_8px_#a855f7]" />
              <span className="font-orbitron text-[10px] text-purple-400 font-bold">
                N0{stats.activeNode || 1}
              </span>
            </div>
          </div>
          
          <div className="flex justify-between items-center gap-1">
            {[...Array(Math.max(5, stats.totalNodes || 5))].map((_, i) => {
              const isActive = (stats.activeNode || 1) === i + 1;
              const isAvailable = i < (stats.totalNodes || 0);
              return (
                <div key={i} className="flex-1 flex flex-col items-center gap-1">
                  <div 
                    className={`w-full h-2 rounded transition-all duration-500 relative overflow-hidden ${
                      isAvailable 
                        ? isActive 
                          ? 'bg-purple-500 shadow-[0_0_15px_#a855f7]' 
                          : 'bg-purple-500/30' 
                        : 'bg-slate-800/50'
                    }`}
                  >
                    {isActive && (
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-[holoShine_2s_linear_infinite]" />
                    )}
                  </div>
                  <span className={`text-[7px] font-mono ${isActive ? 'text-purple-400' : 'text-slate-700'}`}>
                    {i + 1}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* System Info Panel */}
      <div className="flex-1 glass-card-dark p-3 rounded-xl border border-cyan-500/20 flex flex-col gap-3 relative overflow-hidden">
        {/* Header */}
        <div className="flex justify-between items-center pb-2 border-b border-white/5">
          <span className="font-hack text-[9px] tracking-[0.2em] text-slate-600 uppercase">System Intel</span>
          <div className="flex gap-1">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="w-1 h-1 rounded-full bg-cyan-500/40" />
            ))}
          </div>
        </div>

        {/* Network & Uptime */}
        <div className="flex justify-between items-center">
          <DataField label="NETWORK" value={stats.network || 'OFFLINE'} color="cyan" />
          <DataField label="UPTIME" value={stats.uptime} color="blue" align="right" />
        </div>

        {/* Host & OS */}
        {stats.hostname && (
          <div className="flex justify-between items-center pt-2 border-t border-white/5">
            <DataField label="HOST" value={stats.hostname} color="slate" />
            <DataField label="OS" value={stats.os || 'Unknown'} color="slate" align="right" />
          </div>
        )}

        {/* Memory & Disk Details */}
        {stats.memoryTotal > 0 && (
          <div className="flex justify-between items-center pt-2 border-t border-white/5">
            <DataField 
              label="MEM" 
              value={`${stats.memoryUsed}/${stats.memoryTotal}GB`} 
              color="purple" 
            />
            <DataField 
              label="FREE" 
              value={`${stats.diskFree}/${stats.diskTotal}GB`} 
              color="emerald" 
              align="right"
            />
          </div>
        )}

        {/* Network I/O */}
        {(stats.networkSent > 0 || stats.networkRecv > 0) && (
          <div className="flex justify-between items-center pt-2 border-t border-white/5">
            <div className="flex items-center gap-2">
              <span className="text-emerald-500 text-[10px]">↑</span>
              <span className="font-mono text-[10px] text-emerald-400">{stats.networkSent}MB</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-[10px] text-blue-400">{stats.networkRecv}MB</span>
              <span className="text-blue-500 text-[10px]">↓</span>
            </div>
          </div>
        )}

        {/* Command Queue Warning */}
        {queuedCount > 0 && (
          <div className="mt-auto pt-2 border-t border-amber-500/20">
            <div className="flex items-center justify-center gap-2 bg-amber-500/10 rounded-lg py-2">
              <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
              <span className="font-mono text-[10px] text-amber-400">
                {queuedCount} QUEUED
              </span>
            </div>
          </div>
        )}

        {/* Audio Visualizer */}
        <div className="mt-auto pt-2 border-t border-white/5">
          <div className="w-full h-6 flex items-end justify-center gap-0.5 px-2">
            {[...Array(20)].map((_, i) => (
              <div 
                key={i} 
                className="flex-1 bg-gradient-to-t from-cyan-500/60 to-cyan-400/20 rounded-t"
                style={{ 
                  height: `${15 + Math.random() * 85}%`,
                  animation: 'pulse 1.2s infinite ease-in-out',
                  animationDelay: `${i * 0.05}s`,
                  maxWidth: '4px'
                }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Cyber-styled stat box component
const CyberStatBox: React.FC<{ 
  label: string; 
  value: string; 
  progress?: number; 
  icon: string;
  color: 'cyan' | 'purple' | 'emerald' | 'red' | 'yellow' | 'blue';
  warning?: boolean;
}> = ({ label, value, progress, icon, color, warning }) => {
  const colorMap = {
    cyan: { text: 'text-cyan-400', bg: 'bg-cyan-500', border: 'border-cyan-500/30', glow: 'rgba(6, 182, 212, 0.3)' },
    purple: { text: 'text-purple-400', bg: 'bg-purple-500', border: 'border-purple-500/30', glow: 'rgba(139, 92, 246, 0.3)' },
    emerald: { text: 'text-emerald-400', bg: 'bg-emerald-500', border: 'border-emerald-500/30', glow: 'rgba(16, 185, 129, 0.3)' },
    red: { text: 'text-red-400', bg: 'bg-red-500', border: 'border-red-500/30', glow: 'rgba(239, 68, 68, 0.3)' },
    yellow: { text: 'text-yellow-400', bg: 'bg-yellow-500', border: 'border-yellow-500/30', glow: 'rgba(234, 179, 8, 0.3)' },
    blue: { text: 'text-blue-400', bg: 'bg-blue-500', border: 'border-blue-500/30', glow: 'rgba(59, 130, 246, 0.3)' },
  };

  const c = colorMap[color];

  return (
    <div 
      className={`glass-card-dark p-3 rounded-xl flex flex-col justify-between border ${c.border} group transition-all duration-300 hover:border-opacity-60 relative overflow-hidden`}
      style={{ boxShadow: warning ? `0 0 20px ${c.glow}` : 'none' }}
    >
      {/* Corner Accent */}
      <div className={`absolute top-0 right-0 w-6 h-6 ${c.border}`} style={{
        borderRight: `1px solid`,
        borderTop: `1px solid`,
        borderColor: 'inherit'
      }} />
      
      <div className="flex justify-between items-start">
        <div className="flex flex-col">
          <span className="font-hack text-[8px] tracking-[0.15em] text-slate-600 mb-1">{label}</span>
          <span className={`font-orbitron text-lg font-black ${c.text}`} style={{ textShadow: `0 0 10px ${c.glow}` }}>
            {value}
          </span>
        </div>
        <span className={`${c.text} opacity-40 text-lg`}>{icon}</span>
      </div>
      
      {progress !== undefined && (
        <div className="w-full bg-black/50 h-1.5 mt-2 rounded-full overflow-hidden border border-white/5">
          <div 
            className={`h-full ${c.bg} transition-all duration-1000 relative`} 
            style={{ width: `${Math.min(100, progress)}%` }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-[holoShine_2s_linear_infinite]" />
          </div>
        </div>
      )}
      
      {warning && (
        <div className="absolute inset-0 pointer-events-none border-2 border-red-500/20 rounded-xl animate-pulse" />
      )}
    </div>
  );
};

// Data field component
const DataField: React.FC<{ 
  label: string; 
  value: string; 
  color: string;
  align?: 'left' | 'right';
}> = ({ label, value, color, align = 'left' }) => (
  <div className={`flex flex-col ${align === 'right' ? 'items-end' : 'items-start'}`}>
    <span className="font-mono text-[7px] text-slate-700 uppercase tracking-wider">{label}</span>
    <span className={`font-mono text-[10px] text-${color}-400`}>{value}</span>
  </div>
);

export default Dashboard;
