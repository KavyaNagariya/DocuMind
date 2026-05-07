"use client"

import { ChatSidebar } from "@/components/chat-sidebar"
import { ChatInterface } from "@/components/chat-interface"
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { Separator } from "@/components/ui/separator"
import { useChat } from "@/lib/chat-context"

export default function Page() {
  const { activeSession } = useChat()

  return (
    <SidebarProvider>
      <ChatSidebar />
      <SidebarInset>
        <header className="flex h-14 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <div className="flex flex-1 items-center justify-between">
            <h2 className="text-sm font-semibold truncate max-w-[200px] sm:max-w-md">
              {activeSession?.title || "DocuMind Enterprise"}
            </h2>
          </div>
        </header>
        <main className="flex-1 overflow-hidden relative">
          <ChatInterface />
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}
