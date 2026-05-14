import { describe, expect, it, vi } from "vitest";
import { selectOnFocus } from "@/features/shared/utils/selectOnFocus";

describe("selectOnFocus", () => {
  it("selects input value when it is '0'", () => {
    const input = document.createElement("input");
    input.value = "0";
    const selectSpy = vi.spyOn(input, "select");

    selectOnFocus({
      target: input,
    } as React.FocusEvent<HTMLInputElement>);

    expect(selectSpy).toHaveBeenCalled();
  });

  it("selects input value when it is '0.00'", () => {
    const input = document.createElement("input");
    input.value = "0.00";
    const selectSpy = vi.spyOn(input, "select");

    selectOnFocus({
      target: input,
    } as React.FocusEvent<HTMLInputElement>);

    expect(selectSpy).toHaveBeenCalled();
  });

  it("selects input value when it is '0,00'", () => {
    const input = document.createElement("input");
    input.value = "0,00";
    const selectSpy = vi.spyOn(input, "select");

    selectOnFocus({
      target: input,
    } as React.FocusEvent<HTMLInputElement>);

    expect(selectSpy).toHaveBeenCalled();
  });

  it("does not select for other values", () => {
    const input = document.createElement("input");
    input.value = "100";
    const selectSpy = vi.spyOn(input, "select");

    selectOnFocus({
      target: input,
    } as React.FocusEvent<HTMLInputElement>);

    expect(selectSpy).not.toHaveBeenCalled();
  });

  it("does not select for empty string", () => {
    const input = document.createElement("input");
    input.value = "";
    const selectSpy = vi.spyOn(input, "select");

    selectOnFocus({
      target: input,
    } as React.FocusEvent<HTMLInputElement>);

    expect(selectSpy).not.toHaveBeenCalled();
  });
});
