import { defineConfig } from "orval";

export default defineConfig({
  weddingApi: {
    input: "../backend/openapi.json",
    output: {
      mode: "tags-split",
      target: "./src/api/generated/api.ts",
      schemas: "./src/api/generated/models",
      client: "react-query",
      mock: true,
      override: {
        mutator: {
          path: "./src/api/api-instance.ts",
          name: "customInstance",
        },
      },
    },
  },
});
