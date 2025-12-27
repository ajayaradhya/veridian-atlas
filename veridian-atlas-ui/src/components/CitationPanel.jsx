// src/components/CitationPanel.jsx
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";

export default function CitationPanel({ citation, onClose, loading }) {
  if (!citation) return null;

  // Parse chunk for readable metadata
  const docName = citation.id?.split("_SECTION")[0] || citation.id;
  const section = citation.meta?.section_id || "N/A";
  const clause = citation.meta?.clause_id || "N/A";

  return (
    <div
      className="
        fixed right-0 top-[50px]
        h-[calc(100vh-50px)] w-[420px]
        bg-[#0f0f0f]/95 backdrop-blur-xl
        border-l border-[#262626]
        shadow-[0_0_30px_rgba(0,0,0,0.55)]
        z-[60] flex flex-col
        animate-slide-in
      "
    >

      {/* HEADER */}
      <div className="px-4 py-3 flex justify-between items-center border-b border-[#2a2a2a]">
        <div className="flex flex-col leading-tight">
          <h2 className="text-[13px] font-semibold text-gray-200 tracking-wide">
            Source Preview
          </h2>
          <p className="text-[11px] text-gray-500">
            {citation.deal} — {docName}
          </p>
        </div>

        <Button
          variant="ghost"
          size="icon"
          onClick={onClose}
          className="
            h-7 w-7 rounded-md
            text-gray-400 hover:text-white hover:bg-[#1f1f1f]
            transition
          "
          aria-label="Close citation panel"
        >
          <X size={16} />
        </Button>
      </div>

      {/* CONTENT AREA */}
      <div className="flex-1 overflow-y-auto px-6 py-6 dark-scroll">

        {loading ? (
          <p className="italic text-gray-500">Loading source…</p>
        ) : (
          <>
            {/* Title */}
            <p className="text-lg font-semibold text-gray-100 leading-snug mb-4">
              {citation.meta?.clause_title || "Clause"}
            </p>

            {/* Main clause text */}
            <p className="whitespace-pre-wrap text-gray-300 leading-relaxed text-[14px]">
              {citation.content}
            </p>

            {/* Metadata */}
            <div className="pt-6 mt-6 border-t border-[#2d2d2d] text-xs text-gray-500 space-y-1">
              <p><strong>Deal:</strong> {citation.deal}</p>
              <p><strong>Document:</strong> {docName}</p>
              <p><strong>Section:</strong> {section}</p>
              <p><strong>Clause:</strong> {clause}</p>
              <p><strong>Chunk ID:</strong> {citation.id}</p>
            </div>
          </>
        )}

      </div>
    </div>
  );
}
