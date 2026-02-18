
import React, { useMemo } from 'react';
import { JerryStatus } from '../types';

interface OrbProps {
  status: JerryStatus;
  audioLevel?: number;
}

const Orb: React.FC<OrbProps> = ({ status, audioLevel = 0 }) => {
  const { coreColor, rgbColor, statusLabel } = useMemo(() => {
    switch (status) {
      case JerryStatus.LISTENING: 
        return { coreColor: '#06b6d4', rgbColor: '6, 182, 212', statusLabel: 'LISTENING' };
      case JerryStatus.THINKING: 
        return { coreColor: '#8b5cf6', rgbColor: '139, 92, 246', statusLabel: 'PROCESSING' };
      case JerryStatus.SPEAKING: 
        return { coreColor: '#10b981', rgbColor: '16, 185, 129', statusLabel: 'TRANSMITTING' };
      case JerryStatus.EXECUTING: 
        return { coreColor: '#f97316', rgbColor: '249, 115, 22', statusLabel: 'EXECUTING' };
      case JerryStatus.WORKFLOW: 
        return { coreColor: '#eab308', rgbColor: '234, 179, 8', statusLabel: 'WORKFLOW' };
      default: 
        return { coreColor: '#475569', rgbColor: '71, 85, 105', statusLabel: 'STANDBY' };
    }
  }, [status]);

  const isActive = status !== JerryStatus.SLEEPING;
  const scale = 1 + (audioLevel * 0.8);
  const glowIntensity = 30 + (audioLevel * 200);

  return (
    <div className="relative flex items-center justify-center w-[32rem] h-[32rem]">
      {/* Background Hexagon Pattern */}
      <div className="absolute inset-0 opacity-10">
        <svg className="w-full h-full" viewBox="0 0 100 100">
          <defs>
            <pattern id="hexagons" width="10" height="17.32" patternUnits="userSpaceOnUse">
              <polygon 
                points="5,0 10,2.89 10,8.66 5,11.55 0,8.66 0,2.89" 
                fill="none" 
                stroke={coreColor} 
                strokeWidth="0.2"
                opacity="0.3"
              />
            </pattern>
          </defs>
          <circle cx="50" cy="50" r="48" fill="url(#hexagons)" className={isActive ? 'animate-pulse' : ''} />
        </svg>
      </div>

      {/* Outer Data Ring */}
      <svg className="absolute w-full h-full" viewBox="0 0 100 100">
        <defs>
          <linearGradient id="ringGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={coreColor} stopOpacity="0.8" />
            <stop offset="50%" stopColor={coreColor} stopOpacity="0.2" />
            <stop offset="100%" stopColor={coreColor} stopOpacity="0.8" />
          </linearGradient>
        </defs>
        
        {/* Outer Tech Lines */}
        <circle 
          cx="50" cy="50" r="48" 
          fill="none" 
          stroke={coreColor} 
          strokeWidth="0.15" 
          strokeDasharray="2 4 8 4" 
          className={isActive ? 'animate-[spin_60s_linear_infinite]' : ''}
          opacity="0.4"
        />
        
        {/* Secondary Ring with Markers */}
        <circle 
          cx="50" cy="50" r="45" 
          fill="none" 
          stroke={coreColor} 
          strokeWidth="0.3" 
          strokeDasharray="1 9" 
          className={isActive ? 'animate-[spin_30s_linear_infinite_reverse]' : ''}
          opacity="0.5"
        />

        {/* Data Arc Segments */}
        {[0, 60, 120, 180, 240, 300].map((angle, i) => (
          <path
            key={i}
            d={`M ${50 + 42 * Math.cos((angle - 25) * Math.PI / 180)} ${50 + 42 * Math.sin((angle - 25) * Math.PI / 180)} 
                A 42 42 0 0 1 ${50 + 42 * Math.cos((angle + 25) * Math.PI / 180)} ${50 + 42 * Math.sin((angle + 25) * Math.PI / 180)}`}
            fill="none"
            stroke={coreColor}
            strokeWidth="1.5"
            opacity={isActive ? 0.6 : 0.2}
            className={isActive ? 'animate-pulse' : ''}
            style={{ animationDelay: `${i * 0.1}s` }}
          />
        ))}

        {/* Targeting Crosshairs */}
        <g opacity={isActive ? 0.4 : 0.1}>
          <line x1="50" y1="5" x2="50" y2="15" stroke={coreColor} strokeWidth="0.5" />
          <line x1="50" y1="85" x2="50" y2="95" stroke={coreColor} strokeWidth="0.5" />
          <line x1="5" y1="50" x2="15" y2="50" stroke={coreColor} strokeWidth="0.5" />
          <line x1="85" y1="50" x2="95" y2="50" stroke={coreColor} strokeWidth="0.5" />
        </g>

        {/* Corner Brackets */}
        {[[15, 15], [85, 15], [15, 85], [85, 85]].map(([x, y], i) => (
          <g key={i} opacity={isActive ? 0.6 : 0.2}>
            <path
              d={i === 0 ? `M ${x} ${y+5} L ${x} ${y} L ${x+5} ${y}` :
                 i === 1 ? `M ${x-5} ${y} L ${x} ${y} L ${x} ${y+5}` :
                 i === 2 ? `M ${x} ${y-5} L ${x} ${y} L ${x+5} ${y}` :
                          `M ${x-5} ${y} L ${x} ${y} L ${x} ${y-5}`}
              fill="none"
              stroke={coreColor}
              strokeWidth="0.8"
            />
          </g>
        ))}

        {/* Audio Reactive Ring */}
        <circle 
          cx="50" cy="50" 
          r={38 + audioLevel * 8} 
          fill="none" 
          stroke={coreColor} 
          strokeWidth="0.3" 
          opacity={0.3 + audioLevel}
          className="transition-all duration-75"
        />

        {/* Inner Tech Ring */}
        <circle 
          cx="50" cy="50" r="35" 
          fill="none" 
          stroke={coreColor} 
          strokeWidth="2" 
          strokeDasharray="3 20" 
          className={isActive ? 'animate-[spin_20s_linear_infinite]' : ''}
          opacity="0.4"
        />
      </svg>

      {/* Pulse Rings */}
      {isActive && (
        <>
          <div 
            className="absolute inset-4 rounded-full animate-ring" 
            style={{ border: `1px solid rgba(${rgbColor}, 0.3)` }}
          />
          <div 
            className="absolute inset-16 rounded-full animate-ring" 
            style={{ border: `1px solid rgba(${rgbColor}, 0.2)`, animationDelay: '1s' }}
          />
          <div 
            className="absolute inset-24 rounded-full animate-ring" 
            style={{ border: `1px solid rgba(${rgbColor}, 0.1)`, animationDelay: '2s' }}
          />
        </>
      )}

      {/* The Core - Arc Reactor Style */}
      <div 
        className="relative z-10 w-52 h-52 rounded-full transition-all duration-100 flex items-center justify-center"
        style={{ 
          transform: `scale(${scale})`,
          boxShadow: `0 0 ${glowIntensity}px rgba(${rgbColor}, 0.4), 0 0 ${glowIntensity * 2}px rgba(${rgbColor}, 0.2)`,
        }}
      >
        {/* Outer Core Ring */}
        <div 
          className="absolute inset-0 rounded-full"
          style={{
            background: `conic-gradient(from 0deg, transparent, rgba(${rgbColor}, 0.3), transparent, rgba(${rgbColor}, 0.3), transparent)`,
            animation: isActive ? 'spin 4s linear infinite' : 'none'
          }}
        />
        
        {/* Core Container */}
        <div 
          className="w-44 h-44 rounded-full flex items-center justify-center relative overflow-hidden"
          style={{
            background: `radial-gradient(circle at 30% 30%, rgba(${rgbColor}, 0.1) 0%, #000000 60%, #000000 100%)`,
            border: `2px solid rgba(${rgbColor}, 0.4)`,
            boxShadow: `inset 0 0 40px rgba(0,0,0,0.8), inset 0 0 20px rgba(${rgbColor}, 0.1)`
          }}
        >
          {/* Inner Glow */}
          <div 
            className="absolute inset-0 animate-pulse"
            style={{ 
              background: `radial-gradient(circle, rgba(${rgbColor}, 0.2) 0%, transparent 50%)`,
              animationDuration: '2s'
            }}
          />

          {/* Rotating Inner Elements */}
          <div 
            className="absolute inset-4 rounded-full"
            style={{
              border: `1px solid rgba(${rgbColor}, 0.3)`,
              animation: isActive ? 'spin 10s linear infinite reverse' : 'none'
            }}
          >
            {/* Notch Markers */}
            {[0, 45, 90, 135, 180, 225, 270, 315].map((angle, i) => (
              <div
                key={i}
                className="absolute w-1 h-3 rounded-full"
                style={{
                  background: coreColor,
                  opacity: 0.5,
                  left: '50%',
                  top: '0',
                  transform: `translateX(-50%) rotate(${angle}deg)`,
                  transformOrigin: '50% 70px'
                }}
              />
            ))}
          </div>

          {/* Center Nucleus */}
          <div className="relative w-20 h-20 flex items-center justify-center">
            {/* Outer Square */}
            <div 
              className={`absolute inset-0 transition-all duration-700 ${isActive ? 'rotate-45' : 'rotate-0'}`}
              style={{ 
                border: `2px solid ${coreColor}`,
                borderRadius: '20%',
                boxShadow: `0 0 15px rgba(${rgbColor}, 0.5), inset 0 0 15px rgba(${rgbColor}, 0.2)`
              }}
            />
            
            {/* Inner Square */}
            <div 
              className={`absolute inset-3 transition-all duration-1000 ${isActive ? '-rotate-45 scale-90' : 'rotate-0'}`}
              style={{ 
                border: `1px solid ${coreColor}`,
                opacity: 0.6,
                borderRadius: '15%'
              }}
            />

            {/* Center Orb */}
            <div 
              className="w-6 h-6 rounded-full"
              style={{
                background: `radial-gradient(circle at 30% 30%, white, ${coreColor})`,
                boxShadow: `0 0 20px ${coreColor}, 0 0 40px rgba(${rgbColor}, 0.5), 0 0 60px rgba(${rgbColor}, 0.3)`
              }}
            />
          </div>

          {/* Scanning Line */}
          {isActive && (
            <div className="absolute inset-0 overflow-hidden rounded-full">
              <div 
                className="w-full h-0.5 absolute"
                style={{
                  background: `linear-gradient(90deg, transparent, ${coreColor}, transparent)`,
                  animation: 'scan 2.5s linear infinite',
                  top: '0'
                }}
              />
            </div>
          )}
        </div>
      </div>

      {/* Status HUD Display */}
      <div className="absolute -bottom-24 left-1/2 -translate-x-1/2 flex flex-col items-center">
        {/* Connector Line */}
        <div 
          className="w-px h-16 mb-4"
          style={{
            background: `linear-gradient(to top, rgba(${rgbColor}, 0.6), transparent)`
          }}
        />
        
        {/* Status Badge */}
        <div 
          className="glass-card px-6 py-2 rounded-full relative overflow-hidden"
          style={{ 
            border: `1px solid rgba(${rgbColor}, 0.4)`,
            boxShadow: `0 0 20px rgba(${rgbColor}, 0.2)`
          }}
        >
          {/* Animated Background */}
          <div 
            className="absolute inset-0 opacity-20"
            style={{
              background: `linear-gradient(90deg, transparent, rgba(${rgbColor}, 0.3), transparent)`,
              animation: 'holoShine 3s linear infinite'
            }}
          />
          
          <div className="flex items-center gap-3">
            <div 
              className={`w-2 h-2 rounded-full ${isActive ? 'status-pulse' : ''}`}
              style={{ 
                backgroundColor: coreColor,
                color: coreColor
              }}
            />
            <span 
              className="font-orbitron text-[10px] font-black tracking-[0.4em] uppercase"
              style={{ 
                color: coreColor,
                textShadow: `0 0 10px rgba(${rgbColor}, 0.8)`
              }}
            >
              {statusLabel}
            </span>
          </div>
        </div>

        {/* Activity Indicators */}
        <div className="mt-3 flex gap-2">
          {[...Array(7)].map((_, i) => (
            <div 
              key={i} 
              className="w-1 rounded-full transition-all duration-150"
              style={{ 
                height: isActive ? `${8 + Math.random() * 16}px` : '4px',
                backgroundColor: coreColor,
                opacity: isActive ? 0.3 + (Math.random() * 0.7) : 0.2,
                animation: isActive ? `pulse 0.8s infinite alternate ${i * 0.1}s` : 'none',
                boxShadow: isActive ? `0 0 5px rgba(${rgbColor}, 0.5)` : 'none'
              }}
            />
          ))}
        </div>
      </div>

      {/* Corner Data Readouts */}
      <div className="absolute top-4 left-4 font-mono text-[8px] opacity-40" style={{ color: coreColor }}>
        <div>SYS://NEURAL_CORE</div>
        <div>VER: 7.0</div>
      </div>
      <div className="absolute top-4 right-4 font-mono text-[8px] text-right opacity-40" style={{ color: coreColor }}>
        <div>FREQ: {(440 + audioLevel * 1000).toFixed(0)}Hz</div>
        <div>AMP: {(audioLevel * 100).toFixed(1)}%</div>
      </div>
    </div>
  );
};

export default Orb;
