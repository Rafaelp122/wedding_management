import { describe, it, expect, vi, beforeEach } from "vitest";
import { uploadFileToR2 } from "./r2";

describe("uploadFileToR2", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("uploads file to presigned URL successfully", async () => {
    const mockFetch = vi.fn().mockResolvedValue({ ok: true });
    vi.stubGlobal("fetch", mockFetch);

    const file = new File(["test content"], "test.pdf", { type: "application/pdf" });
    await uploadFileToR2("https://r2.example.com/upload", file);

    expect(mockFetch).toHaveBeenCalledWith("https://r2.example.com/upload", {
      method: "PUT",
      body: file,
      headers: { "Content-Type": "application/pdf" },
    });
  });

  it("throws on upload failure", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 403, statusText: "Forbidden" }),
    );

    await expect(
      uploadFileToR2("https://r2.example.com/upload", new File(["test"], "test.pdf")),
    ).rejects.toThrow("Upload failed: 403 Forbidden");
  });

  it("throws on network error", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("Network failure")));

    await expect(
      uploadFileToR2("https://r2.example.com/upload", new File(["test"], "test.pdf")),
    ).rejects.toThrow("Network failure");
  });
});
