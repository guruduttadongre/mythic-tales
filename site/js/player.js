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

audio.addEventListener("error", () => {
  playButton.disabled = true;
  playButton.textContent = "⚠ Audio unavailable — please refresh";
  storyTextDiv.innerHTML = "<p>Sorry, the story couldn't load right now. Try refreshing the page.</p>";
});

// --- Reveal sentences as playback reaches their start time ---
const progressFill = document.getElementById("progress-bar-fill");
audio.addEventListener("timeupdate", () => {
  const currentTime = audio.currentTime;
  if (audio.duration) {
    const percent = (currentTime / audio.duration) * 100;
    progressFill.style.width = `${percent}%`;
  }

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
// --- Gently shift background mood through the story ---
const moodStops = [
  { time: 0, color: "#FDFBF7" },    // calm opening
  { time: 45, color: "#FCEFE8" },   // gentle tension building
  { time: 90, color: "#FBE4D8" },   // doubt / vulnerability
  { time: 130, color: "#F9DAC8" },  // encouragement warms
  { time: 170, color: "#F5C4B3" },  // transformation / rising
  { time: 200, color: "#FDFBF7" }   // triumphant flight, settles back to calm
];

audio.addEventListener("timeupdate", () => {
  const currentTime = audio.currentTime;
  let activeColor = moodStops[0].color;

  for (const stop of moodStops) {
    if (currentTime >= stop.time) {
      activeColor = stop.color;
    }
  }

  document.documentElement.style.setProperty("--mood-bg", activeColor);
});