// Log when the service worker starts
console.log("Background service worker started.")

// Event listener when the extension is installed or updated
chrome.runtime.onInstalled.addListener(() => {
  console.log("Extension installed or updated.")
})

// Listen for messages from popup to check URL
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
  }
})
