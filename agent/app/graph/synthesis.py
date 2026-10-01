import json

from app.graph.state import AgentState
from app.schemas import AnalyzeResponse
from app.utils.llm import extract_text, get_llm


def synthesize_response(state: AgentState) -> AgentState:
    """
    Synthesize a final evidence-grounded response.

    The LLM performs the analysis, while source attribution is
    deterministically rebuilt from the retrieved documents so that
    the final response cannot omit sources that support findings.
    """

    documents = state.get("retrieved_documents", [])
    requested_companies = state.get("companies", [])
    evaluation = state.get("evidence_evaluation")

    print(
        "DEBUG DOCUMENT COMPANIES:",
        [doc.company for doc in documents],
    )
    print(
        "DEBUG REQUESTED COMPANIES:",
        requested_companies,
    )
    print(
        "DEBUG EVALUATION:",
        evaluation,
    )

    # ---------------------------------------------------------
    # No evidence
    # ---------------------------------------------------------

    if not documents:
        return {
            **state,
            "final_response": None,
            "validation_errors": [
                *state.get("validation_errors", []),
                "No evidence available for synthesis.",
            ],
        }

    # ---------------------------------------------------------
    # Insufficient evidence
    # ---------------------------------------------------------

    if evaluation is not None and evaluation.sufficient is False:
        missing = evaluation.missing_information

        return {
            **state,
            "final_response": AnalyzeResponse(
                answer=(
                    "A complete analysis could not be performed because "
                    "sufficient evidence was not available for all requested "
                    "companies."
                ),
                analysis_type=state["analysis_type"],
                companies=requested_companies,
                key_findings=[],
                common_themes=[],
                differences=[],
                sources=[
                    {
                        "title": doc.title,
                        "company": doc.company,
                        "published_date": doc.published_date,
                        "url": doc.source_url,
                    }
                    for doc in documents
                ],
                limitations=missing or [
                    "Retrieved evidence was insufficient for the requested analysis."
                ],
            ),
        }

    # ---------------------------------------------------------
    # Prepare evidence for LLM
    # ---------------------------------------------------------

    source_data = [
        {
            "document_id": doc.document_id,
            "title": doc.title,
            "company": doc.company,
            "published_date": str(doc.published_date),
            "url": doc.source_url,
            "content": doc.content,
        }
        for doc in documents
    ]

    prompt = f"""
You are a Competitive Intelligence Agent.

QUESTION:
{state["question"]}

ANALYSIS TYPE:
{state["analysis_type"]}

REQUESTED COMPANIES:
{json.dumps(requested_companies)}

DATE RANGE:
{state.get("date_from")} to {state.get("date_to")}

CATEGORY:
{state.get("category") or "Not specified"}

SUPPLIED EVIDENCE:
{json.dumps(source_data, ensure_ascii=False)}


Return ONLY valid JSON.

The JSON MUST have exactly this structure:

{{
  "answer": "string",
  "analysis_type": "{state["analysis_type"]}",
  "companies": ["company name"],
  "key_findings": [
    {{
      "company": "company name",
      "finding": "evidence-based finding",
      "source_ids": ["exact_document_id"],
      "source_urls": ["exact_source_url"]
    }}
  ],
  "common_themes": [
    "string"
  ],
  "differences": [
    "string"
  ],
  "sources": [
    {{
      "title": "exact supplied title",
      "company": "exact supplied company",
      "published_date": "YYYY-MM-DD",
      "url": "exact supplied URL"
    }}
  ],
  "limitations": [
    "string"
  ]
}}


STRICT RULES:

1. Use ONLY the supplied evidence.
2. Do not use prior knowledge.
3. Never invent facts, companies, dates, features, statistics, sources,
   URLs, document IDs, or product updates.
4. Every factual key finding MUST contain at least one exact source_id
   and exact source_url from the supplied evidence.
5. source_ids and source_urls MUST correspond to the same evidence.
6. The companies field MUST contain company-name strings only.
7. key_findings MUST contain objects only.
8. common_themes MUST contain strings only.
9. differences MUST contain strings only.
10. sources MUST contain source objects only.
11. limitations MUST contain strings only.
12. Do not create nested or alternative JSON structures.
13. Do not use markdown.
14. Return JSON only.

ANALYSIS RULES:

- Analyze the evidence rather than merely listing it.
- Produce useful findings for every requested company for which relevant
  evidence exists.
- For comparison analysis, compare the actual retrieved evidence across
  companies.
- Only identify a common theme when the supplied evidence genuinely
  supports it.
- Only identify a difference when the supplied evidence genuinely
  supports a comparison.
- Every difference MUST explicitly involve information about at least
  two requested companies.
- Do not turn a company-specific product restriction into a difference
  unless it is explicitly supported as a comparison.
- Do not make unsupported market predictions or judgments.

SOURCE RULES:

- The sources array must contain sources actually used in the findings.
- Use the exact supplied title, company, date, and URL.
- Never invent or modify a source.
- If a finding cites a source, that source must exist in the supplied
  evidence.
- If evidence exists for a requested company, do not claim that the
  company's other reports, products, features, or updates are
  unavailable simply because they were not retrieved.

LIMITATION RULES:

- Limitations must describe genuine limitations of the retrieved evidence
  or analysis.
- Do NOT create limitations based merely on the absence of a particular
  feature, report, or product from the retrieved evidence.
- Do NOT state that a document, report, feature, update, or source does
  not exist unless the supplied evidence explicitly establishes this.
- Absence from retrieved evidence does NOT prove non-existence.
- Do not use limitations to make unsupported negative claims.

CRITICAL MISSING-EVIDENCE RULE:

- If a requested company has NO retrieved evidence, do not create
  findings for that company.
- If a comparison cannot be completed because a requested company has no
  evidence, state that clearly in the answer.
- In that situation, common_themes MUST be [].
- In that situation, differences MUST be [].
- The missing company may be mentioned in limitations as an evidence
  limitation.
- Never use prior knowledge to fill missing evidence.
"""

    print(
        "DEBUG SYNTHESIS EVALUATION SUFFICIENT:",
        evaluation.sufficient if evaluation else None,
    )

    # ---------------------------------------------------------
    # LLM synthesis
    # ---------------------------------------------------------

    try:
        llm = get_llm()

        response = llm.invoke(prompt)
        raw_output = extract_text(response)

        print("DEBUG LLM OUTPUT:")
        print(raw_output)

        data = json.loads(raw_output)

        if not isinstance(data, dict):
            raise ValueError("LLM output must be a JSON object.")

        # -----------------------------------------------------
        # Normalize basic fields
        # -----------------------------------------------------

        data["analysis_type"] = state["analysis_type"]
        data["companies"] = requested_companies

        if not isinstance(data.get("key_findings"), list):
            data["key_findings"] = []

        if not isinstance(data.get("common_themes"), list):
            data["common_themes"] = []

        if not isinstance(data.get("differences"), list):
            data["differences"] = []

        # -----------------------------------------------------
        # Normalize findings
        # -----------------------------------------------------

        normalized_findings = []

        valid_document_map = {
            doc.document_id: doc
            for doc in documents
        }

        valid_url_map = {
            doc.source_url: doc
            for doc in documents
        }

        for finding in data["key_findings"]:
            if not isinstance(finding, dict):
                continue

            company = finding.get("company")
            text = finding.get("finding")

            if not company or not text:
                continue

            source_ids = finding.get("source_ids", [])
            source_urls = finding.get("source_urls", [])

            if not isinstance(source_ids, list):
                source_ids = []

            if not isinstance(source_urls, list):
                source_urls = []

                        # Keep only exact evidence references that belong
            # to the company named in this finding.
            company_documents = {
                doc.document_id: doc
                for doc in documents
                if doc.company.casefold() == str(company).casefold()
            }

            company_urls = {
                doc.source_url: doc
                for doc in documents
                if doc.company.casefold() == str(company).casefold()
            }

            source_ids = [
                source_id
                for source_id in source_ids
                if isinstance(source_id, str)
                and source_id in company_documents
            ]

            source_urls = [
                source_url
                for source_url in source_urls
                if isinstance(source_url, str)
                and source_url in company_urls
            ]

            # If the LLM cited the wrong company's source,
            # recover the source from the retrieved evidence
            # for the same company.
            if not source_ids and company_documents:
                source_ids = [
                    next(iter(company_documents.keys()))
                ]

            if not source_urls and company_urls:
                source_urls = [
                    next(iter(company_urls.keys()))
                ]

            # A factual finding without company-matching
            # evidence is not allowed.
            if not source_ids or not source_urls:
                continue

            # A factual finding without evidence is not allowed.
            if not source_ids or not source_urls:
                continue

            normalized_findings.append(
                {
                    "company": company,
                    "finding": str(text),
                    "source_ids": source_ids,
                    "source_urls": source_urls,
                }
            )

        data["key_findings"] = normalized_findings

        # -----------------------------------------------------
        # Normalize themes and differences
        # -----------------------------------------------------

        data["common_themes"] = [
            str(item)
            for item in data["common_themes"]
            if isinstance(item, str)
        ]

        data["differences"] = [
            str(item)
            for item in data["differences"]
            if isinstance(item, str)
        ]

        # -----------------------------------------------------
        # Rebuild sources deterministically
        #
        # This prevents the LLM from forgetting a source such
        # as the Notion source even when it correctly cites it
        # inside key_findings.
        # -----------------------------------------------------

        used_document_ids = set()
        used_urls = set()

        for finding in normalized_findings:
            used_document_ids.update(finding["source_ids"])
            used_urls.update(finding["source_urls"])

        rebuilt_sources = []

        for doc in documents:
            if (
                doc.document_id in used_document_ids
                or doc.source_url in used_urls
            ):
                rebuilt_sources.append(
                    {
                        "title": doc.title,
                        "company": doc.company,
                        "published_date": doc.published_date,
                        "url": doc.source_url,
                    }
                )

        data["sources"] = rebuilt_sources

        # -----------------------------------------------------
        # Clean limitations
        # -----------------------------------------------------

        limitations = data.get("limitations", [])

        if not isinstance(limitations, list):
            limitations = []

        cleaned_limitations = []

        for item in limitations:
            if isinstance(item, str):
                cleaned_limitations.append(item)
            elif isinstance(item, dict):
                text = item.get("finding")
                if text:
                    cleaned_limitations.append(str(text))

        data["limitations"] = cleaned_limitations

        # -----------------------------------------------------
        # Validate final response
        # -----------------------------------------------------

        final_response = AnalyzeResponse.model_validate(data)

    except Exception as exc:
        return {
            **state,
            "final_response": None,
            "validation_errors": [
                *state.get("validation_errors", []),
                f"Structured synthesis validation failed: {exc}",
            ],
        }

    return {
        **state,
        "final_response": final_response,
    }