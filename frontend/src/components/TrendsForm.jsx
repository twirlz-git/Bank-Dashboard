import React, { useState } from "react";

export default function TrendsForm({ onSubmit, loading }) {
  const [bankName, setBankName] = useState("Сбербанк");
  const [productType, setProductType] = useState("Кредитная карта");
  const [period, setPeriod] = useState("12m");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      bank_name: bankName,
      product_type: productType,
      period
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
          <p className="text-sm font-medium">Trends report</p>
        </div>
        <span className="text-[11px] text-slate-400">
          6–12 месяцев по одному продукту
        </span>
      </div>

      <div className="space-y-3 text-xs">
        <div className="space-y-1.5">
          <label className="block text-slate-300">Банк</label>
          <input
            value={bankName}
            onChange={(e) => setBankName(e.target.value)}
            className="w-full rounded-xl border border-slate-700 bg-slate-950/70 px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-brand-400"
          />
        </div>
        <div className="space-y-1.5">
          <label className="block text-slate-300">Тип продукта</label>
          <input
            value={productType}
            onChange={(e) => setProductType(e.target.value)}
            className="w-full rounded-xl border border-slate-700 bg-slate-950/70 px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-brand-400"
          />
        </div>
        <div className="space-y-1.5">
          <label className="block text-slate-300">Период анализа</label>
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="w-full rounded-xl border border-slate-700 bg-slate-950/70 px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-brand-400"
          >
            <option value="6m">6 месяцев</option>
            <option value="12m">12 месяцев</option>
          </select>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full inline-flex items-center justify-center rounded-xl bg-brand-500 hover:bg-brand-400 text-slate-950 text-xs font-semibold py-2.5 mt-2 transition disabled:opacity-60 disabled:cursor-not-allowed"
      >
        {loading ? "Строим тренды..." : "Построить тренды"}
      </button>
      <p className="text-[11px] text-slate-500">
        В полной версии сюда подтягиваются веб-поиск, исторические условия и
        LLM-комментарии.
      </p>
    </form>
  );
}
