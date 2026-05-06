"use client"

import * as React from "react"
import { Send, User, Bot, Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { FileUpload } from "@/components/file-upload"

type Citation = {
  sources: string
  page: number
  snippet: string
}

type Message = {
  role: "user" | "assistant"
  content: string
  citations?: Citation[]
}

export function ChatInterface() {
  const [messages, setMessages] = React.useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I'm DocuMind. How can I help you today?",
    },
  ])
  const [input, setInput] = React.useState("")
  const [isLoading, setIsLoading] = React.useState(false)
  const scrollRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, isLoading])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = { role: "user", content: input }
    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    try {
      const history = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }))

      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input,
          history: history,
        }),
      })

      if (!response.ok) {
        throw new Error("Chat request failed")
      }

      const data = await response.json()
      
      const assistantMessage: Message = {
        role: "assistant",
        content: data.answer,
        citations: data.citations,
      }
      
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error(error)
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto w-full">
      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="space-y-6 pb-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex gap-3 ${
                message.role === "user" ? "flex-row-reverse" : "flex-row"
              }`}
            >
              <Avatar className="size-8">
                <AvatarFallback className={message.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"}>
                  {message.role === "user" ? <User className="size-4" /> : <Bot className="size-4" />}
                </AvatarFallback>
              </Avatar>
              <div className={`flex flex-col gap-2 max-w-[80%] ${message.role === "user" ? "items-end" : "items-start"}`}>
                <div
                  className={`rounded-lg px-4 py-2 text-sm ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  }`}
                >
                  {message.content}
                </div>
                {message.citations && message.citations.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-1">
                    {message.citations.map((citation, cIndex) => (
                      <Badge key={cIndex} variant="outline" className="text-[10px] py-0 px-1 cursor-help hover:bg-accent" title={citation.snippet}>
                        {citation.sources.split(/[\\/]/).pop()} (p.{citation.page})
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-3">
              <Avatar className="size-8">
                <AvatarFallback className="bg-muted">
                  <Bot className="size-4" />
                </AvatarFallback>
              </Avatar>
              <div className="bg-muted rounded-lg px-4 py-2 text-sm flex items-center">
                <Loader2 className="size-4 animate-spin mr-2" />
                Thinking...
              </div>
            </div>
          )}
        </div>
      </ScrollArea>
      <div className="p-4 border-t bg-background">
        <div className="flex gap-2 max-w-4xl mx-auto items-center">
          <FileUpload />
          <Input
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            disabled={isLoading}
            className="flex-1"
          />
          <Button size="icon" onClick={handleSend} disabled={isLoading || !input.trim()}>
            <Send className="size-4" />
          </Button>
        </div>
        <p className="text-[10px] text-center text-muted-foreground mt-2">
          DocuMind can make mistakes. Verify important information.
        </p>
      </div>
    </div>
  )
}
