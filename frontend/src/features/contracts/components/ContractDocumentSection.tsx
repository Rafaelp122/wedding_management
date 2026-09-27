import { useState } from "react";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";
import * as Sentry from "@sentry/react";

import {
  useContractsUploadFile,
  useContractsDetachFile,
  getContractsListQueryKey,
  getContractsReadQueryKey,
  getContractsDetailsReadQueryKey,
  useContractsUploadUrl,
} from "@/api/generated/v1/endpoints/contracts/contracts";

import { uploadFileToR2 } from "@/services/r2";
import { ContractDocumentSectionView } from "./ContractDocumentSectionView";

interface ContractDocumentSectionProps {
  contractUuid: string;
  hasFile: boolean;
  fileName: string | null | undefined;
  weddingUuid: string;
}

export function ContractDocumentSection({
  contractUuid,
  hasFile,
  fileName,
  weddingUuid,
}: ContractDocumentSectionProps) {
  const queryClient = useQueryClient();
  const [isUploading, setIsUploading] = useState(false);

  const uploadMutation = useContractsUploadFile();
  const deleteUploadMutation = useContractsDetachFile();
  const { mutateAsync: getUploadUrl } = useContractsUploadUrl();

  const invalidateDocumentQueries = () => {
    queryClient.invalidateQueries({
      queryKey: getContractsListQueryKey(),
    });
    queryClient.invalidateQueries({
      queryKey: getContractsReadQueryKey(contractUuid),
    });
    queryClient.invalidateQueries({
      queryKey: getContractsDetailsReadQueryKey(contractUuid),
    });
  };

  const handleUpload = async (selectedFile: File) => {
    if (!selectedFile) return;
    setIsUploading(true);
    try {
      const uploadUrlRes = await getUploadUrl({
        data: {
          filename: selectedFile.name,
          wedding_id: weddingUuid,
        },
      });

      await uploadFileToR2(uploadUrlRes.data.upload_url, selectedFile);

      await uploadMutation.mutateAsync({
        uuid: contractUuid,
        data: {
          pdf_file_key: uploadUrlRes.data.object_key,
        },
      });

      toast.success("Documento enviado com sucesso!");
      invalidateDocumentQueries();
    } catch (error) {
      toast.error("Erro ao enviar documento.");
      Sentry.captureException(error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveFile = () => {
    deleteUploadMutation.mutate(
      { uuid: contractUuid },
      {
        onSuccess: () => {
          toast.success("Documento removido.");
          invalidateDocumentQueries();
        },
        onError: () => {
          toast.error("Erro ao remover documento.");
        },
      },
    );
  };

  return (
    <ContractDocumentSectionView
      hasFile={hasFile}
      fileName={fileName}
      onUpload={handleUpload}
      onRemove={handleRemoveFile}
      isUploading={isUploading || uploadMutation.isPending}
      isRemoving={deleteUploadMutation.isPending}
    />
  );
}
