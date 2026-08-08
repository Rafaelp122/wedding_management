import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Key used to store authentication state in browser localStorage.
 */
export const AUTH_STORAGE_KEY = "wedding-auth-storage";

/**
 * Base URL for backend API requests.
 */
export const API_BASE_URL = process.env.VITE_API_URL ?? "http://localhost:8000";

/**
 * Path to saved storageState JSON for Planner user.
 */
export const PLANNER_STORAGE_PATH = path.resolve(__dirname, "./.auth/planner.json");

/**
 * Path to saved storageState JSON for Admin user.
 */
export const ADMIN_STORAGE_PATH = path.resolve(__dirname, "./.auth/admin.json");
