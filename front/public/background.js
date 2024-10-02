// Log when the service worker starts
console.log("Background service worker started.")

// Event listener when the extension is installed or updated
chrome.runtime.onInstalled.addListener(() => {
  console.log("Extension installed or updated.")
})

// Example: Event listener for tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete") {
    console.log(`Tab url ${tab.url}`, tab.url.includes("hosted.panopto.com"))
    console.log(`Tab ${tabId} has been updated.`)
    // You can inject content scripts here if needed
  }
})

// Listen for messages from popup to check URL
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message === "checkURL") {
    // Get the active tab
    console.log("Checking URL, use effect is called for the Popup component")
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs.length === 0) {
        sendResponse({ isLecturePage: false })
        return
      }

      const activeTab = tabs[0]
      console.log({
        activeTab,
        url: activeTab.url,
        bool: activeTab && activeTab.url
      })
      if (activeTab && activeTab.url) {
        const isLecturePage = activeTab.url.includes("hosted.panopto.com")
        console.log({ isLecturePage })
        sendResponse({ isLecturePage: isLecturePage }) // Send boolean to popup
      } else {
        sendResponse({ isLecturePage: false })
      }
    })

    return true // Indicates that sendResponse will be called asynchronously
  }
})
