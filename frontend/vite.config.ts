import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
export default defineConfig({
  resolve: { alias: { "@": new URL("./src", import.meta.url).pathname } },
  plugins: [
    react(),
    tailwindcss(),
    {
      name: "isolated-python-development-headers",
      configureServer(server) {
        server.middlewares.use((request, response, next) => {
          if (request.url?.startsWith("/python/"))
            response.setHeader("Access-Control-Allow-Origin", "*");
          if (request.url?.startsWith("/sandbox/")) {
            const origin = "http://" + request.headers.host;
            response.setHeader(
              "Content-Security-Policy",
              `default-src 'none'; script-src ${origin}/sandbox/ ${origin}/python/ 'wasm-unsafe-eval'; worker-src blob:; connect-src ${origin}/python/; frame-ancestors 'self'; base-uri 'none'; form-action 'none'`,
            );
          }
          next();
        });
      },
    },
  ],
  server: {
    proxy: { "/api": process.env.ACADEMY_API_PROXY || "http://127.0.0.1:8080" },
  },
});
