// src/components/CitationPanel.jsx
import { Button } from "@/components/ui/button";

export default function CitationPanel({ citation, onClose, loading }) {
  if (!citation) return null;

  return (
    <div
      className="
        fixed right-0 top-0 h-full w-[360px] bg-[#0f0f0f]
        border-l border-gray-800 text-gray-200 shadow-2xl z-50 flex flex-col
        animate-slide-in
      "
    >
      {/* Header */}
      <div className="p-4 flex justify-between items-center border-b border-gray-800">
        <h2 className="text-sm font-semibold">Source Preview</h2>
        <Button
          variant="ghost"
          size="sm"
          className="text-gray-400 hover:text-gray-200"
          onClick={onClose}
        >
          Close
        </Button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {loading ? (
          <p className="italic text-gray-500">Loading...</p>
        ) : (
          <>
            {/* Title */}
            <p className="text-base font-semibold text-white">
              {citation.meta?.clause_title || "Untitled Clause"}
            </p>

            {/* Body */}
            <p className="whitespace-pre-wrap text-gray-300 leading-relaxed text-sm">
              {citation.content}
            </p>

            {/* Metadata */}
            <div className="pt-4 mt-4 border-t border-gray-800 text-xs text-gray-500 leading-6">
              Section: {citation.meta?.section_id || "N/A"} <br />
              Clause: {citation.meta?.clause_id || "N/A"} <br />
              Source ID: {citation.id}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
