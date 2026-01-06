import { useEffect, useState } from "react";

interface Article {
  id: string;
  source: string;
  headline: string;
  summary: string;
  url: string;
  published_at: string;
  bias_score: number;
}

interface Story {
  story_id: string;
  topic: string;
  articles: Article[];
}

const SOURCE_META: Record<
  string,
  { label: string; bg: string; text: string }
> = {
  bbc: { label: "BBC", bg: "bg-red-600", text: "text-white" },
  guardian: { label: "Guardian", bg: "bg-blue-600", text: "text-white" },
  independent: { label: "Independent", bg: "bg-gray-700", text: "text-white" },
  sky: { label: "Sky", bg: "bg-sky-600", text: "text-white" },
  metro: { label: "Metro", bg: "bg-yellow-400", text: "text-black" },
  standard: { label: "Evening Standard", bg: "bg-purple-600", text: "text-white" },
};

const biasLabel = (bias: number) => {
  if (bias < -0.4) return "Left"
  if (bias < -0.15) return "Centre-left"
  if (bias <= 0.15) return "Centre"
  if (bias <= 0.4) return "Centre-right"
  return "Right"
}

const biasColor = (bias: number) => {
  if (bias < -0.4) return "bg-blue-500"
  if (bias < -0.15) return "bg-blue-300"
  if (bias <= 0.15) return "bg-zinc-400"
  if (bias <= 0.4) return "bg-red-300"
  return "bg-red-500"
}

// maps [-1,1] → [0,100]
const biasPosition = (bias: number) =>
  Math.min(100, Math.max(0, (bias + 1) * 50))

export default function App() {
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStories() {
      const res = await fetch("/api/stories");
      const data = await res.json();

      const filtered = (data.stories ?? []).filter(
        (s: Story) => s.articles.length >= 2
      );

      setStories(filtered);
      setLoading(false);
    }

    fetchStories();
  }, []);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      {/* Header */}
      <header className="border-b border-zinc-800">
        <div className="max-w-5xl mx-auto px-6 py-6">
          <h1 className="text-3xl font-bold tracking-tight">
            UK News Decoded
          </h1>
          <p className="text-zinc-400 mt-1">
            One story. Multiple sources.
          </p>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-5xl mx-auto px-6 py-10">
        {loading && (
          <p className="text-zinc-400 text-center">Loading stories…</p>
        )}

        <div className="space-y-8">
          {stories.map((story) => (
            <div
              key={story.story_id}
              className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 shadow-sm"
            >
              {/* Topic */}
              <h2 className="text-lg font-semibold mb-4 text-zinc-200">
                {story.topic}
              </h2>

              {/* Articles */}
              <div className="space-y-4">
                {story.articles.map((article) => {
                  const meta =
                    SOURCE_META[article.source] ??
                    { label: article.source, bg: "bg-zinc-700", text: "text-white" };

                  return (
                    <a
                      key={article.id}
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="relative block p-4 rounded-lg bg-zinc-800 hover:bg-zinc-700 transition"
                    >
                      <div className="flex gap-4">
                        {/* Main content */}
                        <div className="flex items-start gap-3 flex-1">
                          {/* Source badge */}
                          <div
                            className={`px-2 py-1 rounded text-xs font-semibold ${meta.bg} ${meta.text}`}
                          >
                            {meta.label}
                          </div>

                          {/* Text */}
                          <div>
                            <h3 className="font-medium leading-snug">
                              {article.headline}
                            </h3>
                            {article.summary && (
                              <p className="text-sm text-zinc-400 mt-1 line-clamp-2">
                                {article.summary.replace(/<[^>]+>/g, "")}
                              </p>
                            )}
                          </div>
                        </div>

                        {/* Bias indicator */}
                        <div className="flex flex-col items-center gap-2 w-12">
                          {/* Bar */}
                          <div className="relative h-full w-2 bg-zinc-600 rounded">
                            {/* Slider */}
                            <div
                              className={`absolute left-1/2 -translate-x-1/2 w-4 h-2 rounded ${biasColor(
                                article.bias_score
                              )}`}
                              style={{
                                top: `${100 - biasPosition(article.bias_score)}%`,
                              }}
                            />
                          </div>

                          {/* Label */}
                          <span className="text-xs text-zinc-400 text-center leading-tight">
                            {biasLabel(article.bias_score)}
                          </span>
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
    </div>
  );
}