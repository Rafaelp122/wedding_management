import { useRef, useState } from "react";
import { toast } from "sonner";
import { Upload, Loader2, X } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";

import {
  useLogisticsContractsUpload,
  useLogisticsContractsDeleteUpload,
  getLogisticsContractsListQueryKey,
} from "@/api/generated/v1/endpoints/logistics/logistics";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface ContractDocumentSectionProps {
  contractUuid: string;
  hasFile: boolean;
  fileName: string | null | undefined;
}

export function ContractDocumentSection({
  contractUuid,
  hasFile,
  fileName,
}: ContractDocumentSectionProps) {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const uploadMutation = useLogisticsContractsUpload();
  const deleteUploadMutation = useLogisticsContractsDeleteUpload();

  const handleUpload = () => {
    if (!selectedFile) return;
    uploadMutation.mutate(
      { uuid: contractUuid, data: { pdf_file: selectedFile } },
      {
        onSuccess: () => {
          toast.success("Documento enviado com sucesso!");
          queryClient.invalidateQueries({
            queryKey: getLogisticsContractsListQueryKey(),
          });
          setSelectedFile(null);
        },
        onError: () => {
          toast.error("Erro ao enviar documento.");
        },
      },
    );
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
              disabled={deleteUploadMutation.isPending}
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
            />
            <Button
              variant="outline"
              size="sm"
              className="h-8 text-xs shrink-0"
              onClick={handleUpload}
              disabled={uploadMutation.isPending || !selectedFile}
            >
              {uploadMutation.isPending ? (
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
