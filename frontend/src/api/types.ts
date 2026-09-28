export type SortField =
  | "employee_id"
  | "name"
  | "country"
  | "department"
  | "salary"
  | "updated_at";

export type SortOrder = "asc" | "desc";

export interface Employee {
  employee_id: string;
  name: string;
  country: string;
  department: string;
  salary_amount: string;
  currency: string;
  updated_at: string;
}

export interface EmployeePage {
  items: Employee[];
  total: number;
  page: number;
  page_size: number;
}

export interface EmployeeQuery {
  page: number;
  page_size: number;
  search?: string;
  country?: string;
  department?: string;
  currency?: string;
  sort_by: SortField;
  sort_order: SortOrder;
}

export interface EmployeeCountByCountry {
  country: string;
  employee_count: number;
}

export interface EmployeeCountByDepartment {
  department: string;
  employee_count: number;
}

export interface SalaryDistributionBucket {
  currency: string;
  minimum_salary: string;
  maximum_salary: string;
  employee_count: number;
}

export interface SalaryMetricsByCurrency {
  currency: string;
  employee_count: number;
  average_salary: string;
  median_salary: string;
  minimum_salary: string;
  maximum_salary: string;
  salary_distribution: SalaryDistributionBucket[];
}

export interface CompensationAnalytics {
  employee_count: number;
  employees_by_country: EmployeeCountByCountry[];
  employees_by_department: EmployeeCountByDepartment[];
  salary_by_currency: SalaryMetricsByCurrency[];
}

export interface AnalyticsQuery {
  country?: string;
  department?: string;
  currency?: string;
}