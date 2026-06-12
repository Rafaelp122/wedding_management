import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { DataPagination } from "@/components/data-pagination";

const defaultProps = {
  totalPages: 5,
  currentPage: 1,
  onGoToPage: vi.fn(),
} as const;

describe("DataPagination", () => {
  it("shows the range and total", () => {
    const { container } = render(
      <DataPagination
        from={1}
        to={10}
        totalCount={50}
        hasPrevious={false}
        hasNext
        onPrevious={vi.fn()}
        onNext={vi.fn()}
        {...defaultProps}
      />,
    );

    expect(container.textContent).toContain(
      "Mostrando 1 a 10 de 50 resultados",
    );
  });

  it("shows singular for totalCount of 1", () => {
    const { container } = render(
      <DataPagination
        from={1}
        to={1}
        totalCount={1}
        hasPrevious={false}
        hasNext={false}
        onPrevious={vi.fn()}
        onNext={vi.fn()}
        {...defaultProps}
        totalPages={1}
        currentPage={1}
      />,
    );

    expect(container.textContent).toContain(
      "Mostrando 1 de 1 resultado",
    );
  });

  it("hides pagination buttons when single page", () => {
    const { container } = render(
      <DataPagination
        from={1}
        to={4}
        totalCount={4}
        hasPrevious={false}
        hasNext={false}
        onPrevious={vi.fn()}
        onNext={vi.fn()}
        totalPages={1}
        currentPage={1}
        onGoToPage={vi.fn()}
      />,
    );

    expect(
      screen.queryByRole("button", { name: "Anterior" }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Próximo" }),
    ).not.toBeInTheDocument();
    expect(container.textContent).toContain("Mostrando 4 de 4");
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
        {...defaultProps}
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
        {...defaultProps}
        totalPages={5}
        currentPage={5}
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
        {...defaultProps}
        currentPage={2}
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
        {...defaultProps}
        currentPage={2}
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
        {...defaultProps}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Próximo" }));

    expect(onNext).toHaveBeenCalledOnce();
  });

  it("returns null for empty collection", () => {
    render(
      <DataPagination
        from={0}
        to={0}
        totalCount={0}
        hasPrevious={false}
        hasNext={false}
        onPrevious={vi.fn()}
        onNext={vi.fn()}
        {...defaultProps}
        totalPages={1}
        currentPage={1}
      />,
    );

    expect(screen.queryByRole("navigation")).not.toBeInTheDocument();
  });

  it("renders page number buttons", () => {
    render(
      <DataPagination
        from={1}
        to={10}
        totalCount={50}
        hasPrevious={false}
        hasNext
        onPrevious={vi.fn()}
        onNext={vi.fn()}
        totalPages={5}
        currentPage={1}
        onGoToPage={vi.fn()}
      />,
    );

    expect(screen.getByRole("button", { name: "1" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "2" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "5" })).toBeInTheDocument();
  });

  it("calls goToPage when page number is clicked", async () => {
    const goToPage = vi.fn();

    render(
      <DataPagination
        from={1}
        to={10}
        totalCount={50}
        hasPrevious
        hasNext
        onPrevious={vi.fn()}
        onNext={vi.fn()}
        totalPages={5}
        currentPage={1}
        onGoToPage={goToPage}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "3" }));

    expect(goToPage).toHaveBeenCalledWith(3);
  });
});
