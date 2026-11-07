import React, { useState, useEffect } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - 18 Vibrant & Colorful Themes Selector Island
 * Anna University / MIT Campus (Department of Electronics Engineering)
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 * Hardware Safe: Zero background polling, instantaneous CSS variable updates.
 * ========================================================================================
 */

export const THEMES_LIST = [
  {
    id: "cyber-emerald",
    name: "Cyber Emerald & Mint",
    category: "Vibrant Neon",
    badge: "Neon Mint",
    icon: "⚡",
    description: "Deep crystalline teal base with radiant emerald-cyan accents and electric mint glows.",
    primary: "#00F0B5",
    accent: "#10B981",
    bg: "#03261f"
  },
  {
    id: "electric-violet",
    name: "Electric Violet & Magenta",
    category: "Vibrant Neon",
    badge: "Ultraviolet",
    icon: "🔮",
    description: "Royal indigo and cosmic violet with laser magenta highlights and neon purple aura.",
    primary: "#A855F7",
    accent: "#EC4899",
    bg: "#160d33"
  },
  {
    id: "sunset-crimson",
    name: "Sunset Crimson & Amber",
    category: "Sunset Gradient",
    badge: "Solar Sunset",
    icon: "🌅",
    description: "Warm blood-orange and vivid crimson with glowing golden hour horizon gradients.",
    primary: "#F97316",
    accent: "#F43F5E",
    bg: "#260a14"
  },
  {
    id: "oceanic-azure",
    name: "Oceanic Sapphire & Cyan",
    category: "Rich Chromatic",
    badge: "Deep Ocean",
    icon: "🌊",
    description: "Deep ocean trench navy-blue with vivid sky cyan and sapphire luminescence.",
    primary: "#00D8F6",
    accent: "#3B82F6",
    bg: "#061b33"
  },
  {
    id: "golden-mustard",
    name: "Imperial Gold & Warm Mustard",
    category: "Rich Chromatic",
    badge: "Royal Gold",
    icon: "👑",
    description: "Regal warm umber and antique bronze enriched with vivid honey mustard and imperial amber.",
    primary: "#FFC83B",
    accent: "#F59E0B",
    bg: "#241503"
  },
  {
    id: "tokyo-neon",
    name: "Tokyo Cyberpunk Neon",
    category: "Vibrant Neon",
    badge: "Cyberpunk",
    icon: "🗼",
    description: "Electrifying high-voltage neon pink, cyber cyan, and laser lime on deep amethyst.",
    primary: "#FF007F",
    accent: "#00F5FF",
    bg: "#140524"
  },
  {
    id: "nordic-frost",
    name: "Nordic Glacial Frost",
    category: "Rich Chromatic",
    badge: "Glacial Blue",
    icon: "❄️",
    description: "Crystalline Scandinavian fjord blue with arctic ice highlights and frost cyan edges.",
    primary: "#38BDF8",
    accent: "#7DD3FC",
    bg: "#071c2c"
  },
  {
    id: "forest-sage",
    name: "Lush Forest & Olive Sage",
    category: "Rich Chromatic",
    badge: "Pine Forest",
    icon: "🌲",
    description: "Lush evergreen pine canopy paired with olive sage and vibrant lime moss radiance.",
    primary: "#84A950",
    accent: "#10B981",
    bg: "#092112"
  },
  {
    id: "solar-flare",
    name: "Solar Flare & Plasma",
    category: "Sunset Gradient",
    badge: "Solar Plasma",
    icon: "☀️",
    description: "Blazing coronal eruption of radiant cadmium yellow and molten fiery orange.",
    primary: "#FACC15",
    accent: "#FB923C",
    bg: "#2b1003"
  },
  {
    id: "cherry-blossom",
    name: "Kyoto Sakura Blossom",
    category: "Pastel Academy",
    badge: "Sakura Pink",
    icon: "🌸",
    description: "Soft floral blossom pink with radiant ruby highlights and delicate rose petal tones.",
    primary: "#F472B6",
    accent: "#FB7185",
    bg: "#260614"
  },
  {
    id: "pastel-academic",
    name: "Cambridge Academic Pastel",
    category: "Pastel Academy",
    badge: "Ivory / Pastel",
    icon: "🎓",
    description: "Elegant ivory-cream parchment with academic periwinkle, lavender, and mint laurel.",
    primary: "#6366F1",
    accent: "#10B981",
    bg: "#F5F3EC"
  },
  {
    id: "oxford-navy",
    name: "Oxford Collegiate Navy & Gold",
    category: "Rich Chromatic",
    badge: "Collegiate Blue",
    icon: "🏛️",
    description: "Stately university royal navy blue with heraldic gold emblem accents and crisp silver.",
    primary: "#EAB308",
    accent: "#3B82F6",
    bg: "#09152b"
  },
  {
    id: "synthwave-80s",
    name: "80s Retro Synthwave",
    category: "Vibrant Neon",
    badge: "Synthwave",
    icon: "📼",
    description: "Radical dark fuchsia and electric cyan with nostalgic neon grid reflections.",
    primary: "#FF1493",
    accent: "#00E5FF",
    bg: "#190524"
  },
  {
    id: "matrix-terminal",
    name: "Matrix Phosphor CRT",
    category: "Vibrant Neon",
    badge: "CRT Lime",
    icon: "📟",
    description: "Deep cathode dark green with high-intensity phosphor lime terminal glow.",
    primary: "#22C55E",
    accent: "#4ADE80",
    bg: "#04190c"
  },
  {
    id: "lavender-dream",
    name: "Lavender Amethyst Glow",
    category: "Pastel Academy",
    badge: "Soft Lavender",
    icon: "🪻",
    description: "Twilight amethyst background illuminated with serene lavender and periwinkle dreams.",
    primary: "#C084FC",
    accent: "#818CF8",
    bg: "#170f2b"
  },
  {
    id: "autumn-copper",
    name: "Autumn Harvest Copper",
    category: "Sunset Gradient",
    badge: "Copper Bronze",
    icon: "🍂",
    description: "Warm roasted espresso wood tone highlighted with burnished copper and amber honey.",
    primary: "#EA580C",
    accent: "#F59E0B",
    bg: "#261005"
  },
  {
    id: "clean-canvas",
    name: "Modern Pristine Canvas",
    category: "Light Dynamic",
    badge: "Light Studio",
    icon: "✨",
    description: "Clinical, ultra-crisp modern light workspace with cobalt electric blue and emerald accents.",
    primary: "#2563EB",
    accent: "#059669",
    bg: "#F8FAFC"
  },
  {
    id: "cosmic-nebula",
    name: "Cosmic Chromatic Nebula",
    category: "Multi-Chromatic",
    badge: "Multi-Chromatic",
    icon: "🌌",
    description: "Stunning multidimensional chromatic aurora with magenta, starlight teal, and celestial violet.",
    primary: "#D946EF",
    accent: "#06B6D4",
    bg: "#110826"
  }
];

