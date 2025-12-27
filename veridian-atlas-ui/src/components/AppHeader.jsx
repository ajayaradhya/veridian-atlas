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

      {/* Product Name with Hover Underline */}
      <div className="relative group cursor-default">
        <h1 className="text-sm font-semibold text-gray-300 tracking-tight">
          Veridian Atlas
        </h1>

        <span
          className="
            pointer-events-none
            absolute left-0 -bottom-[3px] h-[1px]
            bg-gray-200/60 rounded-full
            w-0
            transition-all duration-200 ease-out
            group-hover:w-full
            z-10
          "
        />
      </div>

      {/* Model Tag */}
      <div
        className="
          text-[11px] text-gray-400
          border border-[#2c2c2c]
          px-2.5 py-1 rounded-md
          hover:border-[#3c3c3c] hover:text-gray-300
          transition cursor-default
        "
      >
        RAG Engine v1
      </div>
    </header>
  );
}
