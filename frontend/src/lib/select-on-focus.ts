export function selectOnFocus(e: React.FocusEvent<HTMLInputElement>) {
  const v = e.target.value;
  if (v === "0" || v === "0.00" || v === "0,00") {
    e.target.select();
  }
}
