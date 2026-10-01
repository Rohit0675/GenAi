import { mockReports } from "./mockReports";

export async function mockGetReports() {
  console.log("Mock Reports Request");

  await new Promise((resolve) => setTimeout(resolve, 500));

  return mockReports;
}