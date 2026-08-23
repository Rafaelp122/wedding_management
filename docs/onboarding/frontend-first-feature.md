# Tutorial: Criando sua Primeira Tela no Frontend (React + Orval + Zod)

> **Objetivo:** Consumir um novo endpoint da API e construir uma interface reativa aplicando o padrão Smart/Dumb components.

---

## Passo 1: Gerar Contrato Orval

Com o backend rodando, execute o Orval no frontend para gerar os hooks TypeScript:

```bash
cd frontend
npm run api:generate
```
Isso atualizará `src/api/generated/` criando o hook fortemente tipado (ex: `useNotesCreate`).

---

## Passo 2: Construir o Componente Presenter (Dumb)

Crie `src/features/notes/components/NoteForm.tsx`:

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";

const schema = z.object({
  title: z.string().min(3, "Título muito curto"),
  content: z.string().min(5, "Conteúdo obrigatório"),
});

export type NoteFormData = z.infer<typeof schema>;

interface Props {
  onSubmit: (data: NoteFormData) => void;
  isLoading: boolean;
}

export function NoteForm({ onSubmit, isLoading }: Props) {
  const form = useForm<NoteFormData>({ resolver: zodResolver(schema) });
  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <input {...form.register("title")} placeholder="Título" />
      <textarea {...form.register("content")} placeholder="Conteúdo" />
      <Button type="submit" disabled={isLoading}>Salvar Nota</Button>
    </form>
  );
}
```

---

## Passo 3: Construir o Container (Smart Component)

Crie `src/features/notes/containers/NotesContainer.tsx`:

```tsx
import { useNotesCreate } from "@/api/generated/notes";
import { NoteForm, NoteFormData } from "../components/NoteForm";
import { toast } from "sonner";

export function NotesContainer() {
  const { mutate, isPending } = useNotesCreate({
    mutation: {
      onSuccess: () => toast.success("Nota salva com sucesso!"),
      onError: () => toast.error("Falha ao salvar nota."),
    }
  });

  const handleSubmit = (data: NoteFormData) => {
    mutate({ data });
  };

  return <NoteForm onSubmit={handleSubmit} isLoading={isPending} />;
}
```
