import { motion } from "framer-motion";
import { Camera, Upload } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export function QuickActionsCard() {
  return (
    <Card className="flex flex-col gap-3 p-6">
      <div>
        <p className="text-sm font-semibold">Log a meal</p>
        <p className="mt-0.5 text-xs text-muted-foreground">
          Capture a tray or upload an image to run analysis instantly.
        </p>
      </div>
      <div className="mt-1 grid grid-cols-2 gap-3">
        <motion.div whileHover={{ y: -2 }} whileTap={{ scale: 0.97 }}>
          <Button variant="outline" className="h-20 w-full flex-col gap-2">
            <Camera size={18} className="text-primary" />
            <span className="text-xs font-medium">Quick Camera</span>
          </Button>
        </motion.div>
        <motion.div whileHover={{ y: -2 }} whileTap={{ scale: 0.97 }}>
          <Button variant="outline" className="h-20 w-full flex-col gap-2">
            <Upload size={18} className="text-primary" />
            <span className="text-xs font-medium">Quick Upload</span>
          </Button>
        </motion.div>
      </div>
    </Card>
  );
}
