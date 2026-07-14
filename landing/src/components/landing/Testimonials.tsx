import { useState } from "react";
import { Star, ChevronLeft, ChevronRight, MessageSquareCode, Quote, CheckCircle2 } from "lucide-react";
import type { Testimonial } from "../../data/types";
import { TESTIMONIALS } from "../../data/landing";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Card } from "../ui/card";

export function Testimonials() {
  const [list, setList] = useState<Testimonial[]>(TESTIMONIALS);
  const [index, setIndex] = useState(0);

  const [showReviewForm, setShowReviewForm] = useState(false);
  const [name, setName] = useState("");
  const [role, setRole] = useState("");
  const [reviewText, setReviewText] = useState("");
  const [rating, setRating] = useState(5);
  const [submitted, setSubmitted] = useState(false);

  const handlePrev = () => {
    setIndex((prev) => (prev === 0 ? list.length - 1 : prev - 1));
  };

  const handleNext = () => {
    setIndex((prev) => (prev === list.length - 1 ? 0 : prev + 1));
  };

  const handleAddReview = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !reviewText.trim()) return;

    const newReview: Testimonial = {
      id: Date.now().toString(),
      name: name.trim(),
      role: role.trim() || "Assessor(a) de Casamentos",
      text: reviewText.trim(),
      rating: rating,
      avatarUrl: "https://i.pravatar.cc/150?u=" + Date.now()
    };

    setList((prev) => [...prev, newReview]);
    setIndex(list.length);
    setName("");
    setRole("");
    setReviewText("");
    setSubmitted(true);
    setTimeout(() => {
      setSubmitted(false);
      setShowReviewForm(false);
    }, 4000);
  };

  const activeReview = list[index];

  return (
    <div className="max-w-4xl mx-auto py-6 px-4">
      <Card className="bg-card rounded-3xl p-8 md:p-12 border border-border/30 shadow-xl relative overflow-hidden group">
        <Quote className="absolute -top-4 -right-4 w-36 h-36 text-primary/5 select-none font-black" />

        <div className="relative z-10 flex flex-col md:flex-row gap-8 items-center md:items-start min-h-[220px]">
          <div className="flex-shrink-0 flex flex-col items-center text-center">
            <img
              src={activeReview.avatarUrl}
              alt={activeReview.name}
              referrerPolicy="no-referrer"
              className="w-20 h-20 md:w-24 md:h-24 rounded-full object-cover border-4 border-primary/10 shadow-lg"
            />
            <div className="mt-4 flex text-amber-500 gap-0.5 justify-center">
              {Array.from({ length: 5 }).map((_, i) => (
                <Star
                  key={i}
                  className={`w-4 h-4 ${
                    i < Math.floor(activeReview.rating) ? "fill-amber-500 text-amber-500" : "text-border"
                  }`}
                />
              ))}
            </div>
            <p className="text-xs font-bold text-amber-600 mt-1">{activeReview.rating.toFixed(1)} de 5</p>
          </div>

          <div className="flex-grow flex flex-col justify-between">
            <div className="space-y-4">
              <p className="text-base md:text-lg text-muted-foreground font-medium italic leading-relaxed">
                "{activeReview.text}"
              </p>
              <div>
                <h4 className="text-lg font-extrabold text-foreground">{activeReview.name}</h4>
                <p className="text-xs font-semibold uppercase tracking-wider text-primary">{activeReview.role}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-between items-center mt-10 pt-6 border-t border-border/20">
          <button
            onClick={handlePrev}
            className="p-3 rounded-full border border-border hover:bg-primary/5 hover:text-primary hover:border-primary/30 transition-all cursor-pointer active:scale-90"
            aria-label="Anterior"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          
          <div className="flex gap-2.5">
            {list.map((_, i) => (
              <button
                key={i}
                onClick={() => setIndex(i)}
                className={`h-2.5 rounded-full transition-all duration-300 ${
                  i === index ? "w-7 bg-primary" : "w-2.5 bg-border hover:bg-muted-foreground"
                }`}
                aria-label={`Slide ${i + 1}`}
              ></button>
            ))}
          </div>

          <button
            onClick={handleNext}
            className="p-3 rounded-full border border-border hover:bg-primary/5 hover:text-primary hover:border-primary/30 transition-all cursor-pointer active:scale-90"
            aria-label="Próximo"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </Card>

      <div className="mt-12 flex flex-col items-center">
        {showReviewForm ? (
          <form
            onSubmit={handleAddReview}
            className="bg-card border border-border/30 rounded-3xl p-6 md:p-8 shadow-lg w-full max-w-2xl space-y-4"
          >
            <h3 className="text-lg font-extrabold text-foreground">Deixe o seu depoimento</h3>
            
            {submitted ? (
              <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-4 rounded-2xl flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
                <div>
                  <p className="font-bold">Obrigado pela sua contribuição!</p>
                  <p className="text-xs text-emerald-700">Seu depoimento foi adicionado e já está visível no slider acima.</p>
                </div>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-bold text-foreground block mb-1.5">Seu Nome</label>
                    <Input
                      type="text"
                      placeholder="Ex: Mariana Silva"
                      value={name}
                      required
                      onChange={(e) => setName(e.target.value)}
                      className="w-full px-4 py-2.5 rounded-xl border border-border text-sm focus:ring-1 focus:ring-primary focus:outline-none bg-muted"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-foreground block mb-1.5">Seu Cargo / Empresa</label>
                    <Input
                      type="text"
                      placeholder="Ex: Diretora, Casar & Cia"
                      value={role}
                      onChange={(e) => setRole(e.target.value)}
                      className="w-full px-4 py-2.5 rounded-xl border border-border text-sm focus:ring-1 focus:ring-primary focus:outline-none bg-muted"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-xs font-bold text-foreground block mb-1.5">Avaliação em Estrelas</label>
                  <div className="flex gap-1.5 items-center">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <button
                        type="button"
                        key={i}
                        onClick={() => setRating(i + 1)}
                        className="p-1 cursor-pointer hover:scale-110 transition-transform"
                      >
                        <Star
                          className={`w-6 h-6 ${
                            i < rating ? "fill-amber-500 text-amber-500" : "text-border"
                          }`}
                        />
                      </button>
                    ))}
                    <span className="text-sm font-bold text-muted-foreground ml-2">{rating.toFixed(1)} de 5</span>
                  </div>
                </div>

                <div>
                  <label className="text-xs font-bold text-foreground block mb-1.5">Seu Depoimento</label>
                  <textarea
                    placeholder="Conte como o Sim, Aceito! facilitou a sua rotina ou ajudou sua assessoria a poupar tempo e estresse..."
                    value={reviewText}
                    required
                    rows={3}
                    onChange={(e) => setReviewText(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-border text-sm focus:ring-1 focus:ring-primary focus:outline-none bg-muted resize-none"
                  ></textarea>
                </div>

                <div className="flex gap-3 justify-end pt-2">
                  <button
                    type="button"
                    onClick={() => setShowReviewForm(false)}
                    className="text-sm font-bold px-5 py-2.5 border border-border text-muted-foreground hover:bg-red-50 hover:text-red-600 rounded-xl transition-all cursor-pointer"
                  >
                    Voltar
                  </button>
                  <Button
                    type="submit"
                    className="bg-primary hover:bg-primary-hover text-white font-bold text-sm px-6 py-2.5 rounded-xl shadow-md transition-all cursor-pointer active:scale-95"
                  >
                    Publicar Depoimento
                  </Button>
                </div>
              </>
            )}
          </form>
        ) : (
          <Button
            onClick={() => setShowReviewForm(true)}
            className="bg-card hover:bg-primary/5 text-primary border border-primary/30 px-6 py-3 rounded-full text-sm font-bold shadow-md hover:shadow-lg transition-all flex items-center gap-2 cursor-pointer active:scale-95"
          >
            <MessageSquareCode className="w-4 h-4 text-primary" />
            <span>Compartilhar Minha História</span>
          </Button>
        )}
      </div>
    </div>
  );
}
