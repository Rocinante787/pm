import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { KanbanBoard } from "@/components/KanbanBoard";
import { initialData } from "@/lib/kanban";

vi.mock("@/lib/api", () => ({
  fetchBoard: vi.fn(() => Promise.resolve(initialData)),
  saveBoard: vi.fn((board) => Promise.resolve(board)),
  resetBoard: vi.fn(() => Promise.resolve(initialData)),
}));

const getFirstColumn = () => screen.getAllByTestId(/column-/i)[0];

describe("KanbanBoard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders five columns", () => {
    render(<KanbanBoard />);
    expect(screen.getAllByTestId(/column-/i)).toHaveLength(5);
  });

  it("renames a column", async () => {
    render(<KanbanBoard />);
    const column = await screen.findByTestId("column-col-backlog");
    const input = within(column).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    expect(input).toHaveValue("New Name");
  });

  it("adds and removes a card", async () => {
    render(<KanbanBoard />);
    const column = await screen.findByTestId("column-col-backlog");
    const addButton = within(column).getByRole("button", {
      name: /add a card/i,
    });
    await userEvent.click(addButton);

    const titleInput = within(column).getByPlaceholderText(/card title/i);
    await userEvent.type(titleInput, "New card");
    const detailsInput = within(column).getByPlaceholderText(/details/i);
    await userEvent.type(detailsInput, "Notes");

    await userEvent.click(within(column).getByRole("button", { name: /add card/i }));

    expect(within(column).getByText("New card")).toBeInTheDocument();

    const deleteButton = within(column).getByRole("button", {
      name: /delete new card/i,
    });
    await userEvent.click(deleteButton);

    expect(within(column).queryByText("New card")).not.toBeInTheDocument();
  });

  it("renders user information and triggers sign out", async () => {
    const handleLogout = vi.fn();
    render(
      <KanbanBoard
        user={{ username: "user", name: "Demo User", token: "tok" }}
        onLogout={handleLogout}
      />
    );

    expect(screen.getByText(/Demo User/i)).toBeInTheDocument();
    const logoutBtn = screen.getByRole("button", { name: /sign out/i });
    expect(logoutBtn).toBeInTheDocument();
    await userEvent.click(logoutBtn);
    expect(handleLogout).toHaveBeenCalledTimes(1);
  });

  it("calls resetBoard when Reset Board button is clicked", async () => {
    const { resetBoard } = await import("@/lib/api");
    render(<KanbanBoard />);
    const resetBtn = screen.getByRole("button", { name: /reset board/i });
    await userEvent.click(resetBtn);
    expect(resetBoard).toHaveBeenCalled();
  });
});
