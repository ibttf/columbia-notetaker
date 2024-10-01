chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "parseHTML") {
    console.log(
      "Coming from the content script, parseHTML action request received"
    )
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
    console.log("Coming from the content script, here's the content", content)

    sendResponse({ textContent: content }) // Send the collected text and time as textContent
  }
})
