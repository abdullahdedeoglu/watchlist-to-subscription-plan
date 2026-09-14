const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("file-input");
const langSelect = document.getElementById("lang-select");
const countrySelect = document.getElementById("country-select");
const progressPanel = document.getElementById("progress");
const progressFill = document.getElementById("progress-bar-fill");
const progressDetail = document.getElementById("progress-detail");
const summaryEl = document.getElementById("summary");
const resultsEl = document.getElementById("results");
const controlSideEl = document.getElementById("control-side");
const controlMainEl = document.getElementById("control-main");
const footerEl = document.getElementById("footer-notes");
const rematchModal = document.getElementById("rematch-modal");
const rematchTitle = document.getElementById("rematch-title");
const rematchClose = document.getElementById("rematch-close");
const rematchBody = document.getElementById("rematch-body");
const rematchSearchInput = document.getElementById("rematch-search-input");
const rematchSearchBtn = document.getElementById("rematch-search-btn");
const randomModal = document.getElementById("random-modal");
const randomClose = document.getElementById("random-close");
const randomBody = document.getElementById("random-body");
const randomPoolPanelEl = document.getElementById("random-pool-panel");
const randomPoolChipsEl = document.getElementById("random-pool-chips");

const OWNED_STORAGE_KEY = "watchlist-owned-platforms";
const WATCHED_STORAGE_KEY = "watchlist-watched";
const COUNTRY_STORAGE_KEY = "watchlist-country";
const RANDOM_POOL_STORAGE_KEY = "watchlist-random-pool";
const LANG_STORAGE_KEY = "watchlist-lang";
const LANG_MANUAL_STORAGE_KEY = "watchlist-lang-manual";

