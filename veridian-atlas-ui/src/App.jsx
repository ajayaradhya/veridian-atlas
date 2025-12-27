import { useState } from "react";
import { motion } from "framer-motion";
import { askRagQuestion, fetchChunk } from "@/api/client";

// shadcn components
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

export default function App() {
  const [query, setQuery] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeCitation, setActiveCitation] = useState(null); // track clicked citation content
  const [chunkCache, setChunkCache] = useState({}); // store fetched chunks to avoid reloading

  const loadCitation = async (id) => {
    // If cached, reuse
    if (chunkCache[id]) {
      setActiveCitation({ id, ...chunkCache[id] });
      return;
    }

    try {
      const res = await fetchChunk(id);

      const normalized = {
        id: res?.ids?.[0] || id,
        content: res?.documents?.[0] || "No document text found.",
        meta: res?.metadatas?.[0] || null
      };

      setChunkCache((prev) => ({ ...prev, [id]: normalized }));
      setActiveCitation({ ...normalized });
    } catch (err) {
      setActiveCitation({ id, content: "Failed to load citation text." });
    }
  };


  const wittyMessages = [
    "Consulting the loan gods...",
    "Interrogating covenants with precision...",
    "Breaking down legal jargon atom by atom...",
    "Feeding the auditors caffeine and hope...",
    "Extracting answers from structured chaos..."
  ];

  const handleAsk = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setData(null);
    setActiveCitation(null);

    try {
      const res = await askRagQuestion(query);
      setData(res);
    } catch {
      setError("Unexpected issue — the contract resisted interrogation.");
    }

    setLoading(false);
  };

  const reset = () => {
    setQuery("");
    setData(null);
    setError("");
    setActiveCitation(null);
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-gray-100 flex flex-col items-center px-6 py-20">
      
      {/* Branding */}
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-16"
      >
        <h1 className="text-6xl font-extrabold tracking-tight bg-gradient-to-r from-sky-500 to-teal-400 text-transparent bg-clip-text">
          Veridian Atlas
        </h1>
        <p className="text-gray-400 mt-5 max-w-2xl mx-auto text-lg leading-relaxed">
          A retrieval-augmented assistant for financial and lending contracts.
          Ask questions about clauses, covenants, collateral, maturity dates, and obligations — get answers you can verify.
        </p>
      </motion.div>

      {/* Query Input */}
      {!data && !loading && (
        <Card className="w-full max-w-3xl bg-neutral-900/70 backdrop-blur border border-neutral-700 shadow-xl">
          <CardContent className="p-8 space-y-5">
            <Textarea
              className="bg-neutral-100 text-neutral-900 border-neutral-300 focus:ring-sky-500 text-lg placeholder-neutral-500"
              placeholder="Example: When does Term Loan A mature?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              rows={3}
            />
            <Button
              className="w-full py-4 bg-sky-600 hover:bg-sky-500 text-lg"
              onClick={handleAsk}
            >
              Ask the Question
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Loading */}
      {loading && (
        <motion.div className="mt-20 text-center space-y-6">
          <p className="text-gray-400 italic animate-pulse text-lg">
            {wittyMessages[Math.floor(Math.random() * wittyMessages.length)]}
          </p>
        </motion.div>
      )}

      {/* Error */}
      {error && (
        <Alert variant="destructive" className="max-w-2xl w-full mt-10">
          <AlertTitle>Request Failed</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Results */}
      {data && (
        <Card className="max-w-3xl w-full mt-12 bg-[#111216] border border-neutral-800 shadow-xl p-10 space-y-10">
          {/* QUESTION */}
          <section>
            <h3 className="text-sm tracking-wider uppercase text-neutral-400">Your Question</h3>
            <p className="text-2xl font-semibold mt-2 text-neutral-100 leading-snug">
              {data.query}
            </p>
          </section>

          {/* ANSWER */}
          <section>
            <h3 className="text-sm tracking-wider uppercase text-neutral-400">Answer</h3>
            <p className="text-xl mt-2 text-teal-300 font-medium leading-relaxed">
              {data.answer}
            </p>
          </section>

          {/* CITATIONS */}
          <section>
            <h3 className="text-sm tracking-wider uppercase text-neutral-400 mb-3">Citations</h3>
            <div className="space-y-3">
              {data.citations?.map((cite, i) => (
                <Popover key={i}>
                  <PopoverTrigger asChild>
                    <button
                      onClick={() => loadCitation(cite)}
                      className="text-sky-400 underline hover:text-sky-300 text-sm"
                    >
                      {cite}
                    </button>
                  </PopoverTrigger>
                  <PopoverContent className="w-96 max-h-64 overflow-y-auto bg-neutral-950 text-gray-300 border border-neutral-800 shadow-xl">
                    {activeCitation?.id === cite ? (
                      <div className="space-y-2">
                        <p className="text-xs text-sky-400 font-semibold">
                          {activeCitation.meta?.clause_title || "Clause"}
                        </p>

                        <p className="whitespace-pre-line text-sm leading-relaxed">
                          {activeCitation.content}
                        </p>

                        <p className="text-xs text-neutral-500 pt-3 border-t border-neutral-800">
                          Section: {activeCitation.meta?.section_id} • Clause {activeCitation.meta?.clause_id}
                        </p>
                      </div>
                    ) : (
                      <p className="text-sm text-neutral-500 italic">Loading...</p>
                    )}
                  </PopoverContent>
                </Popover>
              ))}

            </div>
          </section>

          {/* RESET */}
          <Button
            className="w-full py-4 bg-neutral-700 hover:bg-neutral-600 text-lg"
            onClick={reset}
          >
            Ask Another Question
          </Button>
        </Card>
      )}
    </div>
  );
}
