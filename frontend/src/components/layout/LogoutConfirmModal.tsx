import { useNavigate } from "react-router-dom";
import { Modal } from "@/components/ui/Modal";
import { useAuthStore } from "@/store/authStore";

interface LogoutConfirmModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function LogoutConfirmModal({ open, onOpenChange }: LogoutConfirmModalProps) {
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title="Log out of NutriSense AI?"
      description="You'll need to sign in again to access your dashboard."
      confirmLabel="Log out"
      confirmVariant="destructive"
      onConfirm={() => {
        logout();
        onOpenChange(false);
        navigate("/login");
      }}
    />
  );
}
