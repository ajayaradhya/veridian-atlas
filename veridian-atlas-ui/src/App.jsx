import { useState } from "react";
import { askRagQuestion, fetchChunk } from "@/api/client";
import { motion } from "framer-motion";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
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

  const handleAsk = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setData(null);
    try {
      const res = await askRagQuestion(query);
      setData(res);
    } catch {
      setError("There was an issue fetching results. Try again.");
    }
    setLoading(false);
  };

  const loadCitation = async (id) => {
    if (chunkCache[id]) return setActiveCitation(chunkCache[id]);
    try {
      const res = await fetchChunk(id);
      const normalized = {
        id,
        content: res.documents?.[0] ?? "No text available",
        meta: res.metadatas?.[0] ?? null
      };
      setChunkCache((c) => ({ ...c, [id]: normalized }));
      setActiveCitation(normalized);
    } catch {
      setActiveCitation({ content: "Could not load clause." });
    }
  };

  const reset = () => {
    setQuery("");
    setData(null);
    setError("");
    setActiveCitation(null);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col items-center py-20 px-6">

      {/* HERO / BRAND */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-16 space-y-3"
      >
        <h1 className="text-5xl font-bold tracking-tight text-slate-900">
          Veridian Atlas
        </h1>
        <p className="text-slate-600 max-w-2xl mx-auto leading-relaxed">
          A modern interface for financial and lending documents.
          Ask questions about agreements, covenants, collateral and maturity dates — 
          get answers with citeable sources.
        </p>
      </motion.div>

      {/* INPUT */}
      {!data && !loading && (
        <Card className="bg-white border border-slate-200 shadow-sm w-full max-w-3xl">
          <CardContent className="p-6 flex items-center gap-3">
            <Input
              placeholder="Example: When does Term Loan A mature?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="bg-slate-100 text-slate-800 border-slate-300"
            />
            <Button className="bg-sky-500 hover:bg-sky-600" onClick={handleAsk}>
              Ask
            </Button>
          </CardContent>
        </Card>
      )}

      {/* LOADING */}
      {loading && (
        <div className="mt-10 text-slate-500 italic">
          Thinking, searching, and reading clauses...
        </div>
      )}

      {/* ERROR */}
      {error && (
        <Alert variant="destructive" className="max-w-xl mt-10">
          <AlertTitle>Something went wrong</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* RESULTS */}
      {data && (
        <Card className="max-w-3xl w-full mt-12 bg-white border border-slate-200 shadow-md p-8 space-y-10">
          
          {/* QUESTION */}
          <section>
            <h3 className="text-xs uppercase font-medium text-slate-500">Question</h3>
            <p className="text-xl font-semibold text-slate-900 mt-1">
              {data.query}
            </p>
          </section>

          {/* ANSWER */}
          <section>
            <h3 className="text-xs uppercase font-medium text-slate-500">Answer</h3>
            <p className="text-lg mt-2 text-slate-800 font-medium">
              {data.answer}
            </p>
          </section>

          {/* CITATIONS */}
          <section>
            <h3 className="text-xs uppercase font-medium text-slate-500 mb-2">Citations</h3>
            <div className="flex flex-wrap gap-2">
              {data.citations?.map((id) => (
                <Popover key={id}>
                  <PopoverTrigger asChild>
                    <button
                      onClick={() => loadCitation(id)}
                      className="text-sm bg-slate-100 border border-slate-300 px-3 py-1 rounded-md hover:bg-slate-200 transition"
                    >
                      {id.split("::").slice(-1)}
                    </button>
                  </PopoverTrigger>

                  <PopoverContent className="bg-white border border-slate-200 shadow-lg p-4 w-96 text-sm">
                    {activeCitation?.id === id ? (
                      <>
                        <p className="font-medium text-slate-800">
                          {activeCitation.meta?.clause_title}
                        </p>
                        <p className="whitespace-pre-line text-slate-600 mt-2">
                          {activeCitation.content}
                        </p>
                        <p className="text-xs text-slate-400 border-t pt-2 mt-2">
                          Section {activeCitation.meta?.section_id} • Clause {activeCitation.meta?.clause_id}
                        </p>
                      </>
                    ) : (
                      <p className="italic text-slate-500">Loading clause...</p>
                    )}
                  </PopoverContent>
                </Popover>
              ))}
            </div>
          </section>

          {/* RESET */}
          <Button className="w-full bg-slate-200 text-slate-800 hover:bg-slate-300" onClick={reset}>
            Ask Another Question
          </Button>
        </Card>
      )}
    </div>
  );
}
