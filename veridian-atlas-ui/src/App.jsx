// src/App.jsx
import { useState, useEffect } from "react";

// Components
import Sidebar from "./components/Sidebar";
import PromptInput from "./components/PromptInput";
import ConversationView from "./components/ConversationView";
import LoadingState from "./components/LoadingState";
import AppHeader from "./components/AppHeader";

// API
import { askRagQuestion, listDeals } from "@/api/client";

export default function App() {
  const [query, setQuery] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Multi-deal
  const [deals, setDeals] = useState([]);
  const [selectedDeal, setSelectedDeal] = useState("");

  // Local history
  const [history, setHistory] = useState(() =>
    JSON.parse(localStorage.getItem("veridian-history") || "[]")
  );

  // Load deals
  useEffect(() => {
    async function loadDeals() {
      const serverDeals = await listDeals();
      setDeals(serverDeals);
      if (serverDeals.length > 0) setSelectedDeal(serverDeals[0]);
    }
    loadDeals();
  }, []);

  // Persist history
  useEffect(() => {
    localStorage.setItem("veridian-history", JSON.stringify(history));
  }, [history]);

  // MAIN ASK
  const handleAsk = async () => {
    if (!query.trim() || !selectedDeal) return;
    setLoading(true);
    setError("");
    setData(null);

    try {
      const res = await askRagQuestion(selectedDeal, query, 3);
      setData(res);

      setHistory((prev) => [
        ...prev,
        { deal: selectedDeal, query, timestamp: new Date().toISOString() },
      ]);
    } catch {
      setError("Error: Unable to process request for this deal.");
    }

    setLoading(false);
  };

  // RESET
  const reset = () => {
    setQuery("");
    setData(null);
    setError("");
  };

  return (
    <div className="flex min-h-screen bg-[#101010] text-gray-200 font-brand">

      {/* SIDEBAR */}
      <Sidebar
        history={history}
        setHistory={setHistory}
        onSelect={({ deal, query }) => {
          if (deal) setSelectedDeal(deal);
          if (query) setQuery(query);
        }}
        onNewChat={reset}
      />

      {/* MAIN PANEL */}
      <main className="flex-1 flex flex-col items-center overflow-y-auto relative">

        {/* TOP HEADER */}
        <AppHeader activeDeal={selectedDeal} />

        {/* ================================================================= */}
        {/* BACKDROP GLOW (RESTORED) */}
        {/* ================================================================= */}
        <div className="pointer-events-none absolute inset-0 -z-0">
          <div className="
            absolute inset-0
            bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.12)_0%,rgba(0,0,0,0)_75%)]
          " />
          <div className="
            absolute inset-0
            bg-gradient-to-b from-transparent via-[#0c0c0c66] to-[#0b0b0b]
          " />
          <div className="
            absolute inset-0
            bg-[radial-gradient(circle_at_center,rgba(200,200,200,0.04),transparent_60%)]
            blur-3xl
          " />
        </div>

        {/* ================================================================= */}
        {/* LANDING SCREEN (RESTORED HERO STYLING) */}
        {/* ================================================================= */}
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

            {/* ================================================================= */}
            {/* DEAL SELECTOR (NOW FITS HERO STYLE) */}
            {/* ================================================================= */}
            <select
              value={selectedDeal}
              onChange={(e) => setSelectedDeal(e.target.value)}
              className="
                mb-6 bg-[#161616]/60 backdrop-blur border border-[#2d2d2d]
                text-gray-200 px-3 py-2 rounded-xl text-sm 
                focus:border-[#4a4a4a] transition
              "
            >
              {deals.map((deal) => (
                <option key={deal} value={deal}>{deal}</option>
              ))}
            </select>

            {/* INPUT */}
            <PromptInput
              query={query}
              setQuery={setQuery}
              onAsk={handleAsk}
              selectedDeal={selectedDeal}
            />
          </div>
        )}

        {/* LOADING */}
        {loading && (
          <div className="relative z-10">
            <LoadingState />
          </div>
        )}

        {/* ANSWER OUTPUT */}
        {!loading && data && (
          <div className="w-full flex justify-center relative z-10 mt-10">
            <ConversationView data={data} error={error} reset={reset} />
          </div>
        )}
      </main>
    </div>
  );
}
