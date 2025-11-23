import React from "react";

export default function OutputPreview({
  activeMode,
  urgentResult,
  trendsResult,
  loading,
  error
}) {
  const hasUrgent = !!urgentResult;
  const hasTrends = !!trendsResult;

  return (
    <div className="rounded-3xl bg-slate-950/60 border border-slate-800/70 p-4 sm:p-5 h-full flex flex-col">
      <div className="flex items-center justify-between gap-3 mb-3">
        <div>
          <p className="text-xs text-slate-400">Превью отчёта</p>
          <p className="text-sm font-medium">
            {activeMode === "urgent"
              ? "Сравнение Сбер vs конкурент"
              : "Тренды по продукту"}
          </p>
        </div>
        {loading && (
          <span className="inline-flex items-center gap-2 text-[11px] text-slate-400">
            <span className="h-1.5 w-1.5 rounded-full bg-brand-400 animate-ping" />
            Генерируем...
          </span>
        )}
      </div>

      {error && (
        <div className="mb-3 rounded-xl border border-rose-500/40 bg-rose-500/10 px-3 py-2 text-[11px] text-rose-100">
          {String(error)}
        </div>
      )}

      <div className="text-xs text-slate-300 flex-1 overflow-auto">
        {activeMode === "urgent" && hasUrgent && (
          <UrgentPreviewContent data={urgentResult} />
        )}

        {activeMode === "trends" && hasTrends && (
          <TrendsPreviewContent data={trendsResult} />
        )}

        {!loading && !error && !hasUrgent && activeMode === "urgent" && (
          <p className="text-slate-500 text-[11px]">
            Заполните форму слева и нажмите «Сгенерировать отчёт», чтобы увидеть
            сравнительную таблицу и инсайты.
          </p>
        )}
        {!loading && !error && !hasTrends && activeMode === "trends" && (
          <p className="text-slate-500 text-[11px]">
            Заполните форму слева и нажмите «Построить тренды», чтобы увидеть
            динамику и резюме по ставкам.
          </p>
        )}
      </div>
    </div>
  );
}

function UrgentPreviewContent({ data }) {
  return (
    <div className="space-y-4">
      <div>
        <p className="text-[11px] text-slate-400">Пара</p>
        <p className="text-[13px] font-semibold">
          {data.bank_name} vs {data.competitor_name} · {data.product_type}
        </p>
      </div>

      <div className="rounded-2xl border border-slate-800 overflow-hidden">
        <div className="grid grid-cols-3 text-[11px] bg-slate-900/80 border-b border-slate-800">
          <div className="px-3 py-2 text-slate-400">Параметр</div>
          <div className="px-3 py-2 font-medium text-emerald-300">
            {data.bank_name}
          </div>
          <div className="px-3 py-2 font-medium text-sky-300">
            {data.competitor_name}
          </div>
        </div>
        {data.comparison_table.map((row) => (
          <div
            key={row.parameter}
            className="grid grid-cols-3 text-[11px] border-t border-slate-800/70"
          >
            <div className="px-3 py-2 text-slate-200">{row.parameter}</div>
            <div className="px-3 py-2 text-slate-100">{row.sber_value}</div>
            <div className="px-3 py-2 text-slate-100">
              {row.competitor_value}
            </div>
          </div>
        ))}
      </div>

      {data.insights?.length > 0 && (
        <div>
          <p className="text-[11px] text-slate-400 mb-1.5">Краткие инсайты</p>
          <ul className="space-y-1.5">
            {data.insights.map((item, idx) => (
              <li key={idx} className="flex gap-2">
                <span className="mt-1 h-1 w-1 rounded-full bg-emerald-400" />
                <p className="text-[11px] text-slate-200">{item}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function TrendsPreviewContent({ data }) {
  return (
    <div className="space-y-4">
      <div>
        <p className="text-[11px] text-slate-400">Продукт</p>
        <p className="text-[13px] font-semibold">
          {data.bank_name} · {data.product_type} ({data.period})
        </p>
      </div>

      {/* простой мини-барчарт */}
      <div>
        <p className="text-[11px] text-slate-400 mb-2">Динамика показателя</p>
        <div className="flex items-end gap-1 h-24">
          {data.points.map((p) => (
            <div key={p.label} className="flex-1 flex flex-col items-center">
              <div
                className="w-full rounded-full bg-gradient-to-t from-slate-800 to-brand-400/90"
                style={{ height: `${20 + p.value * 2}%` }}
              />
              <span className="mt-1 text-[9px] text-slate-500">
                {p.label.split(" ")[0]}
              </span>
            </div>
          ))}
        </div>
      </div>

      {data.summary?.length > 0 && (
        <div>
          <p className="text-[11px] text-slate-400 mb-1.5">Резюме</p>
          <ul className="space-y-1.5">
            {data.summary.map((item, idx) => (
              <li key={idx} className="flex gap-2">
                <span className="mt-1 h-1 w-1 rounded-full bg-sky-400" />
                <p className="text-[11px] text-slate-200">{item}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
