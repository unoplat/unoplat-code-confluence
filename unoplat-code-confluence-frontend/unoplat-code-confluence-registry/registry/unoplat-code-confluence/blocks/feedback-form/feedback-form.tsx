"use client"

import * as React from "react"
import { z } from "zod"
import { useForm as useTanstackForm } from "@tanstack/react-form"

import { Button } from "@/registry/unoplat-code-confluence/ui/button"
import { Input } from "@/registry/unoplat-code-confluence/ui/input"
import { Textarea } from "@/registry/unoplat-code-confluence/ui/textarea"
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/registry/unoplat-code-confluence/ui/select"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/registry/unoplat-code-confluence/ui/form"
import { Alert, AlertTitle, AlertDescription } from "@/registry/unoplat-code-confluence/ui/alert"

const feedbackSchema = z.object({
  name: z.string().min(2, { message: "Name must be at least 2 characters." }),
  email: z.string().email({ message: "Please enter a valid email address." }),
  feedbackType: z.enum(["suggestion", "bug", "question", "other"], {
    required_error: "Please select a feedback type.",
  }),
  message: z.string().min(10, { message: "Message must be at least 10 characters." }),
})

type FeedbackFormValues = z.infer<typeof feedbackSchema>

export function FeedbackForm() {
  const [isSubmitted, setIsSubmitted] = React.useState(false)
  
  const form = useTanstackForm({
    defaultValues: {
      name: "",
      email: "",
      feedbackType: "suggestion",
      message: "",
    },
    onSubmit: async ({ value }) => {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))
      console.log("Form submitted:", value)
      setIsSubmitted(true)
    },
  })

  if (isSubmitted) {
    return (
      <Alert variant="success">
        <AlertTitle>Thank you for your feedback!</AlertTitle>
        <AlertDescription>
          We appreciate your input and will review it shortly.
        </AlertDescription>
        <Button 
          className="mt-4" 
          variant="outline" 
          onClick={() => {
            form.reset()
            setIsSubmitted(false)
          }}
        >
          Submit another feedback
        </Button>
      </Alert>
    )
  }

  return (
    <div className="max-w-md w-full mx-auto p-6 bg-background rounded-lg shadow-sm border">
      <h2 className="text-2xl font-bold mb-6 text-center">User Feedback</h2>
      <Form form={form}>
        <div className="space-y-4">
          <FormField
            name="name"
            form={form}
            children={(field) => (
              <FormItem>
                <FormLabel>Name</FormLabel>
                <FormControl>
                  <Input
                    placeholder="Your name"
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    aria-invalid={field.state.meta.errors.length > 0}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          
          <FormField
            name="email"
            form={form}
            children={(field) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input
                    type="email"
                    placeholder="your.email@example.com"
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    aria-invalid={field.state.meta.errors.length > 0}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          
          <FormField
            name="feedbackType"
            form={form}
            children={(field) => (
              <FormItem>
                <FormLabel>Feedback Type</FormLabel>
                <FormControl>
                  <Select
                    value={field.state.value}
                    onValueChange={field.handleChange}
                  >
                    <SelectTrigger aria-invalid={field.state.meta.errors.length > 0}>
                      <SelectValue placeholder="Select feedback type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="suggestion">Suggestion</SelectItem>
                      <SelectItem value="bug">Bug Report</SelectItem>
                      <SelectItem value="question">Question</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          
          <FormField
            name="message"
            form={form}
            children={(field) => (
              <FormItem>
                <FormLabel>Your Feedback</FormLabel>
                <FormControl>
                  <Textarea
                    placeholder="Please provide your detailed feedback here..."
                    className="min-h-[120px]"
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    aria-invalid={field.state.meta.errors.length > 0}
                  />
                </FormControl>
                <FormDescription>
                  Your feedback helps us improve our product.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          
          <Button type="submit" className="w-full mt-2">
            Submit Feedback
          </Button>
        </div>
      </Form>
    </div>
  )
}
