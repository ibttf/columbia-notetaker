chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "parseHTML") {
    const textDivs = Array.from(document.querySelectorAll("div.event-text")) // Select all divs with class "event-text"
    const timeDivs = Array.from(document.querySelectorAll("div.event-time")) // Select all divs with class "event-time"

    let content = []

    textDivs.forEach((textDiv, index) => {
      const timeDiv = timeDivs[index] // Get the corresponding time div
      const textSpans = textDiv.querySelectorAll("span") // Get all span elements inside the text div

      let textContent = ""
      textSpans.forEach((span) => {
        textContent += span.innerText + " "
      })

      let timeContent = ""
      timeContent += timeDiv.innerText

      content += textContent.trim() + timeContent.trim() + "\n" //TODO: CHANGE, WE CAN TURN THIS INTO AN OBJECT AND SEND IT AS A POST REQUEST IF EASIER
    })
    sendResponse({ textContent: content }) // Send the collected text and time as textContent
  } else if (request.action === "notesGenerated") {
    console.log("Notes received in the content script")
    const notesContent = request.notesContent

    // Create a Blob from the notes content
    const blob = new Blob([notesContent], { type: "text/html" })
    const blobUrl = URL.createObjectURL(blob)

    // Open a new tab with the Blob URL
    window.open(blobUrl, "_blank")
  } else if (request.action === "injectBanner") {
    // Check if the banner is already injected
    if (!document.getElementById("vidnotes-extension-root")) {
      // Create a div for the banner
      const rootDiv = document.createElement("div")
      rootDiv.id = "vidnotes-extension-root"
      rootDiv.style.position = "fixed"
      rootDiv.style.top = "10px"
      rootDiv.style.right = "10px"
      rootDiv.style.zIndex = "10000" // Ensure it's above other content
      document.body.appendChild(rootDiv)

      // Inject the bundled React app (inject.bundle.js)
      const script = document.createElement("script")
      script.src = chrome.runtime.getURL("inject.bundle.js")
      document.body.appendChild(script)
    }
    sendResponse({ status: "Banner injected" })
  }
})
