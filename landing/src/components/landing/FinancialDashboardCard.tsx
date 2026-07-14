import { useState } from "react";
import { DollarSign, Landmark, Plus, RefreshCw } from "lucide-react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Card, CardContent } from "../ui/card";

export function FinancialDashboardCard() {
  const [received, setReceived] = useState(24500);
  const [pending, setPending] = useState(3200);
  const [transactions, setTransactions] = useState([
    { id: "t1", desc: "Sinal Casamento Ana & Felipe", value: 3500, type: "recebido" },
    { id: "t2", desc: "Parcela Buffet Bia & Leo", value: 1200, type: "recebido" },
    { id: "t3", desc: "Restante Decoração Carla & Hugo", value: 1800, type: "pendente" }
  ]);

  const [newDesc, setNewDesc] = useState("");
  const [newValue, setNewValue] = useState("");
  const [newType, setNewType] = useState<"recebido" | "pendente">("recebido");

  const handleAddTransaction = (e: React.FormEvent) => {
    e.preventDefault();
    const valNum = parseFloat(newValue);
    if (!newDesc.trim() || isNaN(valNum) || valNum <= 0) return;

    if (newType === "recebido") {
      setReceived((prev) => prev + valNum);
    } else {
      setPending((prev) => prev + valNum);
    }

    const newTx = {
      id: Date.now().toString(),
      desc: newDesc.trim(),
      value: valNum,
      type: newType,
    };

    setTransactions((prev) => [newTx, ...prev]);
    setNewDesc("");
    setNewValue("");
  };

  const resetValues = () => {
    setReceived(24500);
    setPending(3200);
    setTransactions([
      { id: "t1", desc: "Sinal Casamento Ana & Felipe", value: 3500, type: "recebido" },
      { id: "t2", desc: "Parcela Buffet Bia & Leo", value: 1200, type: "recebido" },
      { id: "t3", desc: "Restante Decoração Carla & Hugo", value: 1800, type: "pendente" }
    ]);
  };

  const receivedRatio = Math.min(100, Math.max(20, (received / 40000) * 100));
  const pendingRatio = Math.min(100, Math.max(10, (pending / 15000) * 100));

  const formatBRL = (val: number) => {
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
    }).format(val);
  };

  return (
    <Card className="glass-panel rounded-3xl p-6 hover:-translate-y-1.5 transition-all duration-300 shadow-soft flex flex-col h-full border border-border/30">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
            <Landmark className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 className="font-bold text-lg text-foreground">Financeiro Tolerância Zero</h3>
            <p className="text-xs text-muted-foreground font-medium">Controle de caixa & orçamentos</p>
          </div>
        </div>
        <button
          onClick={resetValues}
          className="p-2 text-muted-foreground hover:text-primary rounded-full hover:bg-primary/5 transition-colors cursor-pointer"
          title="Resetar simulador"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      <CardContent className="bg-muted border border-border/40 rounded-2xl p-5 flex-grow flex flex-col justify-between">
        <h4 className="text-sm font-bold text-foreground mb-3">Dashboard Financeiro</h4>
        
        <div className="h-32 mb-6 relative overflow-hidden rounded-xl bg-card border border-border/20 p-2 shadow-sm">
          <svg className="w-full h-full" preserveAspectRatio="none" viewBox="0 0 400 100">
            <defs>
              <linearGradient id="chartGradient" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stopColor="#630ED4" stopOpacity="0.15" />
                <stop offset="100%" stopColor="#cbdbf5" stopOpacity="0" />
              </linearGradient>
            </defs>
            <path
              d={`M0,80 C50,${90 - receivedRatio / 4} 100,${50 - receivedRatio / 3} 150,${70 - receivedRatio / 2} C200,${85 - pendingRatio / 3} 250,${30 - receivedRatio / 1.5} 300,${50 - receivedRatio / 2} C350,${70 - pendingRatio / 2} 400,${10 + pendingRatio / 5} 400,${10 + pendingRatio / 5} L400,100 L0,100 Z`}
              fill="url(#chartGradient)"
              className="transition-all duration-1000"
            ></path>
            <path
              d={`M0,80 C50,${90 - receivedRatio / 4} 100,${50 - receivedRatio / 3} 150,${70 - receivedRatio / 2} C200,${85 - pendingRatio / 3} 250,${30 - receivedRatio / 1.5} 300,${50 - receivedRatio / 2} C350,${70 - pendingRatio / 2} 400,${10 + pendingRatio / 5}`}
              fill="none"
              stroke="#630ED4"
              strokeWidth="3"
              strokeLinecap="round"
              className="transition-all duration-1000"
            ></path>
            <circle cx="150" cy={70 - receivedRatio / 2} r="5" fill="#630ED4" className="transition-all duration-1000 animate-pulse" />
            <circle cx="300" cy={50 - receivedRatio / 2} r="5" fill="#630ED4" className="transition-all duration-1000 animate-pulse" />
          </svg>
          <div className="absolute top-2 left-3 flex gap-2">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-primary"></span>
            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">Fluxo de Caixa Real</span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 border-t border-border/20 pt-4 mb-4">
          <div>
            <p className="text-[10px] uppercase text-muted-foreground font-semibold tracking-wider mb-1">Total Recebido</p>
            <p className="text-sm md:text-base font-extrabold text-foreground truncate">{formatBRL(received)}</p>
          </div>
          <div>
            <p className="text-[10px] uppercase text-muted-foreground font-semibold tracking-wider mb-1">Pendentes</p>
            <p className="text-sm md:text-base font-extrabold text-red-600 truncate">{formatBRL(pending)}</p>
          </div>
          <div>
            <p className="text-[10px] uppercase text-muted-foreground font-semibold tracking-wider mb-1">Previsão</p>
            <p className="text-sm md:text-base font-extrabold text-emerald-600 truncate">{formatBRL(received + pending)}</p>
          </div>
        </div>

        <div className="bg-card rounded-xl p-3 border border-border/30">
          <p className="text-xs font-bold text-foreground mb-2.5 flex items-center gap-1">
            <Plus className="w-3.5 h-3.5 text-primary" />
            <span>Simular Nova Transação</span>
          </p>
          <form onSubmit={handleAddTransaction} className="flex flex-col gap-2">
            <div className="grid grid-cols-2 gap-2">
              <Input
                type="text"
                placeholder="Ex: Parcela Cerimonial"
                value={newDesc}
                onChange={(e) => setNewDesc(e.target.value)}
                className="px-2.5 py-1.5 border border-border/50 rounded-lg text-xs focus:ring-1 focus:ring-primary focus:outline-none bg-card text-foreground placeholder:text-muted-foreground/40"
              />
              <Input
                type="number"
                placeholder="R$ Valor"
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
                className="px-2.5 py-1.5 border border-border/50 rounded-lg text-xs focus:ring-1 focus:ring-primary focus:outline-none bg-card text-foreground placeholder:text-muted-foreground/40"
              />
            </div>
            <div className="flex gap-2 items-center justify-between">
              <div className="flex gap-3">
                <label className="flex items-center gap-1.5 cursor-pointer text-[11px] font-semibold text-muted-foreground">
                  <input
                    type="radio"
                    name="type"
                    checked={newType === "recebido"}
                    onChange={() => setNewType("recebido")}
                    className="text-primary focus:ring-primary"
                  />
                  <span>Recebido</span>
                </label>
                <label className="flex items-center gap-1.5 cursor-pointer text-[11px] font-semibold text-muted-foreground">
                  <input
                    type="radio"
                    name="type"
                    checked={newType === "pendente"}
                    onChange={() => setNewType("pendente")}
                    className="text-primary focus:ring-primary"
                  />
                  <span>Pendente</span>
                </label>
              </div>
              <Button
                type="submit"
                className="bg-primary hover:bg-primary-hover text-white text-[11px] font-bold px-3 py-1.5 rounded-lg shadow-sm transition-all flex items-center gap-1 cursor-pointer"
              >
                <span>Registrar</span>
              </Button>
            </div>
          </form>
        </div>
      </CardContent>
    </Card>
  );
}
