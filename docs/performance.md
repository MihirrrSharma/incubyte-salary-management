# Performance Notes

- Employee directory filtering, counting, ordering, and `LIMIT`/`OFFSET` pagination run in SQL; the browser requests one page rather than downloading the full employee table.
- Indexes cover country, department, and `(currency, salary_minor_units)`; the employee ID primary key supports ID lookup. Name substring search is a simple `LIKE`, appropriate to the assessment dataset unless measurements show otherwise.
- Analytics use SQL filters, grouped counts and salary aggregates. Median retrieval requests only the middle one or two ordered salary values per currency. Distribution bucket counts are also queried in SQL.
- Seeding uses a fixed random seed, stable synthetic IDs and a fixed UTC timestamp. SQLite conflict handling makes repeated runs idempotent for generated IDs.
- Salary metrics and ranges remain grouped by currency. Cross-currency salary arithmetic and FX conversion are not performed.
- The verified Vite build currently warns that the minified JavaScript bundle is about 892 kB, above its 500 kB advisory threshold (about 263 kB gzipped). It is non-blocking; code splitting could be considered if bundle/load measurements justify it.

For a larger production deployment, measure query plans and write concurrency first. Depending on evidence, consider indexed/full-text name search, cursor pagination for heavily changing data, a server database for multiple application instances or higher write concurrency, and frontend bundle splitting. These are not required infrastructure for the current single-instance assessment.