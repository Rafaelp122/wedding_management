import { describe, expect, it } from "vitest";
import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import {
  buildWeddingMap,
  countContractsByStatus,
  filterContractsBySearch,
} from "./contract-list-helpers";

function makeContract(overrides: Partial<ContractOut>): ContractOut {
  return {
    uuid: "c-1",
    wedding: "w-1",
    name: "Buffet Completo",
    description: "",
    supplier_name: "Buffet Real",
    status: "SIGNED",
    ...overrides,
  } as unknown as ContractOut;
}

describe("contract-list-helpers", () => {
  it("builds wedding map as 'groom & bride'", () => {
    expect(
      buildWeddingMap([{ uuid: "w-1", groom_name: "João", bride_name: "Maria" }]),
    ).toEqual({ "w-1": "João & Maria" });
  });

  it("returns all contracts on blank search", () => {
    const contracts = [makeContract({})];
    expect(filterContractsBySearch(contracts, "   ", {})).toBe(contracts);
  });

  it("filters by contract, supplier or wedding title", () => {
    const contracts = [
      makeContract({ uuid: "c-1", name: "Buffet", supplier_name: "A", wedding: "w-1" }),
      makeContract({ uuid: "c-2", name: "Foto", supplier_name: "Click", wedding: "w-2" }),
    ];
    const map = { "w-2": "João & Maria" };
    expect(filterContractsBySearch(contracts, "buffet", map).map((c) => c.uuid)).toEqual(["c-1"]);
    expect(filterContractsBySearch(contracts, "click", map).map((c) => c.uuid)).toEqual(["c-2"]);
    expect(filterContractsBySearch(contracts, "maria", map).map((c) => c.uuid)).toEqual(["c-2"]);
  });

  it("counts total, signed and pending", () => {
    const contracts = [
      makeContract({ status: "SIGNED" }),
      makeContract({ status: "PENDING" }),
      makeContract({ status: "DRAFT" }),
    ];
    expect(countContractsByStatus(contracts)).toEqual({ total: 3, signed: 1, pending: 1 });
  });
});
