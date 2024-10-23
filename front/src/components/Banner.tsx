import React, { useState, useEffect } from "react"
import { AiOutlineLoading } from "react-icons/ai"

const MiniBanner: React.FC = () => {
  const [notes, setNotes] = useState<string>("")
  const [isLecturePage, setIsLecturePage] = useState<boolean>(false)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<string>("")

  useEffect(() => {
    chrome.runtime.sendMessage("checkURL", (response) => {
      if (response && response.isLecturePage !== undefined) {
        setIsLecturePage(response.isLecturePage)
      }
    })
  }, [])

  const makeError = (text: string) => {
    setError(text)
    setNotes("")
    setIsLoading(false)
  }

  const handleGenerateNotes = () => {
    setIsLoading(true)
    if (chrome && chrome.tabs) {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const activeTab = tabs[0]
        if (activeTab && activeTab.id) {
          // Directly send a message to the content script
          chrome.tabs.sendMessage(
            activeTab.id!,
            { action: "parseHTML" },
            (response) => {
              if (response && response.textContent) {
                // Send data to the background script
                chrome.runtime.sendMessage(
                  {
                    action: "generateNotes",
                    payload: {
                      transcript: response.textContent,
                      baseUrl: activeTab.url
                    }
                  },
                  (response) => {
                    if (response && response.error) {
                      makeError(response.error)
                    }
                  }
                )
              } else {
                makeError("Failed to parse HTML.")
              }
            }
          )
        } else {
          makeError("Sorry, we don't work on these URLs.")
        }
      })
    }
  }

  return (
    <div className="fixed top-4 right-4 z-50 bg-white shadow-lg rounded-lg p-4 border border-gray-300">
      {isLoading ? (
        <div className="flex items-center">
          <AiOutlineLoading className="animate-spin text-blue-500" size={20} />{" "}
        </div>
      ) : isLecturePage ? (
        <button
          className="bg-blue-500 text-white font-bold py-2 px-4 rounded flex items-center justify-center"
          onClick={handleGenerateNotes}
          disabled={isLoading}
        >
          <span className="text-lg">&#10003;</span>
          <span className="ml-2">Generate</span>
        </button>
      ) : (
        <p className="text-gray-500">Not a video lecture</p>
      )}
      {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
    </div>
  )
}

export default MiniBanner
