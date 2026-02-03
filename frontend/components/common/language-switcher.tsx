"use client";

import { useI18n } from "@/lib/i18n-context";
import { DropdownMenuWrapper } from "../ui/dropdown-menu-wrapper";
import { Button } from "../ui/button";
import Image from "next/image";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { FiChevronDown } from "react-icons/fi";

const languages = [
  {
    code: "en",
    label: "English",
    nativeLabel: "English",
    flag: "/flags/gb.svg",
  },
  { code: "pl", label: "Polish", nativeLabel: "Polski", flag: "/flags/pl.svg" },
];

export function LanguageSwitcher() {
  const { locale, setLocale, t } = useI18n();

  const currentLanguage =
    languages.find((lang) => lang.code === locale) || languages[0];

  const handleLanguageChange = (langCode: string) => {
    setLocale(langCode as "en" | "pl");
  };

  const options = languages.map((lang) => ({
    icon: (
      <div className="w-8 h-8 rounded-full overflow-hidden flex-shrink-0 border border-white/10">
        <Image
          src={lang.flag || "/placeholder.svg"}
          alt={lang.nativeLabel}
          width={32}
          height={32}
          className="object-cover w-full h-full"
        />
      </div>
    ),
    label: (
      <span className="ml-3 text-sm font-medium text-white">
        {lang.nativeLabel}
      </span>
    ),
    onClick: () => handleLanguageChange(lang.code),
  }));

  return (
    <TooltipProvider>
      <Tooltip delayDuration={0}>
        <TooltipTrigger asChild>
          <DropdownMenuWrapper
            trigger={(open) => (
              <Button
                variant="ghost"
                size="icon"
                className="relative w-12 h-12 rounded-full bg-white/5 backdrop-blur-sm border-1 border-[#31B7EA]/30 hover:border-[#375DDA] hover:shadow-lg hover:shadow-[#31B7EA]/20 transition-all duration-300 p-0 overflow-visible group focus-visible:outline-none focus-visible:ring-0 cursor-pointer"
              >
                <div className="w-full h-full rounded-full overflow-hidden flex items-center justify-center p-2 cursor-pointer">
                  <Image
                    src={currentLanguage.flag || "/placeholder.svg"}
                    alt={currentLanguage.nativeLabel}
                    width={32}
                    height={32}
                    className="object-cover w-full h-full rounded-full cursor-pointer pointer-events-none"
                  />
                </div>

                <div className="absolute -top-0.5 -right-0.5 w-5 h-5 rounded-full bg-gradient-to-br from-[#31B7EA] via-[#375DDA] to-[#442090] flex items-center justify-center border-2 border-[#0a0a0f] shadow-lg group-hover:scale-110 transition-all duration-300 cursor-pointer pointer-events-none">
                  <FiChevronDown
                    className={`w-3 h-3 text-white transition-transform duration-300 ${open ? "" : "rotate-180"}`}
                  />
                </div>
              </Button>
            )}
            options={options}
            align="start"
          />
        </TooltipTrigger>
        <TooltipContent
          side="right"
          className="bg-[#1a1a2e] border-[#375DDA] text-white"
        >
          <p className="font-medium">{t("lang.switchLanguage")}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
