const playButton = document.getElementById("play-button");
const audio = document.getElementById("story-audio");
const storyTextDiv = document.getElementById("story-text");

let sentences = [];
let nextSentenceIndex = 0;

// --- Load the sentence-timing data ---
fetch("audio/hanuman-leap-of-faith-en-sentences.json")
  .then((response) => response.json())
  .then((data) => {
    sentences = data;
  })
  .catch((error) => {
    console.error("Failed to load sentence timing data:", error);
  });

// --- Play / Pause button behavior ---
playButton.addEventListener("click", () => {
  if (audio.paused) {
    audio.play();
    playButton.textContent = "⏸ Pause";
  } else {
    audio.pause();
    playButton.textContent = "▶ Play story";
  }
});

// --- Reveal sentences as playback reaches their start time ---
audio.addEventListener("timeupdate", () => {
  const currentTime = audio.currentTime;

  while (
    nextSentenceIndex < sentences.length &&
    sentences[nextSentenceIndex].start <= currentTime
  ) {
    const sentenceEl = document.createElement("p");
    sentenceEl.textContent = sentences[nextSentenceIndex].text;
    storyTextDiv.appendChild(sentenceEl);

    // Keep the latest revealed line in view
    sentenceEl.scrollIntoView({ behavior: "smooth", block: "end" });

    nextSentenceIndex++;
  }
});

// --- Reset when the story ends, so replay works cleanly ---
audio.addEventListener("ended", () => {
  playButton.textContent = "▶ Play again";
});

// --- If the user scrubs backward, reset revealed text to match ---
audio.addEventListener("seeked", () => {
  storyTextDiv.innerHTML = "";
  nextSentenceIndex = 0;
  const currentTime = audio.currentTime;
  while (
    nextSentenceIndex < sentences.length &&
    sentences[nextSentenceIndex].start <= currentTime
  ) {
    const sentenceEl = document.createElement("p");
    sentenceEl.textContent = sentences[nextSentenceIndex].text;
    storyTextDiv.appendChild(sentenceEl);
    nextSentenceIndex++;
  }
});