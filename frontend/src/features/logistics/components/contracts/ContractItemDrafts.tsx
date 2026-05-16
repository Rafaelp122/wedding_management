import { useState } from "react";
import { Plus, Check, X } from "lucide-react";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import {
  ACQUISITION_STATUS_OPTIONS,
  ITEM_STATUS_LABELS,
} from "@/features/logistics/constants";

export interface ItemDraft {
  key: string;
  name: string;
  quantity: number;
  acquisition_status: string;
}

interface ContractItemDraftsProps {
  drafts: ItemDraft[];
  onDraftsChange: (drafts: ItemDraft[]) => void;
}

export function ContractItemDrafts({
  drafts,
  onDraftsChange,
}: ContractItemDraftsProps) {
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [status, setStatus] = useState("PENDING");

  const addDraft = () => {
    if (!name.trim()) return;
    onDraftsChange([
      ...drafts,
      {
        key: crypto.randomUUID(),
        name: name.trim(),
        quantity,
        acquisition_status: status,
      },
    ]);
    setName("");
    setQuantity(1);
    setStatus("PENDING");
    setShowForm(false);
  };

  const removeDraft = (key: string) => {
    onDraftsChange(drafts.filter((d) => d.key !== key));
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <label className="text-sm font-medium">Itens (Opcional)</label>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="h-7 text-xs"
          onClick={() => setShowForm(!showForm)}
        >
          <Plus className="size-3 mr-1" />
          Adicionar
        </Button>
      </div>

      {showForm && (
        <div className="flex gap-2 mb-3">
          <Input
            placeholder="Nome do item"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="h-8 text-sm flex-1"
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                addDraft();
              }
            }}
          />
          <Input
            type="number"
            min={1}
            value={quantity}
            onChange={(e) =>
              setQuantity(Math.max(1, Number(e.target.value) || 1))
            }
            className="h-8 text-sm w-16"
          />
          <Select value={status} onValueChange={setStatus}>
            <SelectTrigger className="h-8 text-sm w-28">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {ACQUISITION_STATUS_OPTIONS.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            type="button"
            size="sm"
            className="h-8 text-xs shrink-0"
            onClick={addDraft}
          >
            <Check className="size-3" />
          </Button>
        </div>
      )}

      {drafts.map((d) => (
        <div
          key={d.key}
          className="flex items-center gap-2 text-sm py-1.5 border-b last:border-0"
        >
          <span className="flex-1 truncate">{d.name}</span>
          <span className="w-10 text-center text-muted-foreground text-xs">
            {d.quantity}
          </span>
          <Badge className="text-[10px] h-5" variant="outline">
            {ITEM_STATUS_LABELS[d.acquisition_status] || d.acquisition_status}
          </Badge>
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="size-6"
            onClick={() => removeDraft(d.key)}
          >
            <X className="size-3" />
          </Button>
        </div>
      ))}

      {drafts.length === 0 && !showForm && (
        <p className="text-xs text-muted-foreground">Nenhum item adicionado.</p>
      )}
    </div>
  );
}
