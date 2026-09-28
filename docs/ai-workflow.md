# AI-Assisted Development Workflow

## Purpose

AI assistance was used to accelerate analysis, test-first implementation, review, and refinement of the assessment. Product behavior and constraints came from the committed requirements and architecture; AI suggestions were bounded by those documents and reviewed before acceptance.

## Workflow

Work was divided into reviewable vertical slices: product requirements, architecture, employee directory, salary update, compensation analytics, deterministic seed, and frontend. Prompts named the relevant source documents, the exact slice, prohibited scope, expected tests, and required validation. For backend slices, the instructions explicitly required tests before production code and required the complete backend suite afterward.

Examples of work assisted by AI, as reflected by the repository and commit sequence:

- Inspect requirements and draft the architecture before application implementation.
- Add directory API integration tests, then implement database pagination, search, filters, and allowlisted sorting.
- Add salary validation tests, then implement exact currency-aware conversion and timestamp updates.
- Add analytics tests covering filters, per-currency summaries, medians, and deterministic ranges.
- Add deterministic seed tests for repeatability, valid values, fixed timestamps, and idempotency.
- Build frontend API types, dashboard, directory, salary drawer, and focused interaction tests against the implemented routes.

## Review and Validation

Generated changes were checked against the API schemas/routes, product requirements, and architecture. Automated tests were run after each slice; frontend TypeScript checking and production builds were used to catch integration and contract mismatches. The directory, salary update, and analytics suites use small deterministic fixtures, while seed tests separately verify the default 10,000-row behavior.

The history records incremental commits for requirements, architecture, directory API, salary update, analytics, seed tooling, and frontend. The candidate reviewed the requirements, engineering decisions, tests, and final code; AI output was not treated as authoritative without this review and executable checks.

## Constrained or Rejected Suggestions

- Salary figures were kept grouped by currency; no global average, median, sort, or FX conversion was introduced without a conversion source and requirement.
- A chatbot/LLM product feature, authentication, salary history, approvals, and unrelated infrastructure were excluded because they are outside the assessment scope.
- The documented single-employee GET route is not implemented by the current backend. The frontend uses the complete selected employee row and the salary PATCH response instead of inventing an endpoint or changing backend behavior.
- The architecture stayed as one FastAPI application and one relational database; no service decomposition or extra queue/cache infrastructure was added.

This account summarizes the recorded repository workflow and implementation decisions; it does not reproduce or invent individual prompt transcripts.