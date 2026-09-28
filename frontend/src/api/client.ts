import type {
  AnalyticsQuery,
  CompensationAnalytics,
  Employee,
  EmployeePage,
  EmployeeQuery,
} from "./types";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function readableValidationErrors(details: unknown): string | undefined {
  if (!Array.isArray(details)) return undefined;
  const messages = details
    .map((item) => {
      if (!item || typeof item !== "object" || !("msg" in item)) return undefined;
      return String(item.msg).replace(/^Value error,\s*/i, "");
    })
    .filter((message): message is string => Boolean(message));
  return messages.length ? messages.join("; ") : undefined;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        Accept: "application/json",
        ...(init?.body ? { "Content-Type": "application/json" } : {}),
        ...init?.headers,
      },
    });
  } catch {
    throw new ApiError("Could not connect to the salary service. Check that it is running and try again.", 0);
  }

  if (!response.ok) {
    let message = "The request could not be completed. Please try again.";
    try {
      const body: unknown = await response.json();
      if (body && typeof body === "object" && "detail" in body) {
        const detail = body.detail;
        if (typeof detail === "string") message = detail;
        else message = readableValidationErrors(detail) ?? message;
      }
    } catch {
      // Keep the generic message when an error response has no JSON body.
    }
    throw new ApiError(message, response.status);
  }
  return response.json() as Promise<T>;
}

function queryString(values: Record<string, string | number | undefined>): string {
  const parameters = new URLSearchParams();
  for (const [key, value] of Object.entries(values)) {
    if (value !== undefined && value !== "") parameters.set(key, String(value));
  }
  const encoded = parameters.toString();
  return encoded ? `?${encoded}` : "";
}

export function getEmployees(query: EmployeeQuery): Promise<EmployeePage> {
  return request<EmployeePage>(
    `/api/employees${queryString({ ...query })}`,
  );
}

export function getCompensationAnalytics(
  query: AnalyticsQuery,
): Promise<CompensationAnalytics> {
  return request<CompensationAnalytics>(
    `/api/analytics/compensation${queryString({
      country: query.country,
      department: query.department,
      currency: query.currency,
    })}`,
  );
}

export function updateEmployeeSalary(
  employeeId: string,
  salaryAmount: string,
): Promise<Employee> {
  return request<Employee>(
    `/api/employees/${encodeURIComponent(employeeId)}/salary`,
    {
      method: "PATCH",
      body: JSON.stringify({ salary_amount: salaryAmount }),
    },
  );
}