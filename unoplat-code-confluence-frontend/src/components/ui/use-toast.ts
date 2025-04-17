import { toast as sonnerToast } from "sonner"

interface UseToastResult {
  toast: typeof sonnerToast
}

function useToast(): UseToastResult {
  return { toast: sonnerToast }
}

export { useToast, sonnerToast as toast } 