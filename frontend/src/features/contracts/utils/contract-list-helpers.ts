import type { ContractOut } from "@/api/generated/v1/models/contractOut";

interface WeddingLike {
  uuid: string;
  groom_name?: string | null;
  bride_name?: string | null;
}

/** Monta mapa uuid -> "Noivo & Noiva" para exibição e busca client-side. */
export function buildWeddingMap(weddings: WeddingLike[]): Record<string, string> {
  const map: Record<string, string> = {};
  for (const w of weddings) {
    map[w.uuid] = `${w.groom_name} & ${w.bride_name}`;
  }
  return map;
}

/** Filtra contratos por termo livre (contrato, fornecedor ou casamento). */
export function filterContractsBySearch(
  contracts: ContractOut[],
  search: string,
  weddingMap: Record<string, string>,
): ContractOut[] {
  if (!search.trim()) return contracts;
  const term = search.toLowerCase();
  return contracts.filter((c) => {
    const name = (c.name || c.description || "").toLowerCase();
    const supplierName = (c.supplier_name || "").toLowerCase();
    const weddingTitle = (weddingMap[c.wedding] || "").toLowerCase();
    return (
      name.includes(term) || supplierName.includes(term) || weddingTitle.includes(term)
    );
  });
}

/** Contadores por status para as métricas da visão global. */
export function countContractsByStatus(contracts: ContractOut[]): {
  total: number;
  signed: number;
  pending: number;
} {
  return {
    total: contracts.length,
    signed: contracts.filter((c) => c.status === "SIGNED").length,
    pending: contracts.filter((c) => c.status === "PENDING").length,
  };
}
