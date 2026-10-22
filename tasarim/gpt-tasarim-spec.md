# WatchPlan — onaylı arayüzün uygulama şartnamesi

Tarih: 22 Ekim 2026. Dil: Türkçe. Kapsam: sekiz onaylı raster mockup’ın HTML/CSS uygulamasına aktarılması. Bu belge kod içermez.

## 0. Ölçülerin anlamı ve kaynaklar

Bu görseller bir tarayıcıda oluşturulmuş ekran görüntüleri değildir; görsel üretme aracıyla üretilmiştir. Dolayısıyla arkalarında keşfedilebilecek bir DOM, gerçek font dosyası, kesin renk token’ları veya özgün CSS katmanları bulunmuyor. Aşağıda iki bilgi türü ayrılır:

- **Görsel referansı:** dosyada görülen yerleşimin elle okunmuş yaklaşık sınırları. Kenar yumuşatma, gren ve parıltı nedeniyle sınırlar yaklaşık ±4 px; büyük dokulu sınırlar ±8 px toleranslıdır. Bunları piksel örneklemesiyle elde edilmiş kesin değerler olarak değerlendirmeyin.
- **Uygulama kararı:** aynı görünüşü tutarlı biçimde yeniden kurmak için bu belgede sabitlenen kesin değerler. Renkler, font aileleri, katman opaklıkları, etkileşim ölçüleri ve taşma davranışları bu gruptadır. Tasarım sisteminin normatif kaynağı bunlardır.

Koordinatlar sol üstten ölçülür. Tablolarda `x / y / genişlik / yükseklik` sırası kullanılır. Bir satırda yalnızca koordinat verilmişse kalıtılan görünüm, aşağıdaki ortak bileşen tanımıdır. Metin koordinatları, aksi belirtilmedikçe satır kutusunun sol üstüdür; harfin taban çizgisi değildir.

| Kaynak; tümü `tasarim/watchplan-brand/` altında | Gerçek dosya boyutu | Nasıl okunmalı? |
|---|---:|---|
| results-desktop.png | 1440 × 1024 | Tam masaüstü sonuç sayfası; ana yerleşim referansı |
| results-A-owned.png | 1440 × 1024 | Yalnız ana panel; genişletilmiş ayrıntı görünümü |
| results-B-rent-buy.png | 1440 × 1024 | Yalnız ana panel; genişletilmiş ayrıntı görünümü |
| results-C-unavailable.png | 1440 × 1024 | Yalnız ana panel; genişletilmiş ayrıntı görünümü |
| first-visit-desktop.png | 1440 × 1100 | Tam ilk ziyaret sayfası |
| loading-desktop.png | 1440 × 1050 | Tam arama durumu; iki ilerleme türü birlikte sunuluyor |
| modals-desktop-grid.png | 1435 × 1096 | Dört küçültülmüş masaüstü görünümünden oluşan sunum |
| results-mobile-three-screens.png | 1365 × 1152 | Üç mobil görünümden oluşan sunum; dosyanın tamamı 375 px değildir |

**Öncelik:** Türkçe metinler ve davranış → ortak bileşen kuralları → oranlar → görseldeki yaklaşık koordinatlar. Üretilmiş bir posterdeki oran hatası, rastlantısal gölge veya bir harfin farklı çizilmesi tasarım kuralı değildir. A/B/C’nin büyük başlıklarını dar sonuç paneline aynı büyüklükte taşımayın.

## 1. Global tasarım sistemi

### 1.1 Sayfa zemini: tek resim değil, bağımsız katmanlar

Mockup raster’ında her şey birleşiktir. Uygulama için karar **ayrı katmanlar** kullanmaktır. Tam sayfa ekran görüntüsü arka plan yapılmayacak; metin, kart ve kontrol görüntüye gömülmeyecek. Aşağıdaki opaklıklar dosyanın alfa değerine ek uygulanan katman opaklığıdır.

| Alttan üste sıra | İçerik ve renk | Opaklık | Boyut ve konum | Kullanım |
|---|---|---:|---|---|
| 1 | Düz sıcak zemin `#181815` | %100 | Tüm sayfa ve en az görünür alan yüksekliği | Her ekran |
| 2 | `1-gren.png`: koyu, ince sıcak emülsiyon/kâğıt greni | Masaüstü %18; mobil %6 | 512 × 512 px görüntüleme boyutunda iki yönde tekrar; başlangıç 0,0 | Sayfa arka planı; panelin içine tekrar taşınmaz |
| 3 | Kenar ışık lekeleri: merkez `#B94F1E`, ara `#71351D`, dış şeffaf | Masaüstü tepe %30; mobil %8 | Sağ üstte 560 × 280; sol altta 360 × 280; sağ altta 480 × 320. Sonuç sayfasında alt lekeler yarı güçte | İçeriğin arkasında; turuncu marka rengi değildir |
| 4 | İnce yan kenar emülsiyonu: yanık kehribar tanecikleri ve lekeleri | Masaüstü %45; mobil yok | Her yanda 28 px bant; dışa dayalı; merkeze 24 px içinde söner | Masaüstü sayfa çevresi; bu lekelerin organik ayrıntısı ayrı alfa dokusu olabilir |
| 5 | `3-film-seridi.png`: perforasyon şeridi | İlk ziyaret/yükleme %80; sonuç %35 | Sol ve sağ kenarda 20 px genişlik, kaynak oranına göre 400 px tekrar yüksekliği; sağ şerit yatay aynalanabilir | Yalnız masaüstü. Mobilde kaldırılır |
| 6 | `2-isik.png`: tozlu projektör ışığı | Sonuç %38; ilk ziyaret/yükleme %52; mobil %14 | Başlık alanında kırpılmış; aşağıdaki ışık geometrisine bakın | Metin ve kontrollerin arkasında |
| 7 | İçerik yüzeyleri | %100 veya aşağıdaki bileşen tonu | Gerçek yerleşim kutuları | Doku/gürültünün önünde; okunaklı bölge |
| 8 | Bilete veya çerçeveye özgü doku | Bilet %7; yükleme çerçevesi %100 | Yalnız ilgili dekorasyon alanında kırpılır | Posterlerin, açıklamaların ve düğme yazılarının üstüne yayılmaz |
| 9 | Modal karartması ve diyalog | Karartma %68, diyalog %100 | Görünür alanın tamamı; diyalog onun önünde | Yalnız diyalog açıkken |

**Kenarların varlığı:** masaüstü sonuç, ilk ziyaret ve yükleme ekranlarında sayfanın dış çevresinde bulunur. Sonuç ekranında içerik 28 px içeri alındığı için şerit çok az görünür. Modal arka planında aynı sayfa dekoru karartılarak görünür. Mobilde film şeridi ve yanık sayfa çerçevesi yoktur; yalnız hafif üst ışık ve gren vardır. A/C ayrıntı görsellerindeki renkli dış gren, ana panelin durumunu anlatan sunum dekorudur; kategori değişince gerçek sayfanın bütün kenarları turkuaza dönmez.

**Neden:** ayrı katmanlar farklı ekran boylarında esner, opaklığı ayarlanabilir ve okunabilirlik için panelin altında kalır. Yanık kenar, kontrol veya hata göstergesi gibi algılanmamalıdır.

### 1.2 Projektör ışığının geometrisi

- Onaylı tam sayfalarda ışığın sivri ucu, yaklaşık x=990–1020 / y=80–116 noktasındadır. Işıklı yelpaze bu uçtan sol üste, yaklaşık x=540–800 / y=0 bandına açılır. Pencerenin tüm genişliğine yayılan bir spot değildir.
- Uygulamada sonuç başlığı için sivri uç x=1008, y=78; ilk ziyarette x=996, y=116; yüklemede x=1012, y=110 alınır. Görünen yelpaze yaklaşık 520 × 130 px; en geniş kesiti 180–220 px. İç ışık `#F8D995`, kenar sıcaklığı `#C56B28`; çekirdeğin opaklığı %55, dış yelpazenin %8–18.
- Mevcut `2-isik.png` varlığı ise kaynağı sağ üst köşede olup sol alta açılan bir örtüdür. Mockup’taki sola-yukarı yelpazeyi elde etmek için varlık döndürülüp kırpılmalı ve sivri ucu yukarıdaki noktaya hizalanmalıdır. Dosyayı bütün sayfaya gererek kullanmayın. Gerektiğinde bu yön için ayrı bir ışık varlığı gerekir; burada üretilmeyecek.
- İlk ziyaretin büyük yükleme bileti içinde ikinci bir ışık vardır: sivri uç yaklaşık x=1290, y=836; yelpaze x=820–1080, y=610 bandına açılır. Biletin dekor katmanında kalır; merkezdeki yükleme metnine opak ışık gelmez. Opaklık %32; görünür kutu yaklaşık 570 × 260 px.
- Mobil üst ışığın sivri ucu yaklaşık x=363, y=62; yelpaze sol üste yaklaşık 150 px açılır. Başlık kutusuna kırpılır; aşağıdaki istatistiklere devam etmez.
- Işık hiçbir zaman poster veya düğme üstünde ön katman değildir; tıklama alanı ve yerleşimde kapladığı alan yoktur.

