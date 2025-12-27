// veridian_atlas/ui/src/api/client.js

const BASE = "http://127.0.0.1:8000";

/**
 * List all available deals (for dropdown, onboarding)
 * Endpoint: GET /deals
 */
export async function listDeals() {
  const res = await fetch(`${BASE}/deals`);
  const data = await res.json();
  return data.deals || [];
}

/**
 * Ask a question for a specific deal
 * Endpoint: POST /ask/{dealId}
 */
export async function askRagQuestion(dealId, query, topK = 3) {
  const res = await fetch(`${BASE}/ask/${dealId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      deal_id: dealId,
      query,
      top_k: topK,
    }),
  });

  if (!res.ok) {
    console.error("API Error:", await res.text());
    throw new Error(`RAG API error for deal ${dealId}`);
  }

  return res.json();
}

/**
 * Document / Clause Retrieval (no LLM answer, just context blocks)
 * Endpoint: POST /search/{dealId}
 */
export async function searchDeal(dealId, query, topK = 5) {
  const res = await fetch(`${BASE}/search/${dealId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      deal_id: dealId,
      query,
      top_k: topK,
    }),
  });

  return res.json();
}

/**
 * Fetch a specific chunk by ID for a specific deal
 * Endpoint: GET /chunk/{dealId}/{chunkId}
 */
export async function fetchChunk(dealId, chunkId) {
  const res = await fetch(`${BASE}/chunk/${dealId}/${chunkId}`);
  return res.json();
}

/**
 * Pull listing of raw + processed docs for UI (sidebar / tree)
 * Endpoint: GET /deals/{dealId}/docs
 */
export async function fetchDealDocuments(dealId) {
  const res = await fetch(`${BASE}/deals/${dealId}/docs`);
  return res.json();
}

/**
 * Basic API health check (UI entry screen)
 * Endpoint: GET /health
 */
export async function apiHealth() {
  const res = await fetch(`${BASE}/health`);
  return res.json();
}

export async function fetchChunkForDeal(deal_id, chunk_id) {
  const res = await fetch(`${BASE}/chunk/${deal_id}/${chunk_id}`);
  return res.json();
}

export default {
  listDeals,
  askRagQuestion,
  searchDeal,
  fetchChunk,
  fetchDealDocuments,
  apiHealth,
  fetchChunkForDeal
};
