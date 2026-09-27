import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Compass } from "lucide-react";
import { Button } from "@/components/ui/Button";

export default function NotFoundPage() {
  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-secondary/30 px-4 text-center">
      <div className="pointer-events-none absolute inset-0 -z-10 bg-grid opacity-[0.25] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,black,transparent)]" />

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex flex-col items-center"
      >
        <span className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary">
          <Compass size={30} />
        </span>
        <h1 className="mt-6 text-5xl font-bold tracking-tight">404</h1>
        <p className="mt-2 text-lg font-medium">Page not found</p>
        <p className="mt-1 max-w-sm text-sm text-muted-foreground">
          The page you're looking for doesn't exist or may have been moved.
        </p>
        <div className="mt-8">
          <Link to="/">
            <Button>Back to home</Button>
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
