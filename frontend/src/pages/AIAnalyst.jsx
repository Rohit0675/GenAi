import { useState } from "react";
import { Sparkles, Send, Lightbulb } from "lucide-react";
import { analyzeProducts } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { saveReport } from "../services/firestoreReports";

function AIAnalyst() {
  const { user } = useAuth();
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");
  const [question, setQuestion] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const analyzeQuestion = async () => {
  if (!question.trim()) {
    setError("Please enter a question.");
    return;
  }

  setLoading(true);
  setError("");
  setAnalysis(null);

  try {
    const result = await analyzeProducts({
      question,
      companies: ["Figma", "Canva", "Notion"],
      dateFrom: "",
      dateTo: "",
      category: "AI",
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

const handleSaveReport = async () => {
  if (!analysis || !user) return;

  try {
    setSaving(true);
    setSaveMessage("");

    await saveReport(
      {
        title: "AI Analyst — Competitive Intelligence Analysis",
        question,
        companies: ["Figma", "Canva", "Notion"],
        category: "AI",
        answer: analysis.answer,
        key_findings: analysis.key_findings || [],
        common_themes: analysis.common_themes || [],
        differences: analysis.differences || [],
        sources: analysis.sources || [],
        limitations: analysis.limitations || [],
        analysis_type: analysis.analysis_type || "comparison",
      },
      user.uid,
    );

    setSaveMessage("Report saved successfully.");
  } catch (error) {
    console.error(error);
    setSaveMessage("Unable to save the report.");
  } finally {
    setSaving(false);
  }
};

  const exampleQuestions = [
    "Compare recent AI developments in Figma, Canva and Notion.",
    "What are the major product updates from Figma recently?",
    "What common AI trends are visible across these products?",
  ];

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2 text-sm text-slate-500 mb-2">
          <Sparkles size={16} />
          AI Competitive Analyst
        </div>

        <h2 className="text-3xl font-bold text-slate-900">
          Ask the AI Analyst
        </h2>

        <p className="text-slate-500 mt-2">
          Ask questions about product updates, features, AI developments and
          competitive trends.
        </p>
      </div>

      {/* Question Box */}
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <label className="text-sm font-medium text-slate-700">
          Your question
        </label>

        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Example: Compare the recent AI developments of Figma, Canva and Notion."
          className="w-full mt-3 min-h-32 border border-slate-200 rounded-lg p-4 text-sm outline-none focus:border-slate-400 resize-none"
        />

        <button
          onClick={analyzeQuestion}
          disabled={!question.trim() || loading}
          className="mt-4 flex items-center gap-2 px-5 py-3 bg-slate-900 text-white rounded-lg hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition"
        >
          {loading ? (
            "Analyzing..."
          ) : (
            <>
              <Send size={17} />
              Analyze
            </>
          )}
        </button>

        {error && <p className="text-sm text-red-600 mt-3">{error}</p>}
      </div>

      {/* Example Questions */}
      {!analysis && (
        <div className="mt-6">
          <div className="flex items-center gap-2 text-sm font-medium text-slate-700">
            <Lightbulb size={16} />
            Try asking
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-3">
            {exampleQuestions.map((example) => (
              <button
                key={example}
                onClick={() => setQuestion(example)}
                className="text-left bg-white border border-slate-200 rounded-xl p-4 hover:border-slate-400 transition"
              >
                <p className="text-sm text-slate-600">{example}</p>
              </button>
            ))}
          </div>
        </div>
      )}
      <div className="mt-4 flex items-center gap-3">
        <button
          onClick={handleSaveReport}
          disabled={saving}
          className="flex items-center gap-2 px-4 py-2.5 bg-slate-900 text-white rounded-lg hover:bg-slate-800 disabled:opacity-50 transition"
        >
          {saving ? "Saving..." : "Save Report"}
        </button>

        {saveMessage && <p className="text-sm text-slate-600">{saveMessage}</p>}
      </div>

      {/* Results */}
      {analysis && (
        <div className="mt-6 space-y-6">
          {/* Answer */}
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <div className="flex items-center gap-2">
              <Sparkles size={18} />
              <h3 className="text-lg font-semibold">Analysis</h3>
            </div>

            <p className="text-slate-600 mt-4 leading-7">{analysis.answer}</p>
          </div>

          {/* Findings */}
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="text-lg font-semibold">Key Findings</h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-5">
              {analysis.key_findings?.map((item) => (
                <div
                  key={item.company}
                  className="border border-slate-200 rounded-lg p-4"
                >
                  <p className="font-semibold">{item.company}</p>

                  <p className="text-sm text-slate-600 mt-2">{item.finding}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Themes */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white border border-slate-200 rounded-xl p-6">
              <h3 className="font-semibold">Common Themes</h3>

              <div className="mt-4 space-y-2">
                {analysis.common_themes?.map((theme) => (
                  <div key={theme} className="text-sm text-slate-600">
                    • {theme}
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-xl p-6">
              <h3 className="font-semibold">Key Differences</h3>

              <div className="mt-4 space-y-2">
                {analysis.differences?.map((difference) => (
                  <div key={difference} className="text-sm text-slate-600">
                    • {difference}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Limitation */}
          {analysis.limitations?.length > 0 && (
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-5">
              <p className="text-sm font-medium">Note</p>

              <p className="text-sm text-slate-500 mt-1">
                {analysis.limitations[0]}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default AIAnalyst;
