/**
 * Navbar – top navigation bar with DentalAI branding and nav links.
 */

const NAV_LINKS = [
  { label: 'Analýza', href: '#', active: true },
  { label: 'História', href: '#history' },
  { label: 'Porovnanie', href: '#compare' },
  { label: 'Nastavenia', href: '#settings' },
];

export default function Navbar() {
  return (
    <nav className="glass-panel-strong sticky top-0 z-50 flex items-center justify-between px-6 py-3">
      {/* Logo */}
      <div className="flex items-center gap-3">
        {/* Tooth icon */}
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-dental-primary to-dental-accent">
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="white"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 2C8 2 6 4 6 7c0 2 1 3 1 5s-1 4-1 6c0 2 2 4 4 4h4c2 0 4-2 4-4 0-2-1-4-1-6s1-3 1-5c0-3-2-5-6-5z" />
            <path d="M9 11h6" />
            <path d="M9 15h6" />
          </svg>
        </div>
        <div>
          <h1 className="text-lg font-bold text-dental-textMain text-glow-teal leading-tight">
            Dental<span className="text-dental-primary">AI</span>
          </h1>
          <p className="text-[9px] font-medium uppercase tracking-widest text-dental-textMuted leading-none">
            RTG Analýza
          </p>
        </div>
      </div>

      {/* Nav links */}
      <div className="hidden md:flex items-center gap-1">
        {NAV_LINKS.map((link) => (
          <a
            key={link.label}
            href={link.href}
            className={`
              px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200
              ${link.active
                ? 'bg-dental-primary/15 text-dental-primary'
                : 'text-dental-textMuted hover:text-dental-textMain hover:bg-dental-surfaceHighlight/50'
              }
            `}
          >
            {link.label}
          </a>
        ))}
      </div>

      {/* User avatar */}
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-dental-primary/30 to-dental-accent/30 border border-dental-primary/30">
          <span className="text-xs font-bold text-dental-primary">DR</span>
        </div>
      </div>
    </nav>
  );
}
