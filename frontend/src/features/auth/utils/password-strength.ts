/**
 * Utilitário puro para cálculo de força de senha.
 * Avalia comprimento, complexidade e diversidade de caracteres.
 */

export interface PasswordStrengthResult {
  score: 0 | 1 | 2 | 3 | 4;
  label: string;
  colorClass: string;
  feedback: string;
}

export function calculatePasswordStrength(password: string): PasswordStrengthResult {
  if (!password || password.length === 0) {
    return {
      score: 0,
      label: "",
      colorClass: "bg-zinc-200 dark:bg-zinc-800",
      feedback: "",
    };
  }

  if (password.length < 8) {
    return {
      score: 0,
      label: "Muito fraca",
      colorClass: "bg-red-500",
      feedback: "A senha deve ter no mínimo 8 caracteres.",
    };
  }

  let points = 1; // Já passou dos 8 caracteres

  // Bônus de comprimento (>= 12 caracteres recomendado)
  if (password.length >= 12) {
    points += 1;
  }

  // Contém letras maiúsculas e minúsculas
  const hasLower = /[a-z]/.test(password);
  const hasUpper = /[A-Z]/.test(password);
  if (hasLower && hasUpper) {
    points += 1;
  }

  // Contém números
  const hasNumber = /[0-9]/.test(password);
  if (hasNumber) {
    points += 1;
  }

  // Contém caracteres especiais
  const hasSymbol = /[^a-zA-Z0-9]/.test(password);
  if (hasSymbol) {
    points += 1;
  }

  // Mapeia pontuação (1 a 5) para score de 1 a 4
  if (points <= 2) {
    return {
      score: 1,
      label: "Fraca",
      colorClass: "bg-amber-500",
      feedback: "Adicione letras maiúsculas, números ou símbolos.",
    };
  }

  if (points === 3) {
    return {
      score: 2,
      label: "Média",
      colorClass: "bg-yellow-500",
      feedback: "Boa senha. Use símbolos para torná-la excelente.",
    };
  }

  if (points === 4) {
    return {
      score: 3,
      label: "Forte",
      colorClass: "bg-emerald-500",
      feedback: "Senha segura e forte.",
    };
  }

  return {
    score: 4,
    label: "Muito forte",
    colorClass: "bg-emerald-600",
    feedback: "Excelente! Senha com alta entropia.",
  };
}
