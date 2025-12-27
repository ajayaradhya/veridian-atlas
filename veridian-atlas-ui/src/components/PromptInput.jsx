// src/components/PromptInput.jsx
import { Send } from "lucide-react";

export default function PromptInput({ query, setQuery, onAsk }) {
  const handleSubmit = () => {
    if (!query.trim()) return;
    onAsk();
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
        <input
          className="
            flex-1 bg-transparent text-gray-200 placeholder-gray-500
            focus:outline-none
            text-sm
          "
          placeholder="Ask anything about the deal..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
        />

        <button
          onClick={handleSubmit}
          className="
            h-9 w-9 flex items-center justify-center
            rounded-lg
            bg-[#2c2c2c]
            hover:bg-[#3a3a3a]
            text-gray-300
            transition
          "
        >
          <Send size={20} />
        </button>
      </div>

      <p className="text-[11px] text-gray-500 text-center mt-3">
        Veridian Atlas may produce incomplete or outdated interpretations. Verify citations.
      </p>
    </div>
  );
}