### 1.3 Kesin renkler

Bunlar görseldeki bütün piksellerin aynı olduğu iddiası değil, uygulama paletidir.

| Rol | Değer | Kullanım |
|---|---|---|
| Sayfa zemini | `#181815` | Ana taban |
| Sakin ana panel | `#141612` | Poster ve yoğun metin arkasındaki koyu yüzey |
| Kart / form yüzeyi | `#22221E` | Bilet, giriş, ikincil düğme |
| Yükseltilmiş yüzey | `#292923` | Hover ve fiyat etiketi |
| İç siyah | `#10110F` | Poster kontrol diski; %88 opak |
| Normal sınır | `#48483F` | 1 px panel/giriş kenarı |
| Düşük kontrast ayırıcı | `#35382F` | İç bölümler ve istatistik ayracı |
| Açık sınır | `#8B826D` | Fiyat etiketleri ve poster çizgisi |
| Birincil yazı | `#F1E9D8` | Başlıklar ve temel metin |
| İkincil yazı | `#C8C4B8` | Yıl, yardımcı açıklama |
| Soluk yazı | `#9B9C91` | Placeholder, devre dışı öğe |
| Marka altını | `#DAB56D` | Logo, sıra ve aktif sınır |
| Altın parlak uç | `#F4D695` | Düğme/kelime işareti ışığı |
| Altın orta vurgu | `#E8BE70` | Metalik yüzey |
| Altın koyu uç | `#A87938` | Metalik yüzeyin gölgesi |
| Sahiplik turkuazı | `#79B7A8` | Sahiplik metni/ikon |
| Turkuaz aydınlık uç | `#96D2C3` | Seçili sahiplik kontrolü |
| Sahiplik koyu tabanı | `#1C3935` | Sahip olunan bilet |
| Uyarı turuncusu | `#EF8755` | Eşleşme uyarısı |
| Uyarı koyu tabanı | `#44291F` | Uyarı vurgu zemini |
| Dekor yanık turuncu | `#B94F1E` | Yalnız atmosfer; durum etiketi değildir |

**Metalik altın:** 135° yönünde 0% `#A87938`, 22% `#DAB56D`, 48% `#F4D695`, 68% `#E8BE70`, 100% `#B98C47`. Düğmede kontrastı korumak için koyu uçları %15 aydınlatın; yazı `#181815`. Logo işareti düz `#DAB56D`; işaret üzerinde metalik doku yok. Wordmark’ın “Watch” kısmı krem, “Plan” kısmı açık altın → altın geçişlidir; tamamı tek tipografik kelimedir. Başlıklarda tüm metne metalik efekt uygulamak gerekmez.

**Turkuaz gradyan:** soldan sağa `#254B44` → `#1C3935`; sol kupon parçası `#79B7A8`. Uyarı rengi ile altının birbirine yaklaşmasını önlemek için fiyat etiketleri nötr tutulur.

### 1.4 Tipografi

Görsel üretimi gerçek Fraunces/Instrument Sans/IBM Plex Mono dosyalarını kullanmadı; bazı küçük başlıklarda daha klasik serif görüldü. Aşağıdaki Google Fonts aileleri, bu görünüşü tekrar edilebilir kılmak için seçilen en yakın ailelerdir. Font indirme/kurulum bu belgenin kapsamında değildir.

| Rol | En yakın Google Font ve stil | Masaüstü 1440 px: boyut / satır yüksekliği | Harf aralığı | Mobil 375 px |
|---|---|---:|---:|---:|
| Wordmark | Fraunces, 800 italic, yumuşak yüksek kontrastlı serif | Sonuç 72 / 76; ilk ziyaret 80 / 88 | −2 px | 40 / 44, −1.2 px |
| Seçili platform “TV+” | Fraunces 800 italic | 48 / 52 | −1.4 px | 42 / 46 |
| Gerçek ana panel kategori başlığı | Fraunces 750 italic | 36 / 42 | −0.7 px | 28 / 34 |
| Ayrıntı A/B/C büyük başlıkları | Fraunces 800 italic | A 80/88; B 68/76; C 88/96 | −1.8 px | Bu sunum ölçeği kullanılmaz |
| Modal başlığı | Fraunces 750 italic | 36 / 42 | −0.8 px | 30 / 36 |
| Rehber/açılır bölüm başlığı | Fraunces 650 düz | 24 / 30; sonuçta kompakt 16 / 22 | 0 | 14 / 20 |
| Platform bileti adı | Fraunces 650 düz | 21 / 23 | −0.2 px | 16 / 19 |
| Film adı | Fraunces 650 düz | Tam sayfa 16 / 19; ayrıntı 20 / 24 | −0.1 px | 14 / 17 |
| Gövde / form / açıklama | Instrument Sans 400 | 16 / 22; ilk ziyaret rehberi 18 / 26 | 0 | 14 / 20 |
| Açılış cümlesi | Instrument Sans 400 | 22 / 30 | −0.15 px | Gerekirse 16 / 23, çok satır |
| Düğme | Instrument Sans 600 | 15 / 20 | 0 | 14 / 20 |
| İstatistik sayısı | IBM Plex Mono 600 | 26 / 30 | −0.4 px | 24 / 28 |
| Sıra numarası | IBM Plex Mono 600 | 24 / 28 | −0.6 px | 22 / 26 |
| Üst küçük etiket | IBM Plex Mono 500, büyük harf | 12 / 16 | +1.5 px | 12 / 16, +1.2 px |
| Yıl / fiyat / ilerleme detayı | IBM Plex Mono 400 | Yıl 13/17, fiyat 13/18, ilerleme 26/34 | 0 | Yıl 12 / 16 |
| Küçük “Ayrıca” satırı | Instrument Sans 400 | Tam sayfa 12 / 16; ayrıntı 14 / 18 | 0 | 12 / 16 |
| Eşleşme uyarısı | Instrument Sans 600 | Tam sayfa 12 / 15; ayrıntı 14 / 18 | 0 | 11 / 15 |

Neden: italik serif yalnızca marka ve ana odağı taşır; düz serif platform ve film adlarında festival programı hissi verir. İşlem metinleri sans, sayılar mono kalır. Film adları ile uygulama komutları birbirinden ayrılır. Türkçe karakterleri destekleyen font dosyası ve ağırlık kullanılmalıdır; yapay italik yerine gerçek italik tercih edilir.

### 1.5 Geometri, boşluk ve durumlar

- Boşluk dizisi: **4, 8, 12, 16, 20, 24, 32, 40, 48, 64 px**. Dokulu kenarın dışında rastlantısal küçük boşluklar üretmeyin.
- Ana masaüstü dış boşluk sonuçta 28 px; ilk ziyarette 56 px; yüklemede 48 px. İçerik en fazla 1440 px referans genişliğinde ortalanır. Daha geniş ekranda poster paneli büyüyebilir; tipografi büyütülmez.
- Normal panel/giriş/düğme köşesi 6 px, büyük panel 8 px, modal 12 px, küçük fiyat etiketi 8 px, poster 4 px, pill tam yuvarlak. Mobil bottom sheet üst köşeleri 24 px; alt köşeleri 0.
- Normal çizgi 1 px; aktif bilete 2 px altın; hover adayına 2 px altın; sahiplik kutusuna 1.5 px. Perforasyon süsü kontrolün gerçek sınırı değildir.
- Normal kartlarda belirgin dış gölge yok. Panel iç üst çizgi: krem %4, 1 px. Aktif biletin altın iç ışıması: en fazla 16 px yayılım, altın %8. Modal: aşağı 24 px, 64 px bulanıklık, siyah %55; çerçevede altın %15 / 16 px yumuşak halo.
- Birincil düğme yükseklik 40 px; form girişi 40 px; masaüstü küçük seçimler 34 px. Mobil ana düğme 48–52 px.
- İkon çizgisi 1.75–2 px; genelde 20–24 px. İkon diski ve etkileşim hedefi farklı olabilir. Masaüstü poster diski 28 px, gerçek hedefi 32 px. Mobilde görünür disk ve hedef en az 32 px; mümkün olan yerde 36 px.
- Klavye odağı: dışa 2 px boşluklu 2 px altın halka; sahiplikte turkuaz olabilir. Hover arka planı yükseltilir; aktif/owned/uyarı yalnız renk ile anlatılmaz: sayı, “SAHİBİM”, tik ve üçgen de bulunur.

## 2. Ortak bileşenlerin ayrıntıları

### 2.1 Sinema bileti

Tam sonuçta kart kutusu **276 × 68 px**, soldaki sidebar içinde x=40; aralık 8 px. Son uzun platform adı için 76 px yüksekliğe izin verilir. Sidebar hedef genişliği 312 px; başlangıç brief’indeki yaklaşık 280 px yerine onaylı görselin gerçek oranı izlenir. Kart yüksekliği sabit metin kırparak korunmaz.

