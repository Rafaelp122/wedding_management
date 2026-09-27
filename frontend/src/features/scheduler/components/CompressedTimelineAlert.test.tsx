import { describe, expect, it } from "vitest";
import { http, HttpResponse } from "msw";
import { render, screen, waitFor } from "@/test-utils";
import { server } from "@/mocks/server";
import { CompressedTimelineAlert } from "./CompressedTimelineAlert";

describe("CompressedTimelineAlert", () => {
  it("renders null when timeline is not compressed", async () => {
    server.use(
      http.get("*/api/v1/scheduler/timeline-compression/", () => {
        return HttpResponse.json({
          is_timeline_compressed: false,
          compressed_timeline_message: null,
          days_until_wedding: 180,
        });
      }),
    );

    render(<CompressedTimelineAlert weddingUuid="w-normal" />);

    await waitFor(() => {
      expect(
        screen.queryByText(/cronograma comprimido/i),
      ).not.toBeInTheDocument();
    });
  });

  it("renders warning alert when timeline is compressed (< 90 days)", async () => {
    server.use(
      http.get("*/api/v1/scheduler/timeline-compression/", () => {
        return HttpResponse.json({
          is_timeline_compressed: true,
          compressed_timeline_message:
            "Atenção: Casamento a 45 dias. Checklist ajustado para ritmo de urgência.",
          days_until_wedding: 45,
        });
      }),
    );

    render(<CompressedTimelineAlert weddingUuid="w-urgent" />);

    await waitFor(() => {
      expect(
        screen.getByText(/cronograma comprimido/i),
      ).toBeInTheDocument();
    });

    expect(screen.getByText(/45 dias restantes/i)).toBeInTheDocument();
    expect(
      screen.getByText(/atenção: casamento a 45 dias/i),
    ).toBeInTheDocument();
  });

  it("handles null days_until_wedding gracefully", async () => {
    server.use(
      http.get("*/api/v1/scheduler/timeline-compression/", () => {
        return HttpResponse.json({
          is_timeline_compressed: true,
          compressed_timeline_message: "Cronograma acelerado.",
          days_until_wedding: null,
        });
      }),
    );

    render(<CompressedTimelineAlert weddingUuid="w-urgent-no-days" />);

    await waitFor(() => {
      expect(
        screen.getByText(/cronograma comprimido/i),
      ).toBeInTheDocument();
    });
    expect(screen.getByText(/< 90 dias/i)).toBeInTheDocument();
  });
});
