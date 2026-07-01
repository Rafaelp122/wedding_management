import { describe, expect, it } from "vitest";
import {
  EVENT_TYPE_OPTIONS,
  RECURRENCE_OPTIONS,
  EVENT_LABELS,
  EVENT_COLORS,
} from "./constants";

describe("Scheduler Constants", () => {
  describe("EVENT_TYPE_OPTIONS", () => {
    it("should be defined and not empty", () => {
      expect(EVENT_TYPE_OPTIONS).toBeDefined();
      expect(EVENT_TYPE_OPTIONS.length).toBeGreaterThan(0);
    });

    it("should have correct structure and values", () => {
      expect(EVENT_TYPE_OPTIONS).toEqual([
        { value: "reuniao", label: "Reunião" },
        { value: "visita", label: "Visita Técnica" },
        { value: "degustacao", label: "Degustação" },
        { value: "outro", label: "Outro" },
      ]);
    });
  });

  describe("RECURRENCE_OPTIONS", () => {
    it("should be defined and not empty", () => {
      expect(RECURRENCE_OPTIONS).toBeDefined();
      expect(RECURRENCE_OPTIONS.length).toBeGreaterThan(0);
    });

    it("should have correct structure and values", () => {
      expect(RECURRENCE_OPTIONS).toEqual([
        { value: "none", label: "Nenhuma" },
        { value: "semanal", label: "Semanal" },
        { value: "quinzenal", label: "Quinzenal" },
        { value: "mensal", label: "Mensal" },
      ]);
    });
  });

  describe("EVENT_LABELS", () => {
    it("should be defined and not empty", () => {
      expect(EVENT_LABELS).toBeDefined();
      expect(Object.keys(EVENT_LABELS).length).toBeGreaterThan(0);
    });

    it("should have correct labels", () => {
      expect(EVENT_LABELS).toEqual({
        reuniao: "Reunião",
        pagamento: "Pagamento",
        visita: "Visita Técnica",
        degustacao: "Degustação",
        outro: "Outro",
      });
    });
  });

  describe("EVENT_COLORS", () => {
    it("should be defined and not empty", () => {
      expect(EVENT_COLORS).toBeDefined();
      expect(Object.keys(EVENT_COLORS).length).toBeGreaterThan(0);
    });

    it("should have correct colors", () => {
      expect(EVENT_COLORS).toEqual({
        reuniao: "#3B82F6",
        pagamento: "#22C55E",
        visita: "#A855F7",
        degustacao: "#F97316",
        outro: "#6B7280",
      });
    });
  });

  describe("Consistency", () => {
    it("every event type option should have a label and color mapping", () => {
      EVENT_TYPE_OPTIONS.forEach((option) => {
        expect(EVENT_LABELS[option.value]).toBeDefined();
        expect(EVENT_COLORS[option.value]).toBeDefined();
      });
    });

    it("event labels and colors should have matching keys", () => {
      const labelKeys = Object.keys(EVENT_LABELS).sort();
      const colorKeys = Object.keys(EVENT_COLORS).sort();
      expect(labelKeys).toEqual(colorKeys);
    });
  });
});
