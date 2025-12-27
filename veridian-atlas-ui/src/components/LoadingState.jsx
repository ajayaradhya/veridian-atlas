import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";

const messages = [
  "Reading clauses…",
  "Analyzing covenants…",
  "Extracting legal context…",
  "Evaluating obligations and terms…",
  "Tracing clause lineage…",
  "Linking citations to document sources…",
  "Preparing final answer…"
];

export default function LoadingState() {
  const [index, setIndex] = useState(0);

  // Rotate through messages every 1.5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((i) => (i + 1) % messages.length);
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center mt-24 space-y-6 text-gray-300 relative z-10 animate-fadeIn">
      
      {/* Spinner */}
      <Loader2 className="w-10 h-10 text-gray-400 animate-spin" />

      {/* Dynamic message */}
      <p className="text-lg font-medium text-gray-300 transition-opacity duration-500">
        {messages[index]}
      </p>

      {/* Animated dots */}
      <div className="flex gap-2 mt-2">
        <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
        <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-150" />
        <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-300" />
      </div>
    </div>
  );
}
