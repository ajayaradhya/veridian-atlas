const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function askRagQuestion(query, top_k = 4) {
  const response = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k }),
  });

  if (!response.ok) throw new Error(`API Error: ${response.status}`);
  return await response.json();
}