- Koyu gövde `#22221E`; çok hafif yatay `#2A2922` ışığı. Dış sınır 1 px `#48483F`, köşe 7 px.
- Sol dar altın şerit: 12 px; kartın soluna sıfır dayalı. Altın metalik gradyan yalnız bu şeritte olabilir. Gerçek kart şekli şerit ile birlikte kesilir.
- Sol kenarın dikey ortasında **yarıçapı 8 px içbükey yarım daire**. Daireye sayfa deseni yapıştırılmayacak; gerçek kesik/maskeyle arka yüzey görünür. Sağ kenarda aynı mantıkta 5 px küçük içbükey kesik kullanılabilir; görselde çok siliktir.
- Numara bölmesi: soldan 16–68 px. Sayı x=26 göreli, dikey merkezde. Gövdeyi ayıran çizgi soldan 68 px, üst/alt 14 px boşluk; 1 px `#67634F`, %55 opak. Bazı görsellerde noktalı çizgi gibi görünür; uygulamada 2 px çizgi / 3 px boşluklu perforasyon kullanılır.
- Platform adı soldan 86 px; üst 14 px. Film sayısı onun altında 4 px boşlukla; 14 / 18 px ikincil metin. Sağdaki sahiplik kutusu 20 × 20, sağdan 18 px, dikey merkezde. Metin alanı checkbox’a girmemeli.
- Aktif TV+: 2 px `#DAB56D`, `#2B281E` taban, düşük kontrastlı ince bilet greni %7. Numara altın; isim krem. Sol altın şerit devam eder. Seçim nedeni: aktif platform sayfa üzerinde başka bir bölüme gitmez; sağ panel içeriğini değiştirir.
- Sahip olunan Disney Plus: sol şerit turkuaz; gövde `#254B44` → `#1C3935`; sınır `#5D9C8D`. Sayı yerine 10 / 14 px mono “SAHİBİM”; iki satıra kırpılmaz. Stub 74 px’e çıkabilir, içerik soldan 92 px başlar. Checkbox turkuaz dolu, koyu tiklidir. Sahiplik platformu sıralamada yerinden oynatmaz.
- Diğer platformlar nötr; numaraları altın. HBO Max, Netflix, MUBI, MUBI Amazon Channel yalnız düz metin. Uzun isim en fazla iki satıra sarılır; film sayısı üçüncü satıra gelir, kart 76–88 px’e büyür. Fontu 14 px’in altına düşürmeyin.
- Hover: normal sınır açık altına yaklaşır, taban %5 aydınlanır. Tüm bilete tıklama platformu seçer; sahiplik kutusuna tıklama yalnız sahipliği değiştirir.

### 2.2 Poster kartı

- Görsel **kesin 2:3**; kartın arkasında ayrı dolu kutu yok. Görsel alanı kaplama mantığıyla kırpılır; poster oranı değişmez. 1 px `#6B6A5D` sınır; 4 px köşe.
- Onaylı tam sayfada poster çizimi yaklaşık 130 × 178 px, A/B’de yaklaşık 170 × 235 px görünüyor; bunlar üretim sapmasıdır. Uygulamada tam sayfa 130 × 195; ayrıntı A 170 × 255; mobil yaklaşık 103 × 154.5 kullanılacak. Fotoğrafı yassılaştırmayın.
- Tik: sağ üstten 6 px, 28 px koyu disk, 1 px krem %65 kenar, 16 px krem tik. Çarpı: aynı sağ mesafede, posterin altından 6 px; 16 px çarpı. İkisi de metin kutusunun üzerinde değil poster üzerindedir.
- Mobil: 32 px disk, 18 px ikon, kenarlardan 4 px. Uyarı da en az 32 × 32 px hedefte; sol üstten 4 px. Başka ikonla çakışmamak için 3 sütunda poster en az 100 px olmalıdır.
- Uyarı: sol üstte 28 px hedef içinde 22 px turuncu üçgen, krem/koyu ünlem. Yalnız eşleşme şüphesi olan kartlarda. Alt metin `JustWatch: Kazablanka (1943)` turuncu; en fazla iki satırda, küçültülmeden gösterilir.
- Poster sonrası boşluk 6 px; ad 1–2 satır, yıl sonraki satır; yardımcı satırdan önce 3 px. Satır yüksekliği en uzun kartın içeriğine göre hesaplanır; bir sonraki poster satırı bütün sütunlarda aynı y’de başlar. Metni poster üstüne koymayın.
- Normal ad örnekleri: Gece Treni, Kazablanka, Son Seans, Uzak Kıyı, Mavi Saat, Bir Yaz Günü, Sessiz Şehir. Yardımcı satır `Ayrıca: MUBI, HBO Max`; platformlar değişebilir. Ad en fazla 2 satır; tüm ad etkileşimli ayrıntıda erişilebilir. Yardımcı platform listesi iki satırı aştığında ek sayıyla devam edebilir, kart kolonunu genişletmez.
- Tik düğmesi izlenme durumudur; sırf düğmenin içinde tik var diye film önceden izlenmiş sayılmaz. Gerçek izlenmiş durumda disk turkuaz dolar ve ilgili listeye geçer.

### 2.3 Girişler, düğmeler, disclosure ve kaydırma

Giriş tabanı `#22221E`, 1 px normal sınır, 6 px köşe; yatay iç boşluk 14 px. Arama ikonu 20 px, metne 10 px uzaklık. Placeholder soluk; girilmiş metin krem. Sekonder düğme koyu taban/krem yazı; ana düğme metalik altın/koyu yazı. Metin linki 14 px, alt çizgi %60 opak.

Disclosure satırı normalde 40 px, sağda 16 px iç boşlukta 16 px chevron; açıkken alt içerik gerçek akışta yer alır. Kart üstünde dekoratif şevronları çoğaltmayın; referansların bazılarındaki iki chevron üretim artığıdır, tek durum ikonu yeterlidir.

Masaüstünde sidebar ve ana panel ayrı dikey kaydırılır; başlıklar/pinli kategoriler sabittir. Scroll rayı 8 px, `#22251E`; tutamak `#777A70`, %60; köşe 4 px. İçerik kesildiğinde görünür scrollbar tercih edilir. Sayfa hiçbir zaman tıklanan platform bölümüne aşağı kaymaz. Mobilde tek dikey sayfa ve yatay bilet şeridi vardır; iç içe dikey poster scrollbar’ı yoktur.

## 3. Ekran 1 — results-desktop.png

Referans 1440 × 1024. Sonuçlar 330 px civarında başlar; üst alanın büyüyüp sonuçları aşağı itmesi istenmez.

| Üstten alta eleman | Görsel kutusu yaklaşık x/y/w/h | Uygulama görünümü |
|---|---|---|
| Header | 28 / 0 / 1384 / 80 | Saydam; arkasında üst ışık ve gren |
| Bilet logo | 46 / 14 / 38 / 56 | Düz altın, negatif koyu tik |
| Wordmark | 98 / 3 / 326 / 70 | Fraunces 800 italic 72/76; krem Watch, altın Plan |
| Geri bildirim | 1018 / 32 / 78 / 20 | 14/20 sans link |
| Türkçe | 1124 / 24 / 108 / 36 | Koyu dropdown |
| Türkiye (TR) | 1254 / 24 / 140 / 36 | Koyu dropdown |
| Nasıl kullanılır? | 28 / 84 / 1384 / 40 | Kapalı disclosure; 16/22 düz serif |
| Kullanılmış upload şeridi | 28 / 130 / 1384 / 52 | Koyu panel, 1 px sınır; sol ikon 28 px; metin 16 |
| Üç ikincil işlem | 816 / 138 / 574 / 34 | Letterboxd Top 500 yükle; IMDb Top 250 yükle; Listeyi kaldır. 1 px dikey ayırıcılar |
| TÜRKİYE KATALOĞU | 38 / 192 / 240 / 16 | 12/16 mono, +1.5 px |
| Sekizli istatistik | 32 / 214 / 1376 / 64 | Eşit 172 px hücre; sayı 26/30; etiket 14/18; 1 px dikey ayrım |
| Listende ara... | 28 / 290 / 1384 / 40 | Tam genişlik arama |
| Kontrol odası | 28 / 340 / 1384 / 616 | 8 px köşe; sol/sağ ayrı yüzey ve scroll |
| Sol sidebar | 28 / 340 / 312 / 616 | Sağda 1 px ayırıcı; 12 px yatay iç boşluk |
| Sağ panel | 344 / 340 / 1068 / 616 | Sakin koyu zemin, 18 px iç boşluk |
| İzlediğin filmler (1) | 28 / 968 / 1384 / 40 | Kapalı disclosure; 16/22 düz serif |

İstatistikler sırası: **9 Platform · 99 Yeni abonelikle film · 34 Zaten sende var · 1 İzledin · 61 Kirala/satın al ile izlenebilir · 55 Hiçbir yerde yok · 3 Eşleşme kontrolü önerilir · 250 Toplam watchlist**. 9/99/61 altın, 34 turkuaz, 3 turuncu; diğerleri krem. Aynı sayı boyutu ve eşit hücre genişliği korunur. Uzun etiketler iki satır olabilir.

