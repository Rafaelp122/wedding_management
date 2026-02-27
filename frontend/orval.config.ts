import { defineConfig } from "orval";

export default defineConfig({
  weddingApi: {
    input: "../openapi.json",
    output: {
      mode: "tags-split",
      target: "./src/api/generated/v1/endpoints",
      schemas: "./src/api/generated/v1/models",
      client: "react-query",
      httpClient: "axios",
      prettier: true,
      override: {
        mutator: {
          path: "src/api/custom-instance.ts",
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
      target: "./src/api/generated/v1/zod",
      client: "zod",
      prettier: true,
    },
  },
});
