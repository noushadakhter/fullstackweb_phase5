// frontend/src/app/tasks/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Task } from "@/lib/types";
import { getTasks, createTask, deleteTask, toggleTaskCompletion } from "@/lib/api";
import { isAuthenticated, useAuthStore } from "@/lib/auth";
import TaskCard from "@/components/TaskCard";
import TaskForm from "@/components/TaskForm";

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }

    const fetchTasks = async () => {
      if (!user) {
        // setError("User not authenticated. Please log in.");
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const fetchedTasks = await getTasks(user.id);
        setTasks(fetchedTasks.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()));
      } catch (err: any) {
        setError(err.message || "Failed to fetch tasks.");
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, [router, user]);

  const handleCreateTask = async (taskData: { title: string; description: string }) => {
    if (!user) return;
    try {
      const newTask = await createTask(user.id, taskData);
      setTasks(prevTasks => [newTask, ...prevTasks]);
    } catch (err: any) {
      setError(err.message || "Failed to create task.");
    }
  };

  const handleDeleteTask = async (id: string) => {
    if (!window.confirm("Are you sure you want to delete this task?")) return;
    if (!user) return;
    try {
      await deleteTask(user.id, id);
      setTasks(prevTasks => prevTasks.filter(task => task.id.toString() !== id));
    } catch (err: any) {
      setError(err.message || "Failed to delete task.");
    }
  };

  const handleToggleComplete = async (id: string) => {
    if (!user) return;
    try {
      const updatedTask = await toggleTaskCompletion(user.id, id);
      setTasks(prevTasks => prevTasks.map(task => task.id.toString() === id ? updatedTask : task));
    } catch (err: any) {
      setError(err.message || "Failed to update task status.");
    }
  };

  if (loading) {
    return <div className="text-center mt-8">Loading tasks...</div>;
  }
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
      <div className="md:col-span-1">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold mb-4">Create a New Task</h2>
            <TaskForm onSuccess={handleCreateTask} submitButtonText="Add Task" />
        </div>
      </div>

      <div className="md:col-span-2">
        <h1 className="text-3xl font-bold mb-6">My Tasks</h1>
        {error && <p className="text-red-500 bg-red-100 p-4 rounded-lg mb-4">{error}</p>}
        
        {tasks.length > 0 ? (
          <div className="space-y-4">
            {tasks.map(task => (
              <TaskCard
                key={task.id}
                task={task}
                onDelete={handleDeleteTask}
                onToggleComplete={handleToggleComplete}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 px-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-300">No tasks yet!</h2>
            <p className="text-gray-500 dark:text-gray-400 mt-2">Use the form on the left to add your first task.</p>
          </div>
        )}
      </div>
    </div>
  );
}
