import { LoginForm } from "../components/LoginForm";

export default function LoginPage() {
  return (
    // Ocupa a tela inteira, centraliza o card e mantém margem do PublicLayout
    <div className="flex items-center justify-center min-h-[80vh] px-4 py-12">
      <LoginForm />
    </div>
  );
}
