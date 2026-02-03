"use client";

import { useI18n } from "@/lib/i18n-context";
import { Card } from "@/components/ui/card";
import Link from "next/link";
import Image from "next/image";

export function ProjectDescription() {
  const { t, locale } = useI18n();

  const technologies = [
    { name: "Python", src: "/tech/python.png" },
    { name: "FastAPI", src: "/tech/fastapi.png" },
    { name: "Ray", src: "/tech/ray.png" },
    { name: "Next.js", src: "/tech/nextjs.png" },
    { name: "PostgreSQL", src: "/tech/postgresql.png" },
    { name: "MinIO", src: "/tech/minio.png" },
  ];

  return (
    <Card className="bg-gray-800/40 border-gray-700/50 backdrop-blur-sm p-8 mb-8">
      <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent">
        {t("home.projectTitle")}
      </h2>

      <div className="space-y-3 text-gray-300 leading-relaxed">
        <p>
          {t("home.description.p1.intro")}{" "}
          <span className="font-semibold text-white">
            {t("home.description.p1.highlight1")}
          </span>
          {t("home.description.p1.middle")}{" "}
          <span className="font-semibold text-white">
            {t("home.description.p1.highlight2")}
          </span>
          {t("home.description.p1.end")}
        </p>

        <p>
          {t("home.description.p2.intro")}{" "}
          <span className="font-semibold text-white">
            {t("home.description.p2.highlight1")}
          </span>
          {t("home.description.p2.middle1")}{" "}
          <span className="font-semibold text-white">
            {t("home.description.p2.highlight2")}
          </span>
          {t("home.description.p2.middle2")}{" "}
          <span className="font-semibold text-white">
            {t("home.description.p2.highlight3")}
          </span>
          {t("home.description.p2.middle3")}{" "}
          <span className="font-semibold text-white">
            {t("home.description.p2.highlight4")}
          </span>
          {t("home.description.p2.end")}
        </p>

        <p>
          {t("home.description.p3.intro")}{" "}
          <span className="font-semibold text-white">
            {t("home.description.p3.highlight1")}
          </span>
          {t("home.description.p3.middle1")}{" "}
          <span className="font-semibold text-white">
            {t("home.description.p3.highlight2")}
          </span>
          {t("home.description.p3.middle2")}{" "}
          <span className="font-semibold text-white">
            {t("home.description.p3.highlight3")}
          </span>
          {t("home.description.p3.end")}
        </p>

        <p>
          {t("home.description.p4.intro")}{" "}
          <span className="font-semibold text-white">
            {t("home.description.p4.highlight")}
          </span>
          {t("home.description.p4.end")}
        </p>

        <p className="pt-1">
          <Link
            href="/videos/create"
            className="text-cyan-400 font-semibold hover:text-cyan-300 transition-colors inline-flex items-center gap-2 group"
          >
            {t("home.description.cta")}
            <span className="group-hover:translate-x-1 transition-transform">
              →
            </span>
          </Link>
        </p>
      </div>

      <div className="pt-2">
        <h3 className="text-sm font-semibold text-gray-400 mb-4 uppercase tracking-wider">
          {t("home.techStack")}
        </h3>
        <div className="flex flex-wrap items-center gap-6">
          {technologies.map((tech) => (
            <div
              key={tech.name}
              className="relative w-12 h-12 grayscale hover:grayscale-0 transition-all opacity-70 hover:opacity-100"
              title={tech.name}
            >
              <Image
                src={tech.src || "/placeholder.svg"}
                alt={tech.name}
                fill
                className="object-contain"
              />
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}
