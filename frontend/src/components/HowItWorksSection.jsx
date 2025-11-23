import React from "react";

const STEPS = [
  {
    label: "1",
    title: "Выбираете сценарий",
    body: "Urgent mode — быстрый отчёт по конкретному конкуренту. Trends mode — реконструкция исторических условий."
  },
  {
    label: "2",
    title: "AI собирает и нормализует данные",
    body: "Скрейпинг сайтов, веб-поиск и LLM приводят данные к фиксированной схеме для каждого продукта."
  },
  {
    label: "3",
    title: "Получаете отчёт и инсайты",
    body: "Таблица сравнения, ключевые выводы и готовый файл, который можно сразу нести на встречу."
  }
];

export default function HowItWorksSection() {
  return (
    <section
      id="how-it-works"
      className="max-w-6xl mx-auto px-4 pb-20 text-xs sm:text-sm text-slate-300"
    >
      <h2 className="text-lg sm:text-xl font-semibold mb-4">
        Как это работает
      </h2>
      <div className="grid md:grid-cols-3 gap-4 sm:gap-6">
        {STEPS.map((step) => (
          <div
            key={step.label}
            className="rounded-3xl border border-slate-800 bg-slate-900/80 p-4"
          >
            <div className="flex items-center gap-2 mb-2">
              <div className="h-6 w-6 rounded-full bg-slate-800 flex items-center justify-center text-[11px] font-semibold text-slate-200">
                {step.label}
              </div>
              <p className="font-medium text-slate-50">{step.title}</p>
            </div>
            <p>{step.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
