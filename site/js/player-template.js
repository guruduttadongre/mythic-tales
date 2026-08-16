const playButton = document.getElementById("play-button");
const audio = document.getElementById("story-audio");
const storyTextDiv = document.getElementById("story-text");
const progressFill = document.getElementById("progress-bar-fill");
// --- Set the background watermark image based on this page's own story ---
const pageSlug = window.location.pathname.split("/").pop().replace(".html", "");
document.documentElement.style.setProperty("--story-bg-image", `url('../images/${pageSlug}-card.png')`);let sentences = [];
let nextSentenceIndex = 0;

// --- Derive the sentence-timings file path from the audio file's own path ---
// e.g. "audio/crocodile-monkey-and-the-jamun-fruit-en.mp3"
//   -> "audio/crocodile-monkey-and-the-jamun-fruit-en-sentences.json"
const audioSrc = audio.getAttribute("src");
const sentencesSrc = audioSrc.replace(/\.mp3$/, "-sentences.json");

// --- Load the sentence-timing data ---
fetch(sentencesSrc)
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

// --- Reveal sentences and update progress as playback advances ---
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
    sentenceEl.scrollIntoView({ behavior: "smooth", block: "end" });
    nextSentenceIndex++;
  }
});

audio.addEventListener("ended", () => {
  playButton.textContent = "▶ Play again";
});

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
// Generic proportional stops based on story duration, rather than
// hardcoded absolute seconds (which were specific to Hanuman's pacing)
audio.addEventListener("loadedmetadata", () => {
  const duration = audio.duration;
  window.moodStops = [
    { time: 0, color: "#FDFBF7" },
    { time: duration * 0.2, color: "#FCEFE8" },
    { time: duration * 0.4, color: "#FBE4D8" },
    { time: duration * 0.6, color: "#F9DAC8" },
    { time: duration * 0.8, color: "#F5C4B3" },
    { time: duration, color: "#FDFBF7" }
  ];
});

audio.addEventListener("timeupdate", () => {
  if (!window.moodStops) return;
  const currentTime = audio.currentTime;
  let activeColor = window.moodStops[0].color;
  for (const stop of window.moodStops) {
    if (currentTime >= stop.time) {
      activeColor = stop.color;
    }
  }
  document.documentElement.style.setProperty("--mood-bg", activeColor);
});