### Sidebar içi

- Başlık: x=46, y=358, 180 × 18; `ABONELİK SIRASI`, 12 px mono. + düğmesi x=240,y=352,28×28; zar x=286,y=352,28×28. Gerçek tıklama hedefi 32 px.
- İlk ayırıcı y=388; kategoriler x=46, y=400/428/456, yükseklik 22. Sayılar sağda x≈298. `Zaten sende var` sayısı turkuaz, diğerleri krem. Kategori alanı alt çizgisi y=486.
- Biletlerin x’i 40, genişlik 276; y değerleri yaklaşık 500, 576, 652, 728, 804, 880. TV+ 56 film aktif; Disney Plus 35 film sahip olunan; sonra 02 HBO Max 32 film, 03 Netflix 23 film, 04 MUBI 20 film, 05 MUBI Amazon Channel 19 film. Sıra bu şekilde sabittir.
- Scrollbar x≈332. Üst başlık/kategoriler yerinde; bilet gövdesi kayar. Çok uzun listedeki son biletleri sığdırmak için bütün biletleri küçültmeyin.

### Sağ panel içi

- Başlık satırı x=362,y=350, yükseklik 52. `1. SIRA` pill x=362,y=356,94×32; 1 px altın, 12 px mono. TV+ x=474,y=346,104×54; 48 px italik. `56 film` x=588,y=368,80×24; 18 px.
- Görselde ilk poster satırı y=412; kolon x’leri yaklaşık 362,510,658,806,954,1102,1250; her biri 130 px, yatay aralık 18 px. Görsel ikinci satır y≈672; üçüncü y≈944’te kısmen görünür.
- Uygulamada 7 kolon; kullanılabilir genişlik 1018 px ise (1018−6×18)/7=130 px. İlk poster y=412, yüksekliği 195; başlık grubu 70 px’e kadar; satırlar arasında 16 px. Böylece ikinci satır, kaynak raster’a göre bir miktar aşağı gelebilir. Sıkıştırılmış poster yerine doğru oran korunur.
- Eşleşme uyarısı yalnız Kazablanka’da, yani ilk satır 2. kolonda. Arka plan hiç parlamaz; panelin geniş alanını poster renkleri canlandırır.

**Neden:** üst alan kontrol sunar; sağ panel dikkati içerikte tutar. Platformlar karşılaştırılabilir küçük biletlerdir; her platform için uzun ayrı sayfa bölümü yoktur. 1024 px yükseklikte panelin altından yeni satır görünmesi, içerik devamını anlatır. Daha kısa pencerede panel minimum 400 px olacak şekilde sayfa uzayabilir; bütün UI ölçeklenmez.

## 4. Ekran 2 — results-A-owned.png

1440 × 1024, **yalnız ana panelin bağımsız ayrıntısı**. Tam sayfadaki header/sidebar burada eksik değil; bilerek gösterilmiyor.

| Eleman | Yaklaşık kutu | Özellik |
|---|---|---|
| Dış ana panel | 26 / 28 / 1388 / 992 | 8 px köşe, 1 px normal sınır, sakin koyu yüzey |
| Turkuaz dış gren | Kenarlarda 24 px | Bu ayrıntı sunumuna özgü; gerçek sayfanın kenar dekorunu değiştirmez |
| Zaten sende var | 48 / 42 / 900 / 82 | 80/88 Fraunces bold italic, `#79B7A8` |
| Alt başlık | 48 / 126 / 900 / 30 | `Zaten izleyebilirsin · Disney Plus (34 film)`, 26/32 düz serif |
| Turkuaz ayırıcı | 48 / 160 / 1346 / 1 | Turkuaz %65 |
| İlk poster satırı | 48 / 192; 7 kolon | Yaklaşık 170 px genişlik; x adımı 198 px; aralık 28 px |
| İkinci poster satırı | y≈550 | Aynı kolonlar |
| Üçüncü satır | y≈904 | Alt sınırda kesilir |
| Scrollbar | 1396 / 180 / 12 / 826 | Panel içinde |

Poster/kontrol kuralları ortak tanımdır. Bu büyük ayrıntıda kontrol diski 34 px, ad 20/24, yıl 16/21, yardımcı satır 14/18. Uygulama poster yüksekliği 255 px; ilk satır açıklama alanı 96 px, satır boşluğu 16 px. Kazablanka uyarısının yanında normal “Ayrıca” satırı da gerekiyorsa kart yüksekliği artar; uyarı satırını gizlemeyin.

**Tam sayfa içine aktarım:** sağ panel x=344’te kalır. Başlık 36/42 turkuaz; alt başlık 16/22; ilk poster başlıktan 20 px sonra. Sidebar’da `Zaten sende var 34` aktif kategori görünür; Disney Plus sahiplik bileti aynı yerde kalır. Sahip olunan filmlerin başka platformlarda da bulunması, `Ayrıca` satırını kaldırmaz.

**Neden:** turkuaz “hemen izleyebilirsin” anlamını taşır; yeni bir abonelik sırası gösterilmez. Bu durumda `1. SIRA` pill’i kullanılmaz.

## 5. Ekran 3 — results-B-rent-buy.png

1440 × 1024, yalnız ana panel ayrıntısı. Çevrede ince sıcak gren; iç yüzey sakin koyu.

| Eleman | Yaklaşık kutu | Özellik |
|---|---|---|
| Başlık | 38 / 8 / 1340 / 70 | `Kirala/satın al ile izlenebilir`, 68/76 italic serif, krem; son kısımda hafif altın ışık olabilir |
| Alt başlık | 38 / 82 / 1200 / 30 | `Kirala/Satın Al ile İzleyebilirsin (61)`, 26/32 sans |
| Ayırıcı | 38 / 120 / 1362 / 1 | Altın %65 |
| İlk poster satırı | x≈38,232,426,620,814,1008,1202; y=142 | 172 px civarı poster; 22 px aralık |
| İlk satır ad/yıl | y≈394/418 | 20/24 serif; 16/21 mono |
| Fiyatlar | y≈442–534 | Bir veya iki nötr etiket |
| İkinci poster satırı | y≈552 | Aynı kolonlar |
| Üçüncü satır | y≈948 | Kısmen görünür |
| Scrollbar | 1414 / 128 / 12 / 840 | Sağ kenarda |

### Fiyat etiketleri

Her kartta 1–2 etiket; genişlik kart kadar, yükseklik 48 px; aralarında 6 px. Koyu `#22221E`, 1 px `#8B826D`, köşe 8 px; 12 px yatay / 6 px dikey iç boşluk. Üst satır sağlayıcı 13/17 sans 500; alt satır işlem ve fiyat 13/18 mono. Örnek içerik iki satıra bölünür ama anlamı korunur:

- `Apple TV Store · Kirala · 24,99₺`
- `Amazon Video · Satın Al · 179,99₺`

Referans görselde sağlayıcı ayrı ilk satırdadır; nokta ayırıcıları ikinci satırda kullanılabilir. Gerçek fiyat ve sağlayıcı veriden gelir. Bunlar turuncu, üçgen veya uyarı zeminli değildir. Kazablanka eşleşme uyarısı ayrı turuncu satırdır.

Tam sonuç panelinde başlık 32/38; iki satıra izin verilir, alt başlık 16/22. İki fiyat etiketi bulunan kartların satırı daha yüksek olur; bütün satırdaki diğer poster başlangıçları hizalı kalır. Fiyat listesi uzarsa ilk iki seçenek ve ayrıntı erişimi kullanılır; poster kartı sınırsız uzamaz.

**Neden:** kiralama bir ek ödeme seçeneğidir; abonelik planının sırasına karışmaz. Nötr çipler fiyat bilgisi ile eşleşme uyarısını birbirinden ayırır.

## 6. Ekran 4 — results-C-unavailable.png

1440 × 1024. Poster yok; film başlığı ve yıl içeren akışkan çipler var. Uygulamada çipler metindir, tek bir görsel değildir.

| Eleman | Yaklaşık kutu | Özellik |
|---|---|---|
| Hiçbir yerde yok | 46 / 44 / 1100 / 96 | 88/96 italic serif, krem |
| Alt başlık | 46 / 150 / 1260 / 36 | `Hiçbir platformda abonelikle bulunamadı (55)`, 30/36 sans |
| Ayırıcı | 46 / 196 / 1348 / 1 | Altın %65 |
| Çip bulutu | 44 / 232 / 1338 / 736 | Satır kırılan değişken genişlikli etiketler |
| Scrollbar | 1406 / 218 / 12 / 760 | Sağ kenarda |

Ayrıntı görünümünde çip yüksekliği 52 px, yatay aralık 14 px, dikey aralık 10 px; yatay iç boşluk 18 px. Normal zemin `#20211C`, sınır 1 px `#58594B`, köşe 8 px. Ad 20/24 düz serif 600, yıl 16/22 mono ikincil; aralarında 14 px. Yıl adın bir parçası değil, ayrı tipografik roldedir. İlk satır örnek kutular:

