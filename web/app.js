const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("file-input");
const countrySelect = document.getElementById("country-select");
const progressPanel = document.getElementById("progress");
const progressFill = document.getElementById("progress-bar-fill");
const progressDetail = document.getElementById("progress-detail");
const summaryEl = document.getElementById("summary");
const ownedPlatformsEl = document.getElementById("owned-platforms");
const resultsEl = document.getElementById("results");
const footerEl = document.getElementById("footer-notes");
const rematchModal = document.getElementById("rematch-modal");
const rematchTitle = document.getElementById("rematch-title");
const rematchClose = document.getElementById("rematch-close");
const rematchBody = document.getElementById("rematch-body");
const randomPickerEl = document.getElementById("random-picker");
const randomModal = document.getElementById("random-modal");
const randomClose = document.getElementById("random-close");
const randomBody = document.getElementById("random-body");

const OWNED_STORAGE_KEY = "watchlist-owned-platforms";
const WATCHED_STORAGE_KEY = "watchlist-watched";
const COUNTRY_STORAGE_KEY = "watchlist-country";
const RANDOM_POOL_STORAGE_KEY = "watchlist-random-pool";

function getRandomPoolPlatforms() {
  try {
    return JSON.parse(localStorage.getItem(RANDOM_POOL_STORAGE_KEY) || "[]");
  } catch {
    return [];
  }
}

function setRandomPoolPlatforms(list) {
  localStorage.setItem(RANDOM_POOL_STORAGE_KEY, JSON.stringify(list));
}

function getOwnedPlatforms() {
  try {
    return JSON.parse(localStorage.getItem(OWNED_STORAGE_KEY) || "[]");
  } catch {
    return [];
  }
}

function setOwnedPlatforms(list) {
  localStorage.setItem(OWNED_STORAGE_KEY, JSON.stringify(list));
}

function getWatched() {
  try {
    return JSON.parse(localStorage.getItem(WATCHED_STORAGE_KEY) || "[]");
  } catch {
    return [];
  }
}

function setWatched(list) {
  localStorage.setItem(WATCHED_STORAGE_KEY, JSON.stringify(list));
}

function toggleWatched(uri) {
  const set = new Set(getWatched());
  if (set.has(uri)) set.delete(uri);
  else set.add(uri);
  setWatched(Array.from(set));
}

let COUNTRIES_BY_CODE = {};

async function loadCountries() {
  const res = await fetch("/api/countries");
  const { countries, default: defaultCountry } = await res.json();
  const saved = localStorage.getItem(COUNTRY_STORAGE_KEY);

  countrySelect.innerHTML = "";
  for (const c of countries) {
    COUNTRIES_BY_CODE[c.code] = c.name;
    const opt = document.createElement("option");
    opt.value = c.code;
    opt.textContent = `${c.name} (${c.code})`;
    countrySelect.appendChild(opt);
  }
  countrySelect.value = saved && countries.some((c) => c.code === saved) ? saved : defaultCountry;
}

let lastCsvText = null;
let lastRawPlan = null;

countrySelect?.addEventListener("change", () => {
  localStorage.setItem(COUNTRY_STORAGE_KEY, countrySelect.value);
  if (lastCsvText) uploadCsv(lastCsvText);
});

async function init() {
  await loadCountries();
  const res = await fetch("/api/last-watchlist");
  const { csv } = await res.json();
  if (csv) {
    lastCsvText = csv;
    uploadCsv(csv);
  }
}

init();

const PLATFORM_COLORS = {
  "Netflix": "#E50914",
  "Amazon Prime Video": "#00A8E1",
  "Disney Plus": "#113CCF",
  "TV+": "#a1a1a6",
  "Apple TV+": "#a1a1a6",
  "MUBI": "#3ECF8E",
  "Crunchyroll": "#F47521",
  "HBO Max": "#8B5CF6",
  "BluTV": "#1F87F5",
  "Exxen": "#7A2FF0",
  "Gain": "#00C6AE",
};

