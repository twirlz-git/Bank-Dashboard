import React, { useState } from "react";

const PRODUCT_TYPES = [
  "Кредитная карта",
  "Потребительский кредит",
  "Дебетовая карта",
  "Ипотека"
];

export default function UrgentForm({ onSubmit, loading }) {
  const [bankName, setBankName] = useState("Сбербанк");
  const [competitorName, setCompetitorName] = useState("UBank");
  const [productType, setProductType] = useState(PRODUCT_TYPES[0]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      bank_name: bankName,
      competitor_name: competitorName,
      product_type: productType
    });
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 rounded-3xl bg-slate-900/70 border border-slate-800/60 p-4 sm:p-5"
    >
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs text-slate-400">Режим</p>
          <p className="text-sm font-medium">Urgent report</p>
        </div>
        <span className="text-[11px] text-slate-400">
          1 конкурент · 1 продукт
        </span>
      </div>

      <div className="space-y-3 text-xs">
        <div className="space-y-1.5">
          <label className="block text-slate-300">
            Банк (наш эталон — Сбер)
          </label>
          <input
            value={bankName}
            onChange={(e) => setBankName(e.target.value)}
            className="w-full rounded-xl border border-slate-700 bg-slate-950/70 px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-brand-400"
          />
        </div>
        <div className="space-y-1.5">
          <label className="block text-slate-300">Конкурент</label>
          <input
            value={competitorName}
            onChange={(e) => setCompetitorName(e.target.value)}
            className="w-full rounded-xl border border-slate-700 bg-slate-950/70 px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-brand-400"
          />
        </div>
        <div className="space-y-1.5">
          <label className="block text-slate-300">Тип продукта</label>
          <select
            value={productType}
            onChange={(e) => setProductType(e.target.value)}
            className="w-full rounded-xl border border-slate-700 bg-slate-950/70 px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-brand-400"
          >
            {PRODUCT_TYPES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full inline-flex items-center justify-center rounded-xl bg-brand-500 hover:bg-brand-400 text-slate-950 text-xs font-semibold py-2.5 mt-2 transition disabled:opacity-60 disabled:cursor-not-allowed"
      >
        {loading ? "Генерируем отчёт..." : "Сгенерировать отчёт"}
      </button>
      <p className="text-[11px] text-slate-500">
        В демо используются синтетические данные, но структура отчёта 1:1,
        как в боевой версии.
      </p>
    </form>
  );
}