export default function ThemeSelector({ compact = false }) {
  const [activeThemeId, setActiveThemeId] = useState('cyber-emerald');
  const [isOpen, setIsOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('All');

  // Load saved theme on client mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem('voltcore_theme');
      if (saved && THEMES_LIST.some(t => t.id === saved)) {
        setActiveThemeId(saved);
        applyThemeDOM(saved);
      } else {
        applyThemeDOM('cyber-emerald');
      }
    } catch (e) {
      console.warn("Theme storage read warning:", e);
    }
  }, []);

  const applyThemeDOM = (themeId) => {
    document.documentElement.setAttribute('data-theme', themeId);
    document.body.setAttribute('data-theme', themeId);
    window.dispatchEvent(new CustomEvent('voltcore-theme-changed', { detail: { themeId } }));
  };

  const handleSelectTheme = (themeId) => {
    setActiveThemeId(themeId);
    applyThemeDOM(themeId);
    try {
      localStorage.setItem('voltcore_theme', themeId);
    } catch (e) {
      console.warn("Theme storage write warning:", e);
    }
  };

  const activeTheme = THEMES_LIST.find(t => t.id === activeThemeId) || THEMES_LIST[0];

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  const categories = ['All', 'Vibrant Neon', 'Sunset Gradient', 'Rich Chromatic', 'Pastel Academy', 'Light Dynamic', 'Multi-Chromatic'];
  const filteredThemes = selectedCategory === 'All' 
    ? THEMES_LIST 
    : THEMES_LIST.filter(t => t.category === selectedCategory);

  return (
    <div className="relative inline-block font-mono text-xs">
      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-haspopup="dialog"
        aria-expanded={isOpen}
        aria-label={`Theme Selector: currently ${activeTheme.name}`}
        className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[var(--theme-card)] border border-[var(--theme-border)] hover:border-[var(--theme-primary)] text-[var(--theme-text)] transition-all shadow-md group focus:outline-none focus:ring-2 focus:ring-[var(--theme-primary)]"
        title="Toggle Vibrant 18-Theme Palette (Non-Black Focus)"
      >
        <span className="text-sm">{activeTheme.icon}</span>
        <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: activeTheme.primary }}></span>
        <span className="font-semibold hidden sm:inline">{activeTheme.name}</span>
        <span className="text-[10px] px-1.5 py-0.5 rounded bg-[var(--theme-bg)] text-[var(--theme-text-muted)] border border-[var(--theme-border)]/50 font-bold hidden md:inline">
          {activeTheme.badge}
        </span>
        <svg className={`w-3.5 h-3.5 text-[var(--theme-text-muted)] transition-transform ${isOpen ? 'rotate-180' : ''}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </button>

      {/* Modal / Popover Palette Drawer */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md">
          <div
            role="dialog"
            aria-modal="true"
            aria-label="18 Vibrant & Colorful Themes Palette"
            className="w-full max-w-4xl max-h-[85vh] overflow-hidden rounded-3xl bg-slate-950/95 border border-slate-700 shadow-2xl flex flex-col animate-in fade-in zoom-in-95 duration-200"
          >
            
            {/* Header */}
            <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 to-pink-500 p-0.5 flex items-center justify-center text-xl shadow-lg">
                  🎨
                </div>
                <div>
                  <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                    18 Vibrant &amp; Colorful Themes
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-semibold">
                      Non-Black Focus
                    </span>
                  </h3>
                  <p className="text-[11px] text-slate-400">
                    Engineered for Anna University VoltCore Apex • Instantaneous CSS Variable Switching
                  </p>
                </div>
              </div>
              
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                aria-label="Close theme selection modal"
                className="w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white flex items-center justify-center transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--theme-primary)]"
              >
                ✕
              </button>
            </div>

            {/* Category Filter Chips */}
            <div className="px-5 py-3 border-b border-slate-800/80 bg-slate-900/30 flex items-center gap-2 overflow-x-auto text-[11px]">
              {categories.map(cat => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setSelectedCategory(cat)}
                  aria-pressed={selectedCategory === cat}
                  className={`px-3 py-1 rounded-lg transition-all flex-shrink-0 font-medium focus:outline-none focus:ring-2 focus:ring-emerald-400 ${
                    selectedCategory === cat
                      ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-slate-950 font-bold shadow-md'
                      : 'bg-slate-800/80 text-slate-300 hover:bg-slate-700 hover:text-white'
                  }`}
                >
                  {cat} {cat === 'All' ? `(${THEMES_LIST.length})` : ''}
                </button>
              ))}
            </div>

            {/* Grid of 18 Vibrant Themes */}
            <div className="p-5 overflow-y-auto flex-1 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
              {filteredThemes.map(theme => {
                const isSelected = theme.id === activeThemeId;
                return (
                  <div
                    key={theme.id}
                    role="button"
                    tabIndex={0}
                    aria-pressed={isSelected}
                    aria-label={`Select ${theme.name} theme`}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        handleSelectTheme(theme.id);
                      }
                    }}
                    onClick={() => handleSelectTheme(theme.id)}
                    className={`p-3.5 rounded-2xl border transition-all cursor-pointer relative group flex flex-col justify-between focus:outline-none focus:ring-2 focus:ring-emerald-400 ${
                      isSelected
                        ? 'border-emerald-400 ring-2 ring-emerald-400/30 shadow-lg scale-[1.01]'
                        : 'border-slate-800 hover:border-slate-600 bg-slate-900/50 hover:bg-slate-900/90'
                    }`}
                    style={{
                      background: isSelected 
                        ? `linear-gradient(135deg, ${theme.bg} 0%, rgba(15,23,42,0.95) 100%)` 
                        : undefined
                    }}
                  >
                    <div>
                      {/* Theme Top Bar */}
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{theme.icon}</span>
                          <span className="font-bold text-white text-xs tracking-tight">
                            {theme.name}
                          </span>
                        </div>
                        {isSelected && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-emerald-500 text-slate-950 font-extrabold flex items-center gap-1">
                            ✓ ACTIVE
                          </span>
                        )}
                      </div>

                      {/* Swatches & Gradient Bar */}
                      <div className="flex items-center gap-2 mb-2.5">
                        <div className="flex items-center gap-1">
                          <div
                            className="w-4 h-4 rounded-full border border-black/30 shadow-sm"
                            style={{ backgroundColor: theme.primary }}
                            title={`Primary: ${theme.primary}`}
                          />
                          <div
                            className="w-4 h-4 rounded-full border border-black/30 shadow-sm"
                            style={{ backgroundColor: theme.accent }}
                            title={`Accent: ${theme.accent}`}
                          />
                          <div
                            className="w-4 h-4 rounded-full border border-black/30 shadow-sm"
                            style={{ backgroundColor: theme.bg }}
                            title={`Base: ${theme.bg}`}
                          />
                        </div>
                        <div className="flex-1 h-2 rounded-full overflow-hidden bg-slate-800">
                          <div 
                            className="h-full w-full"
                            style={{
                              background: `linear-gradient(90deg, ${theme.primary} 0%, ${theme.accent} 50%, ${theme.bg} 100%)`
                            }}
                          />
                        </div>
                      </div>

                      {/* Description */}
                      <p className="text-[11px] text-slate-300/90 leading-relaxed mb-3">
                        {theme.description}
                      </p>
                    </div>

                    {/* Footer Meta */}
                    <div className="flex items-center justify-between pt-2 border-t border-slate-800/80 text-[10px] text-slate-400">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-semibold">
                        {theme.category}
                      </span>
                      <span className="font-mono text-slate-400">
                        {theme.id}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-slate-800 bg-slate-900/80 flex items-center justify-between text-[11px]">
              <span className="text-slate-400">
                Selected: <strong className="text-emerald-400">{activeTheme.name}</strong> ({activeTheme.category})
              </span>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="px-4 py-1.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold transition-colors"
              >
                Done / Close Palette
              </button>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}
