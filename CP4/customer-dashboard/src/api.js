// TASK 144: Configure frontend API settings
// DESCRIPTION: Read the FastAPI base URL and API key from Vite environment
// variables so individual React components do not contain hard-coded values.

export const BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

export const API_KEY =
  import.meta.env.VITE_API_KEY;