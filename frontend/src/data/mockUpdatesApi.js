import { mockUpdates } from "./mockUpdates";

export async function mockGetRecentUpdates(filters = {}) {
  console.log("Mock Recent Updates Request:", filters);

  await new Promise((resolve) => setTimeout(resolve, 500));

  return mockUpdates;
}