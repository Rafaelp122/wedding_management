import { APIRequestContext } from "@playwright/test";

const API_BASE_URL = process.env.VITE_API_URL || "http://localhost:8000";

export interface CreateWeddingApiData {
  groom_name: string;
  bride_name: string;
  date: string; // YYYY-MM-DD
  location: string;
  expected_guests?: number;
}

export async function getAuthToken(
  request: APIRequestContext,
  email = "planner@example.com",
  password = "password123" // pragma: allowlist secret
): Promise<string> {
  const response = await request.post(`${API_BASE_URL}/api/v1/auth/token/`, {
    data: { email, password },
  });
  if (!response.ok()) {
    throw new Error(`Failed to get auth token for ${email}: ${response.statusText()}`);
  }
  const data = await response.json();
  return data.access;
}

export async function createWeddingViaApi(
  request: APIRequestContext,
  token: string,
  weddingData: CreateWeddingApiData
) {
  const response = await request.post(`${API_BASE_URL}/api/v1/weddings/`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    data: weddingData,
  });

  if (!response.ok()) {
    const errorText = await response.text();
    throw new Error(`Failed to create wedding via API: ${response.status()} ${errorText}`);
  }

  return await response.json();
}

export async function deleteWeddingViaApi(
  request: APIRequestContext,
  token: string,
  weddingUuid: string
) {
  const response = await request.delete(`${API_BASE_URL}/api/v1/weddings/${weddingUuid}/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok() && response.status() !== 404) {
    throw new Error(`Failed to delete wedding via API: ${response.status()}`);
  }
}
