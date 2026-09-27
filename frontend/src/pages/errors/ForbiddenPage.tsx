import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ShieldAlert, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/Button";

export default function ForbiddenPage() {
  const navigate = useNavigate();

  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-secondary/30 px-4 text-center">
      <div className="pointer-events-none absolute inset-0 -z-10 bg-grid opacity-[0.25] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,black,transparent)]" />

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex flex-col items-center"
      >
        <span className="flex h-16 w-16 items-center justify-center rounded-full bg-red-500/10 text-red-500">
          <ShieldAlert size={30} />
        </span>
        <h1 className="mt-6 text-5xl font-bold tracking-tight">403</h1>
        <p className="mt-2 text-lg font-medium">Access denied</p>
        <p className="mt-1 max-w-sm text-sm text-muted-foreground">
          You don't have permission to view this page. If you think this is a
          mistake, contact your administrator.
        </p>
        <div className="mt-8 flex gap-3">
          <Button variant="outline" onClick={() => navigate(-1)}>
            <ArrowLeft size={15} /> Go back
          </Button>
          <Link to="/dashboard">
            <Button>Go to dashboard</Button>
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
