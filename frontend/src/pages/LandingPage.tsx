import { Suspense, lazy } from "react";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Hero } from "@/components/landing/Hero";

const ProductDemo = lazy(() =>
  import("@/components/landing/ProductDemo").then((m) => ({ default: m.ProductDemo }))
);
const Features = lazy(() =>
  import("@/components/landing/Features").then((m) => ({ default: m.Features }))
);
const AICapabilities = lazy(() =>
  import("@/components/landing/AICapabilities").then((m) => ({ default: m.AICapabilities }))
);
const WorkflowTimeline = lazy(() =>
  import("@/components/landing/WorkflowTimeline").then((m) => ({ default: m.WorkflowTimeline }))
);
const AnalyticsPreview = lazy(() =>
  import("@/components/landing/AnalyticsPreview").then((m) => ({ default: m.AnalyticsPreview }))
);
const Security = lazy(() =>
  import("@/components/landing/Security").then((m) => ({ default: m.Security }))
);
const Testimonials = lazy(() =>
  import("@/components/landing/Testimonials").then((m) => ({ default: m.Testimonials }))
);
const FAQ = lazy(() => import("@/components/landing/FAQ").then((m) => ({ default: m.FAQ })));
const CTABanner = lazy(() =>
  import("@/components/landing/CTABanner").then((m) => ({ default: m.CTABanner }))
);

function SectionFallback() {
  return <div className="h-40 w-full animate-pulse bg-secondary/20" />;
}

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col overflow-x-hidden">
      <Navbar />
      <main className="flex-1">
        <Hero />
        <Suspense fallback={<SectionFallback />}>
          <ProductDemo />
        </Suspense>
        <Suspense fallback={<SectionFallback />}>
          <Features />
        </Suspense>
        <Suspense fallback={<SectionFallback />}>
          <AICapabilities />
        </Suspense>
        <Suspense fallback={<SectionFallback />}>
          <WorkflowTimeline />
        </Suspense>
        <Suspense fallback={<SectionFallback />}>
          <AnalyticsPreview />
        </Suspense>
        <Suspense fallback={<SectionFallback />}>
          <Security />
        </Suspense>
        <Suspense fallback={<SectionFallback />}>
          <Testimonials />
        </Suspense>
        <Suspense fallback={<SectionFallback />}>
          <FAQ />
        </Suspense>
        <Suspense fallback={<SectionFallback />}>
          <CTABanner />
        </Suspense>
      </main>
      <Footer />
    </div>
  );
}
