import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// TASK 133: Configure the Vite development server
// DESCRIPTION: Run React on port 3000 so it matches the FastAPI CORS configuration.

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
  },
});