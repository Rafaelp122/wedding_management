import { useRef, useState } from "react";
import { toast } from "sonner";
import { Upload, Loader2, X } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";

import {
  useLogisticsContractsUpload,
  useLogisticsContractsDeleteUpload,
  getLogisticsContractsListQueryKey,
  useLogisticsContractsUploadUrl,
} from "@/api/generated/v1/endpoints/logistics/logistics";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

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
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const uploadMutation = useLogisticsContractsUpload();
  const deleteUploadMutation = useLogisticsContractsDeleteUpload();
  const { mutateAsync: getUploadUrl } = useLogisticsContractsUploadUrl();

  const handleUpload = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    try {
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

      await uploadMutation.mutateAsync({
        uuid: contractUuid,
        data: {
          pdf_file_key: uploadUrlRes.data.object_key,
        },
      });

      toast.success("Documento enviado com sucesso!");
      queryClient.invalidateQueries({
        queryKey: getLogisticsContractsListQueryKey(),
      });
      queryClient.invalidateQueries({
        queryKey: [`/api/v1/logistics/contracts/${contractUuid}/`],
      });
      setSelectedFile(null);
    } catch (error) {
      toast.error("Erro ao enviar documento.");
      console.error(error);
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
          queryClient.invalidateQueries({
            queryKey: getLogisticsContractsListQueryKey(),
          });
          queryClient.invalidateQueries({
            queryKey: [`/api/v1/logistics/contracts/${contractUuid}/`],
          });
        },
        onError: () => {
          toast.error("Erro ao remover documento.");
        },
      },
    );
  };

  return (
    <div>
      <h4 className="text-sm font-semibold mb-2">Documento</h4>
      {hasFile ? (
        <div className="rounded-lg border bg-muted/30 p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">📎</span>
              <span className="font-medium truncate max-w-[300px]">
                {fileName || "documento"}
              </span>
            </div>
            <Button
              variant="destructive"
              size="sm"
              className="h-7 text-xs"
              onClick={handleRemoveFile}
              disabled={deleteUploadMutation.isPending || isUploading}
            >
              {deleteUploadMutation.isPending ? (
                <Loader2 className="size-3 mr-1 animate-spin" />
              ) : (
                <X className="size-3 mr-1" />
              )}
              Remover
            </Button>
          </div>
        </div>
      ) : (
        <div className="rounded-lg border bg-muted/30 p-3">
          <div className="flex items-center gap-2">
            <Input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.doc,.xlsx,.xls,.png,.jpg,.jpeg,.txt"
              className="flex-1 text-sm"
              onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
              disabled={uploadMutation.isPending || isUploading}
            />
            <Button
              variant="outline"
              size="sm"
              className="h-8 text-xs shrink-0"
              onClick={handleUpload}
              disabled={uploadMutation.isPending || isUploading || !selectedFile}
            >
              {uploadMutation.isPending || isUploading ? (
                <Loader2 className="size-3 mr-1 animate-spin" />
              ) : (
                <Upload className="size-3 mr-1" />
              )}
              Enviar
            </Button>
          </div>
          <p className="text-[11px] text-muted-foreground mt-1">
            Formatos: PDF, Word, Excel, imagens
          </p>
        </div>
      )}
    </div>
  );
}
