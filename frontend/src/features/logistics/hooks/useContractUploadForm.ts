import { useState, useCallback } from "react";
import { useForm, type Resolver } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import type { z } from "zod";

import {
  useLogisticsContractsCreateFull,
  useLogisticsContractsList,
  useLogisticsSuppliersList,
  useLogisticsContractsUploadUrl,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import { useFinancesCategoriesList } from "@/api/generated/v1/endpoints/finances/finances";
import { LogisticsContractsCreateBody } from "@/api/generated/v1/zod/logistics/logistics";
import { uploadFileToR2 } from "@/services/r2";
import type { ItemDraft } from "../components/contracts/ContractItemDrafts";

export type CreateContractFormData = z.input<typeof LogisticsContractsCreateBody>;

export interface ExpenseFieldsState {
  checked: boolean;
  category: string;
  numInstallments: number;
  firstDueDate: string;
}

export interface UseContractUploadFormProps {
  weddingUuid: string;
  prefilledParentUuid?: string | null;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

/**
 * Hook para gerenciar o estado e submissão do formulário de criação de contrato.
 * Encapsula a lógica de formulário, data fetching (fornecedores, contratos e categorias),
 * upload de documentos para o R2, controle de rascunhos de itens e de criação de despesa associada.
 *
 * @param props Propriedades de configuração do hook contendo ID do casamento e callbacks.
 * @returns Estado do formulário, listas de dados, handlers de formulário e controle de diálogo.
 */
export function useContractUploadForm({
  weddingUuid,
  prefilledParentUuid,
  onOpenChange,
  onSuccess,
}: UseContractUploadFormProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [itemDrafts, setItemDrafts] = useState<ItemDraft[]>([]);
  const [expenseChecked, setExpenseChecked] = useState(false);
  const [expenseCategory, setExpenseCategory] = useState("");
  const [expenseNumInstallments, setExpenseNumInstallments] = useState(1);
  const [expenseFirstDueDate, setExpenseFirstDueDate] = useState(
    () => new Date().toISOString().slice(0, 10),
  );

  const { mutateAsync: createFull, isPending: isCreating } =
    useLogisticsContractsCreateFull();
  const { mutateAsync: getUploadUrl } = useLogisticsContractsUploadUrl();

  const { data: suppliersResponse } = useLogisticsSuppliersList();
  const suppliers = suppliersResponse?.data?.items ?? [];

  const { data: contractsResponse } = useLogisticsContractsList({
    wedding_id: weddingUuid,
  });
  const existingContracts = contractsResponse?.data?.items ?? [];

  const { data: categoriesResponse } = useFinancesCategoriesList({
    wedding_id: weddingUuid,
  });
  const categories = categoriesResponse?.data?.items ?? [];

  const form = useForm<CreateContractFormData>({
    resolver: zodResolver(LogisticsContractsCreateBody) as Resolver<CreateContractFormData>,
    defaultValues: {
      wedding: weddingUuid,
      supplier: "",
      name: "",
      total_amount: undefined,
      status: "DRAFT",
      description: "",
      parent: prefilledParentUuid || null,
    },
  });

  const handleExpenseChange = useCallback((v: ExpenseFieldsState) => {
    setExpenseChecked(v.checked);
    setExpenseCategory(v.category);
    setExpenseNumInstallments(v.numInstallments);
    setExpenseFirstDueDate(v.firstDueDate);
  }, []);

  const handleOpenChange = useCallback(
    (open: boolean) => {
      if (!open) {
        form.reset();
        setItemDrafts([]);
        setSelectedFile(null);
      }
      onOpenChange(open);
    },
    [form, onOpenChange],
  );

  const onSubmit = async (data: CreateContractFormData) => {
    try {
      let pdfFileKey: string | null = null;
      if (selectedFile) {
        const uploadUrlRes = await getUploadUrl({
          data: {
            filename: selectedFile.name,
            wedding_id: weddingUuid,
          },
        });

        await uploadFileToR2(uploadUrlRes.data.upload_url, selectedFile);

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
          create_expense: expenseChecked,
          expense_category: expenseChecked ? expenseCategory : null,
          expense_num_installments: expenseChecked
            ? expenseNumInstallments
            : null,
          expense_first_due_date: expenseChecked ? expenseFirstDueDate : null,
          pdf_file_key: pdfFileKey,
        },
      });

      toast.success("Contrato criado com sucesso!");
      form.reset();
      setItemDrafts([]);
      setSelectedFile(null);
      onSuccess();
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Erro desconhecido";
      toast.error(`Erro ao criar contrato: ${message}`);
    }
  };

  return {
    form,
    suppliers,
    existingContracts,
    categories,
    selectedFile,
    setSelectedFile,
    itemDrafts,
    setItemDrafts,
    isCreating,
    isSubmitting: form.formState.isSubmitting,
    handleExpenseChange,
    handleOpenChange,
    onSubmit,
  };
}
