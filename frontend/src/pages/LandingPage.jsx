import React from "react";
import Layout from "../components/Layout";
import Hero from "../components/Hero";
import ModesTabs from "../components/ModesTabs";
import UrgentForm from "../components/UrgentForm";
import TrendsForm from "../components/TrendsForm";
import OutputPreview from "../components/OutputPreview";
import FeaturesSection from "../components/FeaturesSection";
import HowItWorksSection from "../components/HowItWorksSection";
import Footer from "../components/Footer";
import { createUrgentReport, createTrendsReport } from "../lib/api";

export default function LandingPage() {
  const [activeMode, setActiveMode] = React.useState("urgent");
  const [urgentResult, setUrgentResult] = React.useState(null);
  const [trendsResult, setTrendsResult] = React.useState(null);
  const [loadingUrgent, setLoadingUrgent] = React.useState(false);
  const [loadingTrends, setLoadingTrends] = React.useState(false);
  const [error, setError] = React.useState(null);

  const handleModeChange = (mode) => {
    setActiveMode(mode);
    setError(null);
  };

  const handleUrgentSubmit = async (payload) => {
    try {
      setError(null);
      setLoadingUrgent(true);
      const data = await createUrgentReport(payload);
      setUrgentResult(data);
    } catch (err) {
      setError(err.message || "Ошибка при генерации отчёта");
    } finally {
      setLoadingUrgent(false);
    }
  };

  const handleTrendsSubmit = async (payload) => {
    try {
      setError(null);
      setLoadingTrends(true);
      const data = await createTrendsReport(payload);
      setTrendsResult(data);
    } catch (err) {
      setError(err.message || "Ошибка при построении трендов");
    } finally {
      setLoadingTrends(false);
    }
  };

  const loading = activeMode === "urgent" ? loadingUrgent : loadingTrends;

  return (
    <Layout>
      <Hero />

      <section id="demo" className="max-w-6xl mx-auto px-4 pb-16">
        <div className="flex items-center justify-between gap-3 mb-4">
          <div>
            <p className="text-xs text-slate-400">Демо-сценарии</p>
            <h2 className="text-lg sm:text-xl font-semibold">
              Попробуйте urgent и trends на демо-данных
            </h2>
          </div>
          <ModesTabs activeMode={activeMode} onChange={handleModeChange} />
        </div>

        <div className="grid md:grid-cols-[minmax(0,1.1fr),minmax(0,0.9fr)] gap-5 lg:gap-7 items-start">
          {activeMode === "urgent" ? (
            <UrgentForm onSubmit={handleUrgentSubmit} loading={loadingUrgent} />
          ) : (
            <TrendsForm
              onSubmit={handleTrendsSubmit}
              loading={loadingTrends}
            />
          )}
          <OutputPreview
            activeMode={activeMode}
            urgentResult={urgentResult}
            trendsResult={trendsResult}
            loading={loading}
            error={error}
          />
        </div>
      </section>

      <FeaturesSection />
      <HowItWorksSection />
      <Footer />
    </Layout>
  );
}
