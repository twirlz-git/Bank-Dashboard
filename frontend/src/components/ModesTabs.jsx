import React from "react";

export default function ModesTabs({ activeMode, onChange }) {
  return (
    <div className="inline-flex items-center rounded-full border border-slate-800 bg-slate-900/80 p-1 text-xs">
      <button
        type="button"
        onClick={() => onChange("urgent")}
        className={`px-4 py-1.5 rounded-full transition ${
          activeMode === "urgent"
            ? "bg-slate-100 text-slate-900"
            : "text-slate-300 hover:text-white"
        }`}
      >
        Urgent mode
      </button>
      <button
        type="button"
        onClick={() => onChange("trends")}
        className={`px-4 py-1.5 rounded-full transition ${
          activeMode === "trends"
            ? "bg-slate-100 text-slate-900"
            : "text-slate-300 hover:text-white"
        }`}
      >
        Trends mode
      </button>
    </div>
  );
}
