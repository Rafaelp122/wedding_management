import { useState } from "react";
import { CheckSquare, Square, Plus, Trash2 } from "lucide-react";
import type { ChecklistItem } from "../../data/types";
import { Card } from "../ui/card";
import { Input } from "../ui/input";
import { Button } from "../ui/button";

interface ChecklistCardProps {
  initialItems: ChecklistItem[];
}

export function ChecklistCard({ initialItems }: ChecklistCardProps) {
  const [items, setItems] = useState<ChecklistItem[]>(initialItems);
  const [newItemText, setNewItemText] = useState("");

  const handleToggle = (id: string) => {
    setItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, completed: !item.completed } : item
      )
    );
  };

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newItemText.trim()) return;

    const newItem: ChecklistItem = {
      id: Date.now().toString(),
      text: newItemText.trim(),
      completed: false,
    };

    setItems((prev) => [...prev, newItem]);
    setNewItemText("");
  };

  const handleDelete = (id: string) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
  };

  const completedCount = items.filter((item) => item.completed).length;
  const totalCount = items.length;
  const percentage = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  return (
    <Card className="glass-panel rounded-3xl p-6 hover:-translate-y-1.5 transition-all duration-300 shadow-soft flex flex-col h-full border border-border/30">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
          <CheckSquare className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h3 className="font-bold text-lg text-foreground">Checklists Inteligentes</h3>
          <p className="text-xs text-muted-foreground font-medium">Controle de tarefas compartilhadas</p>
        </div>
      </div>

      <div className="bg-primary rounded-2xl p-5 text-white shadow-lg shadow-primary/20 flex-grow flex flex-col">
        <div className="mb-4">
          <h4 className="text-xs font-semibold uppercase tracking-wider opacity-80 mb-1">Checklist do Mês</h4>
          <div className="flex justify-between items-baseline">
            <p className="text-2xl font-black">{percentage}% Completo</p>
            <p className="text-xs font-medium opacity-80">
              {completedCount} de {totalCount} concluídos
            </p>
          </div>
          <div className="w-full bg-white/30 rounded-full h-2 mt-2.5 overflow-hidden">
            <div
              className="bg-white h-full rounded-full transition-all duration-500"
              style={{ width: `${percentage}%` }}
            ></div>
          </div>
        </div>

        <div className="space-y-2 mt-auto bg-card rounded-xl p-3.5 text-foreground max-h-56 overflow-y-auto">
          {items.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between group py-1"
            >
              <label
                onClick={() => handleToggle(item.id)}
                className="flex items-center gap-3 cursor-pointer select-none flex-grow"
              >
                {item.completed ? (
                  <CheckSquare className="w-5 h-5 text-primary fill-primary/10 transition-transform active:scale-90" />
                ) : (
                  <Square className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors active:scale-90" />
                )}
                <span
                  className={`text-sm font-medium transition-all ${
                    item.completed
                      ? "line-through opacity-50 text-muted-foreground"
                      : "text-foreground"
                  }`}
                >
                  {item.text}
                </span>
              </label>
              <button
                onClick={() => handleDelete(item.id)}
                className="text-muted-foreground hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-red-50 dark:hover:bg-red-950/40"
                aria-label="Deletar tarefa"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}

          {items.length === 0 && (
            <p className="text-xs text-muted-foreground text-center py-4">
              Nenhuma tarefa adicionada. Adicione uma abaixo!
            </p>
          )}
        </div>

        <form onSubmit={handleAdd} className="mt-4 flex gap-2">
          <Input
            type="text"
            placeholder="Nova tarefa..."
            value={newItemText}
            onChange={(e) => setNewItemText(e.target.value)}
            className="flex-grow bg-white/10 text-white placeholder-white/60 border border-white/20 rounded-xl px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-white focus:bg-white/20 transition-all"
          />
          <Button
            type="submit"
            className="bg-white text-primary p-2 rounded-xl hover:bg-white/90 active:scale-95 transition-all flex items-center justify-center shrink-0"
            aria-label="Adicionar tarefa"
          >
            <Plus className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </Card>
  );
}
