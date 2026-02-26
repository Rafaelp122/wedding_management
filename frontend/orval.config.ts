import { defineConfig } from "orval";

export default defineConfig({
  weddingApi: {
    input: "../openapi.json",
    output: {
      mode: "tags-split",
      target: "./src/api/generated/endpoints",
      schemas: "./src/api/generated/models",
      client: "react-query",
      httpClient: "axios",
      prettier: true,
      override: {
        mutator: {
          path: "src/api/mutator/custom-instance.ts",
          name: "customInstance",
        },
        query: {
          useQuery: true,
          useInfinite: false,
          useMutation: true,
        },
      },
    },
  },
  weddingZod: {
    input: "../openapi.json",
    output: {
      mode: "tags-split",
      target: "./src/api/generated/zod", // Pasta separada para não bagunçar
      client: "zod",
      prettier: true,
    },
  },
});