function colorForPlatform(name) {
  if (PLATFORM_COLORS[name]) return PLATFORM_COLORS[name];
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  const hue = Math.abs(hash) % 360;
  return `hsl(${hue}, 65%, 55%)`;
}

["dragenter", "dragover"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  })
);

["dragleave", "drop"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
  })
);

dropzone.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  if (file) handleFile(file);
});

dropzone.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
  if (fileInput.files[0]) handleFile(fileInput.files[0]);
});

function handleFile(file) {
  if (!file.name.toLowerCase().endsWith(".csv")) {
    alert("Lutfen bir .csv dosyasi sec.");
    return;
  }
  const reader = new FileReader();
  reader.onload = () => {
    lastCsvText = reader.result;
    uploadCsv(lastCsvText);
  };
  reader.readAsText(file, "utf-8");
}

async function uploadCsv(csvText) {
  resultsEl.classList.add("hidden");
  summaryEl.classList.add("hidden");
  footerEl.classList.add("hidden");
  dropzone.classList.add("compact");
  progressPanel.classList.remove("hidden");
  progressFill.style.width = "6%";
  progressDetail.textContent = "Yukleniyor...";

  const res = await fetch("/api/upload", {
    method: "POST",
    body: JSON.stringify({
      csv: csvText,
      country: countrySelect.value,
      owned_platforms: getOwnedPlatforms(),
    }),
  });
  const { job_id } = await res.json();
  pollStatus(job_id);
}

let currentPollTimer = null;

function pollStatus(jobId) {
  if (currentPollTimer) clearInterval(currentPollTimer);
  const timer = (currentPollTimer = setInterval(async () => {
    const res = await fetch(`/api/status/${jobId}`);
    const job = await res.json();

    if (job.total > 0) {
      const pct = Math.max(6, Math.round((job.done / job.total) * 100));
      progressFill.style.width = pct + "%";
      progressDetail.textContent = `[${job.done}/${job.total}] ${job.current}`;
    } else if (job.status === "running") {
      progressDetail.textContent = "Cache kontrol ediliyor...";
    }

    if (job.status === "done") {
      clearInterval(timer);
      progressFill.style.width = "100%";
      setTimeout(() => {
        progressPanel.classList.add("hidden");
        lastRawPlan = job.result;
        applyAndRender();
      }, 200);
    } else if (job.status === "error") {
      clearInterval(timer);
      progressDetail.textContent = "Hata: " + job.error;
    }
  }, 400));
}

// --- Client-side yeniden hesaplama (sahip olunan platformlar + izlenenler) ---
// Sunucudan gelen ham plan (lastRawPlan) her platformun TUM filmlerini icerir.
// Sahip olunan platform / izlendi isaretlemesi degistiginde sunucuya gitmeden,
// burada aninda yeniden hesaplanir - agdaki tek maliyet ilk CSV/ulke islemidir.

function buildMovieUniverse(rawPlan) {
  const map = new Map();
  for (const movies of Object.values(rawPlan.movies_by_platform || {})) {
    for (const m of movies) map.set(m.uri, m);
  }
  for (const m of rawPlan.not_available_anywhere || []) map.set(m.uri, m);
  return map;
}

function intersectionCount(setA, setB) {
  const [small, big] = setA.size < setB.size ? [setA, setB] : [setB, setA];
  let count = 0;
  for (const x of small) if (big.has(x)) count++;
  return count;
}

