// src/components/CitationPanel.jsx
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";

export default function CitationPanel({ citation, onClose, loading }) {
  if (!citation) return null;

  return (
    <div
      className="
        fixed right-0 top-[50px] /* sits exactly below AppHeader */
        h-[calc(100vh-50px)] w-[380px]
        bg-[#0f0f0f]/95 backdrop-blur-md
        border-l border-[#262626]
        shadow-[0_0_25px_rgba(0,0,0,0.55)]
        z-[60] flex flex-col
        animate-slide-in
      "
    >
      {/* HEADER */}
      <div className="px-4 py-3 flex justify-between items-center border-b border-[#2a2a2a]">
        <h2 className="text-[13px] font-semibold text-gray-300 tracking-wide select-none">
          Source Preview
        </h2>

        <Button
          variant="ghost"
          size="icon"
          onClick={onClose}
          className="
            h-7 w-7 rounded-md
            flex items-center justify-center
            text-gray-400 hover:text-white hover:bg-[#1f1f1f]
            transition
          "
          aria-label="Close citation panel"
        >
          <X size={16} />
        </Button>
      </div>

      {/* BODY */}
      <div className="flex-1 overflow-y-auto px-5 py-6 space-y-6 dark-scroll">
        {loading ? (
          <p className="italic text-gray-500">Loading source…</p>
        ) : (
          <>
            {/* Clause Title */}
            <p className="text-[15px] font-semibold text-gray-100 leading-tight">
              {citation.meta?.clause_title || "Untitled Clause"}
            </p>

            {/* Clause Content */}
            <p className="whitespace-pre-wrap text-gray-300 leading-relaxed text-[14px]">
              {citation.content}
            </p>

            {/* Metadata */}
            <div className="pt-5 mt-4 border-t border-[#2d2d2d] text-xs text-gray-500 space-y-1">
              <p>Section: {citation.meta?.section_id || "N/A"}</p>
              <p>Clause: {citation.meta?.clause_id || "N/A"}</p>
              <p>Source ID: {citation.id}</p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
