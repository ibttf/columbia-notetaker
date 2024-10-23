import React, { useState, useEffect } from "react"
import Loading from "./Loading"
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

  useEffect(() => {
    //check database to see if this id exists, if so, then grab the blob
  })

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
                  console.log({
                    text: response.textContent,
                    base_url: activeTab.url
                  })
                  if (response && response.textContent) {
                    fetch(
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
                      .then((response: any) => {
                        if (!response.ok) {
                          return {
                            error: "An error occurred while generating notes."
                          }
                        }
                        console.log({ response })
                        return response.text()
                      })
                      .then((data) => {
                        if (data && data.error) {
                          throw new Error(data.error)
                        }
                        console.log("Sending notes to the content script file")
                        chrome.tabs.query(
                          { active: true, currentWindow: true },
                          (tabs) => {
                            const activeTab = tabs[0]
                            if (activeTab) {
                              // Send the notes content to the content script
                              chrome.tabs.sendMessage(activeTab.id as number, {
                                action: "notesGenerated",
                                notesContent: data
                              })
                            } else {
                              console.error(
                                "No active tab found to send message."
                              )
                            }
                          }
                        )
                      })
                      .catch((error) => {
                        // clearTimeout(timeout) // Clear the timeout in case of an error
                        makeError("An error occurred while generating notes.")
                      })
                  } else {
                    makeError("Failed to parse HTML.")
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
    <div
      className={`transition-opacity duration-300 opacity-100 w-fit ${
        isLoading && "p-4"
      }`}
    >
      {isLoading ? (
        <div className="flex items-center">
          <Loading time={20} />
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
      {error && <p className="text-red-500 text-xs mt-1">{error}</p>}{" "}
    </div>
  )
}

export default Popup
