// frontend/src/components/TaskCard.tsx
"use client";

import Link from "next/link";
import { Task } from "../lib/types";

interface TaskCardProps {
  task: Task;
  onToggleComplete: (id: string) => void;
  onDelete: (id: string) => void;
}

export default function TaskCard({ task, onToggleComplete, onDelete }: TaskCardProps) {
  return (
    <div className={`p-4 rounded-lg shadow-md transition-colors ${task.completed ? 'bg-green-100 dark:bg-green-900' : 'bg-white dark:bg-gray-800'}`}>
      <div className="flex justify-between items-start">
        <div>
          <h3 className={`text-lg font-bold ${task.completed ? 'line-through text-gray-500' : 'text-gray-900 dark:text-white'}`}>
            {task.title}
          </h3>
          <p className="text-gray-600 dark:text-gray-300 mt-1">
            {task.description}
          </p>
          <p className="text-xs text-gray-400 mt-2">
            Last updated: {new Date(task.updated_at).toLocaleString()}
          </p>
        </div>
        <div className="flex flex-col items-end space-y-2 ml-4 flex-shrink-0">
          <button
            onClick={() => onToggleComplete(task.id.toString())}
            className={`px-3 py-1 text-sm rounded ${task.completed ? 'bg-yellow-500 hover:bg-yellow-600 text-white' : 'bg-green-500 hover:bg-green-600 text-white'}`}
          >
            {task.completed ? "Mark as Incomplete" : "Mark as Complete"}
          </button>
           <Link href={`/tasks/${task.id}`} passHref>
             <span className="w-full text-center px-3 py-1 text-sm rounded bg-blue-500 hover:bg-blue-600 text-white cursor-pointer">
                Edit
             </span>
          </Link>
          <button
            onClick={() => onDelete(task.id.toString())}
            className="px-3 py-1 text-sm rounded bg-red-500 hover:bg-red-600 text-white"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
