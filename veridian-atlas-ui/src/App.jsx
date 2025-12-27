import { useState } from "react";
import { motion } from "framer-motion";
import { askRagQuestion } from "@/api/client";

// shadcn/ui components
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";

export default function App() {
  const [query, setQuery] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const wittyMessages = [
    "Consulting the loan gods...",
    "Interrogating covenants with precision...",
    "Auditors are panicking but the AI isn't...",
    "Untangling a century of legal jargon...",
    "Summoning the spirit of due diligence..."
  ];

  const handleAsk = async () => {
    if (!query.trim()) return; 
    setLoading(true);
    setError("");
    setData(null);

    try {
      const res = await askRagQuestion(query);
      setData(res);
    } catch {
      setError("Something snapped. Finance is hard. Try again.");
    }

    setLoading(false);
  };

  const reset = () => {
    setQuery("");
    setData(null);
    setError("");
  };

  const handleEnter = (e) => e.key === "Enter" && handleAsk();

  return (
    <div className="min-h-screen bg-neutral-950 text-white flex flex-col items-center px-6 py-20">
      
      {/* Branding / Hero */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-16"
      >
        <h1 className="text-6xl font-extrabold bg-gradient-to-r from-blue-500 to-teal-400 bg-clip-text text-transparent">
          Veridian Atlas
        </h1>
        <p className="text-gray-400 mt-5 max-w-2xl mx-auto text-lg">
          AI-powered contract analysis for credit agreements, loan facilities, and covenants. 
          Ask a question and Veridian Atlas retrieves insights — linked to source clauses.
        </p>
      </motion.div>

      {/* Query Input Card */}
      {!data && !loading && (
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.25 }}
          className="w-full max-w-3xl"
        >
          <Card className="bg-neutral-900/60 border-neutral-700 shadow-xl">
            <CardContent className="p-8 space-y-5">
              <Textarea
                placeholder="e.g. What is the interest rate for the Revolving Credit Facility?"
                className="bg-neutral-800 border-neutral-700 text-lg"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleEnter}
                rows={3}
              />
              <Button
                onClick={handleAsk}
                className="w-full bg-blue-600 hover:bg-blue-500 text-lg py-6"
              >
                Ask the Question
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Loading State */}
      {loading && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center mt-12 space-y-6">
          <Skeleton className="h-8 w-64 bg-neutral-800 mx-auto rounded" />
          <Skeleton className="h-8 w-80 bg-neutral-800 mx-auto rounded" />
          <p className="text-gray-400 italic mt-4 animate-pulse">
            {wittyMessages[Math.floor(Math.random() * wittyMessages.length)]}
          </p>
        </motion.div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="max-w-2xl w-full mt-10">
          <Alert variant="destructive">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </div>
      )}

      {/* Results */}
      {data && (
        <motion.div
          initial={{ opacity: 0, y: 25 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-3xl w-full mt-16"
        >
          <Card className="bg-neutral-900/60 border-neutral-700 p-8 space-y-8 shadow-xl">
            
            <section>
              <h3 className="text-gray-400 text-sm uppercase tracking-wide">Your Question</h3>
              <p className="text-2xl font-semibold mt-2">{data.query}</p>
            </section>

            <section>
              <h3 className="text-gray-400 text-sm uppercase tracking-wide">Answer</h3>
              <p className="text-xl mt-2 text-teal-300 font-medium">{data.answer}</p>
            </section>

            <section>
              <h3 className="text-gray-400 text-sm uppercase tracking-wide mb-3">Citations</h3>
              <div className="space-y-2">
                {data.citations?.map((c, i) => (
                  <div 
                    key={i}
                    className="group relative bg-neutral-800 border border-neutral-700 rounded-lg p-3 text-sm cursor-pointer"
                  >
                    <span className="text-blue-400 underline">{c}</span>
                    <div className="absolute hidden group-hover:block bg-neutral-900 border border-neutral-700 
                                    p-4 rounded-lg shadow-xl mt-2 left-0 w-full text-xs text-gray-300">
                      Referenced clause from contract. Full text available in context retrieval.
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <Button 
              onClick={reset}
              className="w-full bg-neutral-700 hover:bg-neutral-600 py-5 text-lg"
            >
              Ask Another Question
            </Button>
          </Card>
        </motion.div>
      )}
    </div>
  );
}
