import React from "react";

const FEATURES = [
  {
    title: "Фокус на продуктовых решениях",
    body: "Отчёты построены вокруг вопросов продакта и маркетинга: где мы дороже, где дешевле, какие условия проще коммуницировать"
  },
  {
    title: "Фиксированная схема сравнения",
    body: "Эталонные продукты Сбера и фиксированные поля позволяют сравнивать любые банки между собой без потери смысла"
  },
  {
    title: "Готово к Excel и презентациям",
    body: "Экспорт в XLSX и аккуратная структура таблиц экономят часы ручной перекладки в презентации"
  }
];

export default function FeaturesSection() {
  return (
    <section className="max-w-6xl mx-auto px-4 pb-16">
      <div className="border border-slate-800/80 rounded-3xl bg-slate-950/60 p-5 sm:p-8">
        <h2 className="text-lg sm:text-xl font-semibold mb-4">
          Зачем это банковским командам
        </h2>
        <div className="grid md:grid-cols-3 gap-4 sm:gap-6 text-xs sm:text-sm">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="rounded-2xl border border-slate-800 bg-slate-900/80 p-4"
            >
              <p className="font-medium mb-2 text-slate-50">{f.title}</p>
              <p className="text-slate-300">{f.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
