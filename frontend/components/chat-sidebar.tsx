"use client"

import * as React from "react"
import { Plus, MessageSquare, Trash2, Pencil, Check, X } from "lucide-react"
import { useChat } from "@/lib/chat-context"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
} from "@/components/ui/sidebar"
import { Input } from "@/components/ui/input"

export function ChatSidebar() {
  const { sessions, activeSessionId, createNewSession, setActiveSession, deleteSession, renameSession } = useChat()
  const [editingId, setEditingId] = React.useState<string | null>(null)
  const [editValue, setEditValue] = React.useState("")

  const handleStartEdit = (id: string, currentTitle: string) => {
    setEditingId(id)
    setEditValue(currentTitle)
  }

  const handleSaveEdit = (id: string) => {
    if (editValue.trim()) {
      renameSession(id, editValue.trim())
    }
    setEditingId(null)
  }

  const handleCancelEdit = () => {
    setEditingId(null)
  }

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg">
              <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                <MessageSquare className="size-4" />
              </div>
              <div className="flex flex-col gap-0.5 leading-none">
                <span className="font-semibold">DocuMind</span>
                <span className="text-xs text-muted-foreground">Enterprise v1.0</span>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton tooltip="New Chat" onClick={createNewSession}>
                  <Plus className="size-4" />
                  <span>New Chat</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        
        {sessions.length > 0 && (
          <SidebarGroup>
            <SidebarGroupLabel>Recent Chats</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {sessions.map((session) => (
                  <SidebarMenuItem key={session.id}>
                    {editingId === session.id ? (
                      <div className="flex items-center gap-1 px-2 py-1 w-full">
                        <Input
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") handleSaveEdit(session.id)
                            if (e.key === "Escape") handleCancelEdit()
                          }}
                          className="h-7 text-xs flex-1"
                          autoFocus
                        />
                        <button 
                          onClick={() => handleSaveEdit(session.id)}
                          className="text-primary hover:text-primary/80"
                        >
                          <Check className="size-3" />
                        </button>
                        <button 
                          onClick={handleCancelEdit}
                          className="text-muted-foreground hover:text-foreground"
                        >
                          <X className="size-3" />
                        </button>
                      </div>
                    ) : (
                      <>
                        <SidebarMenuButton 
                          isActive={activeSessionId === session.id}
                          onClick={() => setActiveSession(session.id)}
                          className="pr-14"
                        >
                          <MessageSquare className="size-4" />
                          <span className="truncate">{session.title}</span>
                        </SidebarMenuButton>
                        <SidebarMenuAction
                          showOnHover
                          onClick={(e) => {
                            e.stopPropagation()
                            handleStartEdit(session.id, session.title)
                          }}
                          className="right-7"
                        >
                          <Pencil className="size-3" />
                          <span className="sr-only">Rename Chat</span>
                        </SidebarMenuAction>
                        <SidebarMenuAction
                          showOnHover
                          onClick={(e) => {
                            e.stopPropagation()
                            deleteSession(session.id)
                          }}
                        >
                          <Trash2 className="size-3 hover:text-destructive" />
                          <span className="sr-only">Delete Chat</span>
                        </SidebarMenuAction>
                      </>
                    )}
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        )}
      </SidebarContent>
      <SidebarFooter>
        {/* Settings and Documents removed as requested/not functional */}
      </SidebarFooter>
    </Sidebar>
  )
}
