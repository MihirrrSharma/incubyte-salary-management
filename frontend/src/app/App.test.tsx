import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { App } from "./App";
import { ApiError, getCompensationAnalytics, getEmployees, updateEmployeeSalary } from "../api/client";
import type { CompensationAnalytics, Employee, EmployeePage } from "../api/types";

vi.mock("../api/client", () => ({
  ApiError: class ApiError extends Error {
    status: number;

    constructor(message: string, status: number) {
      super(message);
      this.status = status;
    }
  },
  getCompensationAnalytics: vi.fn(),
  getEmployees: vi.fn(),
  updateEmployeeSalary: vi.fn(),
}));

const employee: Employee = {
  employee_id: "E001",
  name: "Alice Morgan",
  country: "US",
  department: "Engineering",
  salary_amount: "85000.00",
  currency: "USD",
  updated_at: "2026-09-28T10:00:00Z",
};

const employeePage: EmployeePage = {
  items: [employee],
  total: 31,
  page: 1,
  page_size: 25,
};

const analytics: CompensationAnalytics = {
  employee_count: 1,
  employees_by_country: [{ country: "US", employee_count: 1 }],
  employees_by_department: [{ department: "Engineering", employee_count: 1 }],
  salary_by_currency: [
    {
      currency: "USD",
      employee_count: 1,
      average_salary: "85000.00",
      median_salary: "85000.00",
      minimum_salary: "85000.00",
      maximum_salary: "85000.00",
      salary_distribution: [
        { currency: "USD", minimum_salary: "85000.00", maximum_salary: "85000.00", employee_count: 1 },
      ],
    },
  ],
};

async function usePeopleView() {
  render(<App />);
  const user = userEvent.setup();
  await user.click(screen.getByRole("tab", { name: /people/i }));
  return user;
}

describe("salary management UI", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(getCompensationAnalytics).mockResolvedValue(analytics);
    vi.mocked(getEmployees).mockResolvedValue(employeePage);
    vi.mocked(updateEmployeeSalary).mockResolvedValue({ ...employee, salary_amount: "92000.50" });
  });

  it("renders returned employees in the directory table", async () => {
    await usePeopleView();

    expect(await screen.findByText("Alice Morgan")).toBeInTheDocument();
    expect(screen.getByText("85000.00")).toBeInTheDocument();
    expect(screen.getByRole("table", { name: "Employee directory" })).toBeInTheDocument();
  });

  it("sends search and filters to the employee API", async () => {
    const user = await usePeopleView();
    await user.type(screen.getByRole("textbox", { name: "Search employee ID or name" }), "Alice");
    await user.type(screen.getByRole("textbox", { name: "Country filter" }), "US");
    await user.type(screen.getByRole("textbox", { name: "Department filter" }), "Engineering");

    await waitFor(() => {
      expect(getEmployees).toHaveBeenLastCalledWith(
        expect.objectContaining({
          page: 1,
          search: "Alice",
          country: "US",
          department: "Engineering",
        }),
      );
    });
  });

  it("requests the next server page when pagination changes", async () => {
    const user = await usePeopleView();
    await screen.findByText("Alice Morgan");
    await user.click(screen.getByRole("button", { name: "Go to next page" }));

    await waitFor(() => {
      expect(getEmployees).toHaveBeenLastCalledWith(expect.objectContaining({ page: 2 }));
    });
  });

  it("submits the edited salary value for the selected employee", async () => {
    const user = await usePeopleView();
    await user.click(await screen.findByRole("button", { name: "Open employee E001" }));
    const salaryInput = await screen.findByRole("textbox", { name: "Annual salary" });
    await user.clear(salaryInput);
    await user.type(salaryInput, "92000.50");
    await user.click(screen.getByRole("button", { name: "Save salary" }));

    await waitFor(() => {
      expect(updateEmployeeSalary).toHaveBeenCalledWith("E001", "92000.50");
    });
    expect(await screen.findByText("Salary updated successfully.")).toBeInTheDocument();
  });

  it("displays API errors in the directory view", async () => {
    vi.mocked(getEmployees).mockRejectedValueOnce(new ApiError("Service is unavailable", 503));
    await usePeopleView();

    expect(await screen.findByText("Service is unavailable")).toBeInTheDocument();
    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(within(screen.getByRole("alert")).getByRole("button", { name: "Retry" })).toBeInTheDocument();
  });
});