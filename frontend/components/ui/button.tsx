import * as React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "blue" | "magenta" | "success" | "danger";
  size?: "sm" | "md" | "lg";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "blue", size = "md", ...props }, ref) => {
    const variantStyles = {
      blue: "bg-[#31B7EA] hover:bg-[#358EE3] text-white shadow-lg shadow-[#31B7EA]/20",
      magenta:
        "bg-[#B949A3] hover:bg-[#442090] text-white shadow-lg shadow-[#B949A3]/20",
      success:
        "bg-[#21bb85] hover:bg-[#1a9668] text-white shadow-lg shadow-[#21bb85]/20",
      danger:
        "bg-[#fe7070] hover:bg-[#e65555] text-white shadow-lg shadow-[#fe7070]/20",
    };

    const sizeStyles = {
      sm: "px-3 py-1.5 text-sm",
      md: "px-4 py-2 text-base",
      lg: "px-6 py-3 text-lg",
    };

    return (
      <button
        className={cn(
          "rounded-lg font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer",
          variantStyles[variant],
          sizeStyles[size],
          className,
        )}
        ref={ref}
        {...props}
      />
    );
  },
);
Button.displayName = "Button";

export { Button };