// --- Cok dilli metinler ---
// Yeni bir dil eklerken: asagidaki her anahtara o dilde bir deger ekle,
// lang-select'e <option> ekle, ve gerekirse COUNTRY_DEFAULT_LANG'a
// hangi ulkelerin o dili varsayilan aldigini ekle.
const I18N = {
  tr: {
    pageTitle: "Watchlist Planı",
    headerTitle: "Watchlist → Abonelik Planı",
    subtitle: "Letterboxd watchlist CSV'ni sürükle, hangi sırada hangi platforma abone olman gerektiğini gör.",
    howtoSummary: "Nasıl kullanılır?",
    howtoStep1: "Letterboxd'da <strong>Ayarlar → Import &amp; Export → Export Data</strong> yoluna git ve watchlist'ini dışa aktar (bir <code>.zip</code> dosyası iner).",
    howtoStep2: "ZIP'i aç, içinden <code>watchlist.csv</code> dosyasını çıkar.",
    howtoStep3: "O CSV dosyasını aşağıdaki alana sürükle-bırak (ya da alana tıkla ve dosyayı seç).",
    howtoStep4: "Üst taraftan ülkeni seç — varsayılan Türkiye. JustWatch'ta o ülkedeki abonelik seçenekleri aranır, biraz sürebilir.",
    howtoStep5: "Arama bitince, hangi sırayla hangi platforma abone olursan watchlist'ini en hızlı bitireceğini görürsün.",
    howtoStep6: "Poster'in sağ üstündeki <strong>&check;</strong> izledim işaretler, sol üstteki sarı <strong>&#9888;</strong> ise eşleşmeyi kontrol etmeni önerir.",
    howtoNote: "Watchlist'in bir kere yüklendikten sonra hatırlanır, sayfayı tekrar açtığında otomatik gelir. Güncellemek için yeni CSV'yi tekrar sürükleyip bırakman yeterli.",
    devModeLabel: "Geliştirici modu",
    devClearBtn: "Cache'i temizle",
    devClearBtnWorking: "Temizleniyor...",
    devClearConfirm: "JustWatch eşleştirme cache'i tamamen silinsin mi? Bir sonraki aramada tüm filmler sıfırdan aranacak.",
    countryLabel: "Ülke",
    langLabel: "Dil",
    dropzoneText: "CSV dosyasını buraya sürükle",
    dropzoneSub: "Ya da tıkla ve seç",
    progressTitle: "JustWatch'ta aranıyor…",
    progressLoading: "Yükleniyor...",
    progressCacheCheck: "Cache kontrol ediliyor...",
    progressError: "Hata: ",
    fileTypeAlert: "Lütfen bir .csv dosyası seç.",
    randomPoolLabel: "Rastgele film önerisi hangi platformlar arasından seçilsin? (boş bırakırsan tüm watchlist)",
    randomPickBtn: "🎲 Rastgele film seç",
    randomTriggerTitle: "Rastgele film seç",
    randomEmptyPool: "Bu havuzda seçilebilecek film kalmadı - başka platform seç ya da izlenenleri geri al.",
    randomNoOffers: "Bu film hiçbir platformda abonelikle bulunamadı.",
    randomRerollBtn: "🎲 Başka film",
    markWatchedBtn: "İzledim işaretle",
    rematchTitlePrefix: "Eşleşmeyi kontrol et",
    rematchSubtitle: (m) => `${m.title} (${m.year}) için JustWatch sonuçları`,
    rematchSearching: "Aranıyor...",
    rematchNoResults: "Sonuç bulunamadı. Farklı bir isimle tekrar dene.",
    rematchSaving: "Kaydediliyor...",
    rematchSearchPlaceholder: "Farklı bir isimle JustWatch'ta ara...",
    rematchSearchBtn: "Ara",
    randomModalTitle: "Rastgele Film",
    sidebarTitle: "Abonelik Sırası",
    ownedBadge: "Sahipsin",
    ownedCheckTitle: "Bu platforma zaten sahipsen işaretle",
    statPlatformCount: "Platform",
    statNewMovies: "Yeni abonelikle film",
    statAlreadyOwned: "Zaten sende var",
    statWatched: "İzledin",
    statRentBuy: "Kirala/satın al ile izlenebilir",
    statNowhere: "Hiçbir yerde yok",
    statNeedsReview: "Eşleşme kontrolü önerilir",
    statTotal: "Toplam watchlist",
    catalogBadge: (name) => `${name} kataloğu`,
    watchedToggleTitle: "İzledim işaretle",
    reviewToggleTitle: "Eşleşme yanlış olabilir, kontrol et",
    justwatchMatchNote: (m) => `JustWatch: ${m.matched_title} (${m.matched_year ?? "?"})`,
    alsoOnPrefix: "Ayrıca:",
    alreadyAvailableTitle: (platforms, count) => `Zaten izleyebilirsin - ${platforms} (${count} film)`,
    orderLabel: (n) => `${n}. sıra`,
    movieCountLabel: (n) => `${n} film`,
    rentBuyTitle: (n) => `Kirala/Satın Al ile İzleyebilirsin (${n})`,
    rentLabel: "Kirala",
    buyLabel: "Satın Al",
    nowhereTitle: (n) => `Hiçbir platformda abonelikle bulunamadı (${n})`,
    watchedListTitle: (n) => `İzlediğin filmler (${n})`,
    undoBtn: "Geri al",
    removedTitle: (n) => `Watchlist'ten çıkmış (${n})`,
    errorsTitle: (n) => `Eşleştirilemeyen filmler (${n})`,
  },
  en: {
    pageTitle: "Watchlist Plan",
    headerTitle: "Watchlist → Subscription Plan",
    subtitle: "Drag in your Letterboxd watchlist CSV and see which order to subscribe to which platform.",
    howtoSummary: "How does this work?",
    howtoStep1: "Go to <strong>Settings → Import &amp; Export → Export Data</strong> on Letterboxd and export your watchlist (a <code>.zip</code> file downloads).",
    howtoStep2: "Unzip it and pull out the <code>watchlist.csv</code> file.",
    howtoStep3: "Drag that CSV file onto the box below (or click it and choose the file).",
    howtoStep4: "Pick your country above — Turkey by default. Subscription options in that country are searched on JustWatch, which can take a bit.",
    howtoStep5: "Once the search finishes, you'll see which order to subscribe to which platform to get through your watchlist fastest.",
    howtoStep6: "The <strong>&check;</strong> on a poster's top-right marks it watched; the yellow <strong>&#9888;</strong> on the top-left means the match is worth double-checking.",
    howtoNote: "Your watchlist is remembered after the first upload and loads automatically next time you open the page. To update it, just drag in a new CSV.",
    devModeLabel: "Developer mode",
    devClearBtn: "Clear cache",
    devClearBtnWorking: "Clearing...",
    devClearConfirm: "Clear the entire JustWatch match cache? Every movie will be searched from scratch next time.",
    countryLabel: "Country",
    langLabel: "Language",
    dropzoneText: "Drag your CSV file here",
    dropzoneSub: "Or click to choose",
    progressTitle: "Searching JustWatch…",
    progressLoading: "Loading...",
    progressCacheCheck: "Checking cache...",
    progressError: "Error: ",
    fileTypeAlert: "Please choose a .csv file.",
    randomPoolLabel: "Which platforms should random picks come from? (leave empty for the whole watchlist)",
    randomPickBtn: "🎲 Pick a random movie",
    randomTriggerTitle: "Pick a random movie",
    randomEmptyPool: "No movies left in this pool - pick another platform or undo some watched movies.",
    randomNoOffers: "This movie isn't available with a subscription anywhere.",
    randomRerollBtn: "🎲 Another one",
    markWatchedBtn: "Mark as watched",
    rematchTitlePrefix: "Check the match",
    rematchSubtitle: (m) => `JustWatch results for ${m.title} (${m.year})`,
    rematchSearching: "Searching...",
    rematchNoResults: "No results found. Try a different search term.",
    rematchSaving: "Saving...",
    rematchSearchPlaceholder: "Search JustWatch with a different name...",
    rematchSearchBtn: "Search",
    randomModalTitle: "Random Movie",
    sidebarTitle: "Subscription Order",
    ownedBadge: "Owned",
    ownedCheckTitle: "Check if you already have this platform",
    statPlatformCount: "Platforms",
    statNewMovies: "Movies with new subs",
    statAlreadyOwned: "Already have",
    statWatched: "Watched",
    statRentBuy: "Rent/buy available",
    statNowhere: "Unavailable anywhere",
    statNeedsReview: "Matches to review",
    statTotal: "Total watchlist",
    catalogBadge: (name) => `${name} catalog`,
    watchedToggleTitle: "Mark as watched",
    reviewToggleTitle: "Match might be wrong, check it",
    justwatchMatchNote: (m) => `JustWatch: ${m.matched_title} (${m.matched_year ?? "?"})`,
    alsoOnPrefix: "Also on:",
    alreadyAvailableTitle: (platforms, count) => `You can already watch these - ${platforms} (${count} movies)`,
    orderLabel: (n) => `Step ${n}`,
    movieCountLabel: (n) => `${n} movies`,
    rentBuyTitle: (n) => `Available to Rent/Buy (${n})`,
    rentLabel: "Rent",
    buyLabel: "Buy",
    nowhereTitle: (n) => `Not available with a subscription anywhere (${n})`,
    watchedListTitle: (n) => `Movies you've watched (${n})`,
    undoBtn: "Undo",
    removedTitle: (n) => `Removed from your watchlist (${n})`,
    errorsTitle: (n) => `Movies that couldn't be matched (${n})`,
  },
};

