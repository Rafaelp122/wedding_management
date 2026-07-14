import { useState, useEffect } from "react";
import { Heart, ArrowRight, X, CheckCircle2, Briefcase, Mail, Smartphone } from "lucide-react";
import { Dialog, DialogContent, DialogTitle, DialogDescription } from "../ui/dialog";
import { Input } from "../ui/input";
import { Button } from "../ui/button";

interface LeadModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initialEmail?: string;
}

export function LeadModal({ open, onOpenChange, initialEmail = "" }: LeadModalProps) {
  const [leadName, setLeadName] = useState("");
  const [leadEmail, setLeadEmail] = useState(initialEmail);
  const [leadPhone, setLeadPhone] = useState("");
  const [leadSubmitted, setLeadSubmitted] = useState(false);

  useEffect(() => {
    if (initialEmail) {
      setLeadEmail(initialEmail);
    }
  }, [initialEmail]);

  const handleLeadSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!leadName.trim() || !leadEmail.trim()) return;

    setLeadSubmitted(true);
    setTimeout(() => {
      setLeadSubmitted(false);
      onOpenChange(false);
      setLeadName("");
      setLeadEmail("");
      setLeadPhone("");
    }, 5000);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-card rounded-3xl p-6 md:p-8 max-w-md w-full shadow-2xl border border-border">
        {leadSubmitted ? (
          <div className="text-center py-6 space-y-4">
            <div className="w-16 h-16 bg-emerald-50 rounded-full flex items-center justify-center mx-auto text-emerald-600 border border-emerald-100 animate-bounce">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <div className="space-y-1.5">
              <DialogTitle className="text-xl font-black text-foreground">Sua conta foi criada!</DialogTitle>
              <DialogDescription className="text-sm font-bold text-emerald-600 uppercase tracking-wider">
                Período de teste ativado
              </DialogDescription>
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed max-w-sm mx-auto">
              Enviamos as credenciais de acesso provisórias e o link do seu subdomínio exclusivo de testes (ex: <strong>{leadName.trim() ? `${leadName.toLowerCase().replace(/\s+/g, "").replace(/[^a-z0-9-]/g, "")}.simaceito.com.br` : "sua-assessoria.simaceito.com.br"}</strong>) para o e-mail: <strong>{leadEmail}</strong>. Aproveite!
            </p>
            <div className="pt-4 flex flex-col items-center gap-3">
              <button
                onClick={() => { setLeadSubmitted(false); onOpenChange(false); setLeadName(""); setLeadEmail(""); setLeadPhone(""); }}
                className="text-xs font-bold text-primary hover:underline cursor-pointer"
              >
                Fechar
              </button>
              <span className="text-[10px] text-muted-foreground/60 font-semibold uppercase">
                Redirecionando em instantes...
              </span>
            </div>
          </div>
        ) : (
          <form onSubmit={handleLeadSubmit} className="space-y-5">
            <div className="text-center space-y-1.5">
              <Heart className="w-10 h-10 text-primary fill-primary mx-auto" />
              <DialogTitle className="text-xl md:text-2xl font-black text-foreground tracking-tight">
                Comece seu teste de 14 dias
              </DialogTitle>
              <DialogDescription className="text-xs text-muted-foreground max-w-xs mx-auto">
                Acesso completo e instantâneo a todos os recursos premium do Sim, Aceito! sem necessidade de cartão de crédito.
              </DialogDescription>
            </div>

            <div className="space-y-3.5 pt-2">
              <div className="space-y-1">
                <label className="text-xs font-bold text-foreground flex items-center gap-1.5">
                  <Briefcase className="w-3.5 h-3.5 text-primary" />
                  <span>Nome Completo</span>
                </label>
                <Input
                  type="text"
                  placeholder="Ex: Mariana Albuquerque"
                  required
                  value={leadName}
                  onChange={(e) => setLeadName(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-border text-xs md:text-sm focus:ring-1 focus:ring-primary focus:outline-none bg-muted"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-foreground flex items-center gap-1.5">
                  <Mail className="w-3.5 h-3.5 text-primary" />
                  <span>E-mail Profissional</span>
                </label>
                <Input
                  type="email"
                  placeholder="Ex: mariana@assessoria.com.br"
                  required
                  value={leadEmail}
                  onChange={(e) => setLeadEmail(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-border text-xs md:text-sm focus:ring-1 focus:ring-primary focus:outline-none bg-muted"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-foreground flex items-center gap-1.5">
                  <Smartphone className="w-3.5 h-3.5 text-primary" />
                  <span>Celular / WhatsApp (Opcional)</span>
                </label>
                <Input
                  type="tel"
                  placeholder="Ex: (11) 99999-9999"
                  value={leadPhone}
                  onChange={(e) => setLeadPhone(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-border text-xs md:text-sm focus:ring-1 focus:ring-primary focus:outline-none bg-muted"
                />
              </div>
            </div>

            <Button
              type="submit"
              className="w-full bg-primary hover:bg-primary-hover text-white py-3.5 rounded-xl font-bold text-sm shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95 mt-4"
            >
              <span>Ativar Meu Teste Grátis</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
            <p className="text-[10px] text-muted-foreground text-center mt-2 leading-tight">
              Ao continuar, você concorda com nossos Termos de Uso e Políticas de Privacidade. Sem taxas ocultas após o período de testes.
            </p>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
