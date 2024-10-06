// Log when the service worker starts
console.log("Background service worker started.")

// Event listener when the extension is installed or updated
chrome.runtime.onInstalled.addListener(() => {
  console.log("Extension installed or updated.")
})

// True background worker; listens for tab updates and detects whether the tab is from panopto
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (
    changeInfo.status === "complete" &&
    tab.url &&
    tab.url.includes("hosted.panopto.com")
  ) {
    chrome.action.openPopup() // Automatically open the popup
  } else {
    console.log("Tab updated, but not a lecture")
  }
})

// Listen for messages from popup specifically// background.js

// Log when the service worker starts
console.log("Background service worker started.")

// Event listener when the extension is installed or updated
chrome.runtime.onInstalled.addListener(() => {
  console.log("Extension installed or updated.")
})

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message === "checkURL") {
    // Get the active tab
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs.length === 0) {
        sendResponse({ isLecturePage: false })
        return
      }

      const activeTab = tabs[0]
      if (
        activeTab &&
        activeTab.url &&
        activeTab.url.includes("hosted.panopto.com")
      ) {
        sendResponse({ isLecturePage: true }) // Send boolean to popup
      } else {
        sendResponse({ isLecturePage: false })
      }
    })

    return true // Indicates that sendResponse will be called asynchronously
  } else if (message.action === "generateNotes") {
    const { transcript, baseUrl } = message.payload

    // Call your API to generate notes
    fetch("https://generatenotes.pythonanywhere.com/generate_notes", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ transcript, base_url: baseUrl })
    })
      .then((response) => {
        if (!response.ok) {
          sendResponse({ error: "An error occurred while generating notes." })
          throw new Error("Failed to generate notes.")
        }
        return response.text() // or response.json() based on your API
      })
      .then((data) => {
        // Send the notes content to the content script
        console.log("Sending notes to the content script file")
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          const activeTab = tabs[0]
          if (activeTab) {
            // Send the notes content to the content script
            chrome.tabs.sendMessage(activeTab.id, {
              action: "notesGenerated",
              notesContent: data
            })
          } else {
            console.error("No active tab found to send message.")
          }
        })
      })
      .catch((error) => {
        console.error("Error:", error)
        sendResponse({ error: "An error occurred while generating notes." })
      })

    return true
  }
})
