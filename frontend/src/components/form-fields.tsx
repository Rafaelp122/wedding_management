import { type Control, type FieldValues, type Path } from "react-hook-form";

import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { SELECT_NONE_VALUE } from "@/lib/constants";

interface FormFieldBaseProps<TFieldValues extends FieldValues> {
  control: Control<TFieldValues>;
  name: Path<TFieldValues>;
  label: string;
}

interface FormInputProps<TFieldValues extends FieldValues>
  extends FormFieldBaseProps<TFieldValues> {
  placeholder?: string;
  type?: "text" | "email" | "tel" | "url";
}

export function FormInput<TFieldValues extends FieldValues>({
  control,
  name,
  label,
  placeholder,
  type = "text",
}: FormInputProps<TFieldValues>) {
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem>
          <FormLabel>{label}</FormLabel>
          <FormControl>
            <Input
              {...field}
              value={field.value ?? ""}
              type={type}
              placeholder={placeholder}
            />
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}

interface FormNumberProps<TFieldValues extends FieldValues>
  extends FormFieldBaseProps<TFieldValues> {
  placeholder?: string;
  step?: string;
  min?: number;
  transformEmptyTo?: number | undefined | null;
  disabled?: boolean;
  onFocus?: (e: React.FocusEvent<HTMLInputElement>) => void;
}

export function FormNumber<TFieldValues extends FieldValues>({
  control,
  name,
  label,
  placeholder = "0.00",
  step = "0.01",
  min = 0,
  transformEmptyTo = undefined,
  disabled,
  onFocus,
}: FormNumberProps<TFieldValues>) {
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem>
          <FormLabel>{label}</FormLabel>
          <FormControl>
            <Input
              type="number"
              step={step}
              min={min}
              placeholder={placeholder}
              disabled={disabled}
              value={field.value ?? ""}
              onBlur={field.onBlur}
              name={field.name}
              ref={field.ref}
              onFocus={onFocus}
              onChange={(e) =>
                field.onChange(
                  e.target.value === "" ? transformEmptyTo : Number(e.target.value),
                )
              }
            />
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}

interface FormCurrencyProps<TFieldValues extends FieldValues>
  extends FormFieldBaseProps<TFieldValues> {
  placeholder?: string;
}

export function FormCurrency<TFieldValues extends FieldValues>({
  control,
  name,
  label,
  placeholder = "R$ 0,00",
}: FormCurrencyProps<TFieldValues>) {
  return (
    <FormNumber
      control={control}
      name={name}
      label={label}
      placeholder={placeholder}
      step="0.01"
      min={0}
    />
  );
}

interface FormTextareaProps<TFieldValues extends FieldValues>
  extends FormFieldBaseProps<TFieldValues> {
  placeholder?: string;
}

export function FormTextarea<TFieldValues extends FieldValues>({
  control,
  name,
  label,
  placeholder,
}: FormTextareaProps<TFieldValues>) {
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem>
          <FormLabel>{label}</FormLabel>
          <FormControl>
            <Textarea
              {...field}
              value={field.value ?? ""}
              placeholder={placeholder}
            />
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}

interface FormSelectProps<TFieldValues extends FieldValues, TItem> {
  control: Control<TFieldValues>;
  name: Path<TFieldValues>;
  label: string;
  items: readonly TItem[];
  getItemKey: (item: TItem) => string;
  getItemLabel: (item: TItem) => string;
  placeholder?: string;
}

export function FormSelect<TFieldValues extends FieldValues, TItem>({
  control,
  name,
  label,
  items,
  getItemKey,
  getItemLabel,
  placeholder = "Selecione...",
}: FormSelectProps<TFieldValues, TItem>) {
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem>
          <FormLabel>{label}</FormLabel>
          <Select onValueChange={field.onChange} value={field.value}>
            <FormControl>
              <SelectTrigger>
                <SelectValue placeholder={placeholder} />
              </SelectTrigger>
            </FormControl>
            <SelectContent>
              {items.map((item) => (
                <SelectItem key={getItemKey(item)} value={getItemKey(item)}>
                  {getItemLabel(item)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}

interface FormSelectNullableProps<TFieldValues extends FieldValues, TItem> {
  control: Control<TFieldValues>;
  name: Path<TFieldValues>;
  label: string;
  items: readonly TItem[];
  getItemKey: (item: TItem) => string;
  getItemLabel: (item: TItem) => string;
  placeholder?: string;
  noneLabel?: string;
}

export function FormSelectNullable<TFieldValues extends FieldValues, TItem>({
  control,
  name,
  label,
  items,
  getItemKey,
  getItemLabel,
  placeholder = "Nenhum",
  noneLabel = "Nenhum",
}: FormSelectNullableProps<TFieldValues, TItem>) {
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem>
          <FormLabel>{label}</FormLabel>
          <Select
            onValueChange={(v) =>
              field.onChange(v === SELECT_NONE_VALUE ? null : v)
            }
            value={field.value ?? SELECT_NONE_VALUE}
          >
            <FormControl>
              <SelectTrigger>
                <SelectValue placeholder={placeholder} />
              </SelectTrigger>
            </FormControl>
            <SelectContent>
              <SelectItem value={SELECT_NONE_VALUE}>{noneLabel}</SelectItem>
              {items.map((item) => (
                <SelectItem key={getItemKey(item)} value={getItemKey(item)}>
                  {getItemLabel(item)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}
