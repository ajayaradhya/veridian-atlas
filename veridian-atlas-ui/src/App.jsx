// src/App.jsx
import { useState, useEffect } from "react";

// Components
import Sidebar from "./components/Sidebar";
import PromptInput from "./components/PromptInput";
import ConversationView from "./components/ConversationView";
import LoadingState from "./components/LoadingState";

// API
import { askRagQuestion } from "@/api/client";

export default function App() {
  // ------------------ STATE ------------------
  const [query, setQuery] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [history, setHistory] = useState(() =>
    JSON.parse(localStorage.getItem("veridian-history") || "[]")
  );

  // ------------------ PERSIST HISTORY ------------------
  useEffect(() => {
    localStorage.setItem("veridian-history", JSON.stringify(history));
  }, [history]);

  // ------------------ RUN QUERY ------------------
  const handleAsk = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    setData(null);

    try {
      const res = await askRagQuestion(query);
      setData(res);

      // Save history without duplicate stacking
      if (!history.length || history[history.length - 1].query !== query) {
        setHistory((prev) => [...prev, { query, timestamp: new Date().toISOString() }]);
      }

    } catch (err) {
      console.error("RAG Error:", err);
      setError("Something went wrong while processing your request.");
    }

    setLoading(false);
  };

  // ------------------ RESET ------------------
  const reset = () => {
    setQuery("");
    setData(null);
    setError("");
  };

  // ------------------ RENDER ------------------
  return (
    <div className="flex min-h-screen bg-[#101010] text-gray-200 font-brand">

      {/* SIDEBAR */}
      <Sidebar
        history={history}
        setHistory={setHistory}
        onSelect={setQuery}
        onNewChat={reset}
      />

      {/* MAIN PANEL */}
      <main className="flex-1 flex flex-col items-center overflow-y-auto relative">

        {/* TOP HEADER BAR (ChatGPT-like) */}
        <header
          className="
            w-full border-b border-[#222]
            bg-[#171717]/80 backdrop-blur-md
            sticky top-0 z-40
            flex items-center justify-between px-6 py-3
          "
        >
          <h2 className="text-sm font-medium text-gray-300 tracking-wide">
            Veridian Atlas
          </h2>
          <span className="text-[11px] text-gray-500">
            RAG Engine v1 • Contract Intelligence
          </span>
        </header>

        {/* BACKDROP + RADIAL GLOW */}
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-[#1a1a1a] to-[#0f0f0f]" />
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(150,150,150,0.08),transparent_65%)]" />

        {/* LANDING PAGE (NO DATA + NOT LOADING) */}
        {!data && !loading && (
          <div className="flex flex-col items-center text-center pt-32 pb-24 max-w-3xl relative z-10">

          <div className="absolute top-24 w-96 h-32 blur-3xl bg-[#ffffff0a]" />

          <h1
            className="
              text-6xl font-bold mb-3 select-none font-brand
              bg-gradient-to-r from-[#ECECEC] via-[#D7D7D7] to-[#BEBEBE]
              bg-clip-text text-transparent
              tracking-tight leading-none
              drop-shadow-[0_0_14px_rgba(255,255,255,0.08)]
              hover:drop-shadow-[0_0_22px_rgba(255,255,255,0.12)]
              transition-all duration-300
            "
          >
            Veridian Atlas
          </h1>

          <div className="h-[1px] w-24 bg-gradient-to-r from-transparent via-gray-600 to-transparent my-3" />

          <p
            className="
              text-[15px] font-medium mb-10
              bg-gradient-to-r from-[#F0F0F0] via-[#C8C8C8] to-[#7C7C7C]
              bg-clip-text text-transparent
              tracking-tight leading-snug
            "
          >
            Precision search. Verified citations.
          </p>


          <PromptInput query={query} setQuery={setQuery} onAsk={handleAsk} />
        </div>

        )}

        {/* LOADING EXPERIENCE */}
        {loading && (
          <div className="relative z-10">
            <LoadingState />
          </div>
        )}

        {/* ANSWER RESULT CARD */}
        {!loading && (
          <div className="w-full flex justify-center relative z-10">
            <ConversationView data={data} error={error} reset={reset} />
          </div>
        )}

        {/* BOTTOM INPUT (only after answered) */}
        {data && !loading && (
          <footer
            className="
              sticky bottom-0 w-full flex justify-center
              bg-[#171717]/90 backdrop-blur-lg border-t border-[#222]
              p-6 z-40
            "
          >
            <div className="w-full max-w-3xl">
              <PromptInput query={query} setQuery={setQuery} onAsk={handleAsk} />
            </div>
          </footer>
        )}

      </main>
    </div>
  );
}