function computeDerivedPlan(rawPlan) {
  const owned = new Set(getOwnedPlatforms());
  const watched = new Set(getWatched());
  const universe = buildMovieUniverse(rawPlan);
  const moviesByPlatform = rawPlan.movies_by_platform || {};
  const platforms = Object.keys(moviesByPlatform);

  const filmsByPlatform = {};
  for (const platform of platforms) {
    const uris = new Set();
    for (const movie of moviesByPlatform[platform]) {
      if (!watched.has(movie.uri)) uris.add(movie.uri);
    }
    filmsByPlatform[platform] = uris;
  }

  const alreadySet = new Set();
  const alreadyAvailable = [];
  for (const platform of platforms) {
    if (!owned.has(platform)) continue;
    for (const uri of filmsByPlatform[platform]) {
      if (!alreadySet.has(uri)) {
        alreadySet.add(uri);
        alreadyAvailable.push(universe.get(uri));
      }
    }
  }
  alreadyAvailable.sort((a, b) => a.title.localeCompare(b.title));

  const uncovered = new Set();
  for (const uris of Object.values(filmsByPlatform)) {
    for (const uri of uris) uncovered.add(uri);
  }
  for (const uri of alreadySet) uncovered.delete(uri);

  const monthlyPlan = [];
  let month = 1;
  while (uncovered.size > 0) {
    let bestPlatform = null;
    let bestCount = -1;
    for (const platform of platforms) {
      const count = intersectionCount(filmsByPlatform[platform], uncovered);
      if (count > bestCount) {
        bestCount = count;
        bestPlatform = platform;
      }
    }
    if (bestCount <= 0) break;
    const covered = [...filmsByPlatform[bestPlatform]].filter((uri) => uncovered.has(uri));
    const movies = covered.map((uri) => universe.get(uri)).sort((a, b) => a.title.localeCompare(b.title));
    monthlyPlan.push({ month, platform: bestPlatform, movies });
    for (const uri of covered) uncovered.delete(uri);
    month++;
  }

  const nowhereMovies = (rawPlan.not_available_anywhere || []).filter((m) => !watched.has(m.uri));

  const watchedMovies = Array.from(watched)
    .map((uri) => universe.get(uri))
    .filter(Boolean)
    .sort((a, b) => a.title.localeCompare(b.title));

  return {
    ...rawPlan,
    monthly_plan: monthlyPlan,
    already_available: alreadyAvailable,
    not_available_anywhere: nowhereMovies,
    owned_platforms: Array.from(owned).sort(),
    watched_movies: watchedMovies,
  };
}

function applyAndRender() {
  if (!lastRawPlan) return;
  const derived = computeDerivedPlan(lastRawPlan);
  renderSummary(derived);
  renderOwnedPanel(derived);
  renderRandomPicker(derived);
  renderResults(derived);
  renderFooterNotes(derived);
}

// --- Rastgele film oner ---

function renderRandomPicker(plan) {
  const platforms = Object.keys(plan.movies_by_platform || {});
  if (!platforms.length) {
    randomPickerEl.classList.add("hidden");
    return;
  }

  const selected = new Set(getRandomPoolPlatforms());
  randomPickerEl.innerHTML = "";

  const title = document.createElement("div");
  title.className = "owned-title";
  title.textContent = "Rastgele film onerisi hangi platformlar arasindan secilsin? (bos birakirsan tum watchlist)";
  randomPickerEl.appendChild(title);

  const chips = document.createElement("div");
  chips.className = "owned-chips";
  for (const platform of platforms) {
    const label = document.createElement("label");
    label.className = "owned-chip" + (selected.has(platform) ? " checked" : "");

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = selected.has(platform);
    checkbox.addEventListener("change", () => {
      const current = new Set(getRandomPoolPlatforms());
      if (checkbox.checked) current.add(platform);
      else current.delete(platform);
      setRandomPoolPlatforms(Array.from(current));
      label.classList.toggle("checked", checkbox.checked);
    });

    label.appendChild(checkbox);
    label.appendChild(document.createTextNode(platform));
    chips.appendChild(label);
  }
  randomPickerEl.appendChild(chips);

  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "random-btn";
  btn.textContent = "🎲 Rastgele film sec";
  btn.addEventListener("click", showRandomPick);
  randomPickerEl.appendChild(btn);

  randomPickerEl.classList.remove("hidden");
}

