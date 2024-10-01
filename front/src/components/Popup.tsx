import React, { useState, useEffect } from "react"

const Popup: React.FC = () => {
  const [notes, setNotes] = useState<string | null>(null)
  const [isLecturePage, setIsLecturePage] = useState<boolean>(false)

  // Send message to background script to check the tab URL
  useEffect(() => {
    chrome.runtime.sendMessage("checkURL", (response) => {
      if (response && response.isLecturePage !== undefined) {
        setIsLecturePage(response.isLecturePage) // Update state based on URL check
      }
      console.log({ response })
    })
  }, [])

  const handleGenerateNotes = () => {
    if (chrome && chrome.tabs) {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const activeTab = tabs[0].id
        if (activeTab) {
          // First inject the content script
          chrome.scripting.executeScript(
            {
              target: { tabId: activeTab },
              files: ["contentScript.js"] // Dynamically inject the content script
            },
            () => {
              // Then send the message to the content script
              chrome.tabs.sendMessage(
                activeTab,
                { action: "parseHTML" },
                (response) => {
                  if (response && response.textContent) {
                    setNotes(response.textContent)
                  }
                }
              )
            }
          )
        }
      })
    }
  }
  return (
    <div className="p-4 w-72">
      {isLecturePage ? ( // Only show this if the page is a video lecture
        <>
          <h1 className="text-xl font-bold mb-4">Video lecture found</h1>
          <button
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mb-4"
            onClick={handleGenerateNotes}
          >
            Generate notes?
          </button>
        </>
      ) : (
        <h1 className="text-xl font-bold mb-4">Not a video lecture</h1>
      )}
      {notes && (
        <textarea
          value={notes}
          readOnly
          className="w-full h-40 p-2 border border-gray-300 rounded"
        ></textarea>
      )}
    </div>
  )
}

export default Popup
