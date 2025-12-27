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
    // Shift+Enter = newline (allow)
    if (e.key === "Enter" && e.shiftKey) return;
    // Enter = send
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

    // Cap max height before internal scroll begins
    if (el.scrollHeight > 200) {
      el.style.overflowY = "auto";
    } else {
      el.style.overflowY = "hidden";
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto px-4">

      {/* ACTIVE DEAL INDICATOR
      <div className="mb-2 flex items-center gap-2 text-xs text-gray-400 select-none">
        <span className="opacity-60">Active deal:</span>
        <span
          className="
            text-gray-200 bg-[#202020] border border-[#2f2f2f]
            px-2 py-0.5 rounded-md text-[11px]
          "
        >
          {selectedDeal || "No deal selected"}
        </span>
      </div> */}

      {/* INPUT FIELD */}
      <div
        className={`
          flex items-center gap-3
          w-full rounded-2xl px-5 py-3
          border transition
          bg-[#1a1a1a] hover:border-[#3a3a3a]
          focus-within:border-[#4e4e4e] focus-within:shadow-[0_0_0_2px_rgba(100,100,100,0.15)]
        `}
      >
        <textarea
          ref={textareaRef}
          rows={1}
          className="
            flex-1 bg-transparent text-gray-200 placeholder-gray-500
            resize-none overflow-hidden focus:outline-none
            text-sm leading-[1.4] pt-[4px]
            break-words whitespace-pre-wrap
            max-h-[200px]
          "
          placeholder={
            selectedDeal
              ? `Ask about deal ${selectedDeal}`
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
          disabled={!selectedDeal || !query.trim()}
          className="
            h-9 w-9 flex items-center justify-center rounded-lg
            bg-[#2c2c2c] hover:bg-[#3a3a3a]
            text-gray-300 transition
            disabled:opacity-40 disabled:cursor-not-allowed
          "
        >
          <Send size={18} />
        </button>
      </div>

      {/* HINT TEXT */}
      <p className="text-[11px] text-gray-500 text-center mt-3 select-none">
        Enter to send • Shift+Enter for newline
      </p>
    </div>
  );
}
