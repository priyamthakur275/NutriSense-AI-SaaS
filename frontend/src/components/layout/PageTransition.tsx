import { motion } from "framer-motion";
import { useLocation, Outlet } from "react-router-dom";

export function PageTransition() {
  const location = useLocation();

  return (
    <motion.div
      key={location.pathname}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.2, ease: "easeInOut" }}
    >
      <Outlet />
    </motion.div>
  );
}
