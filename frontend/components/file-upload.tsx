"use client"

import * as React from "react"
import { Upload, X, FileText, Loader2 } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"

export function FileUpload() {
  const [files, setFiles] = React.useState<File[]>([])
  const [isUploading, setIsUploading] = React.useState(false)
  const [isOpen, setIsOpen] = React.useState(false)

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files).filter(
        (file) => file.type === "application/pdf"
      )
      
      if (newFiles.length !== e.target.files.length) {
        toast.error("Only PDF files are supported")
      }
      
      setFiles((prev) => [...prev, ...newFiles])
    }
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const uploadFiles = async () => {
    if (files.length === 0) return

    setIsUploading(true)
    const formData = new FormData()
    files.forEach((file) => {
      formData.append("files", file)
    })

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const response = await fetch(`${apiUrl}/upload`, {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error("Upload failed")
      }

      const result = await response.json()
      toast.success(result.message || "Files uploaded successfully")
      setFiles([])
      setIsOpen(false)
    } catch (error) {
      console.error(error)
      toast.error("Failed to upload files. Make sure the backend is running.")
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="icon">
          <Upload className="size-4" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Upload Documents</DialogTitle>
          <DialogDescription>
            Upload PDF documents to train your DocuMind.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="flex items-center justify-center w-full">
            <label
              htmlFor="dropzone-file"
              className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer bg-muted hover:bg-muted/80 border-border"
            >
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <Upload className="w-8 h-8 mb-3 text-muted-foreground" />
                <p className="mb-2 text-sm text-muted-foreground">
                  <span className="font-semibold">Click to upload</span> or drag and drop
                </p>
                <p className="text-xs text-muted-foreground">PDF (MAX. 10MB)</p>
              </div>
              <input
                id="dropzone-file"
                type="file"
                multiple
                className="hidden"
                accept=".pdf"
                onChange={onFileChange}
                disabled={isUploading}
              />
            </label>
          </div>
          {files.length > 0 && (
            <ScrollArea className="h-32 rounded-md border p-2">
              <div className="space-y-2">
                {files.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2 rounded-md bg-secondary text-secondary-foreground text-xs"
                  >
                    <div className="flex items-center gap-2 truncate">
                      <FileText className="size-3 shrink-0" />
                      <span className="truncate">{file.name}</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="size-6"
                      onClick={() => removeFile(index)}
                      disabled={isUploading}
                    >
                      <X className="size-3" />
                    </Button>
                  </div>
                ))}
              </div>
            </ScrollArea>
          )}
        </div>
        <DialogFooter>
          <Button
            onClick={uploadFiles}
            disabled={files.length === 0 || isUploading}
            className="w-full"
          >
            {isUploading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Ingesting...
              </>
            ) : (
              "Start Ingestion"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
