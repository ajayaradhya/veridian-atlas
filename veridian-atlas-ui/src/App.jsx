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

  // Load deals on app start
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
        { deal_id: selectedDeal, query, timestamp: new Date().toISOString() },
      ]);
    } catch {
      setError("Error: Unable to process request for this deal.");
    }

    setLoading(false);
  };

  // NEW CHAT
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
        onSelect={({ deal, query }) => {
          if (deal) setSelectedDeal(deal);
          if (query) setQuery(query);
        }}
        onNewChat={reset}
      />


      {/* MAIN PANEL */}
      <main className="flex-1 flex flex-col items-center overflow-y-auto relative">

        <AppHeader activeDeal={selectedDeal} />

        {/* LANDING VIEW */}
        {!data && !loading && (
          <div className="flex flex-col items-center text-center pt-24 pb-10 max-w-3xl relative z-10">

            <h1 className="text-6xl font-bold mb-3 text-transparent bg-clip-text bg-white/75">
              Veridian Atlas
            </h1>

            <p className="text-sm text-gray-300 mb-10">
              Select a deal and ask a question — accurate retrieval, guaranteed.
            </p>

            {/* NEW: DEAL SELECTOR (moved here) */}
            <select
              value={selectedDeal}
              onChange={(e) => setSelectedDeal(e.target.value)}
              className="
                mb-6 bg-[#1a1a1a] border border-[#2d2d2d] text-gray-200
                px-3 py-2 rounded-xl text-sm focus:border-[#4a4a4a]
              "
            >
              {deals.map((deal) => (
                <option key={deal} value={deal}>{deal}</option>
              ))}
            </select>

            <PromptInput
              query={query}
              setQuery={setQuery}
              onAsk={handleAsk}
              selectedDeal={selectedDeal}
            />
          </div>
        )}

        {loading && (
          <div className="relative z-10">
            <LoadingState />
          </div>
        )}

        {!loading && data && (
          <div className="w-full flex justify-center relative z-10 mt-10">
            <ConversationView data={data} error={error} reset={reset} />
          </div>
        )}

      </main>
    </div>
  );
}
