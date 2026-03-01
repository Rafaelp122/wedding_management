import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Heart } from "lucide-react";

import { useAuthStore } from "@/stores/authStore";
import { useAuthTokenCreate } from "@/api/generated/v1/endpoints/auth/auth";
import type {
  EmailTokenObtainPairRequest,
  EmailTokenObtainPair,
} from "@/api/generated/v1/models";
import { AuthTokenCreateBody } from "@/api/generated/v1/zod/auth/auth";

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

import type { ErrorType } from "@/api/custom-instance";
import type { AxiosResponse } from "axios";

export function LoginForm() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const { mutate, isPending } = useAuthTokenCreate<ErrorType>();

  const form = useForm<EmailTokenObtainPairRequest>({
    resolver: zodResolver(AuthTokenCreateBody),
    defaultValues: { email: "", password: "" },
  });

  const onSubmit = (data: EmailTokenObtainPairRequest) => {
    mutate(
      { data },
      {
        onSuccess: (response: AxiosResponse<EmailTokenObtainPair>) => {
          const { access, refresh, user } = response.data;
          if (access && refresh && user) {
            login(access, refresh, user);
            toast.success(`Bem-vindo, ${user.first_name}!`);
            navigate("/dashboard");
          }
        },
        onError: (error) => {
          const message =
            error.response?.data?.detail || "E-mail ou senha incorretos.";
          toast.error(message);
        },
      },
    );
  };

  return (
    <Card className="w-full max-w-md shadow-lg border-t-4 border-t-pink-500">
      <CardHeader className="space-y-1 flex flex-col items-center">
        <div className="bg-pink-100 p-3 rounded-full mb-2">
          <Heart className="h-6 w-6 text-pink-600 fill-pink-600" />
        </div>
        <CardTitle className="text-2xl font-bold text-center">
          Wedding Admin
        </CardTitle>
        <CardDescription>Gerencie seus eventos com precisão</CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>E-mail</FormLabel>
                  <FormControl>
                    <Input placeholder="seu@email.com" {...field} />
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
                  <div className="flex items-center justify-between">
                    <FormLabel>Senha</FormLabel>
                    <span className="text-xs text-muted-foreground cursor-default">
                      Esqueceu?
                    </span>
                  </div>
                  <FormControl>
                    <Input type="password" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button
              type="submit"
              className="w-full bg-pink-600 hover:bg-pink-700"
              disabled={isPending}
            >
              {isPending ? "Validando..." : "Entrar no Painel"}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
