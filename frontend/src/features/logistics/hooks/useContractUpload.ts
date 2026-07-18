import { useState } from "react";
import { toast } from "sonner";
import type { z } from "zod";

import {
  useLogisticsContractsCreateFull,
  useLogisticsContractsUploadUrl,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import type { LogisticsContractsCreateBody } from "@/api/generated/v1/zod/logistics/logistics";
import type { ItemDraft } from "../components/contracts/ContractItemDrafts";

type CreateContractFormData = z.input<typeof LogisticsContractsCreateBody>;

interface UseContractUploadProps {
  weddingUuid: string;
  onSuccess: () => void;
}

export function useContractUpload({ weddingUuid, onSuccess }: UseContractUploadProps) {
  const [isPending, setIsPending] = useState(false);
  const { mutateAsync: createFull } = useLogisticsContractsCreateFull();
  const { mutateAsync: getUploadUrl } = useLogisticsContractsUploadUrl();

  const uploadAndCreateContract = async (
    data: CreateContractFormData,
    selectedFile: File | null,
    itemDrafts: ItemDraft[],
    expense: {
      checked: boolean;
      category: string;
      numInstallments: number;
      firstDueDate: string;
    },
  ) => {
    setIsPending(true);
    try {
      let pdfFileKey: string | null = null;
      if (selectedFile) {
        const uploadUrlRes = await getUploadUrl({
          data: {
            filename: selectedFile.name,
            wedding_id: weddingUuid,
          },
        });

        const uploadResponse = await fetch(uploadUrlRes.data.upload_url, {
          method: "PUT",
          body: selectedFile,
          headers: {
            "Content-Type": selectedFile.type || "application/octet-stream",
          },
        });

        if (!uploadResponse.ok) {
          throw new Error(`Erro no envio do arquivo: ${uploadResponse.statusText}`);
        }

        pdfFileKey = uploadUrlRes.data.object_key;
      }

      const itemsData = JSON.stringify(
        itemDrafts.map((d) => ({
          name: d.name,
          quantity: d.quantity,
          acquisition_status: d.acquisition_status,
        })),
      );

      await createFull({
        data: {
          wedding: data.wedding,
          supplier: data.supplier,
          name: data.name,
          total_amount: data.total_amount,
          status: data.status,
          description: data.description,
          parent: data.parent ?? null,
          items_data: itemsData,
          create_expense: expense.checked,
          expense_category: expense.checked ? expense.category : null,
          expense_num_installments: expense.checked
            ? expense.numInstallments
            : null,
          expense_first_due_date: expense.checked ? expense.firstDueDate : null,
          pdf_file_key: pdfFileKey,
        },
      });

      toast.success("Contrato criado com sucesso!");
      onSuccess();
      return true;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Erro desconhecido";
      toast.error(`Erro ao criar contrato: ${message}`);
      return false;
    } finally {
      setIsPending(false);
    }
  };

  return {
    uploadAndCreateContract,
    isPending,
  };
}
