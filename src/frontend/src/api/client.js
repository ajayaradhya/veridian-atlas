// src/api/client.js

// Load backend URL from Vite env file (.env)
// Fallback to localhost if missing
const BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

/**
 * List all available deals
 * GET /deals
 */
export async function listDeals() {
  const res = await fetch(`${BASE}/deals`);
  const data = await res.json();
  return data.deals || [];
}

/**
 * Ask a RAG question for a specific deal
 * POST /ask/{dealId}
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
 * Retrieve chunks (context blocks only)
 * POST /search/{dealId}
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
 * Fetch a specific chunk by ID
 * GET /chunk/{dealId}/{chunkId}
 */
export async function fetchChunk(dealId, chunkId) {
  const res = await fetch(`${BASE}/chunk/${dealId}/${chunkId}`);
  return res.json();
}

/**
 * Document listing for UI tree
 * GET /deals/{dealId}/docs
 */
export async function fetchDealDocuments(dealId) {
  const res = await fetch(`${BASE}/deals/${dealId}/docs`);
  return res.json();
}

/**
 * API Health Check
 * GET /health
 */
export async function apiHealth() {
  const res = await fetch(`${BASE}/health`);
  return res.json();
}

/**
 * Direct chunk fetch (used by Citation viewer)
 * GET /chunk/{deal}/{chunk}
 */
export async function fetchChunkForDeal(deal_id, chunk_id) {
  const res = await fetch(`${BASE}/chunk/${deal_id}/${chunk_id}`);
  return res.json();
}

// Export all
export default {
  listDeals,
  askRagQuestion,
  searchDeal,
  fetchChunk,
  fetchDealDocuments,
  apiHealth,
  fetchChunkForDeal,
};