// Hangi ulkeler hangi arayuz dilini varsayilan alsin (kullanici elle dil
// secmediyse). Yeni bir arayuz dili eklendiginde buraya ilgili ulke
// kodlarini eklemek yeterli - eklenmeyen ulkeler "en"e duser.
const COUNTRY_DEFAULT_LANG = { TR: "tr" };

let currentLang = "tr";

function t(key, ...args) {
  const entry = (I18N[currentLang] || I18N.en)[key];
  return typeof entry === "function" ? entry(...args) : entry;
}

function applyStaticTranslations() {
  document.documentElement.lang = currentLang;
  for (const el of document.querySelectorAll("[data-i18n]")) {
    el.textContent = t(el.dataset.i18n);
  }
  for (const el of document.querySelectorAll("[data-i18n-html]")) {
    el.innerHTML = t(el.dataset.i18nHtml);
  }
  for (const el of document.querySelectorAll("[data-i18n-placeholder]")) {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  }
}

function setLang(lang, manual) {
  currentLang = I18N[lang] ? lang : "en";
  if (langSelect) langSelect.value = currentLang;
  if (manual) {
    localStorage.setItem(LANG_STORAGE_KEY, currentLang);
    localStorage.setItem(LANG_MANUAL_STORAGE_KEY, "1");
  }
  applyStaticTranslations();
  renderCountryOptions();
  if (lastRawPlan) applyAndRender();
}

langSelect?.addEventListener("change", () => setLang(langSelect.value, true));

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

let COUNTRIES_LIST = [];
let DEFAULT_COUNTRY_CODE = "TR";

function countryDisplayName(code) {
  const c = COUNTRIES_LIST.find((c) => c.code === code);
  if (!c) return code;
  return c[`name_${currentLang}`] || c.name_en || c.name_tr;
}

function renderCountryOptions() {
  if (!COUNTRIES_LIST.length) return;
  const current = countrySelect.value;
  countrySelect.innerHTML = "";
  for (const c of COUNTRIES_LIST) {
    const opt = document.createElement("option");
    opt.value = c.code;
    opt.textContent = `${countryDisplayName(c.code)} (${c.code})`;
    countrySelect.appendChild(opt);
  }
  countrySelect.value = current || DEFAULT_COUNTRY_CODE;
}

