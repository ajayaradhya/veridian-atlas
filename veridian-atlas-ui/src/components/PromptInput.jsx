// src/components/PromptInput.jsx
import { useRef } from "react";
import { Send } from "lucide-react";

export default function PromptInput({ query, setQuery, onAsk, selectedDeal }) {
  const textareaRef = useRef(null);

  const handleSubmit = () => {
    if (!query.trim() || !selectedDeal) return;
    onAsk();
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && e.shiftKey) return; // newline
    if (e.key === "Enter") {
      e.preventDefault();
      handleSubmit();
    }
  };

  const autoResize = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  };

  return (
    <div className="w-full max-w-3xl mx-auto px-4 select-text">

      {/* ACTIVE DEAL INDICATOR */}
      <div className="mb-2 text-xs text-gray-400 flex items-center gap-2">
        <span className="opacity-60">Querying deal:</span>
        <span
          className="
            text-gray-200 bg-[#202020] border border-[#2f2f2f]
            px-2 py-0.5 rounded-md text-[11px] tracking-wide
          "
        >
          {selectedDeal || "No deal selected"}
        </span>
      </div>

      {/* INPUT FIELD */}
      <div
        className="
          flex items-center gap-3
          w-full bg-[#1a1a1a]
          border border-[#2d2d2d]
          rounded-2xl px-5 py-3
          shadow-sm transition
          hover:border-[#3a3a3a]
          focus-within:border-[#4a4a4a]
        "
      >
        <textarea
          ref={textareaRef}
          rows={1}
          className="
            flex-1 bg-transparent text-gray-200
            placeholder-gray-500 resize-none overflow-hidden
            focus:outline-none text-sm leading-[1.4] pt-[4px]
          "
          placeholder={
            selectedDeal
              ? `Ask about ${selectedDeal}...`
              : "Select a deal to begin"
          }
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            autoResize();
          }}
          onKeyDown={handleKeyDown}
        />

        <button
          onClick={handleSubmit}
          disabled={!selectedDeal}
          className="
            h-9 w-9 flex items-center justify-center
            rounded-lg bg-[#2c2c2c] text-gray-300
            hover:bg-[#3a3a3a] transition
            disabled:opacity-40 disabled:cursor-not-allowed
          "
          aria-label="Send query"
        >
          <Send size={18} />
        </button>
      </div>

      <p className="text-[11px] text-gray-500 text-center mt-3">
        Enter to send • Shift+Enter for newline
      </p>
    </div>
  );
}
