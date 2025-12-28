// src/components/PromptInput.jsx
import { useRef } from "react";
import { Send } from "lucide-react";

export default function PromptInput({ query, setQuery, onAsk, selectedDeal, disabled }) {
  const textareaRef = useRef(null);

  const handleSubmit = () => {
    if (disabled || !query.trim() || !selectedDeal) return;
    onAsk();
  };

  const handleKeyDown = (e) => {
    if (disabled) return;
    // Shift+Enter = newline
    if (e.key === "Enter" && e.shiftKey) return;
    // Enter = send
    if (e.key === "Enter") {
      e.preventDefault();
      handleSubmit();
    }
  };

  const autoResize = () => {
    if (disabled) return;
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

      {/* INPUT FIELD */}
      <div
        className={`
          flex items-center gap-3
          w-full rounded-2xl px-5 py-3
          border transition
          bg-[#1a1a1a] hover:border-[#3a3a3a]
          focus-within:border-[#4e4e4e] focus-within:shadow-[0_0_0_2px_rgba(100,100,100,0.15)]
          ${disabled ? "opacity-50 cursor-not-allowed" : ""}
        `}
      >
        <textarea
          ref={textareaRef}
          disabled={disabled}
          rows={1}
          className={`
            flex-1 bg-transparent text-gray-200 placeholder-gray-500
            resize-none overflow-hidden focus:outline-none
            text-sm leading-[1.4] pt-[4px]
            break-words whitespace-pre-wrap
            max-h-[200px]
            ${disabled ? "cursor-not-allowed" : ""}
          `}
          placeholder={
            disabled
              ? "No deals available. Query function disabled. Even the servers need therapy."
              : selectedDeal
              ? `Ask about deal "${selectedDeal}"`
              : "Select a deal to begin"
          }
          value={query}
          onChange={(e) => {
            if (disabled) return;
            setQuery(e.target.value);
            autoResize();
          }}
          onKeyDown={handleKeyDown}
        />

        <button
          onClick={handleSubmit}
          disabled={disabled || !selectedDeal || !query.trim()}
          className={`
            h-9 w-9 flex items-center justify-center rounded-lg
            bg-[#2c2c2c] hover:bg-[#3a3a3a]
            text-gray-300 transition
            disabled:opacity-40 disabled:cursor-not-allowed
          `}
        >
          <Send size={18} />
        </button>
      </div>

      {/* HINT TEXT */}
      {!disabled && (
        <p className="text-[11px] text-gray-500 text-center mt-3 select-none">
          Enter to send • Shift+Enter for newline
        </p>
      )}

      {disabled && (
        <p className="text-[11px] text-red-400 text-center mt-3 select-none italic">
          Deals failed to load. Input disabled. Your curiosity deserves better backend decisions.
        </p>
      )}
    </div>
  );
}
