import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";
import { DataPagination } from "@/components/data-pagination";

describe("DataPagination", () => {
  it("shows the range and total", () => {
    render(
      <DataPagination
        from={1}
        to={10}
        totalCount={50}
        hasPrevious={false}
        hasNext
        onPrevious={vi.fn()}
        onNext={vi.fn()}
      />,
    );

    expect(screen.getByText(/1–10 de 50 resultados/)).toBeInTheDocument();
  });

  it("shows singular for totalCount of 1", () => {
    render(
      <DataPagination
        from={1}
        to={1}
        totalCount={1}
        hasPrevious={false}
        hasNext={false}
        onPrevious={vi.fn()}
        onNext={vi.fn()}
      />,
    );

    expect(screen.getByText(/1–1 de 1 resultado$/)).toBeInTheDocument();
  });

  it("disables previous button when hasPrevious is false", () => {
    render(
      <DataPagination
        from={1}
        to={10}
        totalCount={50}
        hasPrevious={false}
        hasNext
        onPrevious={vi.fn()}
        onNext={vi.fn()}
      />,
    );

    const prevButton = screen.getByRole("button", { name: "Anterior" });
    expect(prevButton).toBeDisabled();
  });

  it("disables next button when hasNext is false", () => {
    render(
      <DataPagination
        from={41}
        to={50}
        totalCount={50}
        hasPrevious
        hasNext={false}
        onPrevious={vi.fn()}
        onNext={vi.fn()}
      />,
    );

    const nextButton = screen.getByRole("button", { name: "Próximo" });
    expect(nextButton).toBeDisabled();
  });

  it("disables both buttons when isFetching is true", () => {
    const onPrevious = vi.fn();
    const onNext = vi.fn();

    render(
      <DataPagination
        from={11}
        to={20}
        totalCount={50}
        hasPrevious
        hasNext
        isFetching
        onPrevious={onPrevious}
        onNext={onNext}
      />,
    );

    expect(screen.getByRole("button", { name: "Anterior" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Próximo" })).toBeDisabled();
  });

  it("calls onPrevious when previous is clicked", async () => {
    const onPrevious = vi.fn();

    render(
      <DataPagination
        from={11}
        to={20}
        totalCount={50}
        hasPrevious
        hasNext
        onPrevious={onPrevious}
        onNext={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Anterior" }));

    expect(onPrevious).toHaveBeenCalledOnce();
  });

  it("calls onNext when next is clicked", async () => {
    const onNext = vi.fn();

    render(
      <DataPagination
        from={1}
        to={10}
        totalCount={50}
        hasPrevious={false}
        hasNext
        onPrevious={vi.fn()}
        onNext={onNext}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Próximo" }));

    expect(onNext).toHaveBeenCalledOnce();
  });

  it("shows correct from=0 for empty collection", () => {
    render(
      <DataPagination
        from={0}
        to={0}
        totalCount={0}
        hasPrevious={false}
        hasNext={false}
        onPrevious={vi.fn()}
        onNext={vi.fn()}
      />,
    );

    expect(screen.getByText(/0–0 de 0 resultados/)).toBeInTheDocument();
  });
});
