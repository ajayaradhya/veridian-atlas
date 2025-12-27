// src/components/Sidebar.jsx
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { User } from "lucide-react"; // profile icon

// Group by date buckets like ChatGPT
function groupByDate(history) {
  const today = new Date();
  const startOfToday = new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime();
  const startOfYesterday = startOfToday - 86400000;
  const startOfWeek = startOfToday - 86400000 * 7;

  const groups = {
    Today: [],
    Yesterday: [],
    "This Week": [],
    Older: [],
  };

  history.forEach((item) => {
    const ts = new Date(item.timestamp).getTime();
    if (ts >= startOfToday) groups.Today.push(item);
    else if (ts >= startOfYesterday) groups.Yesterday.push(item);
    else if (ts >= startOfWeek) groups["This Week"].push(item);
    else groups.Older.push(item);
  });

  return groups;
}

export default function Sidebar({ history, setHistory, onSelect, onNewChat }) {
  const [searchTerm, setSearchTerm] = useState("");

  const filtered = history.filter((item) =>
    item.query.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const grouped = groupByDate(filtered);

  const deleteItem = (timestamp) =>
    setHistory((prev) => prev.filter((h) => h.timestamp !== timestamp));

  const deleteAll = () => {
    if (confirm("Clear entire history? This action cannot be undone.")) {
      setHistory([]);
      setSearchTerm("");
    }
  };

  return (
    <div className="h-screen w-64 bg-[#0a0a0a] text-gray-200 border-r border-[#1c1c1c] flex flex-col dark-scroll">

      {/* NEW CHAT */}
      <div className="p-4 border-b border-[#1c1c1c]">
        <Button
          className="w-full bg-[#1a1a1a] hover:bg-[#262626] text-gray-100"
          onClick={() => {
            onNewChat();
            setSearchTerm("");
          }}
        >
          + New Chat
        </Button>
      </div>

      {/* SEARCH INPUT */}
      <div className="p-4 border-b border-[#1c1c1c] space-y-2">
        <input
          placeholder="Search history..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-3 py-2 rounded-md bg-[#1b1b1b] border border-[#2b2b2b]
            text-gray-200 text-sm focus:outline-none focus:border-[#3c3c3c]"
        />
        {searchTerm && (
          <button
            onClick={() => setSearchTerm("")}
            className="text-[11px] text-gray-500 hover:text-gray-300"
          >
            Clear
          </button>
        )}
      </div>

      {/* HISTORY LIST */}
      <ScrollArea className="flex-1 px-3 py-3 space-y-5">
        {Object.values(grouped).every((arr) => arr.length === 0) && (
          <p className="text-xs text-gray-500 mt-4">No history found.</p>
        )}

        {Object.entries(grouped).map(([label, items]) =>
          items.length > 0 && (
            <div key={label}>
              <p className="text-[11px] text-gray-500 uppercase tracking-wide mb-2">
                {label}
              </p>

              {items.map((item) => (
                <div
                  key={item.timestamp}
                  className="flex items-center justify-between group"
                >
                  {/* Select item */}
                  <button
                    onClick={() => onSelect(item.query)}
                    className="flex-1 text-left px-3 py-2 text-sm rounded-md
                      hover:bg-[#1f1f1f] transition"
                  >
                    {item.query}
                  </button>

                  {/* Delete single */}
                  <button
                    onClick={() => deleteItem(item.timestamp)}
                    className="opacity-0 group-hover:opacity-100 transition text-gray-500 hover:text-red-500 px-2"
                    title="Delete"
                  >
                    🗑
                  </button>
                </div>
              ))}
            </div>
          )
        )}
      </ScrollArea>

      {/* FOOTER */}
      <div className="p-4 border-t border-[#1c1c1c] space-y-3">

        {/* DELETE ALL - LIGHTER GRAY BUTTON */}
        <Button 
          variant="outline"
          className="w-full border-[#bababa] text-gray hover:bg-[#212121]"
          onClick={deleteAll}
        >
          Clear History
        </Button>

        {/* CHATGPT-STYLE PROFILE SECTION */}
        <div
          className="flex items-center gap-3 p-2 rounded-lg hover:bg-[#1a1a1a]
            cursor-pointer transition"
        >
          <div className="w-8 h-8 rounded-full bg-[#2a2a2a] flex items-center justify-center">
            <User size={16} className="text-gray-300" />
          </div>

          <div className="flex flex-col leading-tight">
            <span className="text-sm font-medium text-gray-200">Ajay</span>
            <span className="text-[11px] text-gray-500">Manage Account</span>
          </div>
        </div>

      </div>
    </div>
  );
}
