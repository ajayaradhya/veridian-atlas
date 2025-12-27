// src/components/PromptInput.jsx
import { useRef } from "react";
import { Send } from "lucide-react";

export default function PromptInput({ query, setQuery, onAsk }) {
  const textareaRef = useRef(null);

  const handleSubmit = () => {
    if (!query.trim()) return;
    onAsk();
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && e.shiftKey) return; // allow newline
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
    <div className="w-full max-w-3xl mx-auto px-4">
      
      <div
        className="
          flex items-center gap-3
          w-full
          bg-[#1a1a1a]
          border border-[#2d2d2d]
          rounded-2xl
          px-5 py-3
          shadow-sm
          hover:border-[#3a3a3a]
          focus-within:border-[#4a4a4a]
          transition
        "
      >
        {/* Auto-resizing & vertically centered textarea */}
        <textarea
          ref={textareaRef}
          rows={1}
          className="
            flex-1 bg-transparent text-gray-200 placeholder-gray-500
            resize-none overflow-hidden
            focus:outline-none
            text-sm
            leading-[1.4]
            pt-[4px]          /* centers placeholder visually */
          "
          placeholder="Ask anything about the deal..."
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            autoResize();
          }}
          onKeyDown={handleKeyDown}
        />

        <button
          onClick={handleSubmit}
          className="
            h-9 w-9 flex items-center justify-center
            rounded-lg
            bg-[#2c2c2c]
            hover:bg-[#3a3a3a]
            text-gray-300 transition
          "
        >
          <Send size={18} />
        </button>
      </div>

      <p className="text-[11px] text-gray-400 text-center mt-3">
        Press Enter to send • Shift+Enter for a new line
      </p>
    </div>
  );
}
