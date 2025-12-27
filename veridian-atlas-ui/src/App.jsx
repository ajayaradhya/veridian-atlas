import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { askRagQuestion } from "./api/client";
import { InformationCircleIcon, ArrowPathIcon } from "@heroicons/react/24/outline";

export default function App() {
  const [query, setQuery] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const wittyMessages = [
    "Consulting the loan gods...",
    "Dissecting legal clauses...",
    "Untangling financial jargon...",
    "Chasing auditors down the hallway...",
    "Bribing an analyst with coffee..."
  ];

  const handleAsk = async () => {
    if (!query.trim()) return; // block empty requests
    setLoading(true);
    setError("");
    setData(null);

    try {
      const res = await askRagQuestion(query);
      setData(res);
    } catch {
      setError("Something broke. Either contracts are confusing or our server is. Try again?");
    }

    setLoading(false);
  };

  const handleEnter = (e) => e.key === "Enter" && handleAsk();

  const reset = () => {
    setData(null);
    setQuery("");
    setError("");
  };

  return (
    
    <div className="min-h-screen bg-neutral-950 text-white flex flex-col items-center justify-start p-10">
      {/* Header / Branding */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }} 
        animate={{ opacity: 1, y: 0 }}
        className="text-center mt-12"
      >
        <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-500 to-teal-400 bg-clip-text text-transparent">
          Veridian Atlas
        </h1>
        <p className="text-gray-400 mt-3 text-lg">
          AI-powered contract analysis for borrowing agreements, loan covenants, and financial disclosures.
          <br/>Ask a question and let the system unearth the relevant clauses for you.
        </p>
      </motion.div>

      {/* Query Box */}
      {!data && (
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }} 
          animate={{ opacity: 1, scale: 1 }}
          className="mt-16 w-full max-w-2xl"
        >
          <textarea
            value={query}
            onKeyDown={handleEnter}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Try: Who is the borrower? / What is interest rate? / When does the facility mature?"
            className="w-full p-5 bg-neutral-900 border border-neutral-700 rounded-lg text-lg 
                       focus:ring-2 focus:ring-blue-500 focus:outline-none transition"
            rows={3}
          />
          <button
            onClick={handleAsk}
            className="mt-4 w-full py-3 bg-blue-600 hover:bg-blue-500 
                       rounded-lg text-lg font-semibold transition disabled:bg-neutral-700"
            disabled={loading}
          >
            Ask the Question
          </button>
        </motion.div>
      )}

      {/* Loading State */}
      {loading && (
        <motion.div 
          className="mt-20 text-center"
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }}
        >
          <ArrowPathIcon className="h-10 w-10 mx-auto text-blue-500 animate-spin" />
          <p className="text-gray-400 mt-4 text-lg">
            {wittyMessages[Math.floor(Math.random() * wittyMessages.length)]}
          </p>
        </motion.div>
      )}

      {/* Error */}
      {error && (
        <motion.div 
          className="bg-red-900 border border-red-700 text-red-200 p-4 rounded-lg mt-10 w-full max-w-2xl text-center"
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }}
        >
          {error}
        </motion.div>
      )}

      {/* Answer View */}
      {data && (
        <motion.div 
          className="bg-neutral-900 border border-neutral-800 rounded-xl p-8 mt-14 max-w-3xl w-full space-y-8"
          initial={{ opacity: 0, y: 20 }} 
          animate={{ opacity: 1, y: 0 }}
        >
          <div>
            <h2 className="text-2xl font-bold text-blue-300">Your Question</h2>
            <p className="text-gray-300 text-lg mt-2">{data.query}</p>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-teal-300">Answer</h2>
            <p className="text-xl mt-3 text-white font-medium">{data.answer}</p>
          </div>

          {/* Citations */}
          <div>
            <h3 className="text-xl font-semibold text-gray-200 mb-3">Citations</h3>
            <div className="space-y-2">
              {data.citations?.map((c, i) => (
                <div key={i} className="relative group text-sm bg-neutral-800 border border-neutral-700 p-2 rounded-lg">
                  <span className="text-blue-400 underline cursor-pointer">{c}</span>
                  <div className="hidden group-hover:block absolute left-0 top-full w-full
                                  bg-neutral-900 text-gray-300 border border-neutral-700 p-3 rounded-lg
                                  text-xs shadow-xl mt-1">
                    Referenced clause inside agreement. Hover reveals where the answer came from.
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Reset Button */}
          <button 
            onClick={reset}
            className="w-full py-3 bg-neutral-700 hover:bg-neutral-600 rounded-lg font-semibold transition"
          >
            Ask Another Question
          </button>

        </motion.div>
      )}
    </div>
  );
}
