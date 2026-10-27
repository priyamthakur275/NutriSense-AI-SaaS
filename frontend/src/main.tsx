import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "@fontsource-variable/geist";
import "@fontsource-variable/bricolage-grotesque";
import "./index.css";

try {
  const stored = localStorage.getItem("nutrisense-theme");
  if (stored && JSON.parse(stored)?.state?.theme === "dark") {
    document.documentElement.classList.add("dark");
  }
} catch {
  // Corrupt or blocked storage: fall back to the light theme.
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
