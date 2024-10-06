import React, { useState, useEffect } from "react"

const Popup: React.FC = () => {
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
          chrome.scripting.executeScript(
            {
              target: { tabId: activeTab.id },
              files: ["contentScript.js"]
            },
            () => {
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
                        if (response) {
                          if (response.data) {
                            // Create a Blob from the notes content
                            const blob = new Blob([response.data], {
                              type: "text/html"
                            })
                            const blobUrl = URL.createObjectURL(blob)

                            // Open a new tab with the Blob URL
                            window.open(blobUrl, "_blank")
                          } else if (response.error) {
                            makeError(response.error)
                          }
                        } else {
                          makeError(
                            "No response received from the background script."
                          )
                        }
                      }
                    )
                  } else {
                    makeError(
                      "Sorry, there was an error fetching the content on the page."
                    )
                  }
                }
              )
            }
          )
        } else {
          makeError("Sorry, we don't work on these URLs.")
        }
      })
    }
  }

  return (
    <div className="p-4 w-72">
      {isLecturePage ? (
        <>
          <h1 className="text-xl font-bold mb-4">Video lecture found</h1>
          <button
            className={`bg-blue-500 ${
              isLoading ? "bg-gray-200" : "hover:bg-blue-700"
            } text-white font-bold py-2 px-4 rounded mb-4`}
            onClick={handleGenerateNotes}
            disabled={isLoading}
          >
            {isLoading ? "Generating..." : "Generate notes?"}
          </button>
        </>
      ) : (
        <h1 className="text-xl font-bold mb-4">Not a video lecture</h1>
      )}
      {error && <p className="text-red-500">{error}</p>}
    </div>
  )
}

export default Popup
