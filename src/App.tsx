import { useEffect, useState } from "react";

interface Article {
  id: string;
  source: string;
  headline: string;
  summary: string;
  url: string;
  published_at: string;
  bias_score: number;
  lexical_richness: number;
  readability_score: number;
  propaganda_density: number;
  primary_tactic: string;
}

interface Story {
  story_id: string;
  topic: string;
  articles: Article[];
}

const SOURCE_META: Record<string, { label: string; bg: string; text: string }> = {
  bbc: { label: "BBC", bg: "bg-red-600", text: "text-white" },
  guardian: { label: "Guardian", bg: "bg-blue-600", text: "text-white" },
  independent: { label: "Independent", bg: "bg-zinc-800", text: "text-white" },
  sky: { label: "Sky", bg: "bg-sky-600", text: "text-white" },
  metro: { label: "Metro", bg: "bg-yellow-400", text: "text-black" },
  standard: { label: "The Standard", bg: "bg-purple-600", text: "text-white" },
  telegraph: { label: "Telegraph", bg: "bg-orange-600", text: "text-white" },
  dailymail: { label: "Daily Mail", bg: "bg-pink-600", text: "text-white" },
  mirror: { label: "Mirror", bg: "bg-red-800", text: "text-white" },
  gbnews: { label: "GB News", bg: "bg-green-600", text: "text-white" },
  reuters: { label: "Reuters", bg: "bg-gray-500", text: "text-white" },
  times: { label: "The Times", bg: "bg-yellow-700", text: "text-black" },
  morningstar: { label: "Morning Star", bg: "bg-red-700", text: "text-white" },
  novara: { label: "Novara", bg: "bg-pink-700", text: "text-white" },
  unherd: { label: "UnHerd", bg: "bg-zinc-600", text: "text-white" },
  spectator: { label: "Spectator", bg: "bg-red-900", text: "text-white" },
};

const getBiasLabel = (bias: number) => {
  if (bias <= -1.1) return "Far left";
  if (bias <= -0.5) return "Left";
  if (bias < -0.1) return "Centre-left";
  if (bias <= 0.1) return "Centre";
  if (bias <= 0.5) return "Centre-right";
  if (bias <= 1.1) return "Right";
  return "Far right";
};

const getBiasColor = (bias: number) => {
  if (Math.abs(bias) <= 0.1) return "#71717a";
  if (bias < 0) return bias < -0.75 ? "#1e40af" : "#3b82f6";
  return bias > 0.75 ? "#991b1b" : "#ef4444";
};

const SignalMeter = ({ label, value, color, multiplier = 1 }: { label: string; value: number; color: string; multiplier?: number }) => (
  <div className="flex flex-col gap-1 w-full">
    <div className="flex justify-between text-[9px] uppercase tracking-widest text-zinc-500 font-bold">
      <span>{label}</span>
      <span>{value.toFixed(1)}%</span>
    </div>
    <div className="h-1 w-full bg-zinc-800 rounded-full overflow-hidden">
      <div 
        className={`h-full ${color} transition-all duration-700`} 
        style={{ width: `${Math.min(100, value * multiplier)}%` }} 
      />
    </div>
  </div>
);

export default function App() {
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/stories")
      .then(res => res.json())
      .then(data => {
        setStories(data.stories || []);
        setLoading(false);
      });
  }, []);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 font-sans">
      <header className="border-b border-zinc-900 sticky top-0 bg-zinc-950/90 backdrop-blur-sm z-50">
        <div className="max-w-5xl mx-auto px-6 py-6">
          <h1 className="text-3xl font-black tracking-tight uppercase">UK News Decoded</h1>
          <p className="text-zinc-500 text-sm">Automated narrative analysis across the spectrum.</p>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-10">
        {loading && <p className="text-zinc-500 text-center animate-pulse">Analyzing feeds...</p>}
        
        <div className="space-y-12">
          {stories.map((story) => (
            <div key={story.story_id} className="bg-zinc-900/30 border border-zinc-900 rounded-2xl overflow-hidden shadow-xl">
              <div className="p-5 border-b border-zinc-900 bg-zinc-900/50">
                <h2 className="text-xl font-bold">{story.topic}</h2>
              </div>
              
              <div className="p-2 space-y-2">
                {story.articles.map((article) => {
                  const meta = SOURCE_META[article.source] || { label: article.source, bg: "bg-zinc-800", text: "text-white" };
                  
                  const lexicalLabel = 
                    article.lexical_richness > 0.85 ? "High Lexical Depth" : 
                    article.lexical_richness > 0.65 ? "Med Lexical Depth" : 
                    "Standard Lexical Depth";

                  const activeTactic = article.primary_tactic?.toLowerCase();
                  const hasTactic = activeTactic && activeTactic !== "none";

                  return (
                    <a 
                      key={article.id} 
                      href={article.url} 
                      target="_blank" 
                      className="group flex gap-6 p-4 rounded-xl hover:bg-zinc-800/50 transition-all border border-transparent hover:border-zinc-800"
                    >
                      {/* Analysis Left Column */}
                      <div className="flex flex-col items-center justify-center w-20 shrink-0 border-r border-zinc-800 pr-4">
                         <div className="w-1.5 h-16 bg-zinc-800 rounded-full relative overflow-hidden">
                            <div className="absolute top-1/2 left-0 w-full h-[1px] bg-zinc-700 z-10" />
                            <div 
                              className="absolute left-0 w-full transition-all duration-500" 
                              style={{
                                height: `${(Math.abs(article.bias_score) / 1.5) * 50}%`,
                                top: article.bias_score >= 0 ? "50%" : "auto",
                                bottom: article.bias_score < 0 ? "50%" : "auto",
                                backgroundColor: getBiasColor(article.bias_score)
                              }} 
                            />
                         </div>
                         <span className="text-[8px] mt-2 uppercase font-bold text-zinc-500 text-center">
                            {getBiasLabel(article.bias_score)}
                         </span>
                      </div>

                      {/* Content Middle */}
                      <div className="flex-1 space-y-2">
                        <div className="flex items-center gap-2">
                           <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase ${meta.bg} ${meta.text}`}>
                              {meta.label}
                           </span>
                           <span className="text-[8px] border border-zinc-700 px-1.5 py-0.5 rounded text-zinc-500 uppercase font-bold">
                              {lexicalLabel}
                           </span>
                           {hasTactic && (
                              <span className="text-[8px] bg-amber-500/10 text-amber-500 border border-amber-500/30 px-2 py-0.5 rounded font-black tracking-tighter uppercase italic">
                                 ◢ {article.primary_tactic}
                              </span>
                           )}
                        </div>
                        <div>
                          <h3 className="font-semibold leading-snug group-hover:text-white transition-colors text-zinc-200">
                            {article.headline}
                          </h3>
                          <p className="text-xs text-zinc-500 mt-1 line-clamp-2 leading-relaxed">
                            {article.summary}
                          </p>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 pt-1">
                          <SignalMeter 
                            label="Narrative Intensity" 
                            value={article.propaganda_density || 0} 
                            multiplier={10} 
                            color="bg-amber-500" 
                          />
                          <SignalMeter 
                            label="Reading Ease" 
                            value={article.readability_score || 0} 
                            color="bg-sky-500" 
                          />
                        </div>
                      </div>
                    </a>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </main>
      
      <footer className="py-12 border-t border-zinc-900 text-center">
        <p className="text-[10px] text-zinc-600 uppercase tracking-widest px-6">
          Bias and narrative metrics estimated using automated linguistic markers (Ad Fontes / AllSides Standards).
        </p>
      </footer>
    </div>
  );
}