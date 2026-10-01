from app.graph.state import AgentState


def validate_output(state: AgentState) -> AgentState:
    """
    Validate that the final response is grounded in retrieved evidence.
    """

    response = state.get("final_response")
    documents = state.get("retrieved_documents", [])

    errors: list[str] = list(state.get("validation_errors", []))

    if response is None:
        errors.append("No final response was produced.")
        return {
            **state,
            "validation_errors": errors,
        }

    document_map = {
        document.document_id: document
        for document in documents
    }

    source_urls = {
        document.source_url
        for document in documents
    }

    requested_companies = set(state.get("companies", []))

    # Validate companies
    for company in response.companies:
        if requested_companies and company not in requested_companies:
            errors.append(
                f"Response contains unrequested company: {company}"
            )

        # Validate key findings
    for finding in response.key_findings:

        if requested_companies and finding.company not in requested_companies:
            errors.append(
                f"Finding contains unrequested company: {finding.company}"
            )

        if not finding.source_ids:
            errors.append(
                f"Finding for {finding.company} has no source IDs."
            )

        if not finding.source_urls:
            errors.append(
                f"Finding for {finding.company} has no source URLs."
            )

        for source_id in finding.source_ids:
            document = document_map.get(source_id)

            if document is None:
                errors.append(
                    f"Unknown source ID in finding: {source_id}"
                )
                continue

            # Critical grounding check:
            # The source's company must match the finding's company.
            if document.company != finding.company:
                errors.append(
                    f"Company mismatch: finding for {finding.company} "
                    f"uses source {source_id} belonging to {document.company}."
                )

        for source_url in finding.source_urls:
            matching_documents = [
                document
                for document in documents
                if document.source_url == source_url
            ]

            if not matching_documents:
                errors.append(
                    f"Unknown source URL in finding: {source_url}"
                )
                continue

            # Critical grounding check for URLs as well.
            if not any(
                document.company == finding.company
                for document in matching_documents
            ):
                errors.append(
                    f"Company mismatch: finding for {finding.company} "
                    f"uses URL belonging to another company: {source_url}"
                )

    # Validate source list
    for source in response.sources:

        matching_documents = [
            document
            for document in documents
            if document.source_url == source.url
        ]

        if not matching_documents:
            errors.append(
                f"Source URL is not present in retrieved evidence: {source.url}"
            )
            continue

        document = matching_documents[0]

        if source.company != document.company:
            errors.append(
                f"Source company mismatch for URL: {source.url}"
            )


        if source.published_date != document.published_date:
            errors.append(
                f"Source date mismatch for URL: {source.url}"
            )

    return {
        **state,
        "validation_errors": errors,
    }