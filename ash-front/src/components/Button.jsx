import { extendVariants, Button } from "@nextui-org/react";

export const MyButton = extendVariants(Button, {
  variants: {
    // <- modify/add variants
    color: {
      olive: "text-black/70 bg-[#84cc16]",
    },
    isDisabled: {
      true: "bg-[#eaeaea] text-[#000] opacity-50 cursor-not-allowed",
    },
    size: {
      xs: "px-unit-2 min-w-unit-12 h-unit-6 text-tiny gap-unit-1 rounded-small",
      md: "h-6 rounded-small",
      xl: "px-unit-8 min-w-unit-28 h-unit-14 text-large gap-unit-4 rounded-medium",
    },
    radius: {
      small: "8px", // rounded-small
      medium: "12px", // rounded-medium
      large: "14px", // rounded-large
    },
  },
  defaultVariants: {
    // <- modify/add default variants
    size: "md",
  },
});