function randomPool() {
  if (!lastRawPlan) return [];
  const moviesByPlatform = lastRawPlan.movies_by_platform || {};
  const poolPlatforms = getRandomPoolPlatforms();
  const platformsToUse = poolPlatforms.length ? poolPlatforms : Object.keys(moviesByPlatform);
  const watched = new Set(getWatched());
  const universe = buildMovieUniverse(lastRawPlan);

  const uris = new Set();
  for (const platform of platformsToUse) {
    for (const movie of moviesByPlatform[platform] || []) {
      if (!watched.has(movie.uri)) uris.add(movie.uri);
    }
  }
  return Array.from(uris).map((uri) => universe.get(uri)).filter(Boolean);
}

function showRandomPick() {
  randomModal.classList.remove("hidden");
  const pool = randomPool();
  if (!pool.length) {
    randomBody.innerHTML = "Bu havuzda secilebilecek film kalmadi - baska platform sec ya da izlenenleri geri al.";
    return;
  }
  const movie = pool[Math.floor(Math.random() * pool.length)];
  renderRandomResult(movie);
}

function renderRandomResult(movie) {
  randomBody.innerHTML = "";

  const wrap = document.createElement("div");
  wrap.className = "random-result";

  const poster = document.createElement("div");
  poster.className = "random-poster";
  if (movie.poster) poster.style.backgroundImage = `url("${movie.poster}")`;
  wrap.appendChild(poster);

  const title = document.createElement("div");
  title.className = "random-title";
  title.textContent = `${movie.title} (${movie.year})`;
  wrap.appendChild(title);

  const links = document.createElement("div");
  links.className = "random-links";
  if (movie.offers && movie.offers.length) {
    for (const offer of movie.offers) {
      const a = document.createElement("a");
      a.className = "random-link";
      a.href = offer.url;
      a.target = "_blank";
      a.rel = "noopener";
      a.textContent = offer.platform;
      links.appendChild(a);
    }
  } else {
    links.textContent = "Bu film hicbir platformda abonelikle bulunamadi.";
  }
  wrap.appendChild(links);

  const actions = document.createElement("div");
  actions.className = "random-actions";

  const rerollBtn = document.createElement("button");
  rerollBtn.type = "button";
  rerollBtn.className = "random-btn";
  rerollBtn.textContent = "🎲 Baska film";
  rerollBtn.addEventListener("click", showRandomPick);

  const watchedBtn = document.createElement("button");
  watchedBtn.type = "button";
  watchedBtn.className = "undo-watched-btn";
  watchedBtn.textContent = "Izledim isaretle";
  watchedBtn.addEventListener("click", () => {
    toggleWatched(movie.uri);
    closeRandomModal();
    applyAndRender();
  });

  actions.appendChild(rerollBtn);
  actions.appendChild(watchedBtn);
  wrap.appendChild(actions);

  randomBody.appendChild(wrap);
}

function closeRandomModal() {
  randomModal.classList.add("hidden");
  randomBody.innerHTML = "";
}

randomClose.addEventListener("click", closeRandomModal);
randomModal.addEventListener("click", (e) => {
  if (e.target === randomModal) closeRandomModal();
});

// --- Yanlis eslesme duzeltme (rematch) modali ---

function closeRematchModal() {
  rematchModal.classList.add("hidden");
  rematchBody.innerHTML = "";
}

rematchClose.addEventListener("click", closeRematchModal);
rematchModal.addEventListener("click", (e) => {
  if (e.target === rematchModal) closeRematchModal();
});

