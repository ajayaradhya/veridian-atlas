// src/components/ConversationView.jsx
import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import CitationPanel from "./CitationPanel";
import { fetchChunk } from "@/api/client";

export default function ConversationView({ data, error, reset }) {
  const [activeCitation, setActiveCitation] = useState(null);
  const [loadingCitation, setLoadingCitation] = useState(false);

  if (!data && !error) return null;

  const loadCitation = async (id) => {
    try {
      setLoadingCitation(true);
      const res = await fetchChunk(id);
      setActiveCitation({
        id,
        content: res.documents?.[0] ?? "No content available.",
        meta: res.metadatas?.[0] ?? {},
      });
    } finally {
      setLoadingCitation(false);
    }
  };

  return (
    <div className="flex flex-col items-center w-full px-6 pt-10 relative">
      
      {/* ERROR */}
      {error && <p className="text-red-500 mb-6">{error}</p>}

      {/* RESULT CARD */}
      {data && (
        <Card
          className="
            w-full max-w-3xl p-8 space-y-10 text-gray-100
            bg-[#1a1a1a]/80 backdrop-blur-sm
            border border-[#2f2f2f]
            shadow-lg shadow-black/10
          "
        >
          {/* QUESTION */}
          <section className="space-y-1">
            <h3 className="text-xs uppercase text-gray-500 tracking-wide">Question</h3>
            <p className="text-xl font-semibold">{data.query}</p>
          </section>

          {/* ANSWER */}
          <section className="space-y-1">
            <h3 className="text-xs uppercase text-gray-500 tracking-wide">Answer</h3>
            <p className="text-[17px] leading-relaxed text-gray-200">
              {data.answer}
            </p>
          </section>

          {/* CITATIONS */}
          {Array.isArray(data.citations) && data.citations.length > 0 && (
            <section className="space-y-2">
              <h3 className="text-xs uppercase text-gray-500 tracking-wide">Citations</h3>
              <div className="flex flex-wrap gap-2">
                {data.citations.map((id) => (
                  <button
                    key={id}
                    onClick={() => loadCitation(id)}
                    className="
                      text-xs px-3 py-1 rounded-md
                      bg-[#1e1e1e] border border-[#333]
                      hover:bg-[#262626] transition
                      text-gray-200
                    "
                  >
                    {id.split("::").slice(-1)}
                  </button>
                ))}
              </div>
            </section>
          )}

          {/* RESET BUTTON — MATCHES CLEAR HISTORY */}
          <Button
            variant="outline"
            onClick={reset}
            className="
              w-full mt-6
              border-[#bababa]
              text-gray-300
              hover:bg-[#212121]
              transition
            "
          >
            Ask Another Question
          </Button>
        </Card>
      )}

      {/* CITATION PANEL */}
      <CitationPanel
        citation={activeCitation}
        loading={loadingCitation}
        onClose={() => setActiveCitation(null)}
      />
    </div>
  );
}
