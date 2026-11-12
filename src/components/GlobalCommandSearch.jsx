import React, { useState, useEffect, useRef } from 'react';
import { ALL_NAV_ITEMS, searchNavItems, NAVIGATION_CATEGORIES } from '../data/navigationRegistry';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Global ⌘K Command Search & Navigator Island
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 *
 * Capabilities:
 *   - Global Ctrl+K / ⌘K and custom event triggers
 *   - Real-time client-side index filtering across all 14 categories and 86 routes
 *   - Keyboard navigation (ArrowUp, ArrowDown, Enter, Escape)
 *   - Category quick-filter tabs
 *   - Unified theme-adaptive glass aesthetic
 * ========================================================================================
 */

const QUICK_FILTERS = [
  { id: 'all', label: 'All (86 Routes)' },
  { id: 'semester-courses', label: 'Semester Courses' },
  { id: 'engineering-laboratories', label: 'Laboratories' },
  { id: 'practice-assessment', label: 'Practice & Assessment' },
  { id: 'unit-wise-notes', label: 'Notes & Syllabus' },
  { id: 'my-learning', label: 'My Learning' },
];

export default function GlobalCommandSearch() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [selectedIndex, setSelectedIndex] = useState(0);

  const inputRef = useRef(null);
  const listRef = useRef(null);

  // Compute filtered search results
  const results = React.useMemo(() => {
    let pool = query ? searchNavItems(query, 20) : ALL_NAV_ITEMS;
    if (selectedFilter !== 'all') {
      pool = pool.filter((item) => item.categoryId === selectedFilter);
    }
    return pool.slice(0, 10);
  }, [query, selectedFilter]);

  // Open & close handlers
  const openSearch = () => {
    setIsOpen(true);
    setQuery('');
    setSelectedIndex(0);
    setTimeout(() => inputRef.current?.focus(), 50);
  };

  const closeSearch = () => {
    setIsOpen(false);
  };

  // Keyboard and event listeners
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Toggle modal with Ctrl+K or Cmd+K
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsOpen((prev) => !prev);
        if (!isOpen) {
          setTimeout(() => inputRef.current?.focus(), 50);
        }
      }

      // Close modal with Escape
      if (e.key === 'Escape' && isOpen) {
        e.preventDefault();
        closeSearch();
      }

      // Arrow navigation when open
      if (isOpen && results.length > 0) {
        if (e.key === 'ArrowDown') {
          e.preventDefault();
          setSelectedIndex((prev) => (prev + 1) % results.length);
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          setSelectedIndex((prev) => (prev - 1 + results.length) % results.length);
        } else if (e.key === 'Enter') {
          e.preventDefault();
          const target = results[selectedIndex];
          if (target) {
            window.location.href = target.path;
            closeSearch();
          }
        }
      }
    };

    // Custom DOM event listener for Topbar search button
    const handleCustomOpen = () => openSearch();

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('voltcore:open-search', handleCustomOpen);

    // Also attach to legacy search button id if present
    const legacyBtn = document.getElementById('cmd-k-search-trigger');
    legacyBtn?.addEventListener('click', handleCustomOpen);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('voltcore:open-search', handleCustomOpen);
      legacyBtn?.removeEventListener('click', handleCustomOpen);
    };
  }, [isOpen, results, selectedIndex]);

  // Scroll active item into view
  useEffect(() => {
    if (listRef.current) {
      const activeEl = listRef.current.children[selectedIndex];
      if (activeEl) {
        activeEl.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [selectedIndex]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Global ⌘K Command Search"
      className="fixed inset-0 z-50 flex items-start justify-center pt-16 sm:pt-24 px-4 bg-black/75 backdrop-blur-md animate-fadeIn"
      onClick={closeSearch}
    >
      <div
        className="w-full max-w-2xl overflow-hidden rounded-2xl border shadow-2xl transition-all"
        style={{
          background: 'var(--theme-surface, rgba(4, 16, 38, 0.95))',
          borderColor: 'var(--theme-border, rgba(0, 240, 181, 0.35))',
          boxShadow: 'var(--elevation-hover, 0 20px 50px rgba(0,0,0,0.8))',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input Bar */}
        <div
          className="flex items-center gap-3 p-4 border-b"
          style={{
            borderColor: 'var(--theme-border, rgba(0, 240, 181, 0.2))',
            background: 'var(--theme-bg, #020813)',
          }}
        >
          <svg
            className="w-5 h-5 flex-shrink-0"
            style={{ color: 'var(--theme-primary, #00F0B5)' }}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            placeholder="Search subjects, topics, derivations, labs, or notes..."
            className="w-full bg-transparent text-sm sm:text-base text-white placeholder-slate-400 focus:outline-none font-sans"
          />
          <kbd
            onClick={closeSearch}
            className="cursor-pointer px-2 py-1 rounded border text-[10px] font-mono font-bold transition-colors"
            style={{
              background: 'var(--theme-surface, rgba(4, 16, 38, 0.8))',
              borderColor: 'var(--theme-border, rgba(0, 240, 181, 0.25))',
              color: 'var(--theme-text-muted, #94A3B8)',
            }}
          >
            ESC
          </kbd>
        </div>

        {/* Quick Category Chips */}
        <div
          className="flex items-center gap-1.5 p-2.5 overflow-x-auto border-b text-xs font-mono"
          style={{
            borderColor: 'var(--theme-border, rgba(0, 240, 181, 0.15))',
            background: 'rgba(2, 8, 19, 0.4)',
          }}
        >
          {QUICK_FILTERS.map((f) => (
            <button
              key={f.id}
              type="button"
              onClick={() => {
                setSelectedFilter(f.id);
                setSelectedIndex(0);
              }}
              className="px-2.5 py-1 rounded-lg transition-all flex-shrink-0"
              style={{
                backgroundColor:
                  selectedFilter === f.id
                    ? 'var(--theme-primary, #00F0B5)'
                    : 'transparent',
                color: selectedFilter === f.id ? '#020813' : 'var(--theme-text-muted, #94A3B8)',
                fontWeight: selectedFilter === f.id ? 700 : 500,
                border:
                  selectedFilter === f.id
                    ? '1px solid var(--theme-primary, #00F0B5)'
                    : '1px solid rgba(255,255,255,0.06)',
              }}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Search Results List */}
        <div ref={listRef} className="max-h-80 overflow-y-auto p-2 space-y-1">
          {results.length === 0 ? (
            <div className="p-8 text-center text-slate-400 font-mono text-xs">
              <span className="text-2xl block mb-2">🔍</span>
              No routes found matching <span className="text-white font-bold">"{query}"</span>.
              <div className="text-[11px] text-slate-500 mt-1">
                Try searching for subjects ("Digital Signal Processing", "Microcontrollers"), "Wokwi", "STM32", or "GATE".
              </div>
            </div>
          ) : (
            results.map((item, idx) => {
              const isSelected = idx === selectedIndex;
              return (
                <a
                  key={item.path}
                  href={item.path}
                  onClick={closeSearch}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className="flex items-center justify-between p-3 rounded-xl transition-all cursor-pointer group"
                  style={{
                    backgroundColor: isSelected
                      ? 'rgba(0, 240, 181, 0.12)'
                      : 'transparent',
                    border: isSelected
                      ? '1px solid var(--theme-primary, #00F0B5)'
                      : '1px solid transparent',
                  }}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="w-8 h-8 rounded-lg flex items-center justify-center text-lg flex-shrink-0 bg-slate-900/60 border border-slate-800">
                      {item.icon}
                    </span>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-heading font-bold text-xs sm:text-sm text-white truncate group-hover:text-[var(--theme-primary,#00F0B5)]">
                          {item.title}
                        </span>
                        {item.badge && (
                          <span
                            className="text-[9px] px-1.5 py-0.2 rounded font-mono font-bold flex-shrink-0"
                            style={{
                              backgroundColor: `${item.badgeColor || '#00F0B5'}20`,
                              color: item.badgeColor || '#00F0B5',
                              border: `1px solid ${item.badgeColor || '#00F0B5'}40`,
                            }}
                          >
                            {item.badge}
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] text-slate-400 truncate mt-0.5">
                        <span className="font-mono text-slate-500 mr-2">[{item.categoryName}]</span>
                        {item.description}
                      </div>
                    </div>
                  </div>

                  <span className="text-xs text-slate-500 font-mono ml-3 flex-shrink-0 group-hover:translate-x-1 transition-transform">
                    &rarr;
                  </span>
                </a>
              );
            })
          )}
        </div>

        {/* Modal Footer Keybind Legend */}
        <div
          className="flex items-center justify-between p-3 border-t text-[11px] font-mono text-slate-400"
          style={{
            borderColor: 'var(--theme-border, rgba(0, 240, 181, 0.15))',
            background: 'var(--theme-bg, #020813)',
          }}
        >
          <div className="flex items-center gap-3">
            <span>
              <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-200">↑</kbd>
              <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-200 ml-1">↓</kbd> navigate
            </span>
            <span>
              <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-200">↵</kbd> select
            </span>
            <span>
              <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-200">esc</kbd> close
            </span>
          </div>
          <span style={{ color: 'var(--theme-primary, #00F0B5)' }}>
            VoltCore Apex • 14 Unified Categories
          </span>
        </div>
      </div>
    </div>
  );
}
