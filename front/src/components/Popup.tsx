import React, { useState, useEffect } from "react"

const Popup: React.FC = () => {
  const [notes, setNotes] = useState<string | TrustedHTML>("")
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
                async (response) => {
                  if (response && response.textContent) {
                    try {
                      const apiResponse = await fetch(
                        "https://generatenotes.pythonanywhere.com/generate_notes",
                        {
                          method: "POST",
                          headers: {
                            "Content-Type": "application/json"
                          },
                          body: JSON.stringify({
                            transcript: response.textContent,
                            base_url: activeTab.url
                          })
                        }
                      )

                      if (!apiResponse.ok) {
                        makeError("Sorry, there was an error on our end.")
                      }

                      const data = await apiResponse.text()
                      setNotes(data)
                    } catch (error) {
                      console.error("Error:", error)
                      makeError("An error occurred while generating notes.")
                    } finally {
                      setIsLoading(false)
                    }
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
          makeError("Sorry, we don't work on these URL's.")
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
              isLoading ? "bg-blue-300" : "hover:bg-blue-700"
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
      {notes && <div dangerouslySetInnerHTML={{ __html: notes }}></div>}
    </div>
  )
}

export default Popup
