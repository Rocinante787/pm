import { type BoardData, initialData } from "@/lib/kanban";

export const getAuthHeaders = (token?: string): HeadersInit => {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
};

export const fetchBoard = async (token?: string): Promise<BoardData> => {
  try {
    const res = await fetch("/api/board", {
      headers: getAuthHeaders(token),
    });
    if (!res.ok) {
      throw new Error(`Failed to fetch board: ${res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    // If backend is unreachable (e.g. static preview), fallback to initialData
    console.warn("Could not connect to /api/board, using local seed data", err);
    return initialData;
  }
};

export const saveBoard = async (
  board: BoardData,
  token?: string
): Promise<BoardData> => {
  try {
    const res = await fetch("/api/board", {
      method: "PUT",
      headers: getAuthHeaders(token),
      body: JSON.stringify(board),
    });
    if (!res.ok) {
      throw new Error(`Failed to save board: ${res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    console.warn("Could not save to /api/board, changes saved locally only", err);
    return board;
  }
};

export const resetBoard = async (token?: string): Promise<BoardData> => {
  try {
    const res = await fetch("/api/board/reset", {
      method: "POST",
      headers: getAuthHeaders(token),
    });
    if (!res.ok) {
      throw new Error(`Failed to reset board: ${res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    console.warn("Could not reset on server, resetting to local seed", err);
    return initialData;
  }
};
