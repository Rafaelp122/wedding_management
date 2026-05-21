import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate, Link } from "react-router-dom";
import { toast } from "sonner";
import { Heart } from "lucide-react";
import { z } from "zod";

import { useAuthRegisterUser } from "@/api/generated/v1/endpoints/auth/auth";
import { getApiErrorInfo } from "@/api/error-utils";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import type { ErrorType } from "@/api/api-client";

const RegisterFormSchema = z
  .object({
    email: z.string().email(),
    password: z.string().min(1),
    first_name: z.string().default(""),
    last_name: z.string().default(""),
    confirm_password: z.string().min(1, "Confirme sua senha"),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Senhas não conferem",
    path: ["confirm_password"],
  });

type RegisterFormData = z.infer<typeof RegisterFormSchema>;

export function RegisterForm() {
  const navigate = useNavigate();
  const { mutate, isPending } = useAuthRegisterUser<ErrorType>();

  const form = useForm({
    resolver: zodResolver(RegisterFormSchema),
    defaultValues: {
      email: "",
      password: "",
      confirm_password: "",
      first_name: "",
      last_name: "",
    },
  });

  const onSubmit = (data: RegisterFormData) => {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { confirm_password, ...payload } = data;
    mutate(
      { data: payload },
      {
        onSuccess: () => {
          toast.success("Conta criada com sucesso! Faça login para continuar.");
          navigate("/login");
        },
        onError: (error: ErrorType) => {
          const { message } = getApiErrorInfo(
            error,
            "Erro ao criar conta. Verifique os dados e tente novamente.",
          );
          toast.error(message);
        },
      },
    );
  };

  return (
    <Card className="w-full max-w-md shadow-lg border-t-4 border-t-primary">
      <CardHeader className="flex flex-col items-center gap-1">
        <div className="bg-primary-foreground p-3 rounded-full mb-2">
          <Heart className="size-6 text-primary fill-primary" />
        </div>
        <CardTitle className="text-2xl font-bold text-center">
          Criar Conta
        </CardTitle>
        <CardDescription>
          Comece a gerenciar seus eventos em segundos
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className="flex flex-col gap-4"
          >
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="first_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nome</FormLabel>
                    <FormControl>
                      <Input placeholder="João" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="last_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Sobrenome</FormLabel>
                    <FormControl>
                      <Input placeholder="Silva" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>E-mail</FormLabel>
                  <FormControl>
                    <Input
                      type="email"
                      placeholder="seu@email.com"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Senha</FormLabel>
                  <FormControl>
                    <Input type="password" placeholder="Mínimo 8 caracteres" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="confirm_password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Confirmar Senha</FormLabel>
                  <FormControl>
                    <Input type="password" placeholder="Repita a senha" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button
              type="submit"
              className="w-full"
              disabled={isPending}
            >
              {isPending ? "Criando conta..." : "Criar Conta"}
            </Button>
            <p className="text-center text-sm text-muted-foreground">
              Já tem uma conta?{" "}
              <Link
                to="/login"
                className="font-medium text-primary hover:underline"
              >
                Faça login
              </Link>
            </p>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
