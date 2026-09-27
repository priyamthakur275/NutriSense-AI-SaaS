import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import { MailCheck, XCircle, Loader2 } from "lucide-react";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { Button } from "@/components/ui/Button";
import { api } from "@/lib/api";

type Status = "pending" | "verifying" | "success" | "error";

export default function VerifyEmailPage() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const token = params.get("token");
  const [status, setStatus] = useState<Status>(token ? "verifying" : "pending");

  useEffect(() => {
    if (!token) return;

    let cancelled = false;
    (async () => {
      try {
        // Endpoint to be implemented server-side: POST /auth/verify-email
        await api.post("/auth/verify-email", { token });
        if (!cancelled) setStatus("success");
      } catch {
        if (!cancelled) setStatus("error");
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <AuthLayout
      title={
        status === "success"
          ? "Email verified"
          : status === "error"
          ? "Verification failed"
          : "Verify your email"
      }
      description={
        status === "pending"
          ? "We've sent a verification link to your inbox. Click it to activate your account."
          : status === "verifying"
          ? "Confirming your email address..."
          : status === "success"
          ? "Your email has been confirmed. You're all set."
          : "This verification link is invalid or has expired."
      }
      footer={
        <Link to="/login" className="font-medium text-primary hover:underline">
          Back to sign in
        </Link>
      }
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex flex-col items-center gap-4 py-4 text-center"
      >
        <span className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/10 text-primary">
          {status === "verifying" && <Loader2 size={26} className="animate-spin" />}
          {status === "pending" && <MailCheck size={26} />}
          {status === "success" && <MailCheck size={26} />}
          {status === "error" && <XCircle size={26} className="text-red-500" />}
        </span>

        {status === "success" && (
          <Button className="w-full" onClick={() => navigate("/dashboard")}>
            Go to dashboard
          </Button>
        )}
        {status === "error" && (
          <Button variant="outline" className="w-full" onClick={() => navigate("/login")}>
            Return to sign in
          </Button>
        )}
      </motion.div>
    </AuthLayout>
  );
}
