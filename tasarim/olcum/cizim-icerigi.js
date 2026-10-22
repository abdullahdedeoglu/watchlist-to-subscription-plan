// Olcum araci: sonuc ekranina GPT ciziminin icerigini (ayni filmler, ayni
// posterler, Kazablanka eslesme uyarisi, 1 izlenen film) basar; boylece
// cizimle site arasinda sadece tasarim farki kalir. Uygulama kodunu
// degistirmez, tarayici konsolunda calistirilir. Posterler, cizimden
// kirpilip http://127.0.0.1:8799 uzerinden servis edilir (p1..p14.jpg).
(async () => {
  await document.fonts.ready;
  const names = [
    ["Gece Treni", 1998], ["Kazablanka", 1942], ["Son Seans", 2001], ["Uzak Kıyı", 2016],
    ["Mavi Saat", 1995], ["Bir Yaz Günü", 2008], ["Sessiz Şehir", 2020], ["Kırık Zaman", 2010],
    ["Yedinci Kat", 2018], ["Gölgeler", 2003], ["Uzun Yol", 2022], ["Rüya Defteri", 1996],
    ["Sınır", 2011], ["Kayıp Ada", 2019],
  ];
  const fx = names.map(([title, year], i) => ({
    uri: "fx-" + i, title, year,
    poster: `http://127.0.0.1:8799/p${i + 1}.jpg`,
    offers: [{ platform: "TV+", url: "#" }, { platform: "MUBI", url: "#" }, { platform: "HBO Max", url: "#" }],
  }));
  Object.assign(fx[1], { needs_review: true, matched_title: "Kazablanka", matched_year: 1943, offers: [{ platform: "TV+", url: "#" }] });

  const owned = getOwnedPlatforms();
  if (!owned.includes("Disney Plus")) setOwnedPlatforms([...owned, "Disney Plus"]);

  const d = computeDerivedPlan(lastRawPlan);
  const tv = d.platform_movies["TV+"];
  d.platform_movies["TV+"] = [...fx, ...tv.slice(14)];
  d.watched_movies = [tv[20]];
  d.already_available = d.already_available.slice(0, 34);
  activePanelKey = "platform:TV+";
  renderSummary(d);
  renderResults(d);
  renderFooterNotes(d);
  window.scrollTo(0, 0);
})();
