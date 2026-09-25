import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { LoginForm } from "@/components/LoginForm";

describe("LoginForm", () => {
  it("renders username and password inputs and sign-in button", () => {
    render(<LoginForm onSuccess={vi.fn()} />);
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
  });

  it("shows an error when submitting invalid credentials", async () => {
    const handleSuccess = vi.fn();
    render(<LoginForm onSuccess={handleSuccess} />);

    await userEvent.type(screen.getByLabelText(/username/i), "invalid");
    await userEvent.type(screen.getByLabelText(/password/i), "wrongpass");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Invalid username or password");
    expect(handleSuccess).not.toHaveBeenCalled();
  });

  it("calls onSuccess with valid credentials", async () => {
    const handleSuccess = vi.fn();
    render(<LoginForm onSuccess={handleSuccess} />);

    await userEvent.type(screen.getByLabelText(/username/i), "user");
    await userEvent.type(screen.getByLabelText(/password/i), "password");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(handleSuccess).toHaveBeenCalledWith(
      expect.objectContaining({
        username: "user",
        name: "Demo User",
      })
    );
  });
});