async function openRematchModal(movie) {
  rematchModal.classList.remove("hidden");
  rematchTitle.innerHTML = `Eslesmeyi kontrol et<span class="sub">${movie.title} (${movie.year}) icin JustWatch sonuclari</span>`;
  rematchBody.innerHTML = "Araniyor...";

  const res = await fetch("/api/rematch", {
    method: "POST",
    body: JSON.stringify({ title: movie.title, year: movie.year, country: countrySelect.value }),
  });
  const { candidates, error } = await res.json();

  if (error || !candidates || !candidates.length) {
    rematchBody.textContent = error || "Sonuc bulunamadi.";
    return;
  }

  rematchBody.innerHTML = "";
  const grid = document.createElement("div");
  grid.className = "candidate-grid";
  for (const candidate of candidates) {
    const card = document.createElement("div");
    card.className = "candidate-card";

    const poster = document.createElement("div");
    poster.className = "candidate-poster";
    if (candidate.poster) poster.style.backgroundImage = `url("${candidate.poster}")`;

    const title = document.createElement("div");
    title.className = "candidate-title";
    title.textContent = candidate.matched_title;

    const year = document.createElement("div");
    year.className = "candidate-year";
    year.textContent = candidate.matched_year ?? "?";

    card.appendChild(poster);
    card.appendChild(title);
    card.appendChild(year);

    if (candidate.platforms && candidate.platforms.length) {
      const platforms = document.createElement("div");
      platforms.className = "candidate-platforms";
      platforms.textContent = candidate.platforms.join(", ");
      card.appendChild(platforms);
    }

    card.addEventListener("click", () => confirmMatch(movie, candidate));
    grid.appendChild(card);
  }
  rematchBody.appendChild(grid);
}

async function confirmMatch(movie, candidate) {
  rematchBody.innerHTML = "Kaydediliyor...";
  await fetch("/api/confirm-match", {
    method: "POST",
    body: JSON.stringify({
      uri: movie.uri,
      title: movie.title,
      year: movie.year,
      country: countrySelect.value,
      candidate,
    }),
  });
  closeRematchModal();
  if (lastCsvText) uploadCsv(lastCsvText);
}

function renderOwnedPanel(plan) {
  const platforms = Object.keys(plan.movies_by_platform || {});
  if (!platforms.length) {
    ownedPlatformsEl.classList.add("hidden");
    return;
  }

  const owned = new Set(plan.owned_platforms || []);
  ownedPlatformsEl.innerHTML = "";

  const title = document.createElement("div");
  title.className = "owned-title";
  title.textContent = "Zaten sahip oldugun platformlar (varsa isaretle, plan onlari ucretsiz saysin)";
  ownedPlatformsEl.appendChild(title);

  const chips = document.createElement("div");
  chips.className = "owned-chips";
  for (const platform of platforms) {
    const label = document.createElement("label");
    label.className = "owned-chip" + (owned.has(platform) ? " checked" : "");

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = owned.has(platform);
    checkbox.addEventListener("change", () => {
      const current = new Set(getOwnedPlatforms());
      if (checkbox.checked) current.add(platform);
      else current.delete(platform);
      setOwnedPlatforms(Array.from(current));
      label.classList.toggle("checked", checkbox.checked);
      applyAndRender();
    });

    label.appendChild(checkbox);
    label.appendChild(document.createTextNode(platform));
    chips.appendChild(label);
  }
  ownedPlatformsEl.appendChild(chips);
  ownedPlatformsEl.classList.remove("hidden");
}

function countNeedsReview(plan) {
  let count = 0;
  for (const step of plan.monthly_plan) count += step.movies.filter((m) => m.needs_review).length;
  count += (plan.already_available || []).filter((m) => m.needs_review).length;
  count += (plan.not_available_anywhere || []).filter((m) => m.needs_review).length;
  return count;
}

