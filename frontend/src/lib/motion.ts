import type { Variants, Transition } from "framer-motion";

/**
 * Shared Framer Motion variants for consistent animation timing across the
 * app. Components can spread these directly into `initial`/`animate`/`exit`
 * props, or use the stagger container + item pair for orchestrated lists.
 */

export const easeOut: Transition["ease"] = [0.16, 1, 0.3, 1];

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.4, ease: easeOut } },
};

export const slideUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: easeOut } },
};

export const slideDown: Variants = {
  hidden: { opacity: 0, y: -16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: easeOut } },
};

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.94 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.35, ease: easeOut } },
};

/** Wrap a list container with this, then give each child `staggerItem`. */
export const staggerContainer = (staggerDelay = 0.06): Variants => ({
  hidden: {},
  visible: {
    transition: {
      staggerChildren: staggerDelay,
    },
  },
});

export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 14 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: easeOut } },
};

/** Standard hover lift for interactive cards. */
export const hoverLift = {
  whileHover: { y: -3 },
  whileTap: { scale: 0.98 },
  transition: { duration: 0.2 },
};
