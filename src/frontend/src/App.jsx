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

  // ---------------------------------------------------------------------------
  // LOAD DEALS (WITH RETRY & FAILURE HANDLING)
  // ---------------------------------------------------------------------------
  const loadDeals = async () => {
    setLoading(true);
    setError("");
    try {
      const serverDeals = await listDeals();

      if (!serverDeals || serverDeals.length === 0) {
        throw new Error("No deals found");
      }

      setDeals(serverDeals);
      setSelectedDeal(serverDeals[0]);
    } catch (err) {
      setDeals([]);
      setSelectedDeal("");
      setError(
        "Deal fetch failed: the server has abandoned us like a burnt contract. " +
        "No deals mean no queries. Try again when the universe feels generous."
      );
    }
    setLoading(false);
  };

  useEffect(() => {
    loadDeals();
  }, []);

  // ---------------------------------------------------------------------------
  // PERSIST HISTORY
  // ---------------------------------------------------------------------------
  useEffect(() => {
    localStorage.setItem("veridian-history", JSON.stringify(history));
  }, [history]);

  // ---------------------------------------------------------------------------
  // MAIN ASK
  // ---------------------------------------------------------------------------
  const handleAsk = async () => {
    if (!selectedDeal) {
      setError(
        "You cannot query without a deal. It's like asking a bank for money without an account."
      );
      return;
    }

    if (!query.trim()) return;

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
      setError(
        "We tried. The deal tried. The server tried. All parties failed. Consider this query officially rejected."
      );
    }

    setLoading(false);
  };

  // RESET
  const reset = () => {
    setQuery("");
    setData(null);
    setError("");
  };

  // ---------------------------------------------------------------------------
  // DISABLE STATE FLAGS
  // ---------------------------------------------------------------------------
  const noDealsAvailable = deals.length === 0 || !selectedDeal;

  // ---------------------------------------------------------------------------
  // RENDER
  // ---------------------------------------------------------------------------
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

        <AppHeader activeDeal={selectedDeal} />

        {/* BACKDROP EFFECTS */}
        <div className="pointer-events-none absolute inset-0 -z-0">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.12)_0%,rgba(0,0,0,0)_75%)]" />
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#0c0c0c66] to-[#0b0b0b]" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(200,200,200,0.04),transparent_60%)] blur-3xl" />
        </div>

        {/* LANDING PANEL */}
        {!data && !loading && (
          <div className="flex flex-col items-center text-center pt-32 pb-24 relative z-10 max-w-3xl">

            {/* TITLE */}
            <h1 className="text-6xl font-bold mb-3 select-none bg-gradient-to-r from-[#EDEDED] via-[#D7D7D7] to-[#AFAFAF] bg-clip-text text-transparent tracking-tight leading-none">
              Veridian Atlas
            </h1>

            <div className="h-[2px] w-4/5 bg-gradient-to-r from-transparent via-gray-100 to-transparent rounded-full opacity-60 mb-5" />

            <p className="text-[15px] mb-5 bg-gradient-to-r from-[#F0F0F0] via-[#CECECE] to-[#8C8C8C] bg-clip-text text-transparent leading-snug">
              Precision Search. Verified Citations.
            </p>

            {/* DEAL SELECTOR */}
            <select
              value={selectedDeal}
              onChange={(e) => setSelectedDeal(e.target.value)}
              disabled={noDealsAvailable}
              className="mb-6 bg-[#161616]/60 backdrop-blur border border-[#2d2d2d] text-gray-200 px-3 py-2 rounded-xl text-sm focus:border-[#4a4a4a] transition disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {deals.map((deal) => (
                <option key={deal} value={deal}>{deal}</option>
              ))}
            </select>

            {/* ERROR MESSAGE + RETRY BUTTON */}
            {error && (
              <div className="bg-red-900/30 border border-red-700 text-red-300 px-4 py-3 rounded-xl mb-4 w-[85%] text-sm">
                {error}
                <button
                  onClick={loadDeals}
                  className="ml-3 underline text-red-200 hover:text-red-100"
                >
                  Retry Fetch Deals
                </button>
              </div>
            )}

            {/* INPUT */}
            <PromptInput
              query={query}
              setQuery={setQuery}
              onAsk={handleAsk}
              selectedDeal={selectedDeal}
              disabled={noDealsAvailable}
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