function renderSummary(plan) {
  const totalMovies = plan.monthly_plan.reduce((sum, s) => sum + s.movies.length, 0);
  summaryEl.innerHTML = "";

  const countryName = COUNTRIES_BY_CODE[plan.country] || plan.country;
  const badge = document.createElement("div");
  badge.className = "country-badge";
  badge.textContent = `${countryName} katalogu`;
  summaryEl.appendChild(badge);

  const stats = [
    { num: plan.monthly_plan.length, label: "ay" },
    { num: totalMovies, label: "yeni abonelikle film" },
    { num: plan.already_available.length, label: "zaten sende var" },
    { num: plan.watched_movies.length, label: "izledin" },
    { num: plan.not_available_anywhere.length, label: "hicbir yerde yok" },
    { num: countNeedsReview(plan), label: "eslesme kontrolu onerilir" },
    { num: plan.total_movies, label: "toplam watchlist" },
  ];
  for (const s of stats) {
    const div = document.createElement("div");
    div.className = "summary-stat";
    div.innerHTML = `<div class="num">${s.num}</div><div class="label">${s.label}</div>`;
    summaryEl.appendChild(div);
  }
  summaryEl.classList.remove("hidden");
}

function movieCard(movie, platformName, excludePlatforms) {
  const exclude = excludePlatforms || (platformName ? [platformName] : []);

  const a = document.createElement("a");
  a.className = "movie-card";
  const offer = (movie.offers || []).find((o) => o.platform === platformName);
  a.href = offer ? offer.url : movie.uri;
  a.target = "_blank";
  a.rel = "noopener";

  const poster = document.createElement("div");
  poster.className = "movie-poster";
  if (movie.poster) {
    poster.style.backgroundImage = `url("${movie.poster}")`;
  } else {
    poster.textContent = movie.title.charAt(0).toUpperCase();
  }

  const watchedBtn = document.createElement("button");
  watchedBtn.className = "watched-toggle";
  watchedBtn.type = "button";
  watchedBtn.title = "Izledim isaretle";
  watchedBtn.textContent = "✓";
  watchedBtn.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    toggleWatched(movie.uri);
    applyAndRender();
  });
  poster.appendChild(watchedBtn);

  if (movie.needs_review) {
    const reviewBtn = document.createElement("button");
    reviewBtn.className = "review-toggle";
    reviewBtn.type = "button";
    reviewBtn.title = "Eslesme yanlis olabilir, kontrol et";
    reviewBtn.textContent = "⚠";
    reviewBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      openRematchModal(movie);
    });
    poster.appendChild(reviewBtn);
  }

  const title = document.createElement("div");
  title.className = "movie-title";
  title.textContent = movie.title;

  const year = document.createElement("div");
  year.className = "movie-year";
  year.textContent = movie.year;

  a.appendChild(poster);
  a.appendChild(title);
  a.appendChild(year);

  if (movie.needs_review && movie.matched_title) {
    const reviewNote = document.createElement("div");
    reviewNote.className = "movie-also-on";
    reviewNote.style.color = "#ffc857";
    reviewNote.textContent = `JustWatch: ${movie.matched_title} (${movie.matched_year ?? "?"})`;
    a.appendChild(reviewNote);
  }

  const others = (movie.offers || []).map((o) => o.platform).filter((p) => !exclude.includes(p));
  if (others.length) {
    const alsoOn = document.createElement("div");
    alsoOn.className = "movie-also-on";
    alsoOn.textContent = `ayrica: ${others.join(", ")}`;
    alsoOn.title = others.join(", ");
    a.appendChild(alsoOn);
  }

  return a;
}

