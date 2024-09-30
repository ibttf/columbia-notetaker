// Log when the service worker starts
console.log("Background service worker started.")

// Event listener when the extension is installed or updated
chrome.runtime.onInstalled.addListener(() => {
  console.log("Extension installed or updated.")
})

// Example: Event listener for tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete") {
    console.log(`Tab ${tabId} has been updated.`)
    // You can inject content scripts here if needed
  }
})

// Example: Responding to messages sent from other parts of the extension
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message === "hello") {
    console.log("Received hello from popup or content script")
    sendResponse("Hi from the background!")
  }
})
