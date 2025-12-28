// src/components/LoadingState.jsx
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
  const [fade, setFade] = useState(true);

  // Rotate messages every 2 seconds with fade
  useEffect(() => {
    const interval = setInterval(() => {
      setFade(false);
      setTimeout(() => {
        setIndex((i) => (i + 1) % messages.length);
        setFade(true);
      }, 250);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center pt-32 pb-20 relative z-10">
      
      {/* Center Glow */}
      <div className="absolute w-52 h-52 bg-[#ffffff0a] blur-3xl rounded-full" />

      {/* Spinner with soft breathing motion */}
      <div className="flex items-center justify-center mb-6 animate-[pulse_1.8s_ease-in-out_infinite]">
        <Loader2 className="w-12 h-12 text-gray-400 animate-spin drop-shadow-[0_0_6px_rgba(255,255,255,0.25)]" />
      </div>

      {/* Status Message w/ Fade */}
      <p
        className={`
          text-[17px] font-medium text-gray-200 select-none
          transition-opacity duration-300
          ${fade ? "opacity-100" : "opacity-0"}
        `}
      >
        {messages[index]}
      </p>

      {/* Progress Pulse Bar */}
      <div className="mt-6 w-40 h-[3px] bg-[#2a2a2a] rounded-full overflow-hidden">
        <div className="h-full bg-gray-300 rounded-full animate-[loaderbar_1.5s_linear_infinite]" />
      </div>

      {/* Dot loader underbar
      <div className="flex gap-2 mt-4 opacity-70">
        <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
        <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-150" />
        <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-300" />
      </div> */}
    </div>
  );
}
