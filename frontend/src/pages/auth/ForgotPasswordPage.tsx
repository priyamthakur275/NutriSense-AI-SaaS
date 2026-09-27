import { useState } from "react";
import { Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { MailCheck, ArrowLeft } from "lucide-react";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { api } from "@/lib/api";
import { forgotPasswordSchema, type ForgotPasswordFormValues } from "@/lib/validation";

export default function ForgotPasswordPage() {
  const [sent, setSent] = useState(false);
  const [sentTo, setSentTo] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { email: "" },
  });

  async function onSubmit(values: ForgotPasswordFormValues) {
    try {
      // Endpoint to be implemented server-side: POST /auth/forgot-password
      await api.post("/auth/forgot-password", { email: values.email }).catch(() => {
        // Swallow network/404 errors in this scaffold phase — UX still confirms
        // to avoid leaking whether an email is registered.
      });
      setSentTo(values.email);
      setSent(true);
    } catch {
      toast.error("Something went wrong. Please try again.");
    }
  }

  return (
    <AuthLayout
      title={sent ? "Check your inbox" : "Forgot your password?"}
      description={
        sent
          ? `We've sent password reset instructions to ${sentTo}`
          : "Enter your email and we'll send you a reset link"
      }
      footer={
        <Link
          to="/login"
          className="inline-flex items-center gap-1.5 font-medium text-primary hover:underline"
        >
          <ArrowLeft size={14} /> Back to sign in
        </Link>
      }
    >
      <AnimatePresence mode="wait">
        {sent ? (
          <motion.div
            key="sent"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="flex flex-col items-center gap-4 py-4 text-center"
          >
            <span className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/10 text-primary">
              <MailCheck size={26} />
            </span>
            <p className="text-sm text-muted-foreground">
              Didn't get the email? Check your spam folder, or try again in a few
              minutes.
            </p>
            <Button variant="outline" className="w-full" onClick={() => setSent(false)}>
              Use a different email
            </Button>
          </motion.div>
        ) : (
          <motion.form
            key="form"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            onSubmit={handleSubmit(onSubmit)}
            className="flex flex-col gap-4"
            noValidate
          >
            <Input
              label="Email"
              type="email"
              placeholder="you@institution.edu"
              error={errors.email?.message}
              {...register("email")}
            />
            <Button type="submit" className="mt-2 w-full" loading={isSubmitting}>
              {isSubmitting ? "Sending..." : "Send reset link"}
            </Button>
          </motion.form>
        )}
      </AnimatePresence>
    </AuthLayout>
  );
}
