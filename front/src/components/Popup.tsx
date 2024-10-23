import React, { useState, useEffect } from "react"
import { createClient, SupabaseClient } from "@supabase/supabase-js"
import Loading from "./Loading"

interface Note {
  content: string
  video_id: string
}

const supabaseUrl = "https://ldnzntdtvrowsnjhscvj.supabase.co"
const supabaseKey =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxkbnpudGR0dnJvd3NuamhzY3ZqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjk3MTkxMzgsImV4cCI6MjA0NTI5NTEzOH0.q4NG38HESASbRF9vc2BDT6PIKZ4MPMXbQQ6rlz4aGBE"
const supabase: SupabaseClient = createClient(supabaseUrl, supabaseKey)

const Popup: React.FC = () => {
  const [isLecturePage, setIsLecturePage] = useState<boolean>(false)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<string>("")
  const [savedNotes, setSavedNotes] = useState<string | null>(null)
  const [length, setLength] = useState<number>(0)

  useEffect(() => {
    checkIfLecturePage()
    fetchNotes()
  }, [])

  const ensureContentScript = async (tabId: number): Promise<void> => {
    return new Promise((resolve, reject) => {
      // First try to message the content script to see if it's already there
      chrome.tabs.sendMessage(tabId, { action: "ping" }, (response) => {
        if (chrome.runtime.lastError) {
          // Content script isn't there, inject it
          console.log("Injecting content script...")
          chrome.scripting.executeScript(
            {
              target: { tabId },
              files: ["contentScript.js"]
            },
            () => {
              if (chrome.runtime.lastError) {
                reject(new Error("Failed to inject content script"))
              } else {
                // Wait a bit for the script to initialize
                setTimeout(resolve, 100)
              }
            }
          )
        } else {
          // Content script is already there
          resolve()
        }
      })
    })
  }

  const sendMessageToContentScript = async (
    tabId: number,
    message: any
  ): Promise<any> => {
    try {
      await ensureContentScript(tabId)

      return new Promise((resolve, reject) => {
        chrome.tabs.sendMessage(tabId, message, (response) => {
          if (chrome.runtime.lastError) {
            reject(new Error(chrome.runtime.lastError.message))
          } else {
            resolve(response)
          }
        })
      })
    } catch (error) {
      console.error("Error sending message to content script:", error)
      throw error
    }
  }

  const checkIfLecturePage = async () => {
    try {
      const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
      })
      const activeTab = tabs[0]

      if (!activeTab?.url) {
        console.log("No active tab URL found")
        return
      }

      console.log("Checking URL:", activeTab.url)

      chrome.runtime.sendMessage("checkURL", (response) => {
        console.log("checkURL response:", response)
        if (response && response.isLecturePage !== undefined) {
          console.log("Setting isLecturePage to:", response.isLecturePage)
          setIsLecturePage(response.isLecturePage)
        }
      })
    } catch (err) {
      console.error("Error checking lecture page:", err)
    }
  }

  const fetchNotes = async () => {
    try {
      const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
      })
      const activeTab = tabs[0]

      if (!activeTab?.url) {
        throw new Error("No active tab URL found")
      }

      const activeUrl = new URL(activeTab.url)
      const video_id = activeUrl.searchParams.get("id")

      if (!video_id) {
        console.log("No video ID found in URL")
        return
      }

      console.log("Fetching notes for video_id:", video_id)

      const { data, error } = await supabase
        .from("notes")
        .select("content")
        .eq("video_id", video_id)
        .single()

      if (error) {
        if (error.code !== "PGRST116") {
          console.error("Supabase fetch error:", error)
          throw error
        }
        return
      }

      if (data?.content) {
        console.log("Found existing notes")
        setSavedNotes(data.content)
      }
    } catch (err) {
      makeError(err instanceof Error ? err.message : "Failed to fetch notes")
    }
  }

  const makeError = (text: string) => {
    console.error("Error:", text)
    setError(text)
    setIsLoading(false)
  }

  const showSavedNotes = async () => {
    try {
      const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
      })
      const activeTab = tabs[0]

      if (!activeTab?.id || !savedNotes) {
        throw new Error("Cannot display notes at this time")
      }

      await sendMessageToContentScript(activeTab.id, {
        action: "notesGenerated",
        notesContent: savedNotes
      })
    } catch (err) {
      makeError(
        err instanceof Error ? err.message : "Failed to display saved notes"
      )
    }
  }

  const handleGenerateNotes = async () => {
    try {
      const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
      })
      const activeTab = tabs[0]

      if (!activeTab?.id || !activeTab?.url) {
        throw new Error("No active tab found")
      }

      console.log("Getting HTML content")
      const response = await sendMessageToContentScript(activeTab.id, {
        action: "parseHTML"
      })

      if (!response?.textContent) {
        throw new Error("Failed to parse HTML content")
      }
      setLength(response.textContent.length)
      setIsLoading(true)
      setError("")

      console.log("Sending request to generate notes")
      const notesResponse = await fetch(
        "https://generatenotes.pythonanywhere.com/generate_notes",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "text/plain, application/json"
          },
          body: JSON.stringify({
            transcript: response.textContent,
            base_url: activeTab.url
          })
        }
      )

      if (!notesResponse.ok) {
        throw new Error(`Failed to generate notes: ${notesResponse.status}`)
      }

      const notesContent = await notesResponse.text()
      console.log("Generated notes length:", notesContent.length)

      const activeUrl = new URL(activeTab.url)
      const video_id = activeUrl.searchParams.get("id")

      if (!video_id) {
        throw new Error("No video ID found in URL")
      }

      await saveNotesToSupabase(video_id, notesContent)
      setSavedNotes(notesContent)

      console.log("Sending notes to content script")
      await sendMessageToContentScript(activeTab.id, {
        action: "notesGenerated",
        notesContent: notesContent
      })

      setIsLoading(false)
    } catch (err) {
      console.error("Full error:", err)
      makeError(
        err instanceof Error ? err.message : "An unexpected error occurred"
      )
    }
  }

  const saveNotesToSupabase = async (
    video_id: string,
    notesContent: string
  ) => {
    try {
      console.log("Saving notes for video_id:", video_id)
      const { error: insertError } = await supabase
        .from("notes")
        .insert([
          {
            video_id,
            content: notesContent
          }
        ])
        .select()

      if (insertError) {
        if (insertError.code === "23505") {
          // Unique violation
          console.log("Note exists, updating instead")
          const { error: updateError } = await supabase
            .from("notes")
            .update({ content: notesContent })
            .eq("video_id", video_id)
            .select()

          if (updateError) throw updateError
        } else {
          throw insertError
        }
      }

      console.log("Successfully saved notes")
      return { success: true }
    } catch (error) {
      console.error("Supabase save error:", error)
      throw error
    }
  }
  const lengthToSeconds = (length: number): number => {
    return Math.ceil(length / 1000)
  }

  if (!isLecturePage) {
    return <p className="text-gray-500 p-4">Not a video lecture</p>
  }

  return (
    <div className="p-4 space-y-4">
      {isLoading ? (
        <div className="flex items-center justify-center">
          <Loading time={lengthToSeconds(length)} />
        </div>
      ) : (
        <div className="space-y-2">
          {savedNotes ? (
            <>
              <button
                className="w-36 bg-green-500 text-white font-bold py-2 px-4 rounded flex items-center justify-center"
                onClick={showSavedNotes}
              >
                <span className="text-md mr-2">📝</span>
                View Notes
              </button>
            </>
          ) : (
            <button
              className="w-36 bg-blue-500 text-white font-bold py-2 px-4 rounded flex items-center justify-center"
              onClick={handleGenerateNotes}
              disabled={isLoading}
            >
              <span className="text-md mr-2">✨</span>
              Write Notes
            </button>
          )}
        </div>
      )}
      {error && <p className="text-red-500 text-sm">{error}</p>}
    </div>
  )
}

export default Popup
