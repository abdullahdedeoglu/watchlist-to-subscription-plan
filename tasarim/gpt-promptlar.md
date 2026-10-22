# WatchPlan yeniden tasarım: GPT prompt'ları

## Nasıl kullanılır

1. GPT'de **yeni bir sohbet** aç ve önce **0. Ortak brief**'i yapıştır.
   Bir şey çizdirme, sadece "anladım" desin.
2. Sonra aynı sohbette önce **L. Logo ve ikonlar**'ı gönder. Beğendiğin
   logoyu seçtikten sonra sırayla **1 → 2 → 3 → 4 → 5** prompt'larına geç,
   böylece ekranlar seçtiğin logoyla çizilir.
   Hepsini aynı sohbette çizdirmen önemli, yoksa her ekran farklı bir
   tasarım diline kayar.
3. En önemli ekran **1. Sonuç ekranı (masaüstü)**. Önce onu
   beğenene kadar çizdir, diğerlerini ondan türet.
4. Beğendiğin görselleri `tasarim/gpt-cizimler/` klasörüne koy, ben
   oradan koda dökerim.

Prompt'lar İngilizce, çünkü görsel modeller İngilizce prompt'ta daha
isabetli çalışıyor. Ekranda görünecek yazılar ise Türkçe verildi,
GPT onları aynen yazacak.

`mevcut-ekranlar/` klasöründeki görüntüleri GPT'ye **atma**. Onlar
bana lazım: uygularken hiçbir özelliğin kaybolmadığını kontrol etmek için.

---

## 0. Ortak brief (ilk mesaj, bir şey çizdirme)

```
I'm redesigning the UI of a web app called "WatchPlan". Don't draw anything
yet. Read this brief; every screen I ask for later must follow it.

WHAT THE APP DOES
The user uploads their Letterboxd watchlist (a CSV of movies they want to
watch). The app looks up every movie on JustWatch for the chosen country and
answers one question: "In which order should I subscribe to streaming
platforms to watch my watchlist fastest?" The result is an ordered list of
platforms (1st: TV+ with 56 movies, 2nd: Disney Plus with 35, ...). Each
platform shows the posters of the user's movies available there. Users mark
platforms they already own, tick off movies they've watched, and fix
mismatched titles.

CONCEPT: "EMULSION / CONTROL ROOM"
- Mood: analog cinema. Film emulsion, film stock, cinema tickets, a
  projection booth, a festival programme. Warm, tactile, premium. NOT a
  generic dark SaaS dashboard, and not a Netflix clone.
- The results screen is a "control room": a left sidebar of small
  cinema-TICKET cards (one per platform, in a fixed order) and a large
  right pane showing the selected platform's movie posters. Clicking a
  ticket swaps the right pane; the page does not scroll to sections.
- Starting palette (you may refine it, but keep the spirit): near-black
  warm ground, gold/amber as the brand accent, teal for positive states
  ("you already own this"), warm orange for warnings ("match might be
  wrong"). Warning orange must stay clearly distinct from the gold accent.
- Starting type (you may refine it): an elegant italic serif for display
  (like Fraunces Italic), a clean grotesk for body (like Instrument Sans),
  and a monospace for numbers and small labels (like IBM Plex Mono).
- Subtle film grain or texture is welcome; it must never hurt legibility.
- Posters are the hero content: real movie poster images in 2:3 ratio.
  Use generic placeholder posters in the mockups.

HARD RULES
- Platforms appear as TEXT names only (TV+, Disney Plus, HBO Max, Netflix,
  MUBI, MUBI Amazon Channel, Amazon Prime Video...). Don't draw platform
  logos; we don't have the right to use them.
- The UI is in Turkish. Use the exact Turkish labels I give you.
- No donation or "buy me a coffee" button anywhere.
- It must be buildable in plain HTML/CSS: no 3D, no photo-realistic
  scenes, no illustrations that only work as a single image.
- Desktop mockups at 1440px wide; mobile mockups at 375px wide.

Reply only "ready" for now.
```

---

## L. Logo ve ikonlar (ekranlardan önce)

GPT'nin çizdiği logo bir resim olarak gelir. Seçtiğin logoyu ben temiz bir
SVG olarak yeniden çizerim. Böylece sekme ikonunda (16px) da, büyük
boyutta da keskin görünür.

