// Olcum araci: modallari cizimdeki icerikle acar. openMock("A"|"B"|"C"|"D")
(() => {
  const P = (f) => `http://127.0.0.1:8799/${f}`;
  const closeAll = () => document.querySelectorAll(".modal-overlay").forEach((m) => m.classList.add("hidden"));
  window.openMock = (which) => {
    closeAll();
    if (which === "A") {
      document.getElementById("random-modal").classList.remove("hidden");
      document.getElementById("random-pool-panel").classList.remove("hidden");
      renderRandomResult({ uri: "x", title: "Witness for the Prosecution", year: 1957, poster: P("rnd.jpg"),
        offers: [{ platform: "Amazon Prime Video", url: "#" }] });
    } else if (which === "B" || which === "C") {
      const B = which === "B";
      const years = B ? [1943, 1955, 1983, 2002, 1961, 2010, 1997, 2023] : [2006, 1991, 2018, 1989, 2014, 2020, 2001, 1972];
      const names = B ? ["Kazablanka", "Casablanca", "Casablanca", "Casablanca", "Kazablanka", "Casablanca", "Casablanca", "Casablanca"] : Array(8).fill("Paprika");
      const cands = years.map((y, i) => ({ matched_title: names[i], matched_year: y, poster: P(`${B ? "rm" : "af"}${i + 1}.jpg`) }));
      if (B) {
        // gercek aramayi tetiklememek icin openRematchModal yerine elle
        document.getElementById("rematch-modal").classList.remove("hidden");
        document.getElementById("rematch-title").innerHTML =
          `${t("rematchTitlePrefix")}<span class="sub">${t("rematchSubtitle", { title: "Casablanca", year: 1942 })}</span>`;
        document.getElementById("rematch-search-input").value = "Casablanca";
        renderCandidateGrid(document.getElementById("rematch-body"), cands, () => {});
      } else {
        openAddFilmModal();
        document.getElementById("add-film-search-input").value = "Paprika";
        renderCandidateGrid(document.getElementById("add-film-body"), cands, () => {});
      }
    } else if (which === "D") {
      document.getElementById("feedback-modal").classList.remove("hidden");
      document.getElementById("feedback-success").classList.remove("hidden");
    }
    return which;
  };
})();
