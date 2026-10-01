import { useState } from "react";
import { Sparkles, Calendar, Tag } from "lucide-react";
import { analyzeProducts } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { saveReport } from "../services/firestoreReports";

const today = new Date().toISOString().split("T")[0];

const companies = ["Figma", "Canva", "Notion"];

function buildDefaultQuestion(selectedCompanies, category) {
  if (selectedCompanies.length === 0) {
    return "";
  }

  if (selectedCompanies.length === 1) {
    return `Show the recent ${category} developments of ${selectedCompanies[0]}`;
  }

  const companyText = selectedCompanies.join(" and ");

  return `Compare the recent ${category} developments of ${companyText}`;
}

function Compare() {
  const { user } = useAuth();

  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");

  const [selectedCompanies, setSelectedCompanies] = useState([
    "Figma",
    "Canva",
  ]);

  const [category, setCategory] = useState("AI");

  const [question, setQuestion] = useState(
    "Compare the recent AI developments of Figma and Canva"
  );

  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSaveReport = async () => {
    if (!analysis || !user) return;

    try {
      setSaving(true);
      setSaveMessage("");

      await saveReport(
        {
          title: `${selectedCompanies.join(" vs ")} — ${category} Analysis`,
          question,
          companies: selectedCompanies,
          category,
          answer: analysis.answer,
          key_findings: analysis.key_findings || [],
          common_themes: analysis.common_themes || [],
          differences: analysis.differences || [],
          sources: analysis.sources || [],
          analysis_type: analysis.analysis_type || "comparison",
        },
        user.uid
      );

      setSaveMessage("Report saved successfully.");
    } catch (error) {
      console.error(error);
      setSaveMessage("Unable to save the report.");
    } finally {
      setSaving(false);
    }
  };

  const toggleCompany = (company) => {
    let updatedCompanies;

    if (selectedCompanies.includes(company)) {
      updatedCompanies = selectedCompanies.filter(
        (item) => item !== company
      );
    } else if (selectedCompanies.length < 3) {
      updatedCompanies = [...selectedCompanies, company];
    } else {
      return;
    }

    setSelectedCompanies(updatedCompanies);

    // Keep the comparison question synchronized with the selected companies.
    setQuestion(buildDefaultQuestion(updatedCompanies, category));
  };

  const handleCategoryChange = (newCategory) => {
    setCategory(newCategory);

    // Update the default question when category changes.
    setQuestion(
      buildDefaultQuestion(selectedCompanies, newCategory)
    );
  };
  const handleDateFromChange = (value) => {
  setDateFrom(value);

  if (dateTo && value > dateTo) {
    setDateTo(value);
  }
};

const handleDateToChange = (value) => {
  if (dateFrom && value < dateFrom) {
    setError("To Date must be on or after From Date.");
    return;
  }

  setError("");
  setDateTo(value);
};

  const handleAnalyze = async () => {
    if (selectedCompanies.length < 2) {
      setError("Please select at least two companies.");
      return;
    }

    if (!question.trim()) {
      setError("Please enter a comparison question.");
      return;
    }

    setLoading(true);
    setError("");
    setAnalysis(null);

    try {
      const result = await analyzeProducts({
        question,
        companies: selectedCompanies,
        dateFrom,
        dateTo,
        category,
        analysisType: "comparison",
      });

      setAnalysis(result);
    } catch (err) {
      console.error(err);
      setError("Unable to analyze the data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <p className="text-sm text-slate-500 mb-2">
          Competitive Analysis
        </p>

        <h2 className="text-3xl font-bold text-slate-900">
          Compare Products
        </h2>

        <p className="text-slate-500 mt-2">
          Compare recent developments, features and strategic trends.
        </p>
      </div>

      {/* Analysis Controls */}
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-slate-900">
          Select Products
        </h3>

        <p className="text-sm text-slate-500 mt-1">
          Select up to three products for comparison.
        </p>

        {/* Companies */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-5">
          {companies.map((company) => {
            const selected = selectedCompanies.includes(company);

            return (
              <button
                key={company}
                onClick={() => toggleCompany(company)}
                className={`p-4 rounded-xl border text-left transition ${
                  selected
                    ? "border-slate-900 bg-slate-50"
                    : "border-slate-200 hover:border-slate-400"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{company}</span>

                  <div
                    className={`w-4 h-4 rounded-full border ${
                      selected
                        ? "bg-slate-900 border-slate-900"
                        : "border-slate-300"
                    }`}
                  />
                </div>

                <p className="text-xs text-slate-500 mt-2">
                  Digital product
                </p>
              </button>
            );
          })}
        </div>

        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          {/* Date From */}
          <div>
            <label className="text-sm font-medium text-slate-700">
              From Date
            </label>

            <div className="mt-2 flex items-center gap-2 border border-slate-200 rounded-lg px-3 py-2">
              <Calendar size={17} className="text-slate-400" />

              <input
                type="date"
                value={dateFrom} 
                max={dateTo || today}
                onChange={(e) => handleDateFromChange(e.target.value)}
                className="w-full outline-none text-sm"
              />
            </div>
          </div>

          {/* Date To */}
          <div>
            <label className="text-sm font-medium text-slate-700">
              To Date
            </label>

            <div className="mt-2 flex items-center gap-2 border border-slate-200 rounded-lg px-3 py-2">
              <Calendar size={17} className="text-slate-400" />

              <input
                type="date"
                value={dateTo}
                onChange={(e) => handleDateToChange(e.target.value)}
                className="w-full outline-none text-sm"
              />
            </div>
          </div>
        </div>

        {/* Category */}
        <div className="mt-4">
          <label className="text-sm font-medium text-slate-700">
            Category
          </label>

          <div className="mt-2 flex items-center gap-2 border border-slate-200 rounded-lg px-3 py-2">
            <Tag size={17} className="text-slate-400" />

            <select
              value={category}
              onChange={(e) => handleCategoryChange(e.target.value)}
              className="w-full outline-none text-sm bg-transparent"
            >
              <option>AI</option>
              <option>Design</option>
              <option>Collaboration</option>
              <option>Automation</option>
              <option>Security</option>
              <option>Integrations</option>
              <option>Pricing</option>
            </select>
          </div>
        </div>

        {/* Question */}
        <div className="mt-6">
          <label className="text-sm font-medium text-slate-700">
            What do you want to compare?
          </label>

          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Example: Compare the recent AI developments of Figma, Canva and Notion."
            className="w-full mt-2 min-h-28 border border-slate-200 rounded-lg p-3 text-sm outline-none focus:border-slate-400 resize-none"
          />
        </div>

        {/* Error */}
        {error && (
          <p className="text-sm text-red-600 mt-3">
            {error}
          </p>
        )}

        {/* Analyze */}
        <button
          disabled={selectedCompanies.length < 2 || loading}
          onClick={handleAnalyze}
          className="mt-6 flex items-center gap-2 px-5 py-3 bg-slate-900 text-white rounded-lg hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition"
        >
          <Sparkles size={18} />

          {loading ? "Analyzing..." : "Analyze with AI"}
        </button>
      </div>

      {/* Results */}
      {analysis && (
        <div className="mt-6 space-y-6">
          {/* Main Answer */}
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="text-lg font-semibold">
              AI Analysis
            </h3>

            <p className="text-slate-600 mt-3 leading-7">
              {analysis.answer}
            </p>
          </div>

          {/* Key Findings */}
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4">
              Key Findings
            </h3>

            <div className="space-y-4">
              {analysis.key_findings?.map((item) => (
                <div
                  key={item.company}
                  className="border border-slate-200 rounded-lg p-4"
                >
                  <p className="font-semibold">
                    {item.company}
                  </p>

                  <p className="text-sm text-slate-600 mt-1">
                    {item.finding}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Themes + Differences */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white border border-slate-200 rounded-xl p-6">
              <h3 className="font-semibold">
                Common Themes
              </h3>

              <ul className="mt-4 space-y-2">
                {analysis.common_themes?.map((theme) => (
                  <li
                    key={theme}
                    className="text-sm text-slate-600"
                  >
                    • {theme}
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-white border border-slate-200 rounded-xl p-6">
              <h3 className="font-semibold">
                Key Differences
              </h3>

              <ul className="mt-4 space-y-2">
                {analysis.differences?.map((difference) => (
                  <li
                    key={difference}
                    className="text-sm text-slate-600"
                  >
                    • {difference}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Save Report */}
          <button
            onClick={handleSaveReport}
            disabled={saving}
            className="px-4 py-2 rounded-lg bg-slate-900 text-white hover:bg-slate-800 disabled:opacity-50 transition"
          >
            {saving ? "Saving..." : "Save Report"}
          </button>

          {saveMessage && (
            <p className="mt-2 text-sm text-slate-600">
              {saveMessage}
            </p>
          )}

          {/* Sources */}
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold">
              Sources
            </h3>

            <div className="mt-4 space-y-3">
              {analysis.sources?.map((source) => (
                <a
                  key={source.url}
                  href={source.url}
                  target="_blank"
                  rel="noreferrer"
                  className="block border border-slate-200 rounded-lg p-4 hover:bg-slate-50"
                >
                  <p className="font-medium">
                    {source.title}
                  </p>

                  <p className="text-sm text-slate-500 mt-1">
                    {source.company} · {source.published_date}
                  </p>
                </a>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Compare;