```
Before any screen, design the brand identity for "WatchPlan". Show
everything on one presentation sheet.

1) LOGO MARK: 4 different directions, each shown large and also at 32px
   and 16px. It must stay recognisable at 16px, since it will be the
   browser tab icon (favicon). Simple, geometric, at most 2 colours,
   no fine detail and no text inside the mark. Directions to explore
   (you may propose better ones):
   - a cinema ticket stub combined with a checkmark or a play triangle
   - a film frame / sprocket holes forming a "W" or a step-by-step path
   - a numbered queue ("1, 2, 3") made of film frames
   - a clapperboard reduced to its simplest geometric form
   It must NOT look like an emoji, and must not resemble Letterboxd's,
   JustWatch's or any streaming platform's logo.

2) WORDMARK: "WatchPlan" in the display typeface, paired with the mark
   in a horizontal lockup, on the dark background and on a light one.

3) APP ICON: the mark on a rounded square tile (for phone home screens).

4) SOCIAL SHARE CARD: 1200×630, the preview image that appears when the
   site link is shared on WhatsApp/X. Logo, wordmark, and the tagline
   "Watchlist'ini en hızlı hangi platform sırasıyla bitirirsin?"

5) SMALL UI ICONS in the same style: upload/CSV, watched (✓), remove (×),
   warning (⚠), add (+), random (die), search, and feedback.
```

---

## 1. Sonuç ekranı (masaüstü), en önemlisi

```
Draw the main RESULTS screen, desktop, 1440px wide. This is the heart of
the app. Show the user's state after loading a 250-movie list.

TOP OF THE PAGE (compact, the results must dominate)
- Header: the logo lockup we chose (mark + "WatchPlan" wordmark) at left.
  At right: a "Geri bildirim" (feedback) text link, plus two small
  dropdowns: language ("Türkçe") and country ("Türkiye (TR)").
- A collapsed "Nasıl kullanılır?" (How to use) disclosure row.
- A slim, already-used upload strip: "CSV dosyasını buraya sürükle" plus
  three small secondary actions: "Letterboxd Top 500 yükle",
  "IMDb Top 250 yükle", "Listeyi kaldır".

STATS ROW, labelled "TÜRKİYE KATALOĞU": 8 numbers, all equally important,
none of them a giant hero number:
  9 Platform · 99 Yeni abonelikle film · 34 Zaten sende var · 1 İzledin ·
  61 Kirala/satın al ile izlenebilir · 55 Hiçbir yerde yok ·
  3 Eşleşme kontrolü önerilir · 250 Toplam watchlist

A search field above the results: placeholder "Listende ara..."

CONTROL ROOM (fixed-height panel; sidebar and main pane scroll on their own)
Left sidebar (about 280px):
- Header "ABONELİK SIRASI" with two small round icon buttons: "+" (add a
  movie) and a die (pick a random movie).
- Three category links pinned at the top, each with a count:
  "Zaten sende var 34" (teal), "Kirala/satın al ile izlenebilir 61",
  "Hiçbir yerde yok 55".
- Below a divider: platform TICKETS in a fixed order. Each ticket shows a
  big order number, the platform name, the movie count ("56 film") and a
  small custom checkbox meaning "I own this". Draw these tickets:
    01 TV+ 56 film (selected/active state)
    "SAHİBİM" Disney Plus 35 film (owned: checkbox ticked, no number,
      teal-tinted, it keeps its position in the list)
    02 HBO Max 32 film
    03 Netflix 23 film
    04 MUBI 20 film
    05 MUBI Amazon Channel 19 film
  Make them feel like real cinema tickets (perforation, stub, punched
  edge...) but clean.

Main pane:
- Header: a "1. SIRA" pill, the platform name "TV+" in big italic serif,
  "56 film".
- A grid of poster cards, about 7 per row. Each card:
  * poster (2:3)
  * top-right: a small round "✓" button (mark as watched)
  * bottom-right: a small round "×" button (remove from list)
  * on ONE card only: a top-left orange "⚠" badge (match needs review),
    with a small line under the title "JustWatch: Kazablanka (1943)"
  * below the poster: title, year, and a muted line
    "Ayrıca: MUBI, HBO Max" (also available on)

BELOW THE PANEL: a collapsed row "İzlediğin filmler (1)" (watched movies).

Draw it beautifully. The previous attempt (dark background, gold accent,
plain rounded boxes) felt generic; push the cinema/ticket identity
further, without making it noisy.
```

---

## 2. Diğer panel türleri (masaüstü)

```
Same results screen and same design language. Draw three variants of the
MAIN PANE only (the sidebar stays as before; just change which item is
active):

A) "Zaten sende var" selected (teal state).
   Header "Zaten sende var" in teal italic serif, subtitle
   "Zaten izleyebilirsin · Disney Plus (34 film)". Same poster grid.

B) "Kirala/satın al ile izlenebilir" selected (no subscription option,
   rent/buy only). Header plus subtitle "Kirala/Satın Al ile
   İzleyebilirsin (61)". Poster grid, but under each card show 1–2 small
   price chips, e.g. "Apple TV Store · Kirala · 24,99₺",
   "Amazon Video · Satın Al · 179,99₺". The chips must look clearly
   different from the warning badge.

C) "Hiçbir yerde yok" selected (not available anywhere). Header plus
   subtitle "Hiçbir platformda abonelikle bulunamadı (55)". NO posters
   here: a dense, elegant cloud of text chips "Title Year"
   (e.g. "12 Angry Men 1957", "Cinema Paradiso 1988"). One chip has an
   orange ⚠ (needs review).
```

