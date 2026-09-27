import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { PasswordInput } from "@/components/ui/PasswordInput";
import { Checkbox } from "@/components/ui/Checkbox";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import { registerSchema, type RegisterFormValues } from "@/lib/validation";

export default function RegisterPage() {
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      fullName: "",
      email: "",
      password: "",
      confirmPassword: "",
      acceptTerms: false,
    },
  });

  async function onSubmit(values: RegisterFormValues) {
    try {
      const res = await api.post("/auth/register", {
        full_name: values.fullName,
        email: values.email,
        password: values.password,
      });
      login(res.data.user, res.data.access_token);
      toast.success("Account created — welcome to NutriSense AI!");
      navigate("/dashboard");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Registration failed");
    }
  }

  return (
    <AuthLayout
      title="Create your account"
      description="Start monitoring nutrition in minutes"
      footer={
        <>
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-primary hover:underline">
            Sign in
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4" noValidate>
        <Input
          label="Full name"
          placeholder="Jane Doe"
          error={errors.fullName?.message}
          {...register("fullName")}
        />
        <Input
          label="Email"
          type="email"
          placeholder="you@institution.edu"
          error={errors.email?.message}
          {...register("email")}
        />
        <PasswordInput
          label="Password"
          placeholder="••••••••"
          error={errors.password?.message}
          {...register("password")}
        />
        <PasswordInput
          label="Confirm password"
          placeholder="••••••••"
          error={errors.confirmPassword?.message}
          {...register("confirmPassword")}
        />
        <Checkbox
          label="I agree to the Terms of Service and Privacy Policy"
          {...register("acceptTerms")}
        />
        {errors.acceptTerms && (
          <span className="-mt-2 text-xs text-red-500">{errors.acceptTerms.message}</span>
        )}

        <Button type="submit" className="mt-2 w-full" loading={isSubmitting}>
          {isSubmitting ? "Creating account..." : "Create account"}
        </Button>
      </form>
    </AuthLayout>
  );
}
