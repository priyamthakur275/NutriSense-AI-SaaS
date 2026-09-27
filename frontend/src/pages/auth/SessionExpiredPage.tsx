import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Clock } from "lucide-react";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { Button } from "@/components/ui/Button";

export default function SessionExpiredPage() {
  const navigate = useNavigate();

  return (
    <AuthLayout
      title="Your session has expired"
      description="For your security, please sign in again to continue"
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex flex-col items-center gap-4 py-4 text-center"
      >
        <span className="flex h-14 w-14 items-center justify-center rounded-full bg-amber-500/10 text-amber-500">
          <Clock size={26} />
        </span>
        <Button className="w-full" onClick={() => navigate("/login")}>
          Sign in again
        </Button>
      </motion.div>
    </AuthLayout>
  );
}
