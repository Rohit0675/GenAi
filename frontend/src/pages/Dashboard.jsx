import { useNavigate } from "react-router-dom";
function Dashboard() {
  const navigate = useNavigate();
  return (
    <div className="p-8">
      
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-slate-900">
          Competitive Intelligence
        </h2>

        <p className="text-slate-500 mt-2">
          Monitor product updates, features and AI developments.
        </p>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">

        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <p className="text-sm text-slate-500">
            Companies Tracked
          </p>
          <p className="text-3xl font-bold mt-2">
            3
          </p>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <p className="text-sm text-slate-500">
            Recent Updates
          </p>
          <p className="text-3xl font-bold mt-2">
            24
          </p>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <p className="text-sm text-slate-500">
            AI Developments
          </p>
          <p className="text-3xl font-bold mt-2">
            12
          </p>
        </div>

      </div>

      {/* Welcome */}
      <div className="mt-8 bg-white border border-slate-200 rounded-xl p-6">
        <h3 className="text-lg font-semibold">
          Start your analysis
        </h3>

        <p className="text-slate-500 mt-2">
          Compare companies, explore recent product updates,
          or ask the AI Analyst a competitive intelligence question.
        </p>

        <button 
        onClick={() => navigate("/analyst")}
        className="mt-5 px-5 py-2.5 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition">
          Start Analysis
        </button>
      </div>

    </div>
  );
}

export default Dashboard;