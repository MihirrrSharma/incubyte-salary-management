# Salary Management — Product Requirements

## Goal

Build a web-based salary management application for ACME's HR Manager to replace spreadsheet-based salary management for approximately 10,000 employees across multiple countries.

The product should make it easy to search and update employee salary information and provide useful visibility into how compensation is distributed across the organization.

## Scope

### 1. Employee Directory

* View all employees in a searchable, paginated table.
* Search by employee ID or name.
* Filter by country and department.
* Sort by salary and employee attributes.
* View an individual employee's details.

### 2. Salary Management

* Display each employee's current annual salary and currency.
* Allow the HR Manager to update an employee's salary.
* Validate salary values and prevent invalid/negative amounts.
* Record the last updated timestamp.

### 3. Compensation Insights

Provide summary information that helps the HR Manager understand organizational compensation, including:

* Total employee count.
* Average salary.
* Median salary.
* Minimum and maximum salary.
* Employee counts by country.
* Employee counts by department.
* Salary distribution/ranges.

Analytics should respect relevant filters where practical so the HR Manager can compare subsets of employees.

## Deliberately Out of Scope

The following are intentionally excluded from this version:

* Payroll processing and salary payment.
* Tax calculation and statutory compliance.
* Employee self-service access.
* Authentication/SSO/role management beyond the assumed HR Manager persona.
* Performance management and compensation planning workflows.
* Benefits and non-salary compensation.
* Multi-step salary approval workflows.
* Full salary-history/audit-management workflows.
* Natural-language/LLM salary questions.

The assessment asks the system to help HR answer questions about compensation, but it does not define a natural-language interface or require an LLM feature. A structured dashboard, filtering, search, and analytics provide this capability with significantly less complexity and clearer correctness.

## Product / Engineering Decisions

* Treat the HR Manager as the primary user and optimize the application for fast search, updates, and analysis.
* Use a relational data model because employee and salary information is structured and requires filtering and aggregation.
* Support multiple currencies as employee data is distributed across countries. Salary amounts are stored in the employee's local currency; the first version will not perform foreign-exchange normalization because no FX source or comparison requirement is defined.
* Use pagination for employee lists rather than loading all 10,000 records into the browser.
* Keep the architecture simple and modular so additional capabilities such as authentication, salary history, approvals, or normalized cross-currency analytics can be added later.

## Success Criteria

The delivered application should:

1. Be fully functional end-to-end.
2. Seed approximately 10,000 deterministic employees.
3. Allow HR to search, filter, inspect, and update salary data.
4. Provide useful compensation insights.
5. Include meaningful, fast, deterministic automated tests.
6. Be maintainable and understandable by another engineer.
7. Be deployable and accompanied by a short demo/video.
