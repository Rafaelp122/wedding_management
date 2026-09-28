import { useState, useMemo } from "react";
import { AlertCircle, FileText, CheckCircle2, Clock } from "lucide-react";

import { useContractsList } from "@/api/generated/v1/endpoints/contracts/contracts";
import { useSuppliersList } from "@/api/generated/v1/endpoints/suppliers/suppliers";
import { useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";
import { getApiErrorInfo } from "@/api/error-utils";
import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import {
  ListPageErrorState,
  ListPageLoadingState,
} from "@/components/page-states";
import { PageContainer } from "@/components/layouts/PageContainer";
import { PageHeader } from "@/components/layouts/PageHeader";
import { PageFilterBar } from "@/components/layouts/PageFilterBar";
import { PageCardContainer } from "@/components/layouts/PageCardContainer";
import { Card } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { CONTRACT_STATUS_OPTIONS } from "@/features/contracts/constants";
import {
  buildWeddingMap,
  countContractsByStatus,
  filterContractsBySearch,
} from "../utils/contract-list-helpers";
import { ContractsTable } from "../components/ContractsTable";
import { ContractDetailDialog } from "../components/ContractDetailDialog";

export default function ContractsGlobalPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [supplierFilter, setSupplierFilter] = useState<string>("all");
  const [selectedContract, setSelectedContract] = useState<ContractOut | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);

  // Consulta de contratos da assessoria
  const contractsParams = useMemo(() => {
    return {
      status: statusFilter !== "all" ? statusFilter : undefined,
      supplier_id: supplierFilter !== "all" ? supplierFilter : undefined,
    };
  }, [statusFilter, supplierFilter]);

  const {
    data: contractsResponse,
    isLoading: isLoadingContracts,
    error: contractsError,
    refetch,
  } = useContractsList(contractsParams);

  // Consulta de fornecedores para filtro
  const { data: suppliersResponse } = useSuppliersList();
  const suppliers = suppliersResponse?.data?.items ?? [];

  // Consulta de casamentos para identificação visual
  const { data: weddingsResponse } = useWeddingsList();
  const weddings = weddingsResponse?.data?.items ?? [];

  const weddingMap = useMemo(() => buildWeddingMap(weddings), [weddings]);

  const contracts = contractsResponse?.data?.items ?? [];


  const filteredContracts = useMemo(() => {
    return filterContractsBySearch(contracts, search, weddingMap);
  }, [contracts, search, weddingMap]);

  const { total, signed: signedCount, pending: pendingCount } = useMemo(
    () => countContractsByStatus(contracts),
    [contracts],
  );

  const handleOpenDetail = (contract: ContractOut) => {
    setSelectedContract(contract);
    setDetailOpen(true);
  };

  if (contractsError) {
    const { message } = getApiErrorInfo(
      contractsError,
      "Não foi possível carregar os contratos.",
    );
    return <ListPageErrorState message={message} onRetry={refetch} />;
  }

  return (
    <PageContainer>
      <PageHeader
        title="Contratos"
        description="Gestão centralizada de todos os contratos e termos aditivos da assessoria."
      />

      {/* Métricas rápidas da visão global */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="p-4 flex items-center gap-4">
          <div className="p-3 bg-primary/10 rounded-full text-primary">
            <FileText className="size-5" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground uppercase font-medium">
              Total de Contratos
            </p>
            <h3 className="text-2xl font-bold">{total}</h3>
          </div>
        </Card>
        <Card className="p-4 flex items-center gap-4">
          <div className="p-3 bg-green-500/10 rounded-full text-green-600">
            <CheckCircle2 className="size-5" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground uppercase font-medium">
              Formalizados / Assinados
            </p>
            <h3 className="text-2xl font-bold">{signedCount}</h3>
          </div>
        </Card>
        <Card className="p-4 flex items-center gap-4">
          <div className="p-3 bg-yellow-500/10 rounded-full text-yellow-600">
            <Clock className="size-5" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground uppercase font-medium">
              Pendentes de Assinatura
            </p>
            <h3 className="text-2xl font-bold">{pendingCount}</h3>
          </div>
        </Card>
      </div>

      {/* Barra de Filtros */}
      <PageFilterBar
        search={search}
        onSearchChange={setSearch}
        searchPlaceholder="Buscar por contrato, fornecedor ou casamento..."
      >
        <Select
          value={statusFilter}
          onValueChange={(val) => setStatusFilter(val)}
        >
          <SelectTrigger className="w-full sm:w-44" aria-label="Filtrar por status">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos os status</SelectItem>
            {CONTRACT_STATUS_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={supplierFilter}
          onValueChange={(val) => setSupplierFilter(val)}
        >
          <SelectTrigger className="w-full sm:w-52" aria-label="Filtrar por fornecedor">
            <SelectValue placeholder="Fornecedor" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos os fornecedores</SelectItem>
            {suppliers.map((s) => (
              <SelectItem key={s.uuid} value={s.uuid}>
                {s.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </PageFilterBar>

      {/* Conteúdo Principal */}
      <PageCardContainer>
        <div className="px-6 py-4 border-b border-border">
          <h3 className="text-base font-semibold text-foreground">
            {isLoadingContracts
              ? "Carregando contratos..."
              : `${filteredContracts.length} de ${contracts.length} contratos listados`}
          </h3>
        </div>
        <div className="p-6">
          {isLoadingContracts ? (
            <ListPageLoadingState />
          ) : filteredContracts.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <AlertCircle className="mb-4 h-12 w-12 text-muted-foreground" />
              <h3 className="text-lg font-semibold">Nenhum contrato encontrado</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Tente ajustar os filtros de busca ou status.
              </p>
            </div>
          ) : (
            <ContractsTable
              contracts={filteredContracts}
              weddingMap={weddingMap}
              onViewDetails={handleOpenDetail}
            />
          )}
        </div>
      </PageCardContainer>

      {/* Diálogo de Detalhes do Contrato Selecionado */}
      {selectedContract && (
        <ContractDetailDialog
          contractUuid={selectedContract.uuid}
          weddingUuid={selectedContract.wedding}
          open={detailOpen}
          onOpenChange={(open) => {
            setDetailOpen(open);
            if (!open) {
              setSelectedContract(null);
            }
          }}
        />
      )}
    </PageContainer>
  );
}
