// src/components/AppHeader.jsx
import { useEffect, useState } from "react";

export default function AppHeader({ activeDeal, setActiveDeal }) {
  const [deals, setDeals] = useState([]);

  // Fetch deal list from backend
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/deals");
        const data = await res.json();
        setDeals(data.deals ?? []);
      } catch {
        setDeals([]);
      }
    })();
  }, []);

  return (
    <header
      className="
        w-full sticky top-0 z-40
        bg-[#171717]/70 backdrop-blur-md
        border-b border-[#222]
        flex items-center justify-between
        px-6 py-2.5
      "
    >

      {/* Product Name */}
      <div className="relative group cursor-default">
        <h1 className="text-sm font-semibold text-gray-300 tracking-tight">
          Veridian Atlas
        </h1>
        <span
          className="
            pointer-events-none absolute left-0 -bottom-[3px] h-[1px]
            bg-gray-200/60 rounded-full w-0 group-hover:w-full
            transition-all duration-200 ease-out
          "
        />
      </div>

      {/* DEAL SELECTOR */}
      <div className="flex items-center gap-3">
        <select
          value={activeDeal}
          onChange={(e) => setActiveDeal(e.target.value)}
          className="
            bg-[#121212] text-gray-200 text-xs
            border border-[#2a2a2a]
            px-3 py-1.5 rounded-md
            focus:outline-none focus:border-[#3b3b3b]
          "
        >
          {!activeDeal && <option value="">Select Deal...</option>}
          {deals.map((deal) => (
            <option key={deal} value={deal}>
              {deal}
            </option>
          ))}
        </select>

        {/* MODEL TAG */}
        <div
          className="
            text-[11px] text-gray-400
            border border-[#2c2c2c]
            px-2.5 py-1 rounded-md
            hover:border-[#3c3c3c]
            cursor-default
          "
        >
          RAG Engine v1
        </div>
      </div>
    </header>
  );
}
