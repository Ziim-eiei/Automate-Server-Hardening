// MyInput.tsx
import { extendVariants, Input } from "@nextui-org/react";

export const MyInput = extendVariants(Input, {
  variants: {
    textSize: {
      base: {
        input: "text-base",
      },
    },
  },
  defaultVariants: {
    textSize: "base",
    size: "md",
  },
});
