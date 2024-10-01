chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "parseHTML") {
    console.log(
      "Coming from the content script, parseHTML action request received"
    )
    const eventDivs = document.querySelectorAll("div.event-text") // Select all divs with class "event-text"
    let content = ""

    eventDivs.forEach((div) => {
      const spans = div.querySelectorAll("span") // Get all span elements inside the div
      spans.forEach((span) => {
        content += span.innerText + " "
      })
    })

    sendResponse({ textContent: content.trim() }) // Send the collected text
  }
})
