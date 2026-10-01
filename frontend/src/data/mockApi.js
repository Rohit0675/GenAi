import { mockAnalysis } from "./mockData";

export async function mockAnalyzeProducts(request) {
  console.log("Mock Agent Request:", request);

  await new Promise((resolve) => setTimeout(resolve, 1000));

  return {
    ...mockAnalysis,
    companies: request.companies,
  };
}