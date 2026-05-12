"use client"

import * as React from "react"
import { Send, User, Bot, Loader2, MessageSquarePlus, Square } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { useChat, Message } from "@/lib/chat-context"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { FileUpload } from "@/components/file-upload"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"

export function ChatInterface() {
  const { activeSession, addMessageToActiveSession, createNewSession, updateLastMessage } = useChat()
  const [input, setInput] = React.useState("")
  const [isLoading, setIsLoading] = React.useState(false)
  const abortControllerRef = React.useRef<AbortController | null>(null)
  const scrollRef = React.useRef<HTMLDivElement>(null)

  const messages = React.useMemo(() => activeSession?.messages || [], [activeSession])

  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, isLoading])

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
      setIsLoading(false)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading || !activeSession) return

    const userMessage: Message = { role: "user", content: input }
    addMessageToActiveSession(userMessage)
    setInput("")
    setIsLoading(true)

    const controller = new AbortController()
    abortControllerRef.current = controller

    try {
      const history = [...messages, userMessage].map((m) => ({
        role: m.role,
        content: m.content,
      }))

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const response = await fetch(`${apiUrl}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        signal: controller.signal,
        body: JSON.stringify({
          message: input,
          history: history,
        }),
      })


      if (!response.ok) {
        throw new Error("Chat request failed")
      }

      const reader = response.body?.getReader()
      if (!reader) throw new Error("No reader available")

      const decoder = new TextDecoder()

      // Initialize assistant message
      addMessageToActiveSession({
        role: "assistant",
        content: "",
        citations: []
      })

      let currentEvent = ""

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split("\n")

        for (const line of lines) {
          const trimmedLine = line.trim()
          if (!trimmedLine) continue

          if (trimmedLine.startsWith("event: ")) {
            currentEvent = trimmedLine.replace("event: ", "")
          } else if (trimmedLine.startsWith("data: ")) {
            const dataStr = trimmedLine.replace("data: ", "")
            try {
              const data = JSON.parse(dataStr)

              if (currentEvent === "token") {
                updateLastMessage({ content: data.token }, true)
              } else if (currentEvent === "citations") {
                updateLastMessage({ citations: data }, false)
              }
            } catch (e) {
              console.error("Error parsing SSE data", e, dataStr)
            }
          }
        }
      }
    } catch (error: any) {
      if (error.name === "AbortError") {
        updateLastMessage({ content: " [Stopped by user]" }, true)
      } else {
        console.error(error)
        addMessageToActiveSession({
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
        })
      }
    } finally {
      setIsLoading(false)
      abortControllerRef.current = null
    }
  }

  if (!activeSession) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-8">
        <div className="bg-primary/10 p-6 rounded-full mb-4">
          <MessageSquarePlus className="size-12 text-primary" />
        </div>
        <h2 className="text-2xl font-bold mb-2">No Active Chat</h2>
        <p className="text-muted-foreground mb-6 max-w-sm">
          Select a recent chat from the sidebar or start a fresh conversation to begin.
        </p>
        <Button onClick={createNewSession}>
          Create New Chat
        </Button>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto w-full">
      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="space-y-6 pb-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center py-20 text-center opacity-50">
              <Bot className="size-12 mb-4" />
              <p>How can I help you today?</p>
            </div>
          )}
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
                      ? "bg-primary text-primary-foreground whitespace-pre-wrap"
                      : "bg-muted prose prose-sm dark:prose-invert max-w-none"
                  }`}
                >
                  {message.role === "assistant" ? (
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.content}
                    </ReactMarkdown>
                  ) : (
                    message.content
                  )}
                </div>
                {message.citations && message.citations.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-1">
                    {message.citations.map((citation, cIndex) => (
                      <Tooltip key={cIndex}>
                        <TooltipTrigger asChild>
                          <Badge variant="outline" className="text-[10px] py-0 px-1 cursor-help hover:bg-accent">
                            {citation.sources.split(/[\\/]/).pop()} (p.{citation.page})
                          </Badge>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p className="max-w-xs">{citation.snippet}</p>
                        </TooltipContent>
                      </Tooltip>
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
          {isLoading ? (
            <Button size="icon" variant="destructive" onClick={handleStop}>
              <Square className="size-4 fill-current" />
            </Button>
          ) : (
            <Button size="icon" onClick={handleSend} disabled={!input.trim()}>
              <Send className="size-4" />
            </Button>
          )}
        </div>
        <p className="text-[10px] text-center text-muted-foreground mt-2">
          DocuMind can make mistakes. Verify important information.
        </p>
      </div>
    </div>
  )
}
