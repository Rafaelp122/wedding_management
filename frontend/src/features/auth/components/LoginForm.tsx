import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Heart } from "lucide-react";

import { useAuthStore } from "@/stores/authStore";
import { useAuthObtainToken } from "@/api/generated/v1/endpoints/auth/auth";
import { getApiErrorInfo } from "@/api/error-utils";
import type { TokenPayloadIn } from "@/api/generated/v1/models/tokenPayloadIn";
import type { TokenOut } from "@/api/generated/v1/models/tokenOut";
import { AuthObtainTokenBody } from "@/api/generated/v1/zod/auth/auth";

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
  const { mutate, isPending } = useAuthObtainToken<ErrorType>();

  const form = useForm<TokenPayloadIn>({
    resolver: zodResolver(AuthObtainTokenBody),
    defaultValues: { email: "", password: "" },
  });

  const onSubmit = (data: TokenPayloadIn) => {
    mutate(
      { data },
      {
        onSuccess: (response: AxiosResponse<TokenOut>) => {
          const { access, refresh, user } = response.data;
          if (access && refresh && user) {
            login(access, refresh, user);
            toast.success(`Bem-vindo, ${user.first_name}!`);
            navigate("/dashboard");
          }
        },
        onError: (error: ErrorType) => {
          const { message } = getApiErrorInfo(
            error,
            "E-mail ou senha incorretos.",
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
          Wedding Admin
        </CardTitle>
        <CardDescription>Gerencie seus eventos com precisão</CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="flex flex-col gap-4">
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
              className="w-full"
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
