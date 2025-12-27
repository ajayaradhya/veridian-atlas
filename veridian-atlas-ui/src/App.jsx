// src/App.jsx
import { useState, useEffect } from "react";

// Components
import Sidebar from "./components/Sidebar";
import PromptInput from "./components/PromptInput";
import ConversationView from "./components/ConversationView";
import LoadingState from "./components/LoadingState";
import AppHeader from "./components/AppHeader";

// API
import { askRagQuestion } from "@/api/client";

export default function App() {
  const [query, setQuery] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState(() =>
    JSON.parse(localStorage.getItem("veridian-history") || "[]")
  );

  useEffect(() => {
    localStorage.setItem("veridian-history", JSON.stringify(history));
  }, [history]);

  const handleAsk = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setData(null);

    try {
      const res = await askRagQuestion(query);
      setData(res);

      if (!history.length || history[history.length - 1].query !== query) {
        setHistory((prev) => [...prev, { query, timestamp: new Date().toISOString() }]);
      }

    } catch (err) {
      setError("Something went wrong while processing your request.");
    }

    setLoading(false);
  };

  const reset = () => {
    setQuery("");
    setData(null);
    setError("");
  };

  return (
    <div className="flex min-h-screen bg-[#101010] text-gray-200 font-brand">

      {/* LEFT SIDEBAR */}
      <Sidebar
        history={history}
        setHistory={setHistory}
        onSelect={setQuery}
        onNewChat={reset}
      />

      {/* MAIN PANEL */}
      <main className="flex-1 flex flex-col items-center overflow-y-auto relative">

        {/* TOP HEADER BAR */}
        <AppHeader />

        {/* BACKDROP GLOW (center-out, smooth) */}
        <div className="pointer-events-none absolute inset-0">

          {/* Base gradient from center outward */}
          <div className="
            absolute inset-0
            bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.12)_0%,rgba(0,0,0,0)_75%)]
          " />

          {/* Vertical fade for depth */}
          <div className="
            absolute inset-0
            bg-gradient-to-b from-transparent via-[#0c0c0c66] to-[#0b0b0b]
          " />

          {/* Subtle center highlight */}
          <div className="
            absolute inset-0
            bg-[radial-gradient(circle_at_center,rgba(200,200,200,0.04),transparent_60%)]
            blur-3xl
          " />
        </div>

        {/* LANDING SCREEN */}
        {!data && !loading && (
          <div className="flex flex-col items-center text-center pt-32 pb-24 relative z-10 max-w-3xl">

            {/* TITLE */}
            <h1
              className="
                text-6xl font-bold mb-3 select-none
                bg-gradient-to-r from-[#EDEDED] via-[#D7D7D7] to-[#AFAFAF]
                bg-clip-text text-transparent
                tracking-tight leading-none
              "
            >
              Veridian Atlas
            </h1>

            {/* UNDERLINE */}
            <div className="h-[2px] w-4/5 bg-gradient-to-r from-transparent via-gray-100 to-transparent rounded-full opacity-60 mb-5" />

            {/* TAGLINE */}
            <p
              className="
                text-[15px] mb-10
                bg-gradient-to-r from-[#F0F0F0] via-[#CECECE] to-[#8C8C8C]
                bg-clip-text text-transparent leading-snug
              "
            >
              Precision Search. Verified Citations.
            </p>

            {/* INPUT */}
            <PromptInput query={query} setQuery={setQuery} onAsk={handleAsk} />

          </div>
        )}

        {/* LOADING */}
        {loading && (
          <div className="relative z-10">
            <LoadingState />
          </div>
        )}

        {/* ANSWER VIEW */}
        {!loading && (
          <div className="w-full flex justify-center relative z-10">
            <ConversationView data={data} error={error} reset={reset} />
          </div>
        )}

        {/* BOTTOM INPUT (POST-ANSWER) */}
        {/* {data && !loading && (
          <footer className="sticky bottom-0 w-full bg-[#171717]/90 backdrop-blur-md border-t border-[#252525] p-6 z-40">
            <div className="w-full max-w-3xl mx-auto">
              <PromptInput query={query} setQuery={setQuery} onAsk={handleAsk} />
            </div>
          </footer>
        )} */}

      </main>
    </div>
  );
}
