import { useState, useEffect } from "react";

/** Hook que rastreia qual seção da página está visível com base no scroll. */
export function useScrollSpy(sectionIds: string[], offset = 150) {
  const [activeSection, setActiveSection] = useState(sectionIds[0]);

  useEffect(() => {
    let rafId: number;

    const handleScroll = () => {
      if (rafId) return;
      rafId = requestAnimationFrame(() => {
        const scrollPosition = window.scrollY + offset;

        for (const sectionId of sectionIds) {
          const el = document.getElementById(sectionId);
          if (el) {
            const top = el.offsetTop;
            const height = el.offsetHeight;
            if (scrollPosition >= top && scrollPosition < top + height) {
              setActiveSection(sectionId);
              break;
            }
          }
        }
        rafId = 0;
      });
    };

    handleScroll();
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", handleScroll);
      if (rafId) cancelAnimationFrame(rafId);
    };
  }, [sectionIds, offset]);

  return activeSection;
}
