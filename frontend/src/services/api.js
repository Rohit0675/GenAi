import { mockAnalyzeProducts } from "../data/mockApi";

const USE_MOCK_API =
  import.meta.env.VITE_USE_MOCK_API !== "false";

const API_BASE_URL =
  import.meta.env.VITE_AGENT_API_URL || "http://localhost:8000";
import { mockGetRecentUpdates } from "../data/mockUpdatesApi";
import { mockGetReports } from "../data/mockReportsApi";
export async function analyzeProducts({
  question,
  companies,
  dateFrom,
  dateTo,
  category,
  analysisType = "comparison",
}) {
  const request = {
    question,
    companies,
    date_from: dateFrom,
    date_to: dateTo,
    category,
    analysis_type: analysisType,
  };

  // Development mode
  if (USE_MOCK_API) {
    return mockAnalyzeProducts(request);
  }

  // Real Agent API
  const response = await fetch(
    `${API_BASE_URL}/api/analyze`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    }
  );

  if (!response.ok) {
    throw new Error(
      `Agent API request failed: ${response.status}`
    );
  }

  return response.json();
}

export async function getRecentUpdates({
  companies = [],
  dateFrom = "",
  dateTo = "",
  category = "",
  topK = 20,
} = {}) {
  const request = {
    companies,
    date_from: dateFrom,
    date_to: dateTo,
    category,
    top_k: topK,
  };

  if (USE_MOCK_API) {
    return mockGetRecentUpdates(request);
  }

  const response = await fetch(
    `${API_BASE_URL}/api/updates`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    },
  );

  if (!response.ok) {
    throw new Error(
      `Updates API request failed: ${response.status}`,
    );
  }

  return response.json();
}
export async function getReports() {
  if (USE_MOCK_API) {
    return mockGetReports();
  }

  const response = await fetch(
    `${API_BASE_URL}/api/reports`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    },
  );

  if (!response.ok) {
    throw new Error(
      `Reports API request failed: ${response.status}`,
    );
  }

  return response.json();
}