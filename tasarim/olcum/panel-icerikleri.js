// Olcum araci: 2. ekran (A/B/C panelleri) icin cizimdeki icerigi basar.
// Tarayici konsolunda calistir, sonra showPanel("A" | "B" | "C").
// Posterler http://127.0.0.1:8799/a1..a14.jpg ve b1..b14.jpg (cizimden kirpilmis).
(() => {
  const titles = [
    ["Gece Treni", 1998], ["Kazablanka", 1942], ["Son Seans", 2001], ["Uzak Kıyı", 2016],
    ["Mavi Saat", 1995], ["Bir Yaz Günü", 2008], ["Sessiz Şehir", 2020], ["Kırık Zaman", 2010],
    ["Yedinci Kat", 2018], ["Gölgeler", 2003], ["Uzun Yol", 2022], ["Rüya Defteri", 1996],
    ["Sınır", 2011], ["Kayıp Ada", 2019],
  ];
  const offer = (platform, type, price) => ({
    platform, type, price: price + "₺", price_value: parseFloat(price.replace(",", ".")), url: "#",
  });
  const prices = [
    [offer("Apple TV Store", "RENT", "24,99")],
    [offer("Amazon Video", "BUY", "179,99")],
    [offer("Apple TV Store", "RENT", "29,99")],
    [offer("Amazon Video", "RENT", "24,99"), offer("Apple TV Store", "BUY", "149,99")],
    [offer("Google Play", "RENT", "19,99")],
    [offer("Apple TV Store", "RENT", "24,99"), offer("Amazon Video", "BUY", "129,99")],
    [offer("Google Play", "RENT", "24,99")],
    [offer("Amazon Video", "RENT", "22,99"), offer("Apple TV Store", "BUY", "119,99")],
    [offer("Google Play", "RENT", "19,99")],
    [offer("Apple TV Store", "RENT", "24,99"), offer("Amazon Video", "BUY", "99,99")],
    [offer("Google Play", "RENT", "29,99")],
    [offer("Amazon Video", "RENT", "24,99"), offer("Apple TV Store", "BUY", "99,99")],
    [offer("Google Play", "RENT", "19,99")],
    [offer("Apple TV Store", "RENT", "24,99"), offer("Amazon Video", "BUY", "149,99")],
  ];
  const nowhere = `12 Angry Men 1957|Cinema Paradiso 1988|City of God 2002|Harakiri 1962|Persona 1966|Stalker 1979|Yi Yi 2000|A Brighter Summer Day 1991|The Red Shoes 1948|Paris, Texas 1984|Wings of Desire 1987|The Apartment 1960|High and Low 1963|Tokyo Story 1953|Late Spring 1949|Ikiru 1952|The Seventh Seal 1957|Wild Strawberries 1957|Autumn Sonata 1978|Fanny and Alexander 1982|Come and See 1985|The Ascent 1977|Mirror 1975|Andrei Rublev 1966|Solaris 1972|Nostalghia 1983|La Haine 1995|Beau Travail 1999|Chungking Express 1994|In the Mood for Love 2000|Fallen Angels 1995|Happy Together 1997|A Touch of Zen 1971|Still Walking 2008|Nobody Knows 2004|After Life 1998|The Spirit of the Beehive 1973|Cría Cuervos 1976|The Battle of Algiers 1966|Bicycle Thieves 1948|Umberto D. 1952|The 400 Blows 1959|Cléo from 5 to 7 1962|The Umbrellas of Cherbourg 1964|Le Samouraï 1967|Army of Shadows 1969|The Night of the Hunter 1955|Sweet Smell of Success 1957|Sunset Boulevard 1950|The Third Man 1949|Brief Encounter 1945|A Matter of Life and Death 1946|The Passion of Joan of Arc 1928|Metropolis 1927|The General 1926`
    .split("|").map((s, i) => {
      const year = Number(s.slice(-4));
      return { uri: "nw-" + i, title: s.slice(0, -5), year, needs_review: i === 1, offers: [] };
    });

  const film = (prefix, i, extra) => {
    const [title, year] = titles[i];
    const m = {
      uri: `${prefix}-${i}`, title, year, poster: `http://127.0.0.1:8799/${prefix}${i + 1}.jpg`,
      offers: [{ platform: "Disney Plus", url: "#" }, { platform: "MUBI", url: "#" }, { platform: "HBO Max", url: "#" }],
      ...extra,
    };
    if (i === 1) Object.assign(m, { needs_review: true, matched_title: "Kazablanka", matched_year: 1943 });
    return m;
  };

  window.showPanel = (which) => {
    const owned = getOwnedPlatforms();
    if (!owned.includes("Disney Plus")) setOwnedPlatforms([...owned, "Disney Plus"]);
    const d = computeDerivedPlan(lastRawPlan);
    d.already_available = titles.map((_, i) => film("a", i)).concat(d.already_available).slice(0, 34);
    d.rent_buy_available = titles.map((_, i) => film("b", i, { offers: [], rent_buy_offers: prices[i] }))
      .concat(d.rent_buy_available).slice(0, 61);
    d.not_available_anywhere = nowhere;
    activePanelKey = { A: "already", B: "rentbuy", C: "nowhere" }[which];
    renderSummary(d);
    renderResults(d);
    window.scrollTo(0, 0);
    return activePanelKey;
  };
})();
