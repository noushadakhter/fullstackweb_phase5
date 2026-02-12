// frontend/src/app/tasks/[id]/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Task } from "@/lib/types";
import { getTaskById, updateTask } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import TaskForm from "@/components/TaskForm";
import Link from "next/link";

export default function EditTaskPage() {
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const params = useParams();
  const id = params.id as string;

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }

    if (!id) return;

    const fetchTask = async () => {
      try {
        setLoading(true);
        const fetchedTask = await getTaskById(id);
        setTask(fetchedTask);
      } catch (err: any) {
        setError(err.message || "Failed to fetch task.");
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
  }, [id, router]);

  const handleUpdateTask = async (taskData: { title: string, description: string }) => {
    if (!id) return;
    try {
      await updateTask(id, taskData);
      router.push("/tasks");
    } catch (err: any) {
      setError(err.message || "Failed to update task.");
    }
  };

  if (loading) {
    return <div className="text-center mt-8">Loading task...</div>;
  }

  if (error) {
    return <div className="text-center mt-8 text-red-500">{error}</div>;
  }

  return (
    <div>
        <Link href="/tasks" className="text-blue-500 hover:underline mb-6 inline-block">
            &larr; Back to Tasks
        </Link>
        <div className="max-w-xl mx-auto">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
                <h1 className="text-2xl font-bold mb-4">Edit Task</h1>
                {task && (
                <TaskForm
                    task={task}
                    onSuccess={handleUpdateTask}
                    submitButtonText="Update Task"
                />
                )}
            </div>
        </div>
    </div>
  );
}
