import type { FieldPath, FieldValues, UseFormReturn } from "react-hook-form";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";

type WeddingFormShape = {
  groom_name?: string | null;
  bride_name?: string | null;
  date?: string | null;
  location?: string | null;
  expected_guests?: number | null;
};

interface WeddingFormFieldsProps<
  TFormValues extends FieldValues & WeddingFormShape,
> {
  form: UseFormReturn<TFormValues>;
  placeholders?: Partial<
    Record<"groom_name" | "bride_name" | "location", string>
  >;
  expectedGuestsLabel?: string;
}

export function WeddingFormFields<
  TFormValues extends FieldValues & WeddingFormShape,
>({
  form,
  placeholders,
  expectedGuestsLabel = "Número de Convidados",
}: WeddingFormFieldsProps<TFormValues>) {
  return (
    <>
      <div className="grid grid-cols-2 gap-4">
        <FormField
          control={form.control}
          name={"groom_name" as FieldPath<TFormValues>}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Nome do Noivo</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  value={typeof field.value === "string" ? field.value : ""}
                  placeholder={placeholders?.groom_name}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name={"bride_name" as FieldPath<TFormValues>}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Nome da Noiva</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  value={typeof field.value === "string" ? field.value : ""}
                  placeholder={placeholders?.bride_name}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <FormField
          control={form.control}
          name={"date" as FieldPath<TFormValues>}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Data do Casamento</FormLabel>
              <FormControl>
                <Input
                  type="date"
                  {...field}
                  value={typeof field.value === "string" ? field.value : ""}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name={"expected_guests" as FieldPath<TFormValues>}
          render={({ field }) => (
            <FormItem>
              <FormLabel>{expectedGuestsLabel}</FormLabel>
              <FormControl>
                <Input
                  type="number"
                  {...field}
                  value={typeof field.value === "number" ? field.value : ""}
                  onChange={(event) => {
                    const value = event.target.value;
                    field.onChange(value === "" ? undefined : Number(value));
                  }}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      <FormField
        control={form.control}
        name={"location" as FieldPath<TFormValues>}
        render={({ field }) => (
          <FormItem>
            <FormLabel>Local</FormLabel>
            <FormControl>
              <Input
                {...field}
                value={typeof field.value === "string" ? field.value : ""}
                placeholder={placeholders?.location}
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </>
  );
}
