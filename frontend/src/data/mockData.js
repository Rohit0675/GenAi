export const mockAnalysis = {
  answer:
    "The recent updates show that all three platforms are investing in AI-assisted workflows, but their product approaches differ.",

  analysis_type: "comparison",

  companies: ["Figma", "Canva", "Notion"],

  key_findings: [
    {
      company: "Figma",
      finding:
        "Figma is expanding AI-assisted design and workflow capabilities.",
      source_ids: ["figma-001"],
      source_urls: ["https://www.figma.com/blog/"],
    },
    {
      company: "Canva",
      finding:
        "Canva is integrating AI capabilities into its visual content creation workflow.",
      source_ids: ["canva-001"],
      source_urls: ["https://www.canva.com/newsroom/"],
    },
    {
      company: "Notion",
      finding:
        "Notion is using AI to support knowledge management, writing and productivity workflows.",
      source_ids: ["notion-001"],
      source_urls: ["https://www.notion.com/releases"],
    },
  ],

  common_themes: [
    "AI-assisted workflows",
    "Automation",
    "Productivity improvement",
  ],

  differences: [
    "Figma focuses primarily on collaborative design workflows.",
    "Canva focuses heavily on visual content creation.",
    "Notion focuses on knowledge management and productivity.",
  ],

  sources: [
    {
      title: "Figma Updates",
      company: "Figma",
      published_date: "2026-09-20",
      url: "https://www.figma.com/blog/",
    },
    {
      title: "Canva Newsroom",
      company: "Canva",
      published_date: "2026-09-18",
      url: "https://www.canva.com/newsroom/",
    },
    {
      title: "Notion Releases",
      company: "Notion",
      published_date: "2026-09-15",
      url: "https://www.notion.com/releases",
    },
  ],

  limitations: [
    "This is currently demonstration data. Live RAG and Agent integration will be connected later.",
  ],
};