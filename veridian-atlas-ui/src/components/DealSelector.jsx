// src/components/DealSelector.jsx
export default function DealSelector({ deals, selectedDeal, setSelectedDeal }) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-gray-300 text-sm">Deal:</span>
      <select
        value={selectedDeal}
        onChange={(e) => setSelectedDeal(e.target.value)}
        className="bg-[#1A1A1A] border border-[#2A2A2A] text-gray-100 px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-600"
      >
        {deals.map((deal) => (
          <option key={deal} value={deal}>{deal}</option>
        ))}
      </select>
    </div>
  );
}
