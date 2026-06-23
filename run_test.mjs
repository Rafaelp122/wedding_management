import { execSync } from "child_process";
const output = execSync(
  "npx vitest run src/features/dashboard/components/WeddingStatsCards.test.tsx --reporter=verbose",
  { cwd: "/home/rafael/projetos/wedding_management/frontend", encoding: "utf-8", timeout: 120000 }
);
console.log(output);
