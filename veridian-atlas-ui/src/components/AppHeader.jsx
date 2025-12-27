// src/components/AppHeader.jsx
export default function AppHeader() {
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
      <h1 className="text-sm font-semibold text-gray-300 tracking-tight">
        Veridian Atlas
      </h1>

      <div
        className="
          text-[11px] text-gray-400
          border border-[#2c2c2c]
          px-2.5 py-1 rounded-md
          hover:border-[#3c3c3c]
        "
      >
        RAG Engine v1
      </div>
    </header>
  );
}
