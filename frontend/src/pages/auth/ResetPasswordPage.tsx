import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { CheckCircle2 } from "lucide-react";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { Button } from "@/components/ui/Button";
import { PasswordInput } from "@/components/ui/PasswordInput";
import { api } from "@/lib/api";
import { resetPasswordSchema, type ResetPasswordFormValues } from "@/lib/validation";
import { toast } from "sonner";

export default function ResetPasswordPage() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const token = params.get("token") ?? "";
  const [done, setDone] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordFormValues>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: { password: "", confirmPassword: "" },
  });

  async function onSubmit(values: ResetPasswordFormValues) {
    try {
      // Endpoint to be implemented server-side: POST /auth/reset-password
      await api.post("/auth/reset-password", {
        token,
        password: values.password,
      });
      setDone(true);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "This reset link is invalid or expired");
    }
  }

  if (done) {
    return (
      <AuthLayout title="Password updated" description="You can now sign in with your new password">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex flex-col items-center gap-4 py-4 text-center"
        >
          <span className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/10 text-primary">
            <CheckCircle2 size={26} />
          </span>
          <Button className="w-full" onClick={() => navigate("/login")}>
            Continue to sign in
          </Button>
        </motion.div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      title="Set a new password"
      description="Choose a strong password you haven't used before"
      footer={
        <Link to="/login" className="font-medium text-primary hover:underline">
          Back to sign in
        </Link>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4" noValidate>
        <PasswordInput
          label="New password"
          placeholder="••••••••"
          error={errors.password?.message}
          {...register("password")}
        />
        <PasswordInput
          label="Confirm new password"
          placeholder="••••••••"
          error={errors.confirmPassword?.message}
          {...register("confirmPassword")}
        />
        <Button type="submit" className="mt-2 w-full" loading={isSubmitting}>
          {isSubmitting ? "Updating..." : "Update password"}
        </Button>
      </form>
    </AuthLayout>
  );
}
