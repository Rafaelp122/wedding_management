import { memo, useRef, useState } from "react";
import { Upload, Loader2, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export interface ContractDocumentSectionViewProps {
  hasFile: boolean;
  fileName: string | null | undefined;
  onUpload: (file: File) => void;
  onRemove: () => void;
  isUploading: boolean;
  isRemoving: boolean;
}

export const ContractDocumentSectionView = memo(function ContractDocumentSectionView({
  hasFile,
  fileName,
  onUpload,
  onRemove,
  isUploading,
  isRemoving,
}: ContractDocumentSectionViewProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleUploadClick = () => {
    if (!selectedFile) return;
    onUpload(selectedFile);
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const isBusy = isUploading || isRemoving;

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
              onClick={onRemove}
              disabled={isBusy}
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
              disabled={isBusy}
            />
            <Button
              variant="outline"
              size="sm"
              className="h-8 text-xs shrink-0"
              onClick={handleUploadClick}
              disabled={isBusy || !selectedFile}
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
});
