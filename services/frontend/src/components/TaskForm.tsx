// frontend/src/components/TaskForm.tsx
"use client";

import { useState, useEffect } from "react";
import { Task } from "../lib/types";

interface TaskFormProps {
  task?: Task;
  onSuccess: (data: Pick<Task, "title" | "description">) => void;
  submitButtonText?: string;
}

export default function TaskForm({
  task,
  onSuccess,
  submitButtonText = "Create Task",
}: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (task) {
      setTitle(task.title);
      setDescription(task.description);
    }
  }, [task]);

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        setLoading(true);
        onSuccess({ title, description });
        // Don't setLoading(false) here, the parent component
        // will handle the loading state during the API call.
        // Or we can keep it simple for now.
        setLoading(false);
      }}
      className="space-y-4"
    >
      <div>
        <label
          htmlFor="title"
          className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300"
        >
          Title
        </label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          className="w-full px-3 py-2 text-gray-900 bg-gray-50 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
        />
      </div>
      <div>
        <label
          htmlFor="description"
          className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300"
        >
          Description
        </label>
        <textarea
          id="description"
          rows={4}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
          className="w-full px-3 py-2 text-gray-900 bg-gray-50 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
        ></textarea>
      </div>
      
      <button
        type="submit"
        disabled={loading}
        className="w-full px-5 py-3 text-base font-medium text-center text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 disabled:bg-blue-400"
      >
        {loading ? "Submitting..." : submitButtonText}
      </button>
    </form>
  );
}
