import { useLocation } from "react-router-dom";
import { useWeddingsRead, useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";
import { useDocumentTitle } from "@/hooks/useDocumentTitle";

const PAGE_TITLES: Record<string, string> = {
  "/dashboard": "Dashboard Geral",
  "/weddings": "Casamentos",
  "/scheduler": "Scheduler",
  "/suppliers": "Fornecedores",
  "/settings": "Configurações",
};

/**
 * Hook customizado para encapsular a lógica de carregamento de dados do AppLayout,
 * incluindo detecção do ID do casamento atual a partir da rota, chamadas de API
 * e atualização do título do documento.
 */
export const useAppLayoutData = () => {
  const { pathname } = useLocation();

  // Match /weddings/:uuid (ignoring trailing slash or query params)
  const match = pathname.match(/^\/weddings\/([^/]+)$/);
  const weddingUuid = match ? match[1] : null;

  const { data: weddingResponse, isLoading: isLoadingWedding } = useWeddingsRead(
    weddingUuid ?? "",
    { query: { enabled: !!weddingUuid } }
  );
  const wedding = weddingResponse?.data;

  const { data: weddingsListResponse } = useWeddingsList(
    undefined,
    { query: { enabled: !!weddingUuid } }
  );
  const weddingsList = weddingsListResponse?.data?.items ?? [];

  const pageTitle = pathname.startsWith("/weddings/")
    ? "Detalhes do Casamento"
    : pathname.startsWith("/suppliers/")
      ? "Detalhes do Fornecedor"
      : (PAGE_TITLES[pathname] ?? "Painel de Controle");

  useDocumentTitle(
    pathname.startsWith("/weddings/") && wedding
      ? `Casamento: ${wedding.groom_name} & ${wedding.bride_name}`
      : pageTitle
  );

  return {
    weddingUuid,
    wedding,
    isLoadingWedding,
    weddingsList,
    pageTitle,
  };
};
