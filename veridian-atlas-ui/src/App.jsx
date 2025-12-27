// src/App.jsx
import { useState, useEffect } from "react";

// Components
import Sidebar from "./components/Sidebar";
import PromptInput from "./components/PromptInput";
import ConversationView from "./components/ConversationView";
import LoadingState from "./components/LoadingState";
import AppHeader from "./components/AppHeader";
import DealSelector from "./components/DealSelector";

// API
import { askRagQuestion, listDeals } from "@/api/client";

export default function App() {
  const [query, setQuery] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Multi-deal state
  const [deals, setDeals] = useState([]);
  const [selectedDeal, setSelectedDeal] = useState("");

  // Chat history (stored per deal + query)
  const [history, setHistory] = useState(() =>
    JSON.parse(localStorage.getItem("veridian-history") || "[]")
  );

  // Load available deals once
  useEffect(() => {
    async function loadDeals() {
      const serverDeals = await listDeals();
      setDeals(serverDeals);
      if (serverDeals.length > 0) setSelectedDeal(serverDeals[0]); // default
    }
    loadDeals();
  }, []);

  // Persist local history
  useEffect(() => {
    localStorage.setItem("veridian-history", JSON.stringify(history));
  }, [history]);


  // --------------------------------------------------------------
  // MAIN ASK
  // --------------------------------------------------------------
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
        {
          deal: selectedDeal,
          query,
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch {
      setError("Error: Unable to process request for this deal.");
    }

    setLoading(false);
  };

  // Reset for "New Chat"
  const reset = () => {
    setQuery("");
    setData(null);
    setError("");
  };


  // --------------------------------------------------------------
  // RENDER
  // --------------------------------------------------------------
  return (
    <div className="flex min-h-screen bg-[#101010] text-gray-200 font-brand">

      {/* SIDEBAR */}
      <Sidebar
        history={history}
        setHistory={setHistory}
        onSelect={({ deal, query }) => {
          setSelectedDeal(deal);
          setQuery(query);
        }}
        onNewChat={reset}
      />

      {/* MAIN PANEL */}
      <main className="flex-1 flex flex-col items-center overflow-y-auto relative">

        {/* GLOBAL HEADER */}
        <AppHeader
          selectedDeal={selectedDeal}
          setSelectedDeal={setSelectedDeal}
        />

        {/* DEAL SELECTOR (TOP AREA) */}
        <div className="w-full max-w-3xl mx-auto mt-6 mb-6">
          <DealSelector
            deals={deals}
            selectedDeal={selectedDeal}
            setSelectedDeal={setSelectedDeal}
          />
        </div>

        {/* LANDING */}
        {!data && !loading && (
          <div className="flex flex-col items-center text-center pt-24 pb-10 max-w-3xl relative z-10">
            <h1 className="text-6xl font-bold mb-3 text-transparent bg-clip-text bg-white/75">
              Veridian Atlas
            </h1>
            <p className="text-sm text-gray-300 mb-10">
              Select a deal and ask a question — granular citations guaranteed.
            </p>

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

        {/* ANSWER VIEW */}
        {!loading && data && (
          <div className="w-full flex justify-center relative z-10 mt-10">
            <ConversationView data={data} error={error} reset={reset} />
          </div>
        )}
      </main>
    </div>
  );
}
