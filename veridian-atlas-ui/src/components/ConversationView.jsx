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
      
      {/* Error Display */}
      {error && (
        <p className="text-red-500 mb-6">{error}</p>
      )}

      {/* Result Card */}
      {data && (
        <Card className="w-full max-w-3xl bg-[#1a1a1a] border border-gray-800 p-8 text-gray-100 space-y-10 relative">
          
          {/* QUESTION */}
          <section>
            <h3 className="text-xs uppercase text-gray-500">Question</h3>
            <p className="text-xl font-semibold">{data.query}</p>
          </section>

          {/* ANSWER */}
          <section>
            <h3 className="text-xs uppercase text-gray-500">Answer</h3>
            <p className="text-lg leading-relaxed">{data.answer}</p>
          </section>

          {/* CITATIONS / SOURCES */}
          {Array.isArray(data.citations) && data.citations.length > 0 && (
            <section className="space-y-2">
              <h3 className="text-xs uppercase text-gray-500">Citations</h3>
              <div className="flex flex-wrap gap-2">
                {data.citations.map((id) => (
                  <button
                    key={id}
                    onClick={() => loadCitation(id)}
                    className="text-xs bg-[#1f1f1f] border border-gray-700 px-3 py-1 rounded-md
                               hover:bg-[#242424] transition text-gray-200"
                  >
                    {id.split("::").slice(-1)}
                  </button>
                ))}
              </div>
            </section>
          )}

          {/* RESET BUTTON */}
          <Button
            onClick={reset}
            className="w-full bg-gray-800 hover:bg-gray-700 text-gray-200"
          >
            Ask Another Question
          </Button>
        </Card>
      )}

      {/* SIDE PANEL MOUNT */}
      <CitationPanel
        citation={activeCitation}
        loading={loadingCitation}
        onClose={() => setActiveCitation(null)}
      />

    </div>
  );
}
