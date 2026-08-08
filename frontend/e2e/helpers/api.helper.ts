import { APIRequestContext } from "@playwright/test";
import { API_BASE_URL } from "../constants";

/**
 * Payload interface for creating a wedding via API.
 */
export interface CreateWeddingApiData {
  /** Groom's full name. */
  groom_name: string;
  /** Bride's full name. */
  bride_name: string;
  /** Wedding date in YYYY-MM-DD format. */
  date: string;
  /** Venue or city location. */
  location: string;
  /** Optional estimated guest count. */
  expected_guests?: number;
}

/**
 * Authenticates via backend API and returns JWT access token.
 *
 * @param request Playwright APIRequestContext.
 * @param email User email address.
 * @param password User password.
 * @returns JWT access token string.
 */
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

/**
 * Creates a wedding entity directly via backend REST API.
 *
 * @param request Playwright APIRequestContext.
 * @param token JWT access token.
 * @param weddingData Wedding payload data.
 * @returns Created wedding JSON object.
 */
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

/**
 * Deletes a wedding entity directly via backend REST API.
 *
 * @param request Playwright APIRequestContext.
 * @param token JWT access token.
 * @param weddingUuid UUID of the wedding to delete.
 */
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
