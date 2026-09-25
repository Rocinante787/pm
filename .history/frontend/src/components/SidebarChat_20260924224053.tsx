import { useState, useRef, useEffect } from "react";
import type { BoardData } from "@/lib/kanban";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
};

type SidebarChatProps = {
  isOpen: boolean;
  onClose: () => void;
  board: BoardData;
  onUpdateBoard: (newBoard: BoardData) => void;
  token?: string | null;
};

export const SidebarChat = ({ isOpen, onClose, board, onUpdateBoard, token }: SidebarChatProps) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "init",
      role: "assistant",
      content: "Hello! I can help you manage your Kanban board. What would you like to do?",
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/ai/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          prompt: userMsg.content,
          board: board,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response from AI");
      }

      const data = await response.json();
      
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.message || "Done.",
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, aiMsg]);
      
      if (data.board_update) {
        onUpdateBoard(data.board_update);
      }
    } catch (error) {
      console.error(error);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I encountered an error while processing your request.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed right-0 top-0 z-50 flex h-full w-[350px] flex-col border-l border-[var(--stroke)] bg-white/95 shadow-2xl backdrop-blur-md transition-all">
      <div className="flex items-center justify-between border-b border-[var(--stroke)] p-4">
        <h2 className="text-lg font-semibold text-[var(--navy-dark)]">AI Assistant</h2>
        <button
          onClick={onClose}
          className="rounded-full p-2 text-[var(--gray-text)] hover:bg-[var(--stroke)] hover:text-[var(--navy-dark)]"
          aria-label="Close Chat"
        >
          ✕
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2 ${
                msg.role === "user"
                  ? "bg-[var(--primary-blue)] text-white rounded-br-sm"
                  : "bg-[var(--stroke)] text-[var(--navy-dark)] rounded-bl-sm"
              }`}
            >
              <p className="text-sm">{msg.content}</p>
            </div>
            <span className="mt-1 text-xs text-[var(--gray-text)]">
              {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        ))}
        {isLoading && (
          <div className="flex items-start">
            <div className="max-w-[85%] rounded-2xl rounded-bl-sm bg-[var(--stroke)] px-4 py-2 text-[var(--navy-dark)]">
              <div className="flex space-x-1">
                <div className="h-2 w-2 animate-bounce rounded-full bg-[var(--accent-yellow)]" style={{ animationDelay: "0ms" }} />
                <div className="h-2 w-2 animate-bounce rounded-full bg-[var(--accent-yellow)]" style={{ animationDelay: "150ms" }} />
                <div className="h-2 w-2 animate-bounce rounded-full bg-[var(--accent-yellow)]" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-[var(--stroke)] p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me to create a card..."
            className="flex-1 rounded-full border border-[var(--stroke)] bg-[var(--surface)] px-4 py-2 text-sm focus:border-[var(--primary-blue)] focus:outline-none"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--secondary-purple)] text-white transition hover:opacity-90 disabled:opacity-50"
          >
            ↑
          </button>
        </form>
      </div>
    </div>
  );
};
