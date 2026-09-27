import { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/auth/LoginPage";
import RegisterPage from "@/pages/auth/RegisterPage";
import ForgotPasswordPage from "@/pages/auth/ForgotPasswordPage";
import ResetPasswordPage from "@/pages/auth/ResetPasswordPage";
import VerifyEmailPage from "@/pages/auth/VerifyEmailPage";
import SessionExpiredPage from "@/pages/auth/SessionExpiredPage";
import ForbiddenPage from "@/pages/errors/ForbiddenPage";
import NotFoundPage from "@/pages/errors/NotFoundPage";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { ProtectedRoute } from "@/routes/ProtectedRoute";

const OverviewPage = lazy(() => import("@/pages/dashboard/OverviewPage"));
const StudentsPage = lazy(() => import("@/pages/dashboard/StudentsPage"));
const MealsPage = lazy(() => import("@/pages/dashboard/MealsPage"));
const NutritionPage = lazy(() => import("@/pages/dashboard/NutritionPage"));
const AIInsightsPage = lazy(() => import("@/pages/dashboard/AIInsightsPage"));
const CompliancePage = lazy(() => import("@/pages/dashboard/CompliancePage"));
const ReportsPage = lazy(() => import("@/pages/dashboard/ReportsPage"));
const NotificationsPage = lazy(() => import("@/pages/dashboard/NotificationsPage"));
const SettingsPage = lazy(() => import("@/pages/dashboard/SettingsPage"));
const ProfilePage = lazy(() => import("@/pages/dashboard/ProfilePage"));

function DashboardPageFallback() {
  return (
    <div className="flex flex-col gap-6">
      <div className="h-32 w-full animate-pulse rounded-xl bg-secondary/40" />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-24 w-full animate-pulse rounded-xl bg-secondary/40" />
        ))}
      </div>
      <div className="h-64 w-full animate-pulse rounded-xl bg-secondary/40" />
    </div>
  );
}

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Toaster
          position="top-right"
          richColors
          closeButton
          toastOptions={{
            className: "font-sans",
          }}
        />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
          <Route path="/session-expired" element={<SessionExpiredPage />} />
          <Route path="/403" element={<ForbiddenPage />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<DashboardLayout />}>
                            <Route index element={<Suspense fallback={<DashboardPageFallback />}><OverviewPage /></Suspense>} />
              <Route path="students" element={<Suspense fallback={<DashboardPageFallback />}><StudentsPage /></Suspense>} />
              <Route path="meals" element={<Suspense fallback={<DashboardPageFallback />}><MealsPage /></Suspense>} />
              <Route path="nutrition" element={<Suspense fallback={<DashboardPageFallback />}><NutritionPage /></Suspense>} />
              <Route path="ai-insights" element={<Suspense fallback={<DashboardPageFallback />}><AIInsightsPage /></Suspense>} />
              <Route path="compliance" element={<Suspense fallback={<DashboardPageFallback />}><CompliancePage /></Suspense>} />
              <Route path="reports" element={<Suspense fallback={<DashboardPageFallback />}><ReportsPage /></Suspense>} />
              <Route path="notifications" element={<Suspense fallback={<DashboardPageFallback />}><NotificationsPage /></Suspense>} />
              <Route path="settings" element={<Suspense fallback={<DashboardPageFallback />}><SettingsPage /></Suspense>} />
              <Route path="profile" element={<Suspense fallback={<DashboardPageFallback />}><ProfilePage /></Suspense>} />
            </Route>
          </Route>

          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