function renderResults(plan) {
  resultsEl.innerHTML = "";

  if (plan.already_available && plan.already_available.length) {
    const box = document.createElement("div");
    box.className = "already-section";
    const title = document.createElement("div");
    title.className = "already-title";
    title.textContent = `Zaten izleyebilirsin - ${plan.owned_platforms.join(", ")} (${plan.already_available.length} film)`;
    box.appendChild(title);

    const row = document.createElement("div");
    row.className = "movie-row";
    for (const movie of plan.already_available) {
      const hrefPlatform = (movie.offers || [])
        .map((o) => o.platform)
        .find((p) => plan.owned_platforms.includes(p));
      row.appendChild(movieCard(movie, hrefPlatform, plan.owned_platforms));
    }
    box.appendChild(row);
    resultsEl.appendChild(box);
  }

  for (const step of plan.monthly_plan) {
    const color = colorForPlatform(step.platform);

    const section = document.createElement("section");
    section.className = "platform-section";

    const header = document.createElement("div");
    header.className = "platform-header";
    header.innerHTML = `
      <span class="platform-month">Ay ${step.month}</span>
      <span class="platform-name">${step.platform}</span>
      <span class="platform-count">${step.movies.length} film</span>
    `;
    section.appendChild(header);

    const bar = document.createElement("div");
    bar.className = "platform-bar";
    bar.style.background = color;
    section.appendChild(bar);

    const row = document.createElement("div");
    row.className = "movie-row";
    for (const movie of step.movies) row.appendChild(movieCard(movie, step.platform));
    section.appendChild(row);

    resultsEl.appendChild(section);
  }

  if (plan.not_available_anywhere.length) {
    const box = document.createElement("div");
    box.className = "nowhere-section";
    const title = document.createElement("div");
    title.className = "nowhere-title";
    title.textContent = `Hicbir platformda abonelikle bulunamadi (${plan.not_available_anywhere.length})`;
    const grid = document.createElement("div");
    grid.className = "nowhere-grid";
    for (const movie of plan.not_available_anywhere) {
      const chip = document.createElement("span");
      chip.className = "nowhere-chip" + (movie.needs_review ? " needs-review" : "");
      const label = movie.needs_review ? " ⚠" : "";
      chip.innerHTML = `${movie.title} <span class="yr">${movie.year}</span>${label}`;
      if (movie.needs_review) {
        chip.title = "Eslesme yanlis olabilir, kontrol et";
        chip.addEventListener("click", () => openRematchModal(movie));
      }
      grid.appendChild(chip);
    }
    box.appendChild(title);
    box.appendChild(grid);
    resultsEl.appendChild(box);
  }

  resultsEl.classList.remove("hidden");
}

function renderFooterNotes(plan) {
  footerEl.innerHTML = "";
  let any = false;

  if (plan.watched_movies && plan.watched_movies.length) {
    any = true;
    const box = document.createElement("details");
    box.className = "note-box";
    const summary = document.createElement("summary");
    summary.textContent = `Izledigin filmler (${plan.watched_movies.length})`;
    box.appendChild(summary);
    const ul = document.createElement("ul");
    for (const m of plan.watched_movies) {
      const li = document.createElement("li");
      li.textContent = `${m.title} (${m.year}) `;
      const undoBtn = document.createElement("button");
      undoBtn.className = "undo-watched-btn";
      undoBtn.type = "button";
      undoBtn.textContent = "geri al";
      undoBtn.addEventListener("click", () => {
        toggleWatched(m.uri);
        applyAndRender();
      });
      li.appendChild(undoBtn);
      ul.appendChild(li);
    }
    box.appendChild(ul);
    footerEl.appendChild(box);
  }

  if (plan.removed_from_watchlist.length) {
    any = true;
    const box = document.createElement("details");
    box.className = "note-box";
    box.innerHTML = `<summary>Watchlist'ten cikmis (${plan.removed_from_watchlist.length})</summary>
      <ul>${plan.removed_from_watchlist.map((m) => `<li>${m.title} (${m.year})</li>`).join("")}</ul>`;
    footerEl.appendChild(box);
  }

  if (plan.errors.length) {
    any = true;
    const box = document.createElement("details");
    box.className = "note-box error";
    box.innerHTML = `<summary>Eslestirilemeyen filmler (${plan.errors.length})</summary>
      <ul>${plan.errors.map((e) => `<li>${e.title} (${e.year}) &mdash; ${e.error}</li>`).join("")}</ul>`;
    footerEl.appendChild(box);
  }

  if (any) footerEl.classList.remove("hidden");
}
