// src/components/CitationPanel.jsx
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";

export default function CitationPanel({ citation, onClose, loading }) {
  if (!citation) return null;

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
        shadow-[0_0_30px_rgba(0,0,0,0.6)]
        z-[60] flex flex-col
        animate-slide-in
        transition-all duration-300
        overflow-hidden         /* PROTECT container from horizontal scroll */
      "
    >

      {/* HEADER */}
      <div className="px-5 py-3 flex justify-between items-center border-b border-[#2a2a2a]">
        <div className="flex flex-col leading-tight select-none">
          <h2
            className="
              text-[13px] font-semibold tracking-wide
              bg-gradient-to-r from-gray-100 to-gray-400 bg-clip-text text-transparent
            "
          >
            Source Preview
          </h2>
          <p className="text-[11px] text-gray-500">{citation.deal} — {docName}</p>
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

      {/* CONTENT */}
      <div
        className="
          flex-1 overflow-y-auto overflow-x-hidden    /* HIDE horizontal scroll */
          px-6 py-7 dark-scroll relative
          scrollbar-thin scrollbar-thumb-[#2c2c2c] scrollbar-track-transparent
        "
      >
        <div className="absolute left-0 top-0 w-full h-10 bg-gradient-to-b from-[#0f0f0f] to-transparent pointer-events-none" />

        {loading ? (
          <p className="italic text-gray-500 animate-pulse">Loading source…</p>
        ) : (
          <>
            <h3
              className="
                text-[18px] font-semibold tracking-tight mb-4 leading-snug
                bg-gradient-to-r from-gray-200 to-gray-500 bg-clip-text text-transparent
              "
            >
              {citation.meta?.clause_title || "Clause"}
            </h3>

            {/* WRAPPING FIX APPLIED HERE */}
            <p
              className="
                whitespace-pre-wrap break-words break-normal  /* wrap long chunks */
                text-gray-300 leading-[1.6] text-[14px]
                selection:bg-[#3b82f640] selection:text-white
              "
            >
              {citation.content}
            </p>

            <div className="pt-6 mt-6 border-t border-[#2d2d2d]" />

            <div className="text-xs text-gray-500 space-y-1 break-words">
              <p><strong className="text-gray-300">Deal:</strong> {citation.deal}</p>
              <p><strong className="text-gray-300">Document:</strong> {docName}</p>
              <p><strong className="text-gray-300">Section:</strong> {section}</p>
              <p><strong className="text-gray-300">Clause:</strong> {clause}</p>

              {/* Metadata can overflow → wrap */}
              <p className="pt-1 break-all">
                <strong className="text-gray-300">Chunk ID:</strong> {citation.id}
              </p>
            </div>
          </>
        )}
      </div>

      {/* FOOTER */}
      <div
        className="
          border-t border-[#2a2a2a] p-3 bg-[#0d0d0d]/80
          backdrop-blur flex justify-end
        "
      >
        <Button
          onClick={onClose}
          className="bg-[#1a1a1a] hover:bg-[#222] text-gray-200 text-xs px-3 py-1.5"
        >
          Close Panel
        </Button>
      </div>
    </div>
  );
}