async function loadCountries() {
  const res = await fetch("/api/countries");
  const { countries, default: defaultCountry } = await res.json();
  COUNTRIES_LIST = countries;
  DEFAULT_COUNTRY_CODE = defaultCountry;

  const savedCountry = localStorage.getItem(COUNTRY_STORAGE_KEY);
  const initialCountry = savedCountry && countries.some((c) => c.code === savedCountry) ? savedCountry : defaultCountry;

  const savedLang = localStorage.getItem(LANG_STORAGE_KEY);
  const langIsManual = localStorage.getItem(LANG_MANUAL_STORAGE_KEY) === "1";
  const initialLang = langIsManual && savedLang ? savedLang : (COUNTRY_DEFAULT_LANG[initialCountry] || "en");

  currentLang = I18N[initialLang] ? initialLang : "en";
  renderCountryOptions();
  countrySelect.value = initialCountry;
  if (langSelect) langSelect.value = currentLang;
  applyStaticTranslations();
}

let lastCsvText = null;
let lastRawPlan = null;

countrySelect?.addEventListener("change", () => {
  localStorage.setItem(COUNTRY_STORAGE_KEY, countrySelect.value);
  // Dil daha once elle secilmediyse, ulkeye gore otomatik dil ayarla.
  if (localStorage.getItem(LANG_MANUAL_STORAGE_KEY) !== "1") {
    setLang(COUNTRY_DEFAULT_LANG[countrySelect.value] || "en", false);
  }
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

// --- GELISTIRME ARACI - sadece ?dev=1 ile gorunur ---
// Gelistirme bitince bu blogu, index.html'deki #dev-tools bolumunu ve
// server.py'daki /api/clear-cache endpoint'ini birlikte kaldir.
if (new URLSearchParams(location.search).has("dev")) {
  const devTools = document.getElementById("dev-tools");
  const devClearBtn = document.getElementById("dev-clear-cache-btn");
  devTools?.classList.remove("hidden");
  devClearBtn?.addEventListener("click", async () => {
    if (!confirm(t("devClearConfirm"))) return;
    devClearBtn.disabled = true;
    devClearBtn.textContent = t("devClearBtnWorking");
    await fetch("/api/clear-cache", { method: "POST" });
    devClearBtn.disabled = false;
    devClearBtn.textContent = t("devClearBtn");
    if (lastCsvText) uploadCsv(lastCsvText);
  });
}

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

// Kumanda paneli: soldaki sira listesi (bilet + kisayol satirlari) tek bir
// platformu/kategoriyi secili tutar, sag tarafta sadece onun icerigi gorunur.
// Boylece sonuclar tek uzun bir sutunda asagi kaymak yerine, sabit yukseklikli
// bir panelde gezilir. `activePanelKey` render'lar arasinda hangi sekmenin
// secili kaldigini hatirlar (izlendi/sahip-olunan degisince sifirlanmaz).
let activePanelKey = null;

// Tek, duz bir platform listesi - grup yok. Sira, her platformun toplam
// (izlenmemis) film sayisina gore sabittir ve sahip-olma isaretlemesinden
// ETKILENMEZ, boylece bir platformu sahiplendiginde yeri degismez, kaybolmaz.
// Bilet uzerindeki numara herhangi bir "en iyi sira" algoritmasindan degil,
// listedeki sirasindan geliyor (sahip olunanlar sayilmadan 1'den basliyor) -
// boylece numaralar hep bosluksuz ve listeyle ayni sirada gorunur.
function controlRoomEntries(plan) {
  const owned = new Set(plan.owned_platforms || []);

  // Kategori kisayollari (zaten sende var / kirala-satin al / hicbir yerde
  // yok) listenin EN USTUNDE - ozellikle "zaten sende var" bir platformu
  // sahiplendiginde aninda belirir, asagi kaydirmadan gorunsun diye.
  const entries = [];
  if (plan.already_available && plan.already_available.length) {
    entries.push({ key: "already", type: "already" });
  }
  if (plan.rent_buy_available && plan.rent_buy_available.length) {
    entries.push({ key: "rentbuy", type: "rentbuy" });
  }
  if (plan.not_available_anywhere.length) {
    entries.push({ key: "nowhere", type: "nowhere" });
  }

  const platforms = Object.keys(plan.platform_movies || {})
    .filter((p) => (plan.platform_movies[p] || []).length)
    .sort((a, b) => plan.platform_movies[b].length - plan.platform_movies[a].length);

  let counter = 0;
  for (const platform of platforms) {
    const isOwned = owned.has(platform);
    if (!isOwned) counter++;
    entries.push({
      key: `platform:${platform}`,
      type: "platform",
      platform,
      movies: plan.platform_movies[platform],
      owned: isOwned,
      order: isOwned ? null : counter,
    });
  }
  return entries;
}

function toggleOwnedPlatform(platform, isOwned) {
  const current = new Set(getOwnedPlatforms());
  if (isOwned) current.add(platform);
  else current.delete(platform);
  setOwnedPlatforms(Array.from(current));
  applyAndRender();
}

function sidebarRow(entry, plan) {
  if (entry.type === "platform") {
    const leftSlot = entry.owned
      ? `<span class="hticket-owned-badge">${t("ownedBadge")}</span>`
      : entry.order
      ? `<span class="hticket-order">${String(entry.order).padStart(2, "0")}</span>`
      : "<span></span>";
    const el = document.createElement("div");
    el.className = "hticket";
    el.innerHTML = `
      <div class="hticket-top">
        ${leftSlot}
        <span class="platform-count">${t("movieCountLabel", entry.movies.length)}</span>
      </div>
      <div class="hticket-perf"></div>
      <div class="hticket-bottom">
        <input type="checkbox" class="hticket-owned-check" title="${t("ownedCheckTitle")}" ${entry.owned ? "checked" : ""} />
        <span class="hticket-name">${entry.platform}</span>
      </div>
    `;
    const checkbox = el.querySelector(".hticket-owned-check");
    checkbox.addEventListener("click", (e) => e.stopPropagation());
    checkbox.addEventListener("change", () => toggleOwnedPlatform(entry.platform, checkbox.checked));
    return el;
  }

  const label = { already: t("statAlreadyOwned"), rentbuy: t("statRentBuy"), nowhere: t("statNowhere") }[entry.type];
  const count = {
    already: (plan.already_available || []).length,
    rentbuy: (plan.rent_buy_available || []).length,
    nowhere: plan.not_available_anywhere.length,
  }[entry.type];
  const el = document.createElement("div");
  el.className = "side-link";
  el.innerHTML = `<span>${label}</span><b>${count}</b>`;
  return el;
}

function panelForEntry(entry, plan) {
  const panel = document.createElement("div");
  panel.className = "panel active";

  const head = document.createElement("div");
  head.className = "platform-header";

  if (entry.type === "platform") {
    const badge = entry.owned
      ? `<span class="platform-month cat-positive">${t("ownedBadge")}</span>`
      : entry.order
      ? `<span class="platform-month">${t("orderLabel", entry.order)}</span>`
      : "";
    head.innerHTML = `
      ${badge}
      <span class="platform-name">${entry.platform}</span>
      <span class="platform-count">${t("movieCountLabel", entry.movies.length)}</span>
    `;
    panel.appendChild(head);
    const bar = document.createElement("div");
    bar.className = "platform-bar";
    bar.style.background = colorForPlatform(entry.platform);
    panel.appendChild(bar);
    const grid = document.createElement("div");
    grid.className = "control-grid";
    for (const movie of entry.movies) grid.appendChild(movieCard(movie, entry.platform));
    panel.appendChild(grid);
    return panel;
  }

  if (entry.type === "already") {
    head.innerHTML = `<span class="platform-name cat-positive">${t("statAlreadyOwned")}</span>`;
    panel.appendChild(head);
    const sub = document.createElement("p");
    sub.className = "control-main-sub";
    sub.textContent = t("alreadyAvailableTitle", plan.owned_platforms.join(", "), plan.already_available.length);
    panel.appendChild(sub);
    const grid = document.createElement("div");
    grid.className = "control-grid";
    for (const movie of plan.already_available) {
      const hrefPlatform = (movie.offers || [])
        .map((o) => o.platform)
        .find((p) => plan.owned_platforms.includes(p));
      grid.appendChild(movieCard(movie, hrefPlatform, plan.owned_platforms));
    }
    panel.appendChild(grid);
    return panel;
  }

  if (entry.type === "rentbuy") {
    head.innerHTML = `<span class="platform-name cat-warn">${t("statRentBuy")}</span>`;
    panel.appendChild(head);
    const sub = document.createElement("p");
    sub.className = "control-main-sub";
    sub.textContent = t("rentBuyTitle", plan.rent_buy_available.length);
    panel.appendChild(sub);
    const grid = document.createElement("div");
    grid.className = "control-grid";
    for (const movie of plan.rent_buy_available) grid.appendChild(rentBuyCard(movie));
    panel.appendChild(grid);
    return panel;
  }

  // nowhere
  head.innerHTML = `<span class="platform-name cat-dim">${t("statNowhere")}</span>`;
  panel.appendChild(head);
  const sub = document.createElement("p");
  sub.className = "control-main-sub";
  sub.textContent = t("nowhereTitle", plan.not_available_anywhere.length);
  panel.appendChild(sub);
  const grid = document.createElement("div");
  grid.className = "nowhere-grid";
  for (const movie of plan.not_available_anywhere) {
    const chip = document.createElement("span");
    chip.className = "nowhere-chip" + (movie.needs_review ? " needs-review" : "");
    const label = movie.needs_review ? " ⚠" : "";
    chip.innerHTML = `${movie.title} <span class="yr">${movie.year}</span>${label}`;
    if (movie.needs_review) {
      chip.title = t("reviewToggleTitle");
      chip.addEventListener("click", () => openRematchModal(movie));
    }
    grid.appendChild(chip);
  }
  panel.appendChild(grid);
  return panel;
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
    alert(t("fileTypeAlert"));
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
  activePanelKey = null;
  resultsEl.classList.add("hidden");
  summaryEl.classList.add("hidden");
  footerEl.classList.add("hidden");
  dropzone.classList.add("compact");
  progressPanel.classList.remove("hidden");
  progressFill.style.width = "6%";
  progressDetail.textContent = t("progressLoading");

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
      progressDetail.textContent = t("progressCacheCheck");
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
      progressDetail.textContent = t("progressError") + job.error;
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

  // Sira almasa da (baska platformlarda zaten kapsandigi veya sahip olundugu
  // icin), her platform kendi kataloguyla ayri ayri gezilebilsin diye tam
  // (izlenmemis) film listesini de sakliyoruz.
  const platformMovies = {};
  for (const platform of platforms) {
    platformMovies[platform] = [...filmsByPlatform[platform]]
      .map((uri) => universe.get(uri))
      .sort((a, b) => a.title.localeCompare(b.title));
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

  // Abonelikle hicbir yerde bulunamayan filmler icin: kirala/satin al secenegi
  // olanlari ayri bir bolume, hic secenegi olmayanlari "hicbir yerde yok"a ayir.
  const noSubscription = (rawPlan.not_available_anywhere || []).filter((m) => !watched.has(m.uri));
  const rentBuyMovies = noSubscription.filter((m) => (m.rent_buy_offers || []).length > 0);
  const nowhereMovies = noSubscription.filter((m) => !(m.rent_buy_offers || []).length);

  const watchedMovies = Array.from(watched)
    .map((uri) => universe.get(uri))
    .filter(Boolean)
    .sort((a, b) => a.title.localeCompare(b.title));

  return {
    ...rawPlan,
    monthly_plan: monthlyPlan,
    already_available: alreadyAvailable,
    not_available_anywhere: nowhereMovies,
    rent_buy_available: rentBuyMovies,
    owned_platforms: Array.from(owned).sort(),
    watched_movies: watchedMovies,
    platform_movies: platformMovies,
  };
}

function applyAndRender() {
  if (!lastRawPlan) return;
  const derived = computeDerivedPlan(lastRawPlan);
  renderSummary(derived);
  renderRandomPoolChips(derived);
  renderResults(derived);
  renderFooterNotes(derived);
}

// --- Rastgele film oner ---
// Tetikleyici buton artik sidebar'in sag ust kosesinde (bkz. renderResults);
// hangi platformlardan secilecegini belirleyen tikler ise rastgele-film
// modalinin icinde, katlanir bir panelde duruyor - sayfada ayrica yer kaplamaz.

function renderRandomPoolChips(plan) {
  const platforms = Object.keys(plan.movies_by_platform || {});
  if (!platforms.length) {
    randomPoolPanelEl.classList.add("hidden");
    return;
  }

  const selected = new Set(getRandomPoolPlatforms());
  randomPoolChipsEl.innerHTML = "";

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
      showRandomPick();
    });

    label.appendChild(checkbox);
    label.appendChild(document.createTextNode(platform));
    randomPoolChipsEl.appendChild(label);
  }

  randomPoolPanelEl.classList.remove("hidden");
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
    randomBody.innerHTML = t("randomEmptyPool");
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
    links.textContent = t("randomNoOffers");
  }
  wrap.appendChild(links);

  const actions = document.createElement("div");
  actions.className = "random-actions";

  const rerollBtn = document.createElement("button");
  rerollBtn.type = "button";
  rerollBtn.className = "random-btn";
  rerollBtn.textContent = t("randomRerollBtn");
  rerollBtn.addEventListener("click", showRandomPick);

  const watchedBtn = document.createElement("button");
  watchedBtn.type = "button";
  watchedBtn.className = "undo-watched-btn";
  watchedBtn.textContent = t("markWatchedBtn");
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

