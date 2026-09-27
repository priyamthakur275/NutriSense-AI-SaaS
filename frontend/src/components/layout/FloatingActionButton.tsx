import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Plus, Camera, Upload, X } from "lucide-react";
import { cn } from "@/lib/utils";

const actions = [
  { label: "Quick Camera", icon: Camera },
  { label: "Quick Upload", icon: Upload },
];

export function FloatingActionButton() {
  const [open, setOpen] = useState(false);

  return (
    <div className="fixed bottom-6 right-6 z-40 flex flex-col items-end gap-3">
      <AnimatePresence>
        {open &&
          actions.map((action, i) => (
            <motion.button
              key={action.label}
              initial={{ opacity: 0, y: 10, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 10, scale: 0.9 }}
              transition={{ duration: 0.2, delay: i * 0.05 }}
              onClick={() => setOpen(false)}
              className="flex items-center gap-2.5 rounded-full border border-border bg-card py-2 pl-4 pr-2.5 text-sm font-medium shadow-lg"
            >
              {action.label}
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary">
                <action.icon size={15} />
              </span>
            </motion.button>
          ))}
      </AnimatePresence>

      <motion.button
        onClick={() => setOpen((o) => !o)}
        whileTap={{ scale: 0.92 }}
        aria-label="Quick actions"
        className={cn(
          "flex h-14 w-14 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-xl shadow-primary/30 transition-transform"
        )}
      >
        <motion.span animate={{ rotate: open ? 45 : 0 }} transition={{ duration: 0.2 }}>
          {open ? <X size={22} /> : <Plus size={22} />}
        </motion.span>
      </motion.button>
    </div>
  );
}
