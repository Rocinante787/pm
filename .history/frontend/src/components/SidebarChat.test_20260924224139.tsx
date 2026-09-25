import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { SidebarChat } from "./SidebarChat";
import { describe, it, expect, vi } from "vitest";
import type { BoardData } from "@/lib/kanban";

const mockBoard: BoardData = {
  columns: [],
  cards: {}
};

describe("SidebarChat", () => {
  it("does not render when isOpen is false", () => {
    render(
      <SidebarChat
        isOpen={false}
        onClose={vi.fn()}
        board={mockBoard}
        onUpdateBoard={vi.fn()}
      />
    );
    expect(screen.queryByText("AI Assistant")).toBeNull();
  });

  it("renders when isOpen is true", () => {
    render(
      <SidebarChat
        isOpen={true}
        onClose={vi.fn()}
        board={mockBoard}
        onUpdateBoard={vi.fn()}
      />
    );
    expect(screen.getByText("AI Assistant")).toBeDefined();
  });

  it("calls onClose when close button is clicked", () => {
    const handleClose = vi.fn();
    render(
      <SidebarChat
        isOpen={true}
        onClose={handleClose}
        board={mockBoard}
        onUpdateBoard={vi.fn()}
      />
    );
    fireEvent.click(screen.getByLabelText("Close Chat"));
    expect(handleClose).toHaveBeenCalled();
  });

  it("handles user input and API call", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        message: "Sure, card added.",
        board_update: { columns: [], cards: { c1: { id: "c1", title: "New", details: "" } } }
      })
    });

    const handleUpdateBoard = vi.fn();

    render(
      <SidebarChat
        isOpen={true}
        onClose={vi.fn()}
        board={mockBoard}
        onUpdateBoard={handleUpdateBoard}
      />
    );

    const input = screen.getByPlaceholderText("Ask me to create a card...");
    fireEvent.change(input, { target: { value: "Add a card" } });
    
    const submitBtn = screen.getByRole("button", { name: "↑" });
    fireEvent.click(submitBtn);

    expect(screen.getByText("Add a card")).toBeDefined();

    await waitFor(() => {
      expect(screen.getByText("Sure, card added.")).toBeDefined();
    });

    expect(handleUpdateBoard).toHaveBeenCalledWith({
      columns: [],
      cards: { c1: { id: "c1", title: "New", details: "" } }
    });
  });
});