let rematchMovie = null;

function closeRematchModal() {
  rematchModal.classList.add("hidden");
  rematchBody.innerHTML = "";
  rematchSearchInput.value = "";
  rematchMovie = null;
}

rematchClose.addEventListener("click", closeRematchModal);
rematchModal.addEventListener("click", (e) => {
  if (e.target === rematchModal) closeRematchModal();
});

rematchSearchBtn.addEventListener("click", () => {
  const query = rematchSearchInput.value.trim();
  if (query && rematchMovie) runRematchSearch(rematchMovie, query);
});
rematchSearchInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    rematchSearchBtn.click();
  }
});

function openRematchModal(movie) {
  rematchMovie = movie;
  rematchModal.classList.remove("hidden");
  rematchTitle.innerHTML = `${t("rematchTitlePrefix")}<span class="sub">${t("rematchSubtitle", movie)}</span>`;
  rematchSearchInput.value = movie.title;
  runRematchSearch(movie, movie.title);
}

async function runRematchSearch(movie, query) {
  rematchBody.innerHTML = t("rematchSearching");

  const res = await fetch("/api/rematch", {
    method: "POST",
    body: JSON.stringify({ title: query, year: movie.year, country: countrySelect.value }),
  });
  const { candidates, error } = await res.json();

  if (error || !candidates || !candidates.length) {
    rematchBody.textContent = error || t("rematchNoResults");
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
  rematchBody.innerHTML = t("rematchSaving");
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


function countNeedsReview(plan) {
  let count = 0;
  for (const step of plan.monthly_plan) count += step.movies.filter((m) => m.needs_review).length;
  count += (plan.already_available || []).filter((m) => m.needs_review).length;
  count += (plan.not_available_anywhere || []).filter((m) => m.needs_review).length;
  count += (plan.rent_buy_available || []).filter((m) => m.needs_review).length;
  return count;
}

function renderSummary(plan) {
  const totalMovies = plan.monthly_plan.reduce((sum, s) => sum + s.movies.length, 0);
  summaryEl.innerHTML = "";

  const countryName = countryDisplayName(plan.country);
  const badge = document.createElement("div");
  badge.className = "country-badge";
  badge.textContent = t("catalogBadge", countryName);
  summaryEl.appendChild(badge);

  const secondaryStats = [
    { num: plan.monthly_plan.length, label: t("statPlatformCount") },
    { num: totalMovies, label: t("statNewMovies") },
    { num: plan.already_available.length, label: t("statAlreadyOwned") },
    { num: plan.watched_movies.length, label: t("statWatched") },
    { num: plan.rent_buy_available.length, label: t("statRentBuy") },
    { num: plan.not_available_anywhere.length, label: t("statNowhere") },
    { num: countNeedsReview(plan), label: t("statNeedsReview") },
    { num: plan.total_movies, label: t("statTotal") },
  ];
  const row = document.createElement("div");
  row.className = "stat-row-secondary";
  for (const s of secondaryStats) {
    const div = document.createElement("div");
    div.className = "summary-stat-sm";
    div.innerHTML = `<span class="num">${s.num}</span><span class="label">${s.label}</span>`;
    row.appendChild(div);
  }
  summaryEl.appendChild(row);

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
  watchedBtn.title = t("watchedToggleTitle");
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
    reviewBtn.title = t("reviewToggleTitle");
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
    reviewNote.textContent = t("justwatchMatchNote", movie);
    a.appendChild(reviewNote);
  }

  const others = (movie.offers || []).map((o) => o.platform).filter((p) => !exclude.includes(p));
  if (others.length) {
    const alsoOn = document.createElement("div");
    alsoOn.className = "movie-also-on";
    alsoOn.textContent = `${t("alsoOnPrefix")} ${others.join(", ")}`;
    alsoOn.title = others.join(", ");
    a.appendChild(alsoOn);
  }

  return a;
}

function rentBuyCard(movie) {
  const card = document.createElement("div");
  card.className = "movie-card";

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
  watchedBtn.title = t("watchedToggleTitle");
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
    reviewBtn.title = t("reviewToggleTitle");
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

  card.appendChild(poster);
  card.appendChild(title);
  card.appendChild(year);

  if (movie.needs_review && movie.matched_title) {
    const reviewNote = document.createElement("div");
    reviewNote.className = "movie-also-on";
    reviewNote.style.color = "#ffc857";
    reviewNote.textContent = t("justwatchMatchNote", movie);
    card.appendChild(reviewNote);
  }

  const prices = document.createElement("div");
  prices.className = "rentbuy-prices";
  const sorted = [...(movie.rent_buy_offers || [])].sort(
    (a, b) => (a.price_value ?? Infinity) - (b.price_value ?? Infinity)
  );
  for (const offer of sorted) {
    const link = document.createElement("a");
    link.className = "rentbuy-chip";
    link.href = offer.url;
    link.target = "_blank";
    link.rel = "noopener";
    const typeLabel = t(offer.type === "RENT" ? "rentLabel" : "buyLabel");
    link.textContent = offer.price ? `${offer.platform} ${typeLabel} · ${offer.price}` : `${offer.platform} ${typeLabel}`;
    prices.appendChild(link);
  }
  card.appendChild(prices);

  return card;
}

function renderResults(plan) {
  const entries = controlRoomEntries(plan);

  if (!entries.length) {
    resultsEl.classList.add("hidden");
    return;
  }

  if (!activePanelKey || !entries.some((e) => e.key === activePanelKey)) {
    // Ilk acilista kategori kisayollari degil, gercek abonelik onerisi
    // (ilk platform bileti) secili gelsin - kategoriler sadece listede en
    // ustte gorunsun diye orada, varsayilan odak yine plan onerisinde.
    const firstPlatform = entries.find((e) => e.type === "platform");
    activePanelKey = (firstPlatform || entries[0]).key;
  }

  controlSideEl.innerHTML = "";
  controlMainEl.innerHTML = "";

  const sideHeader = document.createElement("div");
  sideHeader.className = "control-side-header";
  const sideTitle = document.createElement("div");
  sideTitle.className = "control-side-title";
  sideTitle.textContent = t("sidebarTitle");
  sideHeader.appendChild(sideTitle);
  const randomBtn = document.createElement("button");
  randomBtn.type = "button";
  randomBtn.className = "random-trigger-btn";
  randomBtn.title = t("randomTriggerTitle");
  randomBtn.textContent = "🎲";
  randomBtn.addEventListener("click", showRandomPick);
  sideHeader.appendChild(randomBtn);
  controlSideEl.appendChild(sideHeader);

  let sawCategory = false;
  let dividerPlaced = false;
  for (const entry of entries) {
    if (entry.type !== "platform") {
      sawCategory = true;
    } else if (sawCategory && !dividerPlaced) {
      const divider = document.createElement("div");
      divider.className = "side-divider";
      controlSideEl.appendChild(divider);
      dividerPlaced = true;
    }

    const row = sidebarRow(entry, plan);
    row.classList.toggle("active", entry.key === activePanelKey);
    row.addEventListener("click", () => {
      activePanelKey = entry.key;
      renderResults(plan);
    });
    controlSideEl.appendChild(row);
  }

  const activeEntry = entries.find((e) => e.key === activePanelKey);
  controlMainEl.appendChild(panelForEntry(activeEntry, plan));

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
    summary.textContent = t("watchedListTitle", plan.watched_movies.length);
    box.appendChild(summary);
    const ul = document.createElement("ul");
    for (const m of plan.watched_movies) {
      const li = document.createElement("li");
      li.textContent = `${m.title} (${m.year}) `;
      const undoBtn = document.createElement("button");
      undoBtn.className = "undo-watched-btn";
      undoBtn.type = "button";
      undoBtn.textContent = t("undoBtn");
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
    box.innerHTML = `<summary>${t("removedTitle", plan.removed_from_watchlist.length)}</summary>
      <ul>${plan.removed_from_watchlist.map((m) => `<li>${m.title} (${m.year})</li>`).join("")}</ul>`;
    footerEl.appendChild(box);
  }

  if (plan.errors.length) {
    any = true;
    const box = document.createElement("details");
    box.className = "note-box error";
    box.innerHTML = `<summary>${t("errorsTitle", plan.errors.length)}</summary>
      <ul>${plan.errors.map((e) => `<li>${e.title} (${e.year}) &mdash; ${e.error}</li>`).join("")}</ul>`;
    footerEl.appendChild(box);
  }

  if (any) footerEl.classList.remove("hidden");
}
