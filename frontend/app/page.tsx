"use client";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { Sidebar } from "@/components/common/sidebar";
import { Header } from "@/components/common/header";
import { ProjectDescription } from "@/components/common/project-description";
import { Card } from "@/components/ui/card";
import { useI18n } from "@/lib/i18n-context";

const authors = [
  {
    name: "Maciej Grzybacz",
    facultyKey: "home.facultyOfComputerScience",
    email: "mgrzybacz@student.agh.edu.pl",
    gradient: "from-[#31B7EA] to-[#358EE3]",
    glowClass: "glow-sky",
    photo: "/authors/maciej.jpg",
  },
  {
    name: "Michał Proć",
    facultyKey: "home.facultyOfComputerScience",
    email: "mproc@student.agh.edu.pl",
    gradient: "from-[#442090] to-[#B949A3]",
    glowClass: "glow-magenta",
    photo: "/authors/michal.jpg",
  },
  {
    name: "Ryszard Żmija",
    facultyKey: "home.facultyOfComputerScience",
    email: "ryszardzmija@student.agh.edu.pl",
    gradient: "from-[#375DDA] to-[#342EBC]",
    glowClass: "glow-royal",
    photo: "/user-placeholder.jpg",
  },
];

export default function Home() {
  const { t } = useI18n();

  return (
    <ProtectedRoute>
      <div className="flex h-screen text-white font-sans">
        <Sidebar />

        <div className="flex-1 flex flex-col">
          <Header title="Authors" />

          <main className="flex-1 overflow-auto p-8">
            <div className="max-w-7xl mx-auto">
              <ProjectDescription />

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {authors.map((author) => (
                  <Card
                    key={author.email}
                    className={`bg-gradient-to-br ${author.gradient} border-none p-6 relative overflow-hidden ${author.glowClass}`}
                  >
                    <div className="relative z-10">
                      <div className="mb-4">
                        <img
                          src={author.photo || "/placeholder.svg"}
                          alt={author.name}
                          className="w-24 h-24 rounded-full mx-auto mb-4 border-4 border-white/20 object-cover object-top"
                        />
                      </div>
                      <h2 className="text-2xl font-bold text-white mb-2 text-center">
                        {author.name}
                      </h2>
                      <p className="text-sm text-white/80 mb-1 text-center font-medium">
                        {t(author.facultyKey)}
                      </p>
                      <a
                        href={`mailto:${author.email}`}
                        className="text-sm text-white underline underline-offset-4 font-medium hover:text-white/80 transition-colors block text-center"
                      >
                        {author.email}
                      </a>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
