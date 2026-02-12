"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/auth";
import api from "@/lib/api";

interface Todo {
  id: number;
  content: string;
  is_completed: boolean;
}

interface ChatMessage {
  id: number;
  sender: "user" | "bot";
  text: string;
}

export default function DashboardPage() {
  const { isLoggedIn: isAuthenticated, logout, user } = useAuthStore();
  const userEmail = user?.email || null;
  const router = useRouter();
  const [todos, setTodos] = useState<Todo[]>([]);
  const [chatInput, setChatInput] = useState<string>("");
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      fetchTodos(); // Fetch todos on initial load if authenticated
    }
  }, [isAuthenticated]);

  const fetchTodos = async () => {
    try {
      setLoading(true);
      const response = await api.get("/tasks");
      setTodos(response.data);
      setError(null);
    } catch (err: any) {
      console.error("Failed to fetch todos:", err);
      setError(err.response?.data?.detail || "Failed to fetch tasks.");
    } finally {
      setLoading(false);
    }
  };

  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMessage: ChatMessage = { id: chatHistory.length + 1, sender: "user", text: chatInput };
    setChatHistory((prev) => [...prev, userMessage]);
    setChatInput("");
    setError(null);
    setLoading(true);

    try {
      const response = await api.post("/chat", { content: chatInput });
      const botResponse: ChatMessage = { id: chatHistory.length + 2, sender: "bot", text: response.data.response };
      setChatHistory((prev) => [...prev, botResponse]);
      setTodos(response.data.tasks); // Update todos from bot response
    } catch (err: any) {
      console.error("Chat error:", err);
      setError(err.response?.data?.detail || "Error communicating with chatbot.");
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return <div className="text-center p-4">Redirecting to login...</div>;
  }

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <header className="bg-white shadow p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">Welcome, {userEmail}!</h1>
        <button
          onClick={logout}
          className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 focus:outline-none"
        >
          Logout
        </button>
      </header>

      <main className="flex flex-grow p-4 space-x-4">
        {/* Chat Section */}
        <div className="flex-1 bg-white rounded-lg shadow-md flex flex-col">
          <div className="p-4 border-b text-lg font-semibold">Chat with Todo Bot</div>
          <div className="flex-grow p-4 overflow-y-auto space-y-4">
            {chatHistory.length === 0 && (
              <p className="text-center text-gray-500">Say something like "add task: buy milk" or "show tasks"</p>
            )}
            {chatHistory.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-xs px-4 py-2 rounded-lg ${
                    msg.sender === "user"
                      ? "bg-blue-500 text-white"
                      : "bg-gray-200 text-gray-800"
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}
            {loading && <div className="text-center text-gray-500">Bot is typing...</div>}
          </div>
          <form onSubmit={handleChatSubmit} className="p-4 border-t flex space-x-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              className="flex-grow px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Type your command..."
              disabled={loading}
            />
            <button
              type="submit"
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none"
              disabled={loading}
            >
              Send
            </button>
          </form>
        </div>

        {/* Todo List Section */}
        <div className="w-1/3 bg-white rounded-lg shadow-md flex flex-col">
          <div className="p-4 border-b text-lg font-semibold">Your Tasks</div>
          <div className="flex-grow p-4 overflow-y-auto space-y-2">
            {error && <p className="text-red-500 text-center">{error}</p>}
            {todos.length === 0 && !loading && (
              <p className="text-gray-500 text-center">No tasks yet!</p>
            )}
            {todos.map((todo) => (
              <div
                key={todo.id}
                className={`p-3 border rounded-md flex items-center justify-between ${
                  todo.is_completed ? "bg-green-100 border-green-300" : "bg-gray-50 border-gray-200"
                }`}
              >
                <span className={`${todo.is_completed ? "line-through text-gray-500" : ""}`}>
                  {todo.id}. {todo.content}
                </span>
                {/* No direct action buttons here, actions are via chat */}
              </div>
            ))}
          </div>
          <div className="p-4 border-t text-sm text-gray-500">
            Manage tasks through the chat interface.
          </div>
        </div>
      </main>
    </div>
  );
}