| İçerik | x/y/w/h |
|---|---|
| 12 Angry Men 1957 | 44 / 232 / 240 / 52 |
| Cinema Paradiso 1988 | 298 / 232 / 306 / 52 |
| City of God 2002 | 618 / 232 / 216 / 52 |
| Harakiri 1962 | 848 / 232 / 192 / 52 |
| Persona 1966 | 1054 / 232 / 188 / 52 |

`Cinema Paradiso 1988` çipinde sol 24 px turuncu uyarı; içerik için fazladan 30 px ayrılır. Görselde sınırı altına yaklaşır; uygulamada durumun kesinliği için `#EF8755` %75 sınır kullanın. Kalan çiplerde turuncu yok. 55 öğe eşit kolonlara zorlanmaz; akış halinde satır tamamlanınca alta geçer. Çok uzun başlık çip maksimum genişliğini aşarsa başlık iki satıra sarılır, yıl son satırda kalır.

Gerçek sağ panelde başlık 36/42; alt başlık 16/22; çipler 38 px minimum yükseklik, ad 15/20, yıl 12/18, yatay boşluk 12, çip aralığı 8 px. Aynı filmler gösterilir; 1440 px ayrıntıdaki 12 satırlık bulutu 1068 px panel içine küçültülmüş resim gibi sığdırmayın.

**Neden:** olmayan içerik için renkli poster duvarı yanlış beklenti yaratır. Yoğun metin listesi gözle taramayı ve eşleşmesi şüpheli başlıkları bulmayı hızlandırır. Alt başlık abonelik bulunamamasını söyler; veri gerçekten kiralama dahil hiçbir seçenek yok anlamına geliyorsa kategori kapsamı veri tarafında tutarlı tutulmalıdır.

## 7. Ekran 5 — first-visit-desktop.png

1440 × 1100. Bu ekranın odağı boş kontrol odası değil, liste yükleme eylemidir. Sonuç listesi, istatistik veya sidebar gösterilmez.

| Eleman | Yaklaşık kutu | Yüzey / yazı |
|---|---|---|
| Header | 56 / 24 / 1332 / 90 | Saydam; sonuçla aynı marka sistemi |
| Bilet / wordmark | 78 / 40 / 412 / 68 | İşaret yaklaşık 42×62; wordmark 80/88 |
| Header sağ kontroller | 986 / 56 / 400 / 40 | Link; 118×40 dil, 154×40 ülke |
| Tek satır anlatım | 78 / 130 / 1260 / 30 | 22/30 sans; tam metin aşağıda |
| Açık rehber paneli | 56 / 184 / 1332 / 400 | Sakin ana panel, 1 px sınır, köşe 8 |
| Nasıl kullanılır? başlık satırı | 78 / 202 / 1288 / 38 | 24/30 düz serif; yukarı chevron sağda |
| Yatay ayırıcı | 78 / 238 / 1288 / 1 | Normal düşük kontrast |
| Beş adım | 82 / 264 / 854 / 296 | Her adımda 44 px numara dairesi ve metin |
| Dikey ayırıcı | 956 / 264 / 1 / 296 | Sağ video alanını ayırır |
| Video kapağı | 990 / 264 / 366 / 264 | 1 px açık sınır, 8 px köşe; görüntü kırpılarak doldurulur |
| Video açıklaması | 990 / 546 / 366 / 24 | 18/24 sans; ortalı |
| Büyük bilet upload alanı | 56 / 608 / 1332 / 360 | Doku/ışık ve ayrı çerçeve; aşağıya bakın |
| İki örnek liste düğmesi | 406 / 990 / 320 / 60; 742 / 990 / 294 / 60 | Koyu taban, altın 1 px sınır, 8 px köşe, 16/22 sans |

Pitch: **Letterboxd watchlist CSV'ni sürükle, hangi sırada hangi platforma abone olman gerektiğini gör.** Bu genişlikte tek satır. Daha dar ekranda doğal sarılmalı; fontu küçültmek için tek satıra zorlanmamalı.

Rehberde daire merkezlerinin y değerleri yaklaşık 286,350,412,474,536. Çizgi 2 px altın; sayı 24/28 mono, krem. Metin x=158’den başlar; 18/26 sans. Uzun adım varsa bir sonraki adıma doğru alan büyür; video dikey ortalı kalır. Tam metinler:

1. Letterboxd'da Profil → Watchlist → Export watchlist yoluna git, bir .csv dosyası doğrudan iner.
2. O CSV dosyasını aşağıdaki alana sürükle-bırak (ya da tıkla ve seç).
3. Üst taraftan ülkeni seç (varsayılan Türkiye).
4. Arama bitince hangi sırayla hangi platforma abone olacağını görürsün.
5. Poster'in sağ üstündeki ✓ izledim işaretler, sol üstteki ⚠ eşleşmeyi kontrol etmeni önerir.

Video etiketi: **1. adımı video olarak izle (56 sn)**. Kapakta oynat ikonu 72 px yuvarlak, 2 px altın, koyu %85 taban; merkezde 28 px üçgen. Bu oynat kontrolü kapağın dosyasına gömülmez; ayrı etkileşim katmanıdır. 1280×720 kaynak görsel mevcut 366×264 kutuda kırpılır; önemli yazı kaybolursa kutuyu 366×206 yapıp kalan yükseklikte açıklamayı ortalayın.

### Upload biletinin yapısı

1. Koyu taban, 1332×360; dış form iki kısa kenarın ortasında 44 px yarıçaplı içbükey çentik taşır. Çentiklerin içinde sayfa zemini görünür.
2. İç yüzey: gren %20; sağdaki projektör yelpazesi %32. Metin çevresindeki yaklaşık x=340–1090/y=790–900 alanına sakin koyu bir geçiş gelir.
3. `4-bilet-cercevesi.png` yalnız çevrede: ince yanık krem kenar; sol/sağ perforasyon, iki büyük çentik. Önerilen görünür kenar kalınlığı 10–18 px; yan perforasyon bandı 40 px. Çerçeve varlığı 2400×700 iken bu kutu daha basıktır; ortayı ölçeklemek kabul edilebilir, çentiklerin daireselliği için köşe/yan parçaları ayrı ölçeklemek daha iyidir.
4. İç kesik çizgi: sınırdan 22 px, 2 px altın, yaklaşık 8 px çizgi / 8 px boşluk; varlığa zaten gömülüyse ikinci kez çizilmez.
5. Upload belge ikonu: yaklaşık x=678,y=686,84×102; 6 px altın çizgi. Metin: `CSV dosyasını buraya sürükle`, x≈386,y≈802; 48/56 Fraunces düz 650, ortalı. Alt satır `ya da tıkla ve seç`, 28/36 sans, y≈862.
6. Tüm alan aynı dosya seçim/drop hedefidir; ikon ayrı zorunlu tıklama noktası değildir. Sürükleme hover’ında iç kesik sınır aydınlanır; doku artmaz.

**Neden:** büyük bilet, yükleme işini görünür tek ana eylem yapar. Ağır görsel enerji yalnız bu ekranda ve bilet çevresindedir; beş adım ve video yazıları sade yüzeyde kalır.

## 8. Ekran 6 — loading-desktop.png

1440 × 1050. Üst bölüm ilk ziyaretin devamıdır; upload küçülür. Rehber kapanır. Görselde iki ilerleme durumu **birlikte karşılaştırma amacıyla** gösterilmiştir; gerçek uygulamada aktif arama aşamasına uygun olanı gösterin, ikisini iki ayrı eşzamanlı iş gibi yorumlamayın.

| Eleman | Yaklaşık kutu | Özellik |
|---|---|---|
| Header | 48 / 32 / 1344 / 92 | Logo x≈78,y=54; wordmark 80/88; sağ kontroller y≈70 |
| Pitch | 72 / 152 / 1296 / 30 | İlk ziyaretle aynı metin, 22/30 sans |
| Nasıl kullanılır? | 48 / 202 / 1344 / 52 | Kapalı, 24/30 düz serif; chevron sağda |
| Slim upload | 48 / 270 / 1344 / 66 | 1 px sınır; belge 30 px; yazı 18/24; işlemler sağda |
| İlerleme kartı | 128 / 384 / 1184 / 496 | 12 px köşe; 1 px altın %70; kenarlarında ince gren; orta sakin |
| İlk ikon | 270 / 450 / 54 / 50 | Altın geometrik film karesi; JustWatch logosu değil |
| JustWatch'ta aranıyor… | 348 / 438 / 900 / 78 | 72/82 italic serif; krem/altın, tek satır |
| Yüzdeli bar | 216 / 546 / 956 / 28 | Koyu ray; %60 altın dolu; tam yuvarlak |
| 60% | 1192 / 544 / 72 / 34 | 26/34 mono, krem |
| [150/250] Dune: Part Two | 216 / 592 / 800 / 34 | 26/34 mono, krem |
| İç ayırıcı | 186 / 648 / 1068 / 1 | Normal sınır |
| İkinci ikon / başlık | 248 / 702 / 900 / 56 | 48 px ikon; `JustWatch kataloğu taranıyor (4/20)`, 44/54 italic serif |
| Belirsiz bar | 222 / 786 / 996 / 32 | Köşe 16; altın/charcoal şeritler |

Yüzdeli barın dolu uzunluğu rayın %60’ıdır; toplam watchlist sayısına göre hesaplanır. Altın yüzey solda `#E8BE70`, ışık şeridinde `#F4D695`, uçta `#DAB56D`; aşırı kabartma yok. Belirsiz bar 45° çizgiler, 24 px altın / 24 px koyu periyot, altın opaklığı %60. Şerit hareketi sakin; bilgi hızı animasyona bağlanmaz. Azaltılmış hareket tercihinde sabit desen yeterlidir. `(4/20)` süreç açıklamasıdır; %20’ye çevrilmiş dolgu değildir.

**Neden:** arama sırasında boş sonuç alanı yerine durum ve son film adı verilir. Büyük başlık bu geçici durumun odağıdır; sonuç paneline aynı boyutta taşınmaz. Çok uzun film adı detay satırında iki satıra sarılır, barı sıkıştırmaz.

## 9. Ekran 7 — modals-desktop-grid.png

### 9.1 Sunum koordinatları ve gerçek diyalog boyutları

Dosya 1435×1096; dört bölmenin her biri yaklaşık 714×536 veya 714×556. Bunlar tam masaüstünün küçültülmüş sunumlarıdır. Bu nedenle dosyadaki 14 px metin gerçek arayüzde 14 px’e karşılık gelmez. Modal genişliklerini ikiye katlayıp başlığı 72 px yapmak da doğru değildir. Aşağıdaki **gerçek uygulama** ölçüleri başlıkların onaylanan ölçülü niteliğini korur.

| Modal | Sunum tuvalindeki yaklaşık kutu | 1440×1024 gerçek pencerede hedef kutu |
|---|---|---|
| Rastgele Film | 168 / 48 / 384 / 454 | x=480,y=162,w=480,h=700 |
| Eşleşmeyi kontrol et | 872 / 42 / 432 / 462 | x=380,y=184,w=680,h=656 |
| Film ekle | 152 / 586 / 424 / 448 | x=380,y=196,w=680,h=632 |
| Geri bildirim | 896 / 606 / 356 / 388 | x=460,y=232,w=520,h=560 |

Gerçek kutular yatay/dikey ortalanır; y değerleri yalnız bu pencere yüksekliğinde referanstır. Dış kenar payı minimum 24 px. İçerik pencereye sığmazsa diyalog içi kayar; kapatma erişilebilir kalır. Arka sayfa kaydırması modal açıkken durur. Karartma tam pencere siyah %68; arka sayfanın tipografisi bulanıklaştırılmak zorunda değildir.

### 9.2 Ortak modal çerçevesi

- Ana yüzey `#1C1D18`; içerik kenarından 24 px içeri başlar. Altın 1 px dış çizgi; 12 px temel köşe; ikinci iç çizgi dıştan 5 px içeride `#DAB56D` %20.
- Sol ve sağda 10 px genişliğinde dar yanık kâğıt bandı: koyu altın/krem, %55 yoğunluk. 8 px aralıklarla 3 px yarıçaplı küçük içbükey girintiler. Şevron/testere değil, eski bilet perforasyonudur. Üst ve altta 8 px genişlikte yumuşak omuz/çentik detayı.
- Bu yan kenar gerçek içerik alanına girmeyen dekor katmanıdır. Uygulama için tek uzun PNG’yi farklı yüksekliğe germek yerine üst/orta/alt çerçeve parçaları veya tekrar eden yan şerit gerekir. Sade geometrik oyuklar CSS maskesiyle yapılabilir; yanık lifler raster gerekir.
- Kapatma: sağ üstten 16 px; görünen 28 px disk, gerçek hedef 36 px. 1 px açık sınır; 16 px krem ×. Modal başlığıyla çakışmaz.
- Başlık 36/42 Fraunces 750 italic; başlık yanındaki ikon 28 px altın. Çerçeve doku %10’dan fazlası metin alanına yayılmaz. Güçlü dış gölge global tanımdaki gibidir.

### 9.3 A — Rastgele Film

Gerçek 480×700 modal içinde koordinatlar sol üstüne göredir:

| Eleman | Göreli x/y/w/h | Görünüm |
|---|---|---|
| Başlık ve zar | 24 / 24 / 400 / 42 | `Rastgele Film`; 28 px altın geometrik zar |
| Kapalı seçim disclosure | 24 / 82 / 432 / 70 | Koyu form yüzeyi, 1 px sınır, 6 px köşe; 14/20 sans |
| Büyük poster | 140 / 172 / 200 / 300 | 2:3; 4 px köşe; ince açık sınır; tek sahte mahkeme posteri |
| Film adı | 24 / 492 / 432 / 52 | `Witness for the Prosecution (1957)`, 22/26 düz serif; iki satıra izin |
| Platform çipi | Merkez / 558 / içerik kadar / 30 | `Amazon Prime Video`; 14/20 sans, altın 1 px sınır, koyu zemin |
| Ana düğme | 24 / 622 / 208 / 44 | `🎲 Başka film`, metalik altın; 15/20 koyu sans |
| İkincil düğme | 248 / 622 / 208 / 44 | `İzledim işaretle`, koyu zemin altın sınır |

Son düğmenin altında 34 px nefes payı kalır. Modal minimum yüksekliği içerikten gelir; uzun başlık veya açık disclosure varsa gövde büyür ve pencere sınırında kayar. Sunum posterinin 172×212 gibi yassı görünmesi üretim sapmasıdır; 2:3 korunur. Disclosure tam metni: **Rastgele film önerisi hangi platformlar arasından seçilsin? (boş bırakırsan tüm watchlist)**. Açıldığında platform seçimleri görülür; boş seçim tüm watchlist demektir.

Neden: tek büyük poster çekiliş hissini verir; ikinci film önerisi hızlıdır. Zar emoji yerine onaylı geometrik zar ikonu olarak çizilebilir; düğmenin erişilebilir metni aynı kalır.

### 9.4 B — Eşleşmeyi kontrol et

680×656 modal içinde: başlık x=24,y=24; alt başlık x=24,y=74,632×24; **Casablanca (1942) için JustWatch sonuçları**, 16/22 sans. Arama y=112,h=40; giriş x=24,w=530, Ara x=566,w=90. Alan değeri `Casablanca`.

Sonuç ızgarası x=40,y=172,w=600: 4 kolon, 40 px yatay aralık; poster 120×180; ad 14/18 düz serif, yıl 12/16 mono. İlk satır açıklamaları için 42 px, satırlar arasında 20 px; ikinci satır başlangıcı y=414. Böylece sekiz adayın tamamı görünür, son açıklama alanı y=636’da biter ve altta 20 px kalır. Tüm aday kartlarının tıklama alanı görsel+metindir. Uzun aday adları bu 42 px alanı aşarsa satır yüksekliği büyür; diyalog gövdesi y=160’tan itibaren kayabilir. Maksimum diyalog yüksekliği pencerenin %90’ıdır; isim sığdırmak için posterler yassılaştırılmaz.

Adaylar dört üst/dört alt: Kazablanka 1943; Casablanca 1955; Casablanca 1983; Casablanca 2002; Kazablanka 1961; Casablanca 2010; Casablanca 1997; Casablanca 2023. İkinci aday hover: 2 px altın dış sınır, 4 px köşe, %6 altın iç ışık. Bu henüz seçim kaydedildi anlamına gelmez; tıklama ile seçim yapılır. Görseldeki imleç gerçek asset değildir.

### 9.5 C — Film ekle

680×632 modal. Başlık x=24,y=24; arama x=24,y=82,w=530,h=40; Ara x=566,y=82,w=90,h=40. Alan değeri `Paprika`. B’nin 120×180 posterli dört kolon düzeni; ilk satır y=144, ikinci y=386; ad/yıl alanı 42 px. Alt kenar payı minimum 24 px; gerektiğinde gövde kayar.

Sekiz aday: Paprika 2006, 1991, 2018, 1989, 2014, 2020, 2001, 1972. Arama sonucu başlıkları gerçek veride farklı olabilir. Adaya tıklamak filmi ekleme işlemidir; her poster üstüne sonuç listesindeki ✓/× düğmeleri konulmaz.

### 9.6 D — Geri bildirim

520×560 modal içi:

| Eleman | Göreli x/y/w/h | Görünüm |
|---|---|---|
| Başlık | 24 / 24 / 400 / 42 | 36/42 italic, konuşma balonu 28 px |
| Hangi film hakkında? (opsiyonel) | 24 / 92 / 472 / 22 | 14/20 sans |
| Listende ara... | 24 / 122 / 472 / 40 | Normal arama girişi |
| Mesajın | 24 / 184 / 472 / 22 | 14/20 sans |
| Ne olduğunu anlat... | 24 / 214 / 472 / 128 | Textarea; 14/20; dikey büyüyebilir |
| Gönder | 376 / 358 / 120 / 42 | Altın birincil düğme |
| İnce ayırıcı | 24 / 418 / 472 / 1 | Düşük kontrast |
| Başarı kutusu | 24 / 434 / 472 / 80 | `#1C3935`, turkuaz 1 px sınır, köşe 6 |

Başarı metni: **Site veya film hatalarında geri dönütleriniz için teşekkürler! 🙏**. 14/20 sans, turkuazın açık tonu; solda 24 px turkuaz tik diski. Metin 2–3 satır sarılır. Referansta form ve başarı birlikte gösteriliyor; uygulamada bu mesaj başarılı gönderimden sonra görünür, başlangıçta kalıcı başarı bildirimine dönüşmez.

**Tüm modalların nedeni:** ortak çerçeve festival bileti hissini korur; asıl görev büyük ve düzenli içerik alanındadır. İç yüzeyi komple dokulu kâğıt resmi yapmak, küçük arama sonuçlarını okunmaz hale getirir.

## 10. Ekran 8 — results-mobile-three-screens.png

### 10.1 Ölçek ve genel kurallar

Sunum dosyası 1365×1152. Yaklaşık ekran sınırları: sol x=11–449, orta x=463–903, sağ x=916–1356. Aradaki beyaz boşluklar **sunum oluğudur; gerçek uygulama zemini değildir**. Her görünüm yaklaşık 440×1152 raster piksel; **375 px mantıksal genişliğe** indirgenince yükseklik yaklaşık 982 px olur. Aşağıdaki koordinatlar 375×982 mantıksal ekran içindir. İkinci/üçüncü görünümde üst header tekrar gösterilmiştir; gerçek sayfada header sabit tutulabilir. Bunlar üç ayrı rota değil aynı deneyimin görünüm durumlarıdır.

- Eşik kararı: 768 px altı mobil bilet şeridi, 768 ve üzerinde sidebar. 768–1199 arası posterler 4–5 kolon; 1200 ve üzerinde 7 kolon hedeflenir. Referanslar bu ara boyları çizmedi; bu eşikler uygulama kararlarıdır.
- Dış yatay boşluk 16 px; ızgarada 12–16 px. Doku masaüstünün yaklaşık üçte biri. Yan perforasyon ve yanık film sayfa sınırı kaldırılır.
- Sayfa tek dikey akış; yatay bilet şeridi ayrı kayar. Yatay taşma bütün sayfaya değil yalnız şeride aittir. Belirli yüksekliğe sabitlenmiş iç poster paneli yoktur.
- Üç kolon poster: kullanılabilir 343 px; aralık 12 px; poster genişliği yaklaşık 106 px. 2:3 yükseklik 159 px. 32 px kontrol iki üst köşede birbirine değmeden sığar.

### 10.2 Mobil 1 — üst alan ve istatistik

| Eleman | Mantıksal yaklaşık x/y/w/h | Özellik |
|---|---|---|
| Header | 16 / 12 / 343 / 84 | İki satır; hafif üst ışık |
| Ticket/logo | 20 / 16 / 28 / 38 | Altın; wordmark x=56, 40/44 |
| Geri bildirim | 286 / 28 / 74 / 18 | 11/16 sans link |
| Dil / ülke | 158 / 66 / 82 / 30; 250 / 66 / 109 / 30 | 11/16 sans, 4 px köşe |
| Nasıl kullanılır? | 16 / 104 / 343 / 34 | Kapalı; 14/20 |
| CSV şeridi | 16 / 146 / 343 / 60 | İkon 24 px; `CSV dosyasını buraya sürükle`, 14/20 |
| İki örnek liste eylemi | 16 / 212 / 182 / 38; 206 / 212 / 153 / 38 | 11/16 sans; belge ikonu 16 px |
| Listeyi kaldır | 16 / 256 / 343 / 38 | İkincil; 12/18; çöp ikonu 18 px |
| TÜRKİYE KATALOĞU | 18 / 316 / 330 / 18 | 12/16 mono |
| İstatistik gridi | 18 / 342 / 341 / 310 | 2 kolon, 4 satır; yatay/dikey 1 px ayırıcı |
| ABONELİK SIRASI ve +/zar | 18 / 666 / 341 / 38 | Başlık 12/16 mono; kontroller 36 px |
| Bilet şeridi | 0 / 710 / 375 / 78 | Kırpılmış yatay kaydırma; aşağıda ayrıntı |
| Şerit kaydırma göstergesi | 12 / 794 / 351 / 10 | Nötr ray; gerçek kaydırmaya bağlı |
| Listende ara... | 16 / 822 / 343 / 38 | 14/20 sans |
| Seçili platform başlığı | 16 / 876 / 343 / 46 | Pill + 42/46 italic TV+ + 16 px sayı |

İstatistik hücreleri eşit önemdedir; yaklaşık 170×77 px. Sayı 24/28; etiket 13/18; sayıdan etikete 4 px. Sol/sağ eşler sırasıyla 9/99, 34/1, 61/55, 3/250. `Kirala/satın al ile izlenebilir` ve `Eşleşme kontrolü önerilir` iki satır. Bu bölümde turkuaz ve turuncu yalnız ilgili metrikte. Sayıları tek bir büyük kahraman toplam etrafında kurmayın.

Neden: ilk ekran veri kapsamını küçük ama eşit hücrelerde anlatır. Üç ikincil eylem 375 px’te aynı satıra zorlanmaz. Gerçek font genişliğinde düğme metinleri sığmazsa ilk ikisi de tam genişlik alt alta olabilir; 10 px altına küçültmeyin.

### 10.3 Mobil 2 — kontrol odası

| Eleman | Mantıksal yaklaşık x/y/w/h | Özellik |
|---|---|---|
| Header | 16 / 12 / 343 / 84 | Mobil 1 ile aynı |
| ABONELİK SIRASI | 18 / 122 / 212 / 20 | 12/16 mono; + x=272, zar x=324; 36×36 |
| Yatay bilet şeridi | 0 / 158 / 375 / 78 | Taşan sağ kenar; aşağıya bakın |
| Kaydırma rayı | 8 / 242 / 359 / 10 | Küçük nötr gösterge |
| Arama | 16 / 268 / 343 / 38 | Listende ara... |
| Platform başlık satırı | 16 / 320 / 343 / 46 | Pill x=16,w=84,h=30; TV+ x≈116; 56 film x≈222 |
| İlk poster satırı | x≈16,136,256; y≈376 | 103–106 px genişlik; doğru oran 155–159 px |
| İlk açıklama alanı | y≈534–598 | Ad/yıl/yardımcı ya da uyarı |
| İkinci poster satırı | y≈618 | Aynı kolonlar |
| Üçüncü satır | y≈858 | Alt kenarda devam eder |

Biletlerin normal genişliği 156 px, yükseklik 78 px; aralık 8 px. Kategori bileti 118 px olabilir. TV+ aktif bilette altın şerit 10 px, çentik yarıçap 7 px, sıra 22/26 mono, platform 16/19 serif, film sayısı 12/16. Owned stub etiketi 9/12 mono; sahiplik checkbox 20 px görünür, 32 px hedeflidir.

Görsel şerit kaydırılmış durumdadır: ilk `Zaten sende var 34` biletinin son 70 px’i solda görünür; TV+ x≈80–236 arasında tamamı görünür; Disney Plus x≈244’ten başlar, sağda kesilir. `02 HBO Max 32 film` veri sırasındaki bir sonraki bilettir; kadraja sığması için biletleri daraltmayın. İlk kategori, abonelik ticket’ıyla aynı yükseklikte ama sıra numarasız turkuaz paneldir. +/zar şeritle birlikte kaymaz; başlıkta erişilebilir kalır.

Poster ✓ ve ×: 32 px disk, 18 px ikon, sağdan 4 px; uyarı 32 px hedef, sol 4 px. Kazablanka’nın turuncu satırı iki satırdır; “Ayrıca” zorunluysa onun altına gelir. Kaynak resimde posterler biraz uzun görünür; 2:3 normu geçerlidir. Dokunmada hover’a bağımlı bilgi yoktur.

Neden: sidebar’ın mantığı korunur, yönü değişir. Sağdan kesilen bilet daha fazla seçenek olduğunu anlatır. Posterler üç kolonla görsel ağırlığı korur; 32 px kontroller için 4 kolon kullanılmaz.

### 10.4 Mobil 3 — Rastgele Film bottom sheet

Arka plan mobil 2; siyah %68 örtü. Onaylı görselde sheet üstü yaklaşık y=278’dir. Sheet üstünde merkezde tutamak; aşağıya uzanır ve ekran tabanına sıfır dayanır. Görselin altı sayfa kartı değil alt paneldir.

| Eleman | Mantıksal yaklaşık kutu | Özellik |
|---|---|---|
| Sheet | 0 / 278 / 375 / 704 | Üst köşe 24; alt köşe 0; 1 px altın; sakin koyu yüzey |
| Tutamak | 160 / 292 / 56 / 5 | `#777A70`, köşe 3 |
| Kapat | 330 / 294 / 32 / 32 | Krem ×; ince açık sınır |
| Başlık/zar | 24 / 326 / 312 / 38 | 30/36 italic serif; 28 px zar |
| Kapalı platform disclosure | 16 / 380 / 343 / 60 | 12/18 sans; tam metin 2–3 satır |
| Poster | 86 / 460 / 203 / 244, görsel referansı | Raster oranı sapmış; uygulamada aşağıdaki düzeltme |
| Film adı | 20 / 712 / 335 / 48 | 20/25 serif; iki satır, ortalı |
| Amazon Prime Video | Ortalı / 774 / 180 / 30 | 14/20 nötr çip; altın 1 px kenar |
| Başka film | 16 / 820 / 343 / 52 | Ana altın düğme |
| İzledim işaretle | 16 / 884 / 343 / 52 | İkincil koyu düğme |

**Uygulama kararı:** poster 160×240 px, ortalı; böylece 2:3 düzelir ve alt düğmeler korunur. Başlık ve disclosure aralıkları 16 px; posterin üst/altı 16 px. Sheet yüksekliği içeriğe bağlıdır, en fazla görünür alanın %92’si. 982 px’ten kısa pencerede sheet daha yukarı açılır ve yalnız iç gövde kayar; iki alt düğme güvenli alt alana yapışık kalabilir. Alt boşluk minimum 20 px + cihazın güvenli alanı. Rastgele film uzun başlığı iki/üç satır olduğunda poster en fazla 160 px genişlikte kalır, düğmeler kırpılmaz.

Tam disclosure: **Rastgele film önerisi hangi platformlar arasından seçilsin? (boş bırakırsan tüm watchlist)**. Platform seçimi disclosure içinde açılır. Düğme etiketleri **🎲 Başka film** ve **İzledim işaretle**. Bütün sheet’i masaüstü modal gibi merkezde boşlukla yüzdürmeyin. Sunumdaki gibi masaüstü perforasyon şeritleri eklemeyin; üstte tek ince altın kenar yeterlidir.

Neden: alttan gelen panel başparmak erişimine uygundur; seçilen film ana içerikten kopmadan görülebilir. Sheet’in kaydırma/kapama davranışı gerçek uygulamada belirgin olmalı; süs panelin kapanmasını zorlaştırmamalıdır.

## 11. Ayrı görsel varlık envanteri

Bu bölüm üretim listesi ve mevcut dosyaların rolünü tanımlar; yeni görsel üretilmemiştir. Tam sayfa birleşik arka plan gerekmiyor. Renkler, sınırlar, düz ışık geçişleri, pill’ler, çentiklerin geometrisi, progress çizgileri ve metinler kodla oluşturulabilir. Aşağıdaki **organik doku / resim içeriği** aynı görünüm için ayrı dosya ister.

| Varlık | İçerik ve alfa | Kaynak boyutu | Tekrar / yerleşim | Durum |
|---|---|---:|---|---|
| Koyu emülsiyon greni | Yakın siyah ince sıcak kâğıt/film greni; yazı yok | 1024×1024 | İki yönde tekrar; 512 px görüntüleme ölçeği | `gpt-assets/1-gren.png` mevcut |
| Projektör ışığı | Altın/turuncu yarı saydam ışık ve ince toz; arka plan alfa | 1920×1080 | Header/bilet içinde döndürülüp kırpılır; tekrar yok | `gpt-assets/2-isik.png` mevcut; dosya yönü mockup’a doğrudan uymuyor |
| Dikey film perforasyonu | Tek kolon organik selüloit ve sıcak glow; çevresi alfa | 80×1600 | Dikey tekrar; 20 px genişlikte gösterim | `gpt-assets/3-film-seridi.png` mevcut |
| Upload bilet çerçevesi | Yanık krem lifler, delikler ve iki yan çentik; merkez ve dış tamamen alfa | 2400×700 | Yalnız büyük yükleme alanı; tercihen kenar parçaları ayrılarak | `gpt-assets/4-bilet-cercevesi.png` mevcut |
| Sosyal paylaşım posteri | Logo/wordmark ve onaylı Türkçe slogan; opak | 1200×630 | Sayfanın UI zemini değil, paylaşım önizlemesi | `gpt-assets/5-paylasim-karti.png` mevcut |
| Rehber video kapağı | Watchlist ve Export watchlist içeren stilize tarayıcı ve ışık; oynat ikonu yok | 1280×720 | Rehber içindeki video kartı | `gpt-assets/6-video-kapagi.png` mevcut |
| Organik dış kenar lekesi | Çok ince yanık turuncu emülsiyon/toz; orta tamamen alfa; çerçeve veya yazı yok | İki yan için 128×1024 veya tek 2048×1536 alfa örtü | Yalnız masaüstü sayfa kenarları | Mevcut altı dosyada bağımsız sürümü yok; salt renk glow’u düz geçişle yapılabilir, tanecik ayrıntısı için gerekir |
| Modal perforasyon dokusu | Koyu altın yanık kâğıt kenarı; içerik tamamen alfa | Üst 800×32, alt 800×32, tekrar eden yan 24×256 | Üst/alt ayrı; yanlar tekrar ederek farklı modal yüksekliğine uyar | Ayrı üretim gerekli olabilir; büyük upload çerçevesini modala germeyin |
| Çok hafif bilet kâğıdı greni | Nötr ince lif; alfa veya nötr gri, turuncu baskın değil | 256×256 | Yalnız bilet yüzeyinde %7; mevcut grenden de türetilebilir | Bağımsız yeni dosya zorunlu değil |
| Yer tutucu film posterleri | Tek tek 2:3, genel sinematik illüstrasyon; gerçek film sanatını taklit etmez | Her biri en az 400×600; öneri 600×900 | Her kart ayrı görsel; tam UI’dan kesilmiş poster kullanılmaz | Üretimde gerçek poster URL’leri gelir; mockup/prototip için ayrı yer tutucu set gerekir |
| Rastgele seçim posteri | Genel mahkeme silueti; yazısız | 600×900 | Modal ve sheet | Ayrı yer tutucu gerekir; gerçek film görseliyle sonradan değişebilir |

Logo ve UI ikonları raster doku değildir: basit bilet+tik, +, zar, arama, belge, çarpı, chevron, konuşma balonu, tik ve uyarı geometrik varlıklardır. Düz CSS/ikon geometrisiyle yapılabilirler. Wordmark fontla kurulabilir; markanın birebir harf şekilleri isteniyorsa ayrıca onaylı wordmark dosyası gerekir. Bu belgede bu dosyalar üretilmemiştir. Logo içinde yazı, platform logosu veya emoji görünümü yoktur; film/işlem ikonlarında aynı çizgi kalınlığı korunur.

### Varlıkların uygulamadan önce teknik kontrolü

Mevcut alfa kanalı, merkezin her pikselinin şeffaf olduğu veya tekrar sınırlarının matematiksel olarak dikişsiz olduğu anlamına gelmez. Önceki üretimde dosyaların boyutları ve alfa kanalının varlığı doğrulandı; **gren ve perforasyonun kusursuz tekrar birleşimi sayısal olarak doğrulanmış değildir**. Döşeme sırasında 3×3 tekrar önizlemesiyle birleşim çizgisi kontrol edilmeli; görünürse aynı varlık düzeltilmelidir. Aynı şekilde çerçevenin merkezindeki tam alfa ve ışığın karartmadan bindirilebilmesi kontrol edilmelidir. Bunlar onaylı UI görünüşünü değiştiren yeni tasarım kararları değildir.

## 12. Gerçek veriyle tasarımı koruma ilkeleri

- Arka planın atmosferi dekor katmanıdır; içerik okumak için gerekli değildir. Metin ve ikonlar her zaman gerçek öğedir.
- Font metrikleri üretim görseliyle birebir eşleşmeyecektir. Önce aile/stil, sonra satır yüksekliği ve kolon genişliği eşleştirilir; tek tek sözcükleri konumlandırarak görünüm taklit edilmez.
- Bütün metinler belgede yazıldığı gibi Türkçe kalır. Özel adlarda orijinal film başlığı kullanılabilir. Platform adları yalnız yazıdır.
- Masaüstü platform seçiminde aktif içerik değişir; sahiplik değişiminde sıra sabit kalır. Kategoriler ve biletler görsel olarak farklı olsa da aynı paneli yönetir.
- Uzun isimde font küçültmek yerine iki satır ve gereken yükseklik verilir. Poster oranı, düğme hedefi ve anlaşılır etiket korunur.
- Uyarı turuncusu yalnız eşleşme uyarısına ayrılır; altın dekor ışığıyla karıştırılmaz. Fiyatlar, sahiplik ve aktif seçim ayrı biçimlerle anlatılır.
- Mobilde 32 px minimum poster hedefi daraltılmaz. İçerik boyu arttığında sayfa/sheet kayar; ekranın tamamı küçültülmez.
- Maketlerde görünmeyen yükleme hatası, boş arama sonucu ve devre dışı durumlar aynı renk/boşluk sistemiyle kurulmalıdır; bu belge onlar için yeni görsel veya yeni metin tanımlamaz.
