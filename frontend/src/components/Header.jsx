import React, { useState, useEffect } from 'react';
import {
  Train,
  Activity,
  Bell,
  Sun,
  Moon,
  User,
  Menu,
  X,
  Search,
  MapPin,
  Clock,
  ShieldAlert,
  LayoutDashboard,
} from 'lucide-react';

/**
 * Modern Transportation Control Center Header
 * Includes sticky layout, Rail Radar branding, navigation tabs, notifications,
 * dark mode toggle, and mobile responsive drawer.
 */
export const Header = ({
  activeTab = 'dashboard',
  onSelectTab = () => {},
  alertCount = 0,
  onOpenSearch = () => {},
}) => {
  const [isDark, setIsDark] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Initialize theme from localStorage or system preference
  useEffect(() => {
    const saved = localStorage.getItem('railradar_theme');
    if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      setIsDark(true);
      document.documentElement.classList.add('dark');
    } else {
      setIsDark(false);
      document.documentElement.classList.remove('dark');
    }
  }, []);

  const toggleTheme = () => {
    const nextDark = !isDark;
    setIsDark(nextDark);
    if (nextDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('railradar_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('railradar_theme', 'light');
    }
  };

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'live_trains', label: 'Live Trains', icon: Train },
    { id: 'stations', label: 'Stations', icon: MapPin },
    { id: 'delays', label: 'Delays', icon: Clock },
    { id: 'alerts', label: 'Alerts', icon: ShieldAlert, badge: alertCount },
  ];

  const handleNavClick = (id) => {
    onSelectTab(id);
    setMobileMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-50 bg-white/95 dark:bg-slate-950/95 backdrop-blur-md border-b border-slate-200/90 dark:border-slate-800 shadow-xs transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-18">
          {/* LEFT: Branding */}
          <div
            onClick={() => handleNavClick('dashboard')}
            className="flex items-center space-x-3 cursor-pointer group"
          >
            <div className="w-10 h-10 sm:w-11 sm:h-11 rounded-xl bg-gradient-to-br from-blue-700 via-indigo-700 to-slate-900 text-white flex items-center justify-center shadow-md shadow-blue-900/20 ring-2 ring-blue-500/20 group-hover:scale-105 transition-transform shrink-0">
              <Train className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-base sm:text-lg text-slate-950 dark:text-white tracking-tight leading-none font-sans">
                  RAIL RADAR
                </span>
                <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-extrabold tracking-wider bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                  LIVE
                </span>
              </div>
              <p className="text-[10px] sm:text-[11px] text-slate-500 dark:text-slate-400 font-medium tracking-wide leading-tight mt-0.5">
                Live Indian Railway Intelligence
              </p>
            </div>
          </div>

          {/* CENTER: Navigation Tabs (Desktop & Tablet) */}
          <nav className="hidden md:flex items-center space-x-1 lg:space-x-1.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => handleNavClick(item.id)}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer relative ${
                    isActive
                      ? 'bg-slate-100 dark:bg-slate-800 text-blue-600 dark:text-blue-400 shadow-2xs'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800/50'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{item.label}</span>
                  {item.badge > 0 && (
                    <span className="ml-1 px-1.5 py-0.2 rounded-full text-[10px] font-bold bg-amber-500 text-white">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* RIGHT: Action Controls (Theme, Notifications, Profile, Mobile Menu) */}
          <div className="flex items-center space-x-2 sm:space-x-2.5">
            {/* Quick Search Shortcut */}
            <button
              type="button"
              onClick={onOpenSearch}
              title="Focus train search"
              className="p-2 rounded-xl text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer"
            >
              <Search className="w-4 h-4" />
            </button>

            {/* Notification Bell */}
            <button
              type="button"
              onClick={() => handleNavClick('alerts')}
              title={`${alertCount} Live Alerts`}
              className="p-2 rounded-xl text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer relative"
            >
              <Bell className="w-4 h-4" />
              {alertCount > 0 && (
                <span className="absolute top-1.5 right-1.5 flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500" />
                </span>
              )}
            </button>

            {/* Dark Mode Toggle */}
            <button
              type="button"
              onClick={toggleTheme}
              title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
              className="p-2 rounded-xl text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer"
            >
              {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}
            </button>

            {/* User / Profile Icon */}
            <div
              title="Operational Controller"
              className="w-8 h-8 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 flex items-center justify-center border border-slate-200/80 dark:border-slate-700 text-xs font-bold"
            >
              <User className="w-4 h-4" />
            </div>

            {/* Mobile Hamburger Button */}
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Slide-down Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden py-3 px-2 border-t border-slate-100 dark:border-slate-800 space-y-1.5 animate-in slide-in-from-top-2 duration-150">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => handleNavClick(item.id)}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition cursor-pointer ${
                    isActive
                      ? 'bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300'
                      : 'text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-center space-x-2.5">
                    <Icon className="w-4 h-4 text-slate-500 dark:text-slate-400" />
                    <span>{item.label}</span>
                  </div>
                  {item.badge > 0 && (
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500 text-white">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
