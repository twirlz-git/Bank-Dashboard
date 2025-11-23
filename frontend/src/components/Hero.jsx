import React from "react";

export default function Hero() {
  return (
    <section
      id="product"
      className="max-w-6xl mx-auto px-4 pt-10 pb-16 lg:pt-16 lg:pb-20"
    >
      <div className="grid md:grid-cols-[1.1fr,0.9fr] gap-10 items-center">
        {/* Левая колонка — текст и CTA */}
        <div className="space-y-6">
          <p className="inline-flex items-center gap-2 rounded-full border border-emerald-500/40 bg-slate-900/40 px-3 py-1 text-xs text-emerald-300">
            <span className="inline-flex h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            AI-отчёты по банковским продуктам за минуты
          </p>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-semibold tracking-tight">
            Сравнивайте{" "}
            <span className="bg-gradient-to-r from-brand-400 to-emerald-400 bg-clip-text text-transparent">
              банковские продукты
            </span>{" "}
            с помощью AI
          </h1>
          <p className="text-sm sm:text-base text-slate-300 max-w-xl">
            Bank Product Analyzer собирает условия конкурентов, нормализует их
            к эталонным продуктам Сбера и выдаёт понятные отчёты в XLSX и в
            интерфейсе. Всё — за время одной встречи.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 sm:items-center">
            <a
              href="#demo"
              className="inline-flex items-center justify-center px-5 py-2.5 rounded-full bg-brand-500 hover:bg-brand-400 text-slate-950 font-semibold text-sm shadow-soft"
            >
              Запустить тестовый отчёт
            </a>
            <div className="text-xs text-slate-400">
              <div>Без регистрации. Только демо-данные.</div>
              <div>Поддерживаем urgent и trends сценарии.</div>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-4 pt-3 text-xs text-slate-400">
            <div className="flex -space-x-2">
              <div className="h-6 w-6 rounded-full bg-gradient-to-br from-brand-400 to-emerald-400 border border-slate-900" />
              <div className="h-6 w-6 rounded-full bg-slate-600 border border-slate-900" />
              <div className="h-6 w-6 rounded-full bg-slate-500 border border-slate-900" />
            </div>
            <span>Продуктовые, аналитики и маркетинг в одном канвасе.</span>
          </div>
        </div>

        {/* Правая колонка — "карточка отчёта" как у data.to.design */}
        <div className="relative">
          <div className="absolute -inset-4 bg-gradient-to-br from-brand-500/20 via-sky-500/10 to-purple-500/20 blur-3xl opacity-70" />
          <div className="relative rounded-3xl bg-slate-900/70 border border-slate-800/60 shadow-soft p-5 sm:p-6 backdrop-blur">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-xs text-slate-400">Сравнительный отчёт</p>
                <p className="text-sm font-semibold">
                  Сбербанк vs UBank · Кредитная карта
                </p>
              </div>
              <span className="px-2.5 py-1 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-400/40">
                Urgent mode
              </span>
            </div>

            {/* Мини-табличка */}
            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 overflow-hidden">
              <div className="grid grid-cols-3 text-[11px] bg-slate-900/80 border-b border-slate-800">
                <div className="px-3 py-2 text-slate-400">Параметр</div>
                <div className="px-3 py-2 font-medium text-emerald-300">
                  Сбербанк
                </div>
                <div className="px-3 py-2 font-medium text-sky-300">
                  UBank
                </div>
              </div>
              {[
                ["Ставка", "19.9%", "21.5%"],
                ["Обслуживание", "0 ₽", "1 200 ₽"],
                ["Кэшбэк", "до 15%", "до 10%"]
              ].map(([name, sber, comp]) => (
                <div
                  key={name}
                  className="grid grid-cols-3 text-[11px] border-t border-slate-800/80"
                >
                  <div className="px-3 py-2 text-slate-300">{name}</div>
                  <div className="px-3 py-2 text-slate-100">{sber}</div>
                  <div className="px-3 py-2 text-slate-100">{comp}</div>
                </div>
              ))}
            </div>

            {/* Мини-график-тренд (фейк, просто полоски) */}
            <div className="mt-4">
              <p className="text-xs text-slate-400 mb-2">
                Тренд ставки за 6 месяцев
              </p>
              <div className="flex items-end gap-1 h-16">
                {[40, 55, 65, 60, 50, 45, 38].map((h, idx) => (
                  <div
                    key={idx}
                    className="flex-1 rounded-full bg-gradient-to-t from-slate-800 to-brand-400/80"
                    style={{ height: `${h}%` }}
                  />
                ))}
              </div>
            </div>

            <div className="mt-4">
              <p className="text-xs text-slate-400 mb-1">Главный инсайт</p>
              <p className="text-xs text-slate-200">
                Сбер сохраняет конкурентное преимущество по ставке и цене
                обслуживания, конкурент — сильнее в партнёрском кэшбэке.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
