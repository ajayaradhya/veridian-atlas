const BASE = "http://127.0.0.1:8000";

export async function askRagQuestion(query) {
  const res = await fetch(`${BASE}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query })
  });
  return res.json();
}

export async function fetchChunk(id) {
  const res = await fetch(`${BASE}/chunk/${id}`);
  return res.json();
}
