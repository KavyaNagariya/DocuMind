"use client"

import * as React from "react"

export type Citation = {
  sources: string
  page: number
  snippet: string
}

export type Message = {
  role: "user" | "assistant"
  content: string
  citations?: Citation[]
}

export type ChatSession = {
  id: string
  title: string
  messages: Message[]
  createdAt: number
}

interface ChatContextType {
  sessions: ChatSession[]
  activeSessionId: string | null
  activeSession: ChatSession | null
  createNewSession: () => void
  setActiveSession: (id: string) => void
  addMessageToActiveSession: (message: Message) => void
  updateLastMessage: (partial: Partial<Message>, append?: boolean) => void
  deleteSession: (id: string) => void
  renameSession: (id: string, newTitle: string) => void
}

const ChatContext = React.createContext<ChatContextType | undefined>(undefined)

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [sessions, setSessions] = React.useState<ChatSession[]>([])
  const [activeSessionId, setActiveSessionId] = React.useState<string | null>(null)
  const [isLoaded, setIsLoaded] = React.useState(false)

  // Load from localStorage
  React.useEffect(() => {
    const savedSessions = localStorage.getItem("documind_sessions")
    const savedActiveId = localStorage.getItem("documind_active_session_id")
    
    if (savedSessions) {
      try {
        const parsed = JSON.parse(savedSessions)
        setSessions(parsed)
      } catch (e) {
        console.error("Failed to parse sessions", e)
      }
    }
    
    if (savedActiveId) {
      setActiveSessionId(savedActiveId)
    }
    
    setIsLoaded(true)
  }, [])

  // Save to localStorage
  React.useEffect(() => {
    if (isLoaded) {
      localStorage.setItem("documind_sessions", JSON.stringify(sessions))
      if (activeSessionId) {
        localStorage.setItem("documind_active_session_id", activeSessionId)
      } else {
        localStorage.removeItem("documind_active_session_id")
      }
    }
  }, [sessions, activeSessionId, isLoaded])

  const createNewSession = () => {
    const newSession: ChatSession = {
      id: crypto.randomUUID(),
      title: "New Chat",
      messages: [],
      createdAt: Date.now(),
    }
    setSessions((prev) => [newSession, ...prev])
    setActiveSessionId(newSession.id)
  }

  const setActiveSession = (id: string) => {
    setActiveSessionId(id)
  }

  const updateLastMessage = (partial: Partial<Message>, append: boolean = true) => {
    setSessions((prev) =>
      prev.map((s) => {
        if (s.id === activeSessionId) {
          const newMessages = [...s.messages]
          if (newMessages.length > 0) {
            const lastMessage = newMessages[newMessages.length - 1]
            newMessages[newMessages.length - 1] = {
              ...lastMessage,
              ...partial,
              content: partial.content !== undefined 
                ? (append ? lastMessage.content + partial.content : partial.content)
                : lastMessage.content,
              citations: partial.citations !== undefined ? partial.citations : lastMessage.citations
            }
          }
          return { ...s, messages: newMessages }
        }
        return s
      })
    )
  }

  const addMessageToActiveSession = (message: Message) => {
    setSessions((prev) =>
      prev.map((s) => {
        if (s.id === activeSessionId) {
          const newMessages = [...s.messages, message]
          // Update title based on first user message if it's still "New Chat"
          let newTitle = s.title
          if (s.title === "New Chat" && message.role === "user") {
            newTitle = message.content.slice(0, 30) + (message.content.length > 30 ? "..." : "")
          }
          return { ...s, messages: newMessages, title: newTitle }
        }
        return s
      })
    )
  }

  const deleteSession = (id: string) => {
    setSessions((prev) => prev.filter((s) => s.id !== id))
    if (activeSessionId === id) {
      setActiveSessionId(null)
    }
  }

  const renameSession = (id: string, newTitle: string) => {
    setSessions((prev) =>
      prev.map((s) => (s.id === id ? { ...s, title: newTitle } : s))
    )
  }

  const activeSession = React.useMemo(
    () => sessions.find((s) => s.id === activeSessionId) || null,
    [sessions, activeSessionId]
  )

  return (
    <ChatContext.Provider
      value={{
        sessions,
        activeSessionId,
        activeSession,
        createNewSession,
        setActiveSession,
        addMessageToActiveSession,
        updateLastMessage,
        deleteSession,
        renameSession,
      }}
    >
      {children}
    </ChatContext.Provider>
  )
}

export function useChat() {
  const context = React.useContext(ChatContext)
  if (context === undefined) {
    throw new Error("useChat must be used within a ChatProvider")
  }
  return context
}
