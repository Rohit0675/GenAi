import { useEffect, useState } from "react";
import { Calendar, Filter, ExternalLink } from "lucide-react";
import { getRecentUpdates } from "../services/api";

function RecentUpdates() {
  const [company, setCompany] = useState("All");
  const [category, setCategory] = useState("All");

  const [updates, setUpdates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadUpdates = async () => {
      setLoading(true);
      setError("");

      try {
        const result = await getRecentUpdates({
          companies: company === "All" ? [] : [company],
          category: category === "All" ? "" : category,
          topK: 20,
        });

        setUpdates(result);
      } catch (err) {
        console.error(err);
        setError("Unable to load recent updates.");
      } finally {
        setLoading(false);
      }
    };

    loadUpdates();
  }, [company, category]);

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <p className="text-sm text-slate-500 mb-2">
          Product Intelligence
        </p>

        <h2 className="text-3xl font-bold text-slate-900">
          Recent Updates
        </h2>

        <p className="text-slate-500 mt-2">
          Explore recent product developments across tracked companies.
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Filter size={17} />

          <h3 className="font-semibold">
            Filters
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Company */}
          <div>
            <label className="text-sm text-slate-600">
              Company
            </label>

            <select
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              className="w-full mt-2 border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none"
            >
              <option>All</option>
              <option>Figma</option>
              <option>Canva</option>
              <option>Notion</option>
            </select>
          </div>

          {/* Category */}
          <div>
            <label className="text-sm text-slate-600">
              Category
            </label>

            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full mt-2 border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none"
            >
              <option>All</option>
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
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
          <p className="text-sm text-red-600">
            {error}
          </p>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="bg-white border border-slate-200 rounded-xl p-10 text-center">
          <p className="text-sm text-slate-500">
            Loading recent updates...
          </p>
        </div>
      )}

      {/* Updates */}
      {!loading && (
        <div className="space-y-4">
          {updates.map((update) => (
            <div
              key={update.document_id}
              className="bg-white border border-slate-200 rounded-xl p-6 hover:border-slate-300 transition"
            >
              <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                <div className="flex-1">
                  {/* Company + Category */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm font-semibold">
                      {update.company}
                    </span>

                    <span className="text-xs px-2 py-1 rounded-full bg-slate-100 text-slate-600">
                      {update.category}
                    </span>
                  </div>

                  {/* Title */}
                  <h3 className="text-lg font-semibold mt-3">
                    {update.title}
                  </h3>

                  {/* Summary */}
                  <p className="text-sm text-slate-600 mt-2 leading-6">
                    {update.summary}
                  </p>

                  {/* Metadata */}
                  <div className="flex items-center gap-4 mt-4 text-xs text-slate-500">
                    <span className="flex items-center gap-1">
                      <Calendar size={14} />
                      {update.published_date}
                    </span>

                    <span>
                      {update.source_type === "official"
                        ? "Official Source"
                        : update.source_type}
                    </span>
                  </div>
                </div>

                {/* Source */}
                <a
                  href={update.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900"
                >
                  <ExternalLink size={15} />
                  View Source
                </a>
              </div>
            </div>
          ))}

          {updates.length === 0 && (
            <div className="bg-white border border-slate-200 rounded-xl p-10 text-center">
              <p className="text-slate-500">
                No updates match the selected filters.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Demo Notice */}
      <div className="mt-6 bg-slate-50 border border-slate-200 rounded-xl p-4">
        <p className="text-xs text-slate-500">
          Demo data is currently displayed. Updates will later be populated
          automatically through the RAG ingestion pipeline.
        </p>
      </div>
    </div>
  );
}

export default RecentUpdates;