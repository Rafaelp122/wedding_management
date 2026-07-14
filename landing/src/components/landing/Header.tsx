import { useState, useEffect } from "react";
import { Menu, X, ChevronDown, ArrowRight, Sun, Moon } from "lucide-react";
import { useTheme } from "../../contexts/ThemeContext";

interface HeaderProps {
  activeSection: string;
}

const navItems = [
  { label: "Visão Geral", href: "#overview", id: "overview" },
  { label: "Recursos", href: "#features", id: "features" },
  { label: "Metodologia", href: "#process", id: "process" },
  { label: "Preços", href: "#pricing", id: "pricing" },
  { label: "Dúvidas", href: "#faq", id: "faq" },
];

export function Header({ activeSection }: HeaderProps) {
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-white/90 dark:bg-surface-dark/90 backdrop-blur-md border-b border-border/30 shadow-sm py-3"
          : "bg-transparent py-5"
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 md:px-12 flex justify-between items-center">
        <a
          href="#"
          className="flex items-center gap-3 text-xl font-bold tracking-tight text-foreground hover:opacity-90 transition-all group"
        >
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center shadow-glow">
            <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="9" cy="13" r="5.5" />
              <circle cx="15" cy="11" r="5.5" />
            </svg>
          </div>
          <span>Sim, Aceito!</span>
        </a>

        <nav className="hidden md:flex items-center gap-1">
          <div className="relative">
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              onBlur={() => setTimeout(() => setDropdownOpen(false), 200)}
              aria-expanded={dropdownOpen}
              aria-haspopup="true"
              className="text-muted-foreground hover:text-primary transition-colors hover:bg-primary/5 px-4 py-2 rounded-full text-base font-medium flex items-center gap-1.5 cursor-pointer"
            >
              <span>Produtos</span>
              <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${dropdownOpen ? "rotate-180" : ""}`} />
            </button>

            {dropdownOpen && (
              <div className="absolute top-full left-0 mt-2 w-56 bg-card rounded-2xl shadow-xl border border-border/30 py-2">
                <a href="#features" className="block px-4 py-2.5 text-sm text-muted-foreground hover:bg-primary/5 hover:text-primary transition-colors">
                  Dashboard Financeiro
                </a>
                <a href="#features" className="block px-4 py-2.5 text-sm text-muted-foreground hover:bg-primary/5 hover:text-primary transition-colors">
                  Checklists Inteligentes
                </a>
                <a href="#features" className="block px-4 py-2.5 text-sm text-muted-foreground hover:bg-primary/5 hover:text-primary transition-colors">
                  Diretório de Fornecedores
                </a>
                <div className="border-t border-border/20 my-1"></div>
                <a href="#process" className="block px-4 py-2.5 text-sm text-muted-foreground hover:bg-primary/5 hover:text-primary transition-colors font-medium">
                  Metodologia Completa
                </a>
              </div>
            )}
          </div>

          {navItems.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className={`px-4 py-2 rounded-full text-base font-medium transition-all ${
                activeSection === item.id
                  ? "text-primary bg-primary/5 font-semibold"
                  : "text-muted-foreground hover:text-primary hover:bg-primary/5"
              }`}
            >
              {item.label}
            </a>
          ))}
        </nav>

        <div className="hidden md:flex items-center gap-4">
          <button
            onClick={toggleTheme}
            className="p-2 text-muted-foreground hover:text-primary rounded-full hover:bg-primary/5 transition-all duration-300 flex items-center justify-center cursor-pointer"
            aria-label="Alternar tema"
          >
            {theme === "dark" ? (
              <Sun className="w-5 h-5 text-amber-400 fill-amber-400/20" />
            ) : (
              <Moon className="w-5 h-5 text-primary" />
            )}
          </button>

          <a
            href="https://app.simaceito.site/login"
            className="text-muted-foreground hover:text-primary font-semibold text-base px-4 py-2 hover:bg-primary/5 rounded-full transition-colors"
          >
            Login
          </a>
          <a
            href="https://app.simaceito.site/register"
            className="bg-primary hover:bg-primary-hover text-white font-semibold text-sm tracking-wide px-6 py-2.5 rounded-full shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 transition-all flex items-center gap-2 active:scale-95 duration-150"
          >
            <span>Criar Conta</span>
            <ArrowRight className="w-4 h-4" />
          </a>
        </div>

        <div className="flex items-center gap-2 md:hidden">
          <button
            onClick={toggleTheme}
            className="p-2 text-muted-foreground hover:text-primary rounded-full hover:bg-primary/5 transition-all duration-300"
            aria-label="Alternar tema"
          >
            {theme === "dark" ? <Sun className="w-6 h-6 text-amber-400" /> : <Moon className="w-6 h-6" />}
          </button>

          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 text-muted-foreground hover:text-primary rounded-full hover:bg-primary/5 transition-colors"
            aria-label="Abrir menu"
            aria-expanded={mobileMenuOpen}
            aria-haspopup="true"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {mobileMenuOpen && (
        <div className="md:hidden absolute top-full left-0 right-0 bg-card border-b border-border shadow-xl p-6 flex flex-col gap-4">
          <div className="text-xs font-semibold text-muted-foreground/50 uppercase tracking-wider mb-1">Menu</div>

          <a
            href="#features"
            onClick={() => setMobileMenuOpen(false)}
            className="text-lg font-medium text-muted-foreground hover:text-primary transition-colors py-1"
          >
            Recursos
          </a>
          <a
            href="#process"
            onClick={() => setMobileMenuOpen(false)}
            className="text-lg font-medium text-muted-foreground hover:text-primary transition-colors py-1"
          >
            Metodologia
          </a>
          <a
            href="#pricing"
            onClick={() => setMobileMenuOpen(false)}
            className="text-lg font-medium text-muted-foreground hover:text-primary transition-colors py-1"
          >
            Preços
          </a>
          <a
            href="#faq"
            onClick={() => setMobileMenuOpen(false)}
            className="text-lg font-medium text-muted-foreground hover:text-primary transition-colors py-1"
          >
            Dúvidas Frequentes
          </a>

          <div className="border-t border-border my-2"></div>

          <div className="flex flex-col gap-3">
            <a
              href="https://app.simaceito.site/login"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full text-center py-3 rounded-full text-muted-foreground hover:bg-primary/5 border border-border font-medium transition-colors"
            >
              Login
            </a>
            <a
              href="https://app.simaceito.site/register"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full text-center bg-primary text-white py-3 rounded-full font-semibold shadow-lg shadow-primary/10 hover:bg-primary-hover transition-colors flex items-center justify-center gap-2"
            >
              <span>Começar Grátis</span>
              <ArrowRight className="w-4 h-4" />
            </a>
          </div>
        </div>
      )}
    </header>
  );
}
