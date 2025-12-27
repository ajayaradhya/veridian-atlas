// src/components/ConversationView.jsx
import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import CitationPanel from "./CitationPanel";
import { fetchChunkForDeal } from "@/api/client";

export default function ConversationView({ data, error, reset }) {
  const [activeCitation, setActiveCitation] = useState(null);
  const [loadingCitation, setLoadingCitation] = useState(false);

  if (!data && !error) return null;

  const deal_id = data?.deal_id; // now reliable once server is fixed

  const loadCitation = async (chunk_id) => {
    if (!deal_id) return;
    try {
      setLoadingCitation(true);
      const res = await fetchChunkForDeal(deal_id, chunk_id);

      setActiveCitation({
        id: chunk_id,
        deal: deal_id,
        content: res.documents?.[0] ?? "No content returned.",
        meta: res.metadatas?.[0] ?? {},
      });

    } finally {
      setLoadingCitation(false);
    }
  };

  return (
    <div className="flex flex-col items-center w-full px-6 pt-10 relative">
      
      {error && <p className="text-red-500 mb-6">{error}</p>}

      {data && (
        <Card className="w-full max-w-3xl p-8 space-y-10 bg-[#1a1a1a]/80 border border-[#2f2f2f] text-gray-100 shadow-lg shadow-black/10">

          {/* DEAL ID TAG */}
          {deal_id && (
            <div className="text-xs text-gray-400 tracking-wider uppercase mb-1">
              Deal Context: <span className="text-gray-200 font-semibold">{deal_id}</span>
            </div>
          )}

          {/* QUESTION */}
          <section>
            <h3 className="text-xs uppercase text-gray-500 tracking-wide">Question</h3>
            <p className="text-xl font-semibold">{data.query}</p>
          </section>

          {/* ANSWER */}
          <section>
            <h3 className="text-xs uppercase text-gray-500 tracking-wide">Answer</h3>
            <p className="text-[17px] leading-relaxed text-gray-200">{data.answer}</p>
          </section>

          {/* CITATIONS */}
          {!!data.citations?.length && (
            <section className="space-y-2">
              <h3 className="text-xs uppercase text-gray-500 tracking-wide">Citations</h3>
              <div className="flex flex-wrap gap-2">
                {data.citations.map((chunk_id) => (
                  <button
                    key={chunk_id}
                    onClick={() => loadCitation(chunk_id)}
                    className="text-xs px-3 py-1 rounded-md bg-[#1e1e1e] border border-[#333] hover:bg-[#262626] transition text-gray-200"
                  >
                    {chunk_id.replace(/^VA_/, "")}
                  </button>
                ))}
              </div>
            </section>
          )}

          {/* RESET */}
          <Button
            variant="outline"
            onClick={reset}
            className="w-full mt-6 border-[#bababa] text-gray-300 hover:bg-[#212121] transition"
          >
            Ask Another Question
          </Button>
        </Card>
      )}

      {/* SLIDE-OUT SOURCE VIEW */}
      <CitationPanel
        citation={activeCitation}
        loading={loadingCitation}
        onClose={() => setActiveCitation(null)}
      />
    </div>
  );
}
