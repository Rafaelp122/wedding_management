import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { PasswordStrengthMeter } from "./PasswordStrengthMeter";
import { calculatePasswordStrength } from "../utils/password-strength";

describe("calculatePasswordStrength", () => {
  it("returns score 0 for empty or very short password", () => {
    expect(calculatePasswordStrength("").score).toBe(0);
    expect(calculatePasswordStrength("123").score).toBe(0);
    expect(calculatePasswordStrength("short").label).toBe("Muito fraca");
  });

  it("returns score 1 for basic password with 8 characters", () => {
    const res = calculatePasswordStrength("abcdefgh");
    expect(res.score).toBe(1);
    expect(res.label).toBe("Fraca");
  });

  it("returns higher scores for mixed characters and length", () => {
    const medium = calculatePasswordStrength("Abcdefgh1");
    expect(medium.score).toBeGreaterThanOrEqual(2);

    const strong = calculatePasswordStrength("Abcdefgh1!");
    expect(strong.score).toBeGreaterThanOrEqual(3);

    const veryStrong = calculatePasswordStrength("SuperSecurePassword2026!@#");
    expect(veryStrong.score).toBe(4);
    expect(veryStrong.label).toBe("Muito forte");
  });
});

describe("PasswordStrengthMeter component", () => {
  it("renders nothing when password is empty", () => {
    render(<PasswordStrengthMeter password="" />);
    expect(screen.queryByText("Força da senha:")).not.toBeInTheDocument();
  });

  it("renders strength label and feedback for weak password", () => {
    render(<PasswordStrengthMeter password="weak" />); // pragma: allowlist secret
    expect(screen.getByText("Força da senha:")).toBeInTheDocument();
    expect(screen.getByText("Muito fraca")).toBeInTheDocument();
    expect(screen.getByText("A senha deve ter no mínimo 8 caracteres.")).toBeInTheDocument();
  });

  it("renders correct label for strong password", () => {
    render(<PasswordStrengthMeter password="StrongP@ssw0rd2026!" />); // pragma: allowlist secret
    expect(screen.getByText("Força da senha:")).toBeInTheDocument();
    expect(screen.getByText(/forte/i)).toBeInTheDocument();
  });
});
