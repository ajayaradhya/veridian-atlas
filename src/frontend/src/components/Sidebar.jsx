// src/components/Sidebar.jsx
import { useState, useRef, useEffect } from "react";
import { Trash2, User } from "lucide-react";

// --------------------------------------
// DATE GROUPING
// --------------------------------------
function groupByDate(history) {
  const today = new Date();
  const start = new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime();
  const yesterdayStart = start - 86400000;
  const weekStart = start - 86400000 * 7;

  const groups = { Today: [], Yesterday: [], "This Week": [], Older: [] };

  history.forEach((item) => {
    const ts = new Date(item.timestamp).getTime();
    if (ts >= start) groups.Today.push(item);
    else if (ts >= yesterdayStart) groups.Yesterday.push(item);
    else if (ts >= weekStart) groups["This Week"].push(item);
    else groups.Older.push(item);
  });

  return groups;
}

// Format Time Display
function formatTime(timestamp) {
  const d = new Date(timestamp);
  return d.toLocaleString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

export default function Sidebar({ history, setHistory, onSelect, onNewChat }) {
  const [search, setSearch] = useState("");
  const [width, setWidth] = useState(280);
  const [hoverItem, setHoverItem] = useState(null);
  const [hoverPos, setHoverPos] = useState({ x: 0, y: 0 });
  const resizing = useRef(false);

  // --------------------------------------
  // RESIZE LOGIC
  // --------------------------------------
  const startResize = () => {
    resizing.current = true;
    document.body.style.userSelect = "none";
  };
  const resize = (e) => {
    if (!resizing.current) return;
    setWidth(Math.min(Math.max(e.clientX, 240), 420));
  };
  const stopResize = () => {
    resizing.current = false;
    document.body.style.userSelect = "";
  };
  useEffect(() => {
    window.addEventListener("mousemove", resize);
    window.addEventListener("mouseup", stopResize);
    return () => {
      window.removeEventListener("mousemove", resize);
      window.removeEventListener("mouseup", stopResize);
    };
  }, []);

  // DELETE
  const deleteItem = (id) => setHistory((prev) => prev.filter((x) => x.timestamp !== id));
  const clearAll = () => setHistory([]);

  const filtered = history.filter((x) =>
    (x.query + (x.deal || "")).toLowerCase().includes(search.toLowerCase())
  );
  const grouped = groupByDate(filtered);

  // Hover logic
  const handleHover = (e, item) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setHoverPos({ x: rect.right + 10, y: rect.top + rect.height / 2 });
    setHoverItem(item);
  };
  const clearHover = () => setHoverItem(null);

  // --------------------------------------
  return (
    <aside
      style={{ width }}
      className="relative flex flex-col h-screen bg-[#0d0d0d] border-r border-[#1a1a1a] dark-scroll"
    >
      {/* Resize Handle */}
      <div
        onMouseDown={startResize}
        className="absolute right-0 top-0 w-[6px] h-full cursor-col-resize hover:bg-white/10 z-40"
      />

      {/* NEW CHAT */}
      <div className="border-b border-[#1a1a1a] p-3">
        <button
          className="w-full bg-[#161616] hover:bg-[#212121] py-2 text-sm rounded-md"
          onClick={onNewChat}
        >
          + New Chat
        </button>
      </div>

      {/* SEARCH */}
      <div className="border-b border-[#1a1a1a] p-3">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search history..."
          className="w-full px-3 py-2 text-sm rounded-md bg-[#111] border border-[#2b2b2b] focus:border-[#3b3b3b] outline-none"
        />
      </div>

        {/* HISTORY LIST */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6 max-h-[calc(100vh-230px)] dark-scroll">
          {Object.values(grouped).every((v) => v.length === 0) && (
            <p className="text-xs text-gray-500 pl-1">No history found.</p>
          )}

          {Object.entries(grouped).map(([label, items]) => {
            if (items.length === 0) return null;

            const sortedItems = [...items].sort(
              (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
            );

            return (
              <div key={label} className="space-y-2">
                <p className="text-[11px] text-gray-500 uppercase tracking-wide pl-1">{label}</p>

                {sortedItems.map((item) => (
                  <div
                    key={item.timestamp}
                    className="
                      relative flex items-center justify-between
                      bg-[#0f0f0f] hover:bg-[#1a1a1a]
                      rounded-md px-3 py-2 cursor-pointer transition
                    "
                    onMouseEnter={(e) => handleHover(e, item)}
                    onMouseLeave={clearHover}
                  >
                    <div
                      className="flex-1 min-w-0"
                      onClick={() => onSelect({ deal: item.deal, query: item.query })}
                    >
                      <p className="text-sm text-gray-200 truncate">{item.query}</p>
                      {item.deal && (
                        <span className="text-[10px] text-gray-500 bg-[#1c1c1c] px-2 py-[1px] rounded mt-1 inline-block truncate">
                          {item.deal}
                        </span>
                      )}
                    </div>

                    {/* DELETE ICON ALWAYS VISIBLE BUT LIGHT */}
                    <button
                      className="
                        text-gray-600 opacity-60
                        hover:opacity-100 hover:text-red-500
                        transition ml-2 z-50
                      "
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteItem(item.timestamp);
                      }}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                ))}
              </div>
            );
          })}
        </div>


      {/* FLOATING HOVER PREVIEW */}
      {hoverItem && (
        <div
          className="fixed bg-[#0e0e0e]/95 backdrop-blur-xl border border-[#272727]
          rounded-xl shadow-2xl p-4 text-sm text-gray-200 w-[260px]
          z-[9999] pointer-events-none animate-fadeIn"
          style={{
            top: hoverPos.y - 40,
            left: hoverPos.x
          }}
        >
          <p className="mb-2 leading-relaxed">{hoverItem.query}</p>

          {hoverItem.deal && (
            <p className="text-[11px] text-gray-400 border-t border-[#222] pt-2">
              Deal: <span className="text-gray-300">{hoverItem.deal}</span>
            </p>
          )}

          <p className="text-[11px] text-gray-500 mt-1">
            {formatTime(hoverItem.timestamp)}
          </p>
        </div>
      )}

      {/* FOOTER */}
      <div className="border-t border-[#1a1a1a] p-3 space-y-3">
        {history.length > 0 && (
          <button
            className="w-full border border-[#333] hover:bg-[#191919] text-gray-300 rounded-md py-2 text-sm"
            onClick={clearAll}
          >
            Clear History
          </button>
        )}

        <div className="flex items-center gap-2 p-2 rounded-md hover:bg-[#111] cursor-pointer">
          <div className="w-8 h-8 bg-[#222] rounded-full flex items-center justify-center">
            <User size={15} className="text-gray-300" />
          </div>
          <div>
            <p className="text-sm">Ajay</p>
            <p className="text-[11px] text-gray-500">Manage Account</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
