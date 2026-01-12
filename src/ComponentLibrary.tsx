// ComponentLibrary.tsx
export const SignalMeter = ({ label, value, color }: { label: string, value: number, color: string }) => (
  <div className="flex flex-col gap-1 w-full">
    <div className="flex justify-between text-[10px] uppercase tracking-widest text-zinc-500">
      <span>{label}</span>
      <span>{Math.round(value)}%</span>
    </div>
    <div className="h-1 w-full bg-zinc-800 rounded-full overflow-hidden">
      <div 
        className={`h-full ${color} transition-all duration-1000`} 
        style={{ width: `${value}%` }} 
      />
    </div>
  </div>
);

export const LexicalBadge = ({ richness }: { richness: number }) => {
  const label = richness > 0.8 ? "High Vocabulary" : richness > 0.5 ? "Standard" : "Simplified";
  return (
    <span className="text-[9px] px-1.5 py-0.5 rounded border border-zinc-700 text-zinc-400">
      {label}
    </span>
  );
};