---

## 3. İlk giriş ve arama ekranı (masaüstü)

```
Same design language. Draw the FIRST-VISIT screen (no list loaded yet),
desktop 1440px, plus a second small frame showing the loading state.

Frame 1, empty state:
- Header as before ("WatchPlan", "Geri bildirim", language and country
  dropdowns).
- One-line pitch: "Letterboxd watchlist CSV'ni sürükle, hangi sırada hangi
  platforma abone olman gerektiğini gör."
- "Nasıl kullanılır?" disclosure, drawn OPEN: 5 numbered steps on the
  left, a small video thumbnail card on the right, labelled
  "1. adımı video olarak izle (56 sn)". The steps:
   1. Letterboxd'da Profil → Watchlist → Export watchlist yoluna git, bir
      .csv dosyası doğrudan iner.
   2. O CSV dosyasını aşağıdaki alana sürükle-bırak (ya da tıkla ve seç).
   3. Üst taraftan ülkeni seç (varsayılan Türkiye).
   4. Arama bitince hangi sırayla hangi platforma abone olacağını görürsün.
   5. Poster'in sağ üstündeki ✓ izledim işaretler, sol üstteki ⚠ eşleşmeyi
      kontrol etmeni önerir.
- A large, inviting drop zone: "CSV dosyasını buraya sürükle" /
  "ya da tıkla ve seç". (Film-frame or ticket-stub motifs are welcome.)
- Under it, two "try it without your own list" buttons:
  "Letterboxd Top 500 yükle", "IMDb Top 250 yükle".

Frame 2, searching: the drop zone collapsed into a slim strip, plus a
progress card: "JustWatch'ta aranıyor…", a progress bar at about 60%, and
a monospace detail line "[150/250] Dune: Part Two". Also show the
alternate indeterminate (striped) bar with the text
"JustWatch kataloğu taranıyor (4/20)".
```

---

## 4. Modallar (masaüstü)

```
Same design language. Draw four modal dialogs (centered over a dimmed
results screen), as a 2×2 sheet:

A) "Rastgele Film" (random pick): a collapsed disclosure at the top,
   "Rastgele film önerisi hangi platformlar arasından seçilsin? (boş
   bırakırsan tüm watchlist)". Below it one big poster, the title
   "Witness for the Prosecution (1957)", a platform chip
   "Amazon Prime Video", and two buttons: "🎲 Başka film" (primary) and
   "İzledim işaretle" (secondary).

B) "Eşleşmeyi kontrol et" (fix a match): subtitle "Casablanca (1942) için
   JustWatch sonuçları", a search field with an "Ara" button, then a grid
   of 8 candidate posters with title and year (e.g. Kazablanka 1943,
   Casablanca 1955...). Clicking one picks it, so show a hover state on
   one card.

C) "Film ekle" (add a movie): the same search field and button, and a
   grid of result posters (e.g. "Paprika" 2006, 1991, 2018...).

D) "Geri bildirim" (feedback): label "Hangi film hakkında? (opsiyonel)"
   with a search input "Listende ara...", label "Mesajın" with a textarea
   "Ne olduğunu anlat...", and a "Gönder" button. Also show the small
   success message: "Site veya film hatalarında geri dönütleriniz için
   teşekkürler! 🙏"
```

---

## 5. Mobil (375px)

```
Same design language. Draw the results experience on MOBILE, 375px wide,
as 3 phone frames side by side:

1) Top of page: compact header ("WatchPlan", "Geri bildirim", a language
   and a country dropdown), a slim upload strip, the 3 secondary actions,
   and the 8 stats in a compact 2-column or 4×2 layout.

2) The control room on mobile: the sidebar becomes a horizontally
   scrollable strip of the same TICKETS ("Zaten sende var 34",
   "01 TV+ 56 film", "SAHİBİM Disney Plus", "02 HBO Max"...), with the
   "+" and die buttons reachable. Below it the selected platform's
   header ("1. SIRA · TV+ · 56 film") and the poster grid in 3 columns,
   cards with the ✓ / × / ⚠ buttons still easy to tap (at least 32px).

3) A modal on mobile: the "Rastgele Film" sheet as a bottom sheet.
```
