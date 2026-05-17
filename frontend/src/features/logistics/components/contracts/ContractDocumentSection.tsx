import { useRef, useState } from "react";
import { toast } from "sonner";
import { Upload, Loader2, X } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";

import { AXIOS_INSTANCE } from "@/api/axios-instance";

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
  const [isRemoving, setIsRemoving] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const handleUpload = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    const formData = new FormData();
    formData.append("pdf_file", selectedFile);
    try {
      await AXIOS_INSTANCE.post(
        `/api/v1/logistics/contracts/${contractUuid}/upload/`,
        formData,
      );
      toast.success("Documento enviado com sucesso!");
      queryClient.invalidateQueries({
        queryKey: ["/api/v1/logistics/contracts/"],
      });
      setSelectedFile(null);
    } catch {
      toast.error("Erro ao enviar documento.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveFile = async () => {
    setIsRemoving(true);
    try {
      await AXIOS_INSTANCE.delete(
        `/api/v1/logistics/contracts/${contractUuid}/upload/`,
      );
      toast.success("Documento removido.");
      queryClient.invalidateQueries({
        queryKey: ["/api/v1/logistics/contracts/"],
      });
    } catch {
      toast.error("Erro ao remover documento.");
    } finally {
      setIsRemoving(false);
    }
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
              disabled={isRemoving}
            >
              {isRemoving ? (
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
              disabled={isUploading || !selectedFile}
            >
              {isUploading ? (
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
