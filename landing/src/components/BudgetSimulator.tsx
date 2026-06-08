import { useState, useEffect } from "react";

type WeddingStyle = "praia" | "campo" | "classico";

interface Task {
  title: string;
  tag: string;
}

export default function BudgetSimulator() {
  const [guests, setGuests] = useState<number>(200);
  const [style, setStyle] = useState<WeddingStyle>("praia");
  const [budget, setBudget] = useState<number>(0);
  const [styleTitle, setStyleTitle] = useState<string>("");
  const [tasks, setTasks] = useState<Task[]>([]);

  useEffect(() => {
    let costPerGuest = 550; // Praia standard
    let title = "Praia Premium";
    let styleTasks: Task[] = [];

    if (style === "campo") {
      costPerGuest = 500;
      title = "Campo Charmoso";
      styleTasks = [
        {
          title: "Mapeamento de backup contra chuva na Fazenda Vila Rica",
          tag: "Fase 1 • Plano B",
        },
        {
          title: "Dimensionamento de gerador sobressalente para luz decorativa",
          tag: "Fase 1 • Carga",
        },
        {
          title: "Sinalização de acesso rodoviário para fornecedores",
          tag: "Fase 1 • Acesso",
        },
      ];
    } else if (style === "classico") {
      costPerGuest = 750;
      title = "Clássico Sofisticado";
      styleTasks = [
        {
          title: "Aprovação do layout de iluminação cenográfica clássica",
          tag: "Fase 1 • Design",
        },
        {
          title: "Reserva de espaço fechado com proteção termoacústica",
          tag: "Fase 1 • Espaço",
        },
        {
          title: "Alinhamento com coral clássico e músicos de entrada",
          tag: "Fase 1 • Protocolo",
        },
      ];
    } else {
      // Praia
      styleTasks = [
        {
          title:
            "Verificar autorização da Capitania dos Portos para cerimônia na areia",
          tag: "Fase 1 • Licença",
        },
        {
          title:
            "Definir plano B de lona ou espaço coberto contra brisa e maré",
          tag: "Fase 1 • Logística",
        },
        {
          title: "Definição do menu Fasano com opções de frutos do mar frescos",
          tag: "Fase 1 • Menu",
        },
      ];
    }

    setBudget(guests * costPerGuest);
    setStyleTitle(title);
    setTasks(styleTasks);
  }, [guests, style]);

  const spaceAlloc = budget * 0.3;
  const buffetAlloc = budget * 0.4;
  const decoAlloc = budget * 0.3;

  const formatBRL = (value: number) => {
    return value.toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
      minimumFractionDigits: 2,
    });
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
      {/* Simulator Text Context */}
      <div className="lg:col-span-5 space-y-6 text-left">
        <span className="text-xs font-bold text-aura-600 dark:text-aura-400 uppercase tracking-widest bg-aura-50 dark:bg-aura-900/30 px-3 py-1.5 rounded-full">
          Simulador de Custos MVP
        </span>
        <h2 className="font-display text-3xl sm:text-4xl font-extrabold text-zinc-950 dark:text-white tracking-tight leading-none">
          Planeje a distribuição de faturamento em segundos.
        </h2>
        <p className="text-zinc-500 dark:text-zinc-400 text-sm leading-relaxed font-medium">
          Experimente uma demonstração da lógica integrada do Sim, Aceito!.
          Selecione o número de convidados planejado e o estilo do evento para
          ver o algoritmo estimar o orçamento ideal e os primeiros marcos do
          checklist de tarefas do casal de forma 100% automatizada.
        </p>

        <div className="space-y-4">
          {/* Control 1: Convidados */}
          <div>
            <label
              className="block text-xs font-bold text-zinc-400 uppercase tracking-wider mb-2"
              htmlFor="simGuests"
            >
              Número de Convidados
            </label>
            <select
              id="simGuests"
              value={guests}
              onChange={(e) => setGuests(parseInt(e.target.value))}
              className="w-full px-3.5 py-2.5 bg-white dark:bg-surface-darkSecondary border border-zinc-200 dark:border-zinc-800 rounded-xl text-xs font-medium focus:ring-1.5 focus:ring-aura-500 outline-none text-zinc-900 dark:text-zinc-100"
            >
              <option value="100">Mini Wedding (Até 100 convidados)</option>
              <option value="200">
                Casamento Médio (100 a 200 convidados)
              </option>
              <option value="350">
                Grande Casamento (Mais de 300 convidados)
              </option>
            </select>
          </div>

          {/* Control 2: Estilo */}
          <div>
            <label className="block text-xs font-bold text-zinc-400 uppercase tracking-wider mb-2">
              Estilo de Casamento
            </label>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setStyle("praia")}
                className={`px-3 py-2 border rounded-xl text-xs font-bold btn-transition ${
                  style === "praia"
                    ? "border-aura-500 bg-aura-50 dark:bg-aura-900/20 text-aura-600 dark:text-aura-300"
                    : "border-zinc-200 dark:border-zinc-800 text-zinc-600 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800"
                }`}
              >
                Praia
              </button>
              <button
                type="button"
                onClick={() => setStyle("campo")}
                className={`px-3 py-2 border rounded-xl text-xs font-bold btn-transition ${
                  style === "campo"
                    ? "border-aura-500 bg-aura-50 dark:bg-aura-900/20 text-aura-600 dark:text-aura-300"
                    : "border-zinc-200 dark:border-zinc-800 text-zinc-600 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800"
                }`}
              >
                Campo
              </button>
              <button
                type="button"
                onClick={() => setStyle("classico")}
                className={`px-3 py-2 border rounded-xl text-xs font-bold btn-transition ${
                  style === "classico"
                    ? "border-aura-500 bg-aura-50 dark:bg-aura-900/20 text-aura-600 dark:text-aura-300"
                    : "border-zinc-200 dark:border-zinc-800 text-zinc-600 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800"
                }`}
              >
                Clássico
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Simulator Interactive Output Card */}
      <div className="lg:col-span-7 relative">
        <div className="absolute -inset-2 bg-gradient-to-r from-aura-500 to-indigo-500 rounded-2xl opacity-15 blur-xl"></div>
        <div className="bg-white dark:bg-surface-darkSecondary rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-2xl p-6 space-y-6 relative overflow-hidden text-left">
          {/* Output Header */}
          <div className="flex items-center justify-between border-b border-zinc-100 dark:border-zinc-800 pb-4">
            <div className="flex items-center gap-2">
              <span className="text-xl">📊</span>
              <h3 className="font-display font-bold text-sm text-zinc-950 dark:text-white">
                Estimativa Financeira do Casamento
              </h3>
            </div>
            <span className="text-[10px] font-mono font-bold text-aura-600 dark:text-aura-300 bg-aura-100 dark:bg-aura-900/20 px-2 py-0.5 rounded uppercase tracking-wider">
              Sim, Aceito! Core Algorithm
            </span>
          </div>

          {/* Computed Budget Result KPI */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-[#FBFBFE] dark:bg-zinc-900/40 p-4 rounded-xl border border-zinc-200/60 dark:border-zinc-800/80">
              <span className="text-[9px] font-bold text-zinc-400 uppercase tracking-wider block">
                Orçamento Ideal Estimado
              </span>
              <span className="font-mono text-xl font-bold text-zinc-950 dark:text-white mt-1 block">
                {formatBRL(budget)}
              </span>
            </div>
            <div className="bg-[#FBFBFE] dark:bg-zinc-900/40 p-4 rounded-xl border border-zinc-200/60 dark:border-zinc-800/80">
              <span className="text-[9px] font-bold text-zinc-400 uppercase tracking-wider block">
                Estilo Recomendado
              </span>
              <span className="text-xs font-bold text-aura-600 dark:text-aura-400 mt-2 block font-display uppercase tracking-wide">
                {styleTitle}
              </span>
            </div>
          </div>

          {/* Category Allocation bars computed */}
          <div className="space-y-3">
            <h4 className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider">
              Distribuição Recomendada por Setor
            </h4>

            <div className="space-y-3 text-xs">
              {/* Category 1 */}
              <div className="space-y-1">
                <div className="flex justify-between font-medium">
                  <span className="text-zinc-600 dark:text-zinc-400 font-semibold">
                    Locação do Espaço (30%)
                  </span>
                  <span className="font-mono font-bold text-zinc-900 dark:text-white">
                    {formatBRL(spaceAlloc)}
                  </span>
                </div>
                <div className="w-full bg-zinc-100 dark:bg-zinc-800 rounded-full h-1 overflow-hidden">
                  <div
                    className="bg-[#7C3AED] h-1 rounded-full animate-progress"
                    style={{ width: "30%" }}
                  ></div>
                </div>
              </div>
              {/* Category 2 */}
              <div className="space-y-1">
                <div className="flex justify-between font-medium">
                  <span className="text-zinc-600 dark:text-zinc-400 font-semibold">
                    Gastronomia & Buffet (40%)
                  </span>
                  <span className="font-mono font-bold text-zinc-900 dark:text-white">
                    {formatBRL(buffetAlloc)}
                  </span>
                </div>
                <div className="w-full bg-zinc-100 dark:bg-zinc-800 rounded-full h-1 overflow-hidden">
                  <div
                    className="bg-[#7C3AED] h-1 rounded-full animate-progress"
                    style={{ width: "40%" }}
                  ></div>
                </div>
              </div>
              {/* Category 3 */}
              <div className="space-y-1">
                <div className="flex justify-between font-medium">
                  <span className="text-zinc-600 dark:text-zinc-400 font-semibold">
                    Decoração & Flores (30%)
                  </span>
                  <span className="font-mono font-bold text-zinc-900 dark:text-white">
                    {formatBRL(decoAlloc)}
                  </span>
                </div>
                <div className="w-full bg-zinc-100 dark:bg-zinc-800 rounded-full h-1 overflow-hidden">
                  <div
                    className="bg-[#7C3AED] h-1 rounded-full animate-progress"
                    style={{ width: "30%" }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {/* Dynamic tasks output */}
          <div className="space-y-2">
            <h4 className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">
              Primeiras Tarefas Ativadas pelo Template
            </h4>
            <div className="space-y-2">
              {tasks.map((task, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-2.5 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-[11px] font-medium text-zinc-700 dark:text-zinc-300"
                >
                  <div className="flex items-start gap-2.5 pr-2 text-left">
                    <div className="w-3.5 h-3.5 border border-zinc-300 dark:border-zinc-700 rounded bg-white dark:bg-zinc-800 shrink-0 mt-0.5" />
                    <span className="leading-tight">
                      <span className="sr-only">(Pendente) </span>
                      {task.title}
                    </span>
                  </div>
                  <span className="bg-aura-100 dark:bg-aura-900/30 text-aura-700 dark:text-aura-300 px-2 py-0.5 rounded text-[8px] font-bold whitespace-nowrap">
                    {task.tag}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
