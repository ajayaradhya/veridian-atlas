// src/App.jsx
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { askRagQuestion, fetchChunk } from "@/api/client";

// shadcn UI
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Popover, PopoverTrigger, PopoverContent } from "@/components/ui/popover";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";

export default function App() {
  const [query, setQuery] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeCitation, setActiveCitation] = useState(null);
  const [chunkCache, setChunkCache] = useState({});

  // -----------------------------------
  // Handlers
  // -----------------------------------
  const handleAsk = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setData(null);

    try {
      const res = await askRagQuestion(query);
      setData(res);
    } catch {
      setError("Something went wrong while retrieving data. Try again.");
    }

    setLoading(false);
  };

  const loadCitation = async (id) => {
    if (chunkCache[id]) return setActiveCitation(chunkCache[id]);

    try {
      const res = await fetchChunk(id);
      const formatted = {
        id,
        content: res.documents?.[0] ?? "No text available.",
        meta: res.metadatas?.[0] ?? null,
      };
      setChunkCache((prev) => ({ ...prev, [id]: formatted }));
      setActiveCitation(formatted);
    } catch {
      setActiveCitation({ content: "Could not load clause text." });
    }
  };

  const reset = () => {
    setQuery("");
    setData(null);
    setError("");
    setActiveCitation(null);
  };

  // -----------------------------------
  // UI & Layout
  // -----------------------------------

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col items-center
    px-4 sm:px-8 md:px-10 lg:px-16 xl:px-24 py-16">

      {/* ------------------ BRAND / LOGO ------------------ */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center mb-10 md:mb-16 space-y-4"
      >
        {/* Placeholder logo shape */}
        <div className="mx-auto h-14 w-14 rounded-lg bg-sky-200 border border-sky-300 flex items-center justify-center shadow-sm">
          <span className="text-sky-700 font-bold tracking-tight">VA</span>
        </div>

        <h1 className="font-semibold text-4xl sm:text-5xl md:text-6xl tracking-tight text-slate-900">
          Veridian Atlas
        </h1>

        <p className="text-slate-600 max-w-2xl mx-auto leading-relaxed text-base sm:text-lg">
          AI-assisted analysis for lending and financial contracts. Ask about clauses, covenants, collateral, 
          maturity dates, and obligations — get answers you can verify.
        </p>
      </motion.div>

      {/* ------------------ QUERY INPUT ------------------ */}
      {!data && !loading && (
        <Card className="w-full max-w-lg sm:max-w-2xl lg:max-w-3xl bg-white border border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle className="text-base font-medium text-slate-700">
              Ask a contractual or financial question
            </CardTitle>
          </CardHeader>
          <CardContent className="p-5 flex flex-col sm:flex-row gap-3">
            <Input
              placeholder="Example: When does Term Loan A mature?"
              className="bg-slate-100 text-slate-800 border-slate-300 focus:ring-sky-400"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAsk()}
            />
            <Button className="w-full sm:w-auto bg-sky-500 hover:bg-sky-600 transition" onClick={handleAsk}>
              Ask
            </Button>
          </CardContent>
        </Card>
      )}

      {/* ----------- Sticky Mobile CTA ----------- */}
      {!data && !loading && (
        <div className="fixed bottom-4 left-0 right-0 px-4 sm:hidden">
          <Button onClick={handleAsk} className="w-full py-4 bg-sky-500 hover:bg-sky-600 shadow-lg text-base">
            Ask the Question
          </Button>
        </div>
      )}

      {/* ------------------ LOADING ------------------ */}
      <AnimatePresence>
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="mt-10 text-slate-500 italic text-center"
          >
            Reading clauses, checking covenants, scanning ledgers...
          </motion.div>
        )}
      </AnimatePresence>

      {/* ------------------ ERROR ------------------ */}
      {error && (
        <Alert variant="destructive" className="max-w-xl mt-10">
          <AlertTitle>Something went wrong</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* ------------------ ANSWER CARD ------------------ */}
      {data && (
        <Card className="w-full max-w-lg sm:max-w-2xl lg:max-w-3xl mt-14 bg-white border border-slate-200 shadow-md 
        p-8 sm:p-10 md:p-12 space-y-10">

          {/* ------------------ QUESTION ------------------ */}
          <section className="space-y-1">
            <h3 className="text-xs uppercase font-medium text-slate-500">Question</h3>
            <p className="text-xl font-semibold text-slate-900">{data.query}</p>
          </section>

          {/* ------------------ ANSWER ------------------ */}
          <section className="space-y-1">
            <h3 className="text-xs uppercase font-medium text-slate-500">Answer</h3>
            <p className="text-lg text-slate-800 font-medium leading-relaxed">
              {data.answer}
            </p>
          </section>

          {/* ------------------ CITATIONS ------------------ */}
          <section className="space-y-2">
            <h3 className="text-xs uppercase font-medium text-slate-500">Citations</h3>
            <div className="flex flex-wrap gap-2">
              {data.citations?.map((id) => (
                <Popover key={id}>
                  <PopoverTrigger asChild>
                    <button
                      onClick={() => loadCitation(id)}
                      className="text-xs sm:text-sm bg-slate-100 border border-slate-300 px-2 sm:px-3 py-1 
                      rounded-md hover:bg-slate-200 transition"
                    >
                      {id.split("::").slice(-1)}
                    </button>
                  </PopoverTrigger>

                  <PopoverContent className="bg-white border border-slate-200 p-4 w-[95vw] sm:w-80 md:w-96 text-sm space-y-2 shadow-xl">
                    {activeCitation?.id === id ? (
                      <>
                        <p className="font-medium text-slate-800">{activeCitation.meta?.clause_title}</p>
                        <p className="whitespace-pre-line text-slate-600">{activeCitation.content}</p>
                        <p className="text-xs text-slate-400 border-t pt-2 mt-2">
                          Section {activeCitation.meta?.section_id} • Clause {activeCitation.meta?.clause_id}
                        </p>
                      </>
                    ) : (
                      <p className="italic text-slate-500">Loading...</p>
                    )}
                  </PopoverContent>
                </Popover>
              ))}
            </div>
          </section>

          {/* ------------------ RESET ------------------ */}
          <Button
            className="w-full bg-slate-200 text-slate-800 hover:bg-slate-300"
            onClick={reset}
          >
            Ask Another Question
          </Button>
        </Card>
      )}
    </div>
  );
}
