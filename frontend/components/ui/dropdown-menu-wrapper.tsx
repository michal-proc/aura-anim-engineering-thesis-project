"use client";

import { useState, type ReactNode } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface DropdownOption {
  icon: ReactNode;
  label: string | ReactNode;
  onClick?: () => void;
  href?: string;
}

interface DropdownMenuWrapperProps {
  trigger: ReactNode | ((open: boolean) => ReactNode);
  options: DropdownOption[];
  align?: "start" | "center" | "end";
}

export function DropdownMenuWrapper({
  trigger,
  options,
  align = "end",
}: DropdownMenuWrapperProps) {
  const [open, setOpen] = useState(false);

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        {typeof trigger === "function" ? trigger(open) : trigger}
      </DropdownMenuTrigger>
      <DropdownMenuContent
        className="bg-[#1a1a2e] border-[#375DDA] text-white min-w-[180px]"
        align={align}
      >
        {options.map((option, index) => (
          <DropdownMenuItem
            key={index}
            className="cursor-pointer hover:bg-[#252540] focus:bg-[#252540] flex items-center gap-3 py-2.5"
            onClick={option.onClick}
          >
            <span className="text-[#31B7EA]">{option.icon}</span>
            <span className="text-sm font-medium">{option.label}</span>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
