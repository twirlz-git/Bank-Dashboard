import React from "react";

export default function Footer() {
  return (
    <footer className="border-t border-slate-800/80 py-6 text-xs text-slate-500">
      <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <p>© {new Date().getFullYear()} Bank Product Analyzer</p>
        <p className="text-[11px]">
          Концепт для MVP: urgent и trends отчёты по банковским продуктам.
        </p>
      </div>
    </footer>
  );
}
