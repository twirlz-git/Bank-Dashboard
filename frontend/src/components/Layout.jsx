
import React from "react";

export default function Layout({ children }) {
  return (
    <div className="min-h-screen gradient-bg text-slate-50">
      <header className="border-b border-slate-800/60 sticky top-0 z-30 backdrop-blur">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-brand-400 to-emerald-400 flex items-center justify-center text-xs font-bold shadow-soft">
              BA
            </div>
            <span className="font-semibold tracking-tight">
              Bank Product Analyzer
            </span>
          </div>
          <nav className="hidden sm:flex items-center gap-4 text-xs text-slate-300">
            <a href="#demo" className="hover:text-white transition">
              Demo
            </a>
            <a href="#features" className="hover:text-white transition">
              Что умеет
            </a>
            <a href="#how-it-works" className="hover:text-white transition">
              Как работает
            </a>
          </nav>
          <a
            href="#demo"
            className="text-xs sm:text-sm px-3 sm:px-4 py-2 rounded-full bg-brand-400 text-slate-950 font-semibold transition shadow-soft hover:brightness-110"
          >
            Попробовать демо
          </a>
        </div>
      </header>
      <main>{children}</main>
    </div>
  );
}
