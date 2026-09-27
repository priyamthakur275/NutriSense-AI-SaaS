import { useState } from "react";
import { Leaf, Code2, MessageCircle, Globe, Mail, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

const columns = [
  {
    title: "Product",
    links: ["Features", "AI Capabilities", "Analytics", "Security", "Pricing"],
  },
  {
    title: "Company",
    links: ["About", "Careers", "Blog", "Contact"],
  },
  {
    title: "Resources",
    links: ["Documentation", "API Reference", "Support", "Status"],
  },
  {
    title: "Legal",
    links: ["Privacy Policy", "Terms of Service", "Data Processing", "Compliance"],
  },
];

const socials = [
  { icon: Code2, href: "https://github.com", label: "GitHub" },
  { icon: MessageCircle, href: "https://twitter.com", label: "Twitter" },
  { icon: Globe, href: "https://linkedin.com", label: "LinkedIn" },
];

export function Footer() {
  const [email, setEmail] = useState("");
  const [subscribed, setSubscribed] = useState(false);

  function handleSubscribe(e: React.FormEvent) {
    e.preventDefault();
    if (!email) return;
    setSubscribed(true);
    setEmail("");
  }

  return (
    <footer className="border-t border-border bg-secondary/20">
      <div className="mx-auto max-w-7xl px-6 py-16">
        <div className="grid grid-cols-1 gap-12 border-b border-border pb-12 lg:grid-cols-2 lg:items-center">
          <div>
            <div className="flex items-center gap-2 text-lg font-semibold">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                <Leaf size={18} />
              </span>
              NutriSense AI
            </div>
            <p className="mt-3 max-w-sm text-sm text-muted-foreground">
              AI-powered nutritional intelligence for institutions — food
              analysis, compliance, and agentic recommendations in one
              platform.
            </p>
          </div>

          <form onSubmit={handleSubscribe} className="flex w-full max-w-md flex-col gap-2 sm:flex-row lg:ml-auto">
            <Input
              type="email"
              placeholder="you@institution.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              aria-label="Email for newsletter"
            />
            <Button type="submit" className="flex-shrink-0">
              {subscribed ? "Subscribed" : "Subscribe"} <ArrowRight size={15} />
            </Button>
          </form>
        </div>

        <div className="grid grid-cols-2 gap-10 py-12 md:grid-cols-4">
          {columns.map((col) => (
            <div key={col.title}>
              <h4 className="text-sm font-semibold">{col.title}</h4>
              <ul className="mt-4 flex flex-col gap-3">
                {col.links.map((link) => (
                  <li key={link}>
                    <a
                      href="#"
                      className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="flex flex-col items-center justify-between gap-4 border-t border-border pt-8 text-sm text-muted-foreground md:flex-row">
          <p>© {new Date().getFullYear()} NutriSense AI. All rights reserved.</p>
          <div className="flex items-center gap-3">
            <a
              href="mailto:hello@nutrisense.ai"
              aria-label="Email"
              className="flex h-9 w-9 items-center justify-center rounded-lg border border-border transition-colors hover:bg-secondary hover:text-foreground"
            >
              <Mail size={15} />
            </a>
            {socials.map((s) => (
              <a
                key={s.label}
                href={s.href}
                target="_blank"
                rel="noreferrer"
                aria-label={s.label}
                className="flex h-9 w-9 items-center justify-center rounded-lg border border-border transition-colors hover:bg-secondary hover:text-foreground"
              >
                <s.icon size={15} />
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
