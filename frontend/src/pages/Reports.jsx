import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { Eye, Trash2, X } from "lucide-react";
import { deleteReport, getUserReports } from "../services/firestoreReports";

function Reports() {
  const [selectedReport, setSelectedReport] = useState(null);
  const { user } = useAuth();

  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadReports() {
      if (!user) return;

      try {
        setLoading(true);
        setError("");

        const data = await getUserReports(user.uid);
        setReports(data);
      } catch (err) {
        console.error(err);
        setError("Unable to load your saved reports.");
      } finally {
        setLoading(false);
      }
    }

    loadReports();
  }, [user]);

  const handleDelete = async (reportId) => {
    try {
      await deleteReport(reportId);

      setReports((currentReports) =>
        currentReports.filter((report) => report.id !== reportId),
      );
    } catch (err) {
      console.error(err);
      setError("Unable to delete the report.");
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-6xl">
        <h1 className="text-2xl font-bold text-slate-900">Saved Reports</h1>

        <p className="mt-1 text-sm text-slate-500">
          Reports saved to your account.
        </p>

        {loading && (
          <div className="mt-8 bg-white rounded-xl border border-slate-200 p-6">
            <p className="text-sm text-slate-500">Loading reports...</p>
          </div>
        )}

        {error && (
          <div className="mt-8 bg-red-50 border border-red-200 rounded-xl p-4">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {!loading && !error && reports.length === 0 && (
          <div className="mt-8 bg-white rounded-xl border border-slate-200 p-8 text-center">
            <h2 className="text-lg font-semibold text-slate-900">
              No saved reports yet
            </h2>

            <p className="mt-2 text-sm text-slate-500">
              Run an analysis and save it to see your reports here.
            </p>
          </div>
        )}

        {!loading && reports.length > 0 && (
          <div className="mt-8 space-y-4">
            {reports.map((report) => (
              <div
                key={report.id}
                className="bg-white rounded-xl border border-slate-200 p-6"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-900">
                      {report.title}
                    </h2>

                    <p className="mt-2 text-sm text-slate-600">
                      {report.question}
                    </p>

                    <div className="mt-3 flex flex-wrap gap-2">
                      {report.companies?.map((company) => (
                        <span
                          key={company}
                          className="px-2.5 py-1 bg-slate-100 rounded-full text-xs text-slate-600"
                        >
                          {company}
                        </span>
                      ))}
                    </div>

                    <p className="mt-3 text-xs text-slate-400">
                      {report.category || "General"}
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setSelectedReport(report)}
                      className="flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition"
                    >
                      <Eye size={17} />
                      View
                    </button>

                    <button
                      onClick={() => handleDelete(report.id)}
                      className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
                      title="Delete report"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      {selectedReport && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-6 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-slate-200">
              <div>
                <h2 className="text-xl font-bold text-slate-900">
                  {selectedReport.title}
                </h2>

                <p className="text-sm text-slate-500 mt-1">
                  {selectedReport.category || "General"} ·{" "}
                  {selectedReport.analysis_type || "Analysis"}
                </p>
              </div>

              <button
                onClick={() => setSelectedReport(null)}
                className="p-2 text-slate-400 hover:text-slate-900 rounded-lg"
              >
                <X size={20} />
              </button>
            </div>

            <div className="p-6 space-y-6">
              <div>
                <h3 className="font-semibold text-slate-900">Question</h3>

                <p className="text-sm text-slate-600 mt-2">
                  {selectedReport.question}
                </p>
              </div>

              <div>
                <h3 className="font-semibold text-slate-900">AI Analysis</h3>

                <p className="text-sm text-slate-600 mt-2 leading-7">
                  {selectedReport.answer}
                </p>
              </div>

              {selectedReport.key_findings?.length > 0 && (
                <div>
                  <h3 className="font-semibold text-slate-900">Key Findings</h3>

                  <div className="mt-3 space-y-3">
                    {selectedReport.key_findings.map((item, index) => (
                      <div
                        key={index}
                        className="border border-slate-200 rounded-lg p-4"
                      >
                        <p className="font-medium">{item.company}</p>

                        <p className="text-sm text-slate-600 mt-1">
                          {item.finding}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selectedReport.common_themes?.length > 0 && (
                <div>
                  <h3 className="font-semibold text-slate-900">
                    Common Themes
                  </h3>

                  <ul className="mt-3 space-y-2">
                    {selectedReport.common_themes.map((theme, index) => (
                      <li key={index} className="text-sm text-slate-600">
                        • {theme}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedReport.differences?.length > 0 && (
                <div>
                  <h3 className="font-semibold text-slate-900">
                    Key Differences
                  </h3>

                  <ul className="mt-3 space-y-2">
                    {selectedReport.differences.map((difference, index) => (
                      <li key={index} className="text-sm text-slate-600">
                        • {difference}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedReport.sources?.length > 0 && (
                <div>
                  <h3 className="font-semibold text-slate-900">Sources</h3>

                  <div className="mt-3 space-y-2">
                    {selectedReport.sources.map((source, index) => (
                      <a
                        key={index}
                        href={source.url}
                        target="_blank"
                        rel="noreferrer"
                        className="block border border-slate-200 rounded-lg p-3 hover:bg-slate-50"
                      >
                        <p className="text-sm font-medium">{source.title}</p>

                        <p className="text-xs text-slate-500 mt-1">
                          {source.company} · {source.published_date}
                        </p>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Reports;
