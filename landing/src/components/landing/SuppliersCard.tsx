import { useState } from "react";
import { Store, Star, Plus, Search, Check, AlertCircle } from "lucide-react";
import type { Supplier } from "../../data/types";
import { Card } from "../ui/card";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { Slider } from "../ui/slider";

interface SuppliersCardProps {
  initialItems: Supplier[];
}

export function SuppliersCard({ initialItems }: SuppliersCardProps) {
  const [suppliers, setSuppliers] = useState<Supplier[]>(initialItems);
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("Todos");

  const [showAddForm, setShowAddForm] = useState(false);
  const [newName, setNewName] = useState("");
  const [newCategory, setNewCategory] = useState("Fotografia");
  const [newRating, setNewRating] = useState(5.0);

  const categories = ["Todos", "Fotografia", "Confeitaria", "Buffet", "Decoração", "Música"];

  const handleAddSupplier = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;

    const newSup: Supplier = {
      id: crypto.randomUUID(),
      name: newName.trim(),
      category: newCategory,
      rating: parseFloat(newRating.toFixed(1)),
      isCustom: true,
    };

    setSuppliers((prev) => [...prev, newSup]);
    setNewName("");
    setNewRating(5.0);
    setShowAddForm(false);
  };

  const filteredSuppliers = suppliers.filter((sup) => {
    const matchesSearch = sup.name.toLowerCase().includes(search.toLowerCase()) ||
                          sup.category.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = selectedCategory === "Todos" || sup.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <Card className="glass-panel rounded-3xl p-6 hover:-translate-y-1.5 transition-all duration-300 shadow-soft flex flex-col h-full border border-border/30">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
          <Store className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h3 className="font-bold text-lg text-foreground">Diretório de Fornecedores</h3>
          <p className="text-xs text-muted-foreground font-medium">Parceiros recomendados e avaliações</p>
        </div>
      </div>

      <div className="bg-card border border-border/40 rounded-2xl p-4 flex-grow flex flex-col justify-between">
        <div className="mb-4 space-y-2">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground/50" />
            <Input
              type="text"
              placeholder="Pesquisar fornecedores..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-muted text-xs py-2 pl-9 pr-4 rounded-xl border border-border/50 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all text-foreground placeholder:text-muted-foreground/40"
            />
          </div>
          <div className="flex flex-wrap gap-1.5">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-2.5 py-1 rounded-full text-[10px] font-semibold transition-all cursor-pointer ${
                  selectedCategory === cat
                    ? "bg-primary/10 text-primary"
                    : "bg-muted text-muted-foreground hover:bg-primary/5 hover:text-primary"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-2.5 flex-grow max-h-60 overflow-y-auto pr-1 mb-4">
          {filteredSuppliers.map((sup) => (
            <div
              key={sup.id}
              className="bg-muted rounded-xl p-3 border border-border/20 flex items-center gap-3 hover:bg-primary/5 hover:border-primary/20 transition-all duration-200 group"
            >
              {sup.avatarUrl ? (
                <img
                  src={sup.avatarUrl}
                  alt={sup.name}
                  referrerPolicy="no-referrer"
                  className="w-10 h-10 rounded-full object-cover bg-border/30 ring-2 ring-card"
                />
              ) : (
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-sm ring-2 ring-card">
                  {sup.name.slice(0, 2).toUpperCase()}
                </div>
              )}
              <div className="flex-grow">
                <h4 className="text-sm font-bold text-foreground group-hover:text-primary transition-colors">
                  {sup.name}
                </h4>
                <span className="text-[10px] bg-primary/5 text-primary font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider">
                  {sup.category}
                </span>
              </div>
              <div className="flex items-center text-amber-500 bg-amber-50 px-2 py-1 rounded-lg border border-amber-100">
                <Star className="w-3.5 h-3.5 fill-amber-500" />
                <span className="text-xs font-black ml-1 text-amber-700">{sup.rating.toFixed(1)}</span>
              </div>
            </div>
          ))}

          {filteredSuppliers.length === 0 && (
            <div className="text-center py-6 text-muted-foreground/60 flex flex-col items-center gap-2">
              <AlertCircle className="w-5 h-5 text-muted-foreground/40" />
              <p className="text-xs">Nenhum fornecedor encontrado nesta categoria.</p>
            </div>
          )}
        </div>

        {showAddForm ? (
          <form onSubmit={handleAddSupplier} className="border-t border-border/20 pt-3.5 space-y-3">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label htmlFor="supplier-name" className="text-[10px] font-bold text-muted-foreground block mb-1">Nome do Fornecedor</label>
                <Input
                  id="supplier-name"
                  type="text"
                  placeholder="Ex: Cerimonial Prime"
                  value={newName}
                  required
                  onChange={(e) => setNewName(e.target.value)}
                  className="w-full px-2.5 py-1.5 border border-border/50 rounded-lg text-xs focus:ring-1 focus:ring-primary focus:outline-none bg-muted"
                />
              </div>
              <div>
                <label htmlFor="supplier-category" className="text-[10px] font-bold text-muted-foreground block mb-1">Categoria</label>
                <select
                  id="supplier-category"
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  className="w-full px-2.5 py-1.5 border border-border/50 rounded-lg text-xs focus:ring-1 focus:ring-primary focus:outline-none bg-muted"
                >
                  <option value="Fotografia">Fotografia</option>
                  <option value="Confeitaria">Confeitaria</option>
                  <option value="Buffet">Buffet</option>
                  <option value="Decoração">Decoração</option>
                  <option value="Música">Música</option>
                </select>
              </div>
            </div>

            <div className="flex gap-4 items-center justify-between">
              <div className="flex-grow">
                <label className="text-[10px] font-bold text-muted-foreground block mb-1">Avaliação: {newRating.toFixed(1)} ★</label>
                <Slider
                  min={3.0}
                  max={5.0}
                  step={0.1}
                  value={[newRating]}
                  onValueChange={([v]) => setNewRating(v)}
                  className="w-full"
                />
              </div>
              <div className="flex gap-2 shrink-0">
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="text-xs font-semibold px-2.5 py-1.5 border border-border/50 rounded-lg text-muted-foreground hover:bg-red-50 hover:text-red-600 transition-colors cursor-pointer"
                >
                  Cancelar
                </button>
                <Button
                  type="submit"
                  className="bg-primary hover:bg-primary-hover text-white text-xs font-bold px-3 py-1.5 rounded-lg shadow-sm transition-all flex items-center gap-1 cursor-pointer"
                >
                  <Check className="w-3.5 h-3.5" />
                  <span>Salvar</span>
                </Button>
              </div>
            </div>
          </form>
        ) : (
          <button
            onClick={() => setShowAddForm(true)}
            className="w-full bg-muted hover:bg-primary/5 hover:text-primary rounded-xl py-3 border border-dashed border-border hover:border-primary/50 flex items-center justify-center gap-2 transition-all cursor-pointer text-xs font-bold text-muted-foreground"
          >
            <Plus className="w-4 h-4" />
            <span>Adicionar Novo Fornecedor</span>
          </button>
        )}
      </div>
    </Card>
  );
}
