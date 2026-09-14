# Watchlist -> Abonelik Plani

Letterboxd watchlist CSV'sini JustWatch katalogu ile eslestirip, "hangi ay
hangi platforma abone olursam watchlist'i en hizli bitiririm" planini
cikaran bir script. Ulke secilebilir (varsayilan Turkiye).

## Kurulum

```
pip install -r requirements.txt
```

Kurulum sirasinda hata alirsan (ozellikle Linux/Mac'te "externally managed
environment" hatasi):

```
pip install -r requirements.txt --break-system-packages
```

## Kullanim (gorsel arayuz - onerilen)

```
python server.py
```

Tarayicida otomatik olarak bir sayfa acilir (http://localhost:8765).
Ustteki acilir menuden ulke sec (varsayilan Turkiye), watchlist CSV
dosyasini sayfaya surukle birak (ya da tikla ve sec) - JustWatch'ta arama
arka planda ilerleme cubugu ile calisir, bitince her platformun altinda
hangi filmleri izleyebilecegin poster'lariyla gorunur. Bir postere
tiklarsan o filmi o platformda izleyebilecegin sayfa yeni sekmede acilir.
Sectigin ulke tarayicida hatirlanir.

Her filmin altinda o filmin bulundugu diger platformlar da kucuk harfle
gorunur ("ayrica: ...").

**Sahip oldugun platformlar**: Stat kutularinin altinda tum platformlar
checkbox olarak listelenir. Zaten abone oldugun platformlari isaretlersen,
plan o platformlardaki filmleri "ucretsiz" sayip yesil bir "Zaten
izleyebilirsin" bolumunde ayri gosterir, aylik plani da sadece geri kalan
filmler icin yeniden kurar. Bu isaretleme sunucuya gitmez, tamamen
tarayicida (aninda) hesaplanir - secimin de tarayicida hatirlanir.

**Izledim isaretleme**: Her film posterinin sag ust kosesindeki tikle
tiklarsan, o film "izlendi" sayilir; plandan (aylik plan, zaten
izleyebilirsin, hicbir yerde yok - hepsinden) kaybolur ve istatistikler
yeniden hesaplanir. En altta "Izledigin filmler" bolumunden hangilerini
izledigini gorebilir, "geri al" ile yanlislikla isaretledigini geri
cikarabilirsin. Bu da tamamen tarayicida, aninda calisir.

**Rastgele film oner**: "Sahip oldugun platformlar" panelinin altinda ayri
bir platform secim listesi ve "Rastgele film sec" butonu var. Hicbir
platform secmezsen tum watchlist'teki izlenebilir filmler arasindan (en az
bir platformda bulunanlar; izledigin filmler havuza girmez), platform
secersen sadece o platform(lar)daki filmler arasindan rastgele bir film
onerir. Postere/baslige tiklamana gerek yok - "Baska film" ile tekrar
zar atabilir, "Izledim isaretle" ile direkt oradan isaretleyebilirsin.

**Eslesme kontrolu**: Bir filmin JustWatch'ta bulunan yili CSV'deki yille
uyusmuyorsa (remake, ayni isimli baska film riski), poster'in sol ust
kosesinde sari bir uyari isareti cikar ve filmin altinda hangi filme
eslesildigi yazar ("JustWatch: ..."). Isarete (ya da "hicbir yerde yok"
listesindeki sari cerceveli filme) tiklarsan, JustWatch'taki tum aday
sonuclar poster'lariyla acilir - dogru olani secince eslesme kalici olarak
duzeltilir ve plan yeniden hesaplanir. Bu, mevcut cache'teki eski
eslesmeler icin de (yeniden arama yapmadan) geriye donuk calisir.

**Watchlist hatirlanir**: Bir kere CSV surukleyip biraktiktan sonra, sunucu
onu `last_watchlist.csv` dosyasina kaydeder. Sayfayi kapatip tekrar
actiginda watchlist otomatik yuklenir - CSV'yi tekrar surukleman gerekmez.
Ulke acilir menusunden farkli bir ulke sectiginde de, elindeki watchlist
icin otomatik olarak o ulkede arama baslar (sadece cache'te olmayanlar
aranir, aynen yukaridaki mantikla). CSV'yi sadece watchlist gercekten
degistiginde (yeni film ekleyip cikardiginda) tekrar suruklemen yeterli -
bu durumda da sadece yeni eklenenler aranir.

Kapatmak icin terminal penceresini kapat ya da Ctrl+C.

## Kullanim (terminal / CLI)

```
python sync.py watchlist-feelslikesyd-2026-08-17-15-39-utc.csv --country TR
```

CSV dosya adini vermezsen, script klasordeki `watchlist-*.csv` pattern'ine
uyan ilk dosyayi otomatik kullanir. `--country` verilmezse TR kullanilir:

```
python sync.py
python sync.py --country US
python sync.py --owned "Netflix,Disney Plus"
```

`--owned` ile zaten sahip oldugun platformlari virgulle ayirarak
verebilirsin - bu platformlardaki filmler "zaten sahip oldugun
platformlarda izleyebilirsin" listesine ayrilir, aylik plan sadece geri
kalan filmler icin kurulur.

Desteklenen ulke kodlari icin `core.py` icindeki `COUNTRIES` sozlugune bak
(TR, US, GB, DE, FR, ES, IT, NL, PT, BR, CA, AU, MX, PL, SE, IN, JP, KR, RU, AR).

Gorsel arayuz ile CLI ayni `justwatch_cache.json` dosyasini paylasir -
hangisini kullanirsan kullan, diger tarafta da cache guncel kalir. Cache
her ulke icin ayri ayri tutulur, yani bir filmi bir kere TR icin aramak
US sonuclarini etkilemez (ve tam tersi).

## Ne yapiyor?

1. CSV'yi okur (`Date, Name, Year, Letterboxd URI` kolonlari).
2. `justwatch_cache.json` icindeki cache'e bakar. Secilen ulke icin
   cache'te olmayan (yeni eklenen, ya da daha once baska bir ulke icin
   aranmis) filmleri tespit edip **sadece onlari** JustWatch'ta arar - ayni
   anda en fazla 6 istek paralel gider (ag gecikmesi darbogaz oldugu icin
   bu onemli hiz kazandirir), ayni baslik+yil birden fazla satirda geciyorsa
   tek arama yapilip sonuc hepsine uygulanir. Zaten o ulke icin cache'te olan
   filmler icin tekrar istek atmaz.
3. Her film icin arama sonuclarindan yil eslesen kaydi secer; eslesme yoksa
   ilk sonucu kullanir. Sadece `FLATRATE` (abonelik) tipi teklifleri
   platform listesine ekler - kirala/satin al teklifleri sayilmaz.
4. CSV'den cikmis ama cache'te hala duran filmleri "watchlist'ten cikmis"
   olarak raporlar (cache'ten silmez, sadece bilgi verir).
5. Sahip oldugun platform olarak isaretlenenler varsa (`--owned` / gorsel
   arayuzdeki checkbox'lar), o platformlardaki filmleri once "zaten
   izleyebilirsin" listesine ayirir, aylik plana dahil etmez.
6. Kalan filmler icin greedy set-cover algoritmasi ile aylik plan uretir:
   her adimda, kalan filmlerin en cogunu kapsayan platformu secer, o
   filmleri listeden dusurur, kalan filmler icin tekrarlar. Hicbir
   platformda (abonelikle) bulunamayan filmler ayri bir grupta gosterilir.
7. Yil eslesmeyen filmleri "kontrol onerilir" olarak isaretler (CLI'da
   rapor sonunda listelenir; gorsel arayuzde tek tek duzeltilebilir).
8. Sonucu hem terminale yazdirir hem de `plan.json` dosyasina kaydeder.

## Watchlist'i guncelleme

1. Letterboxd'dan watchlist'i tekrar CSV olarak export et (Letterboxd
   ayarlari -> Import & Export -> Export Data).
2. Yeni CSV dosyasini gorsel arayuze surukle birak, ya da
   `python sync.py <yeni-csv-dosyasi>` calistir.

Sadece yeni eklenen filmler JustWatch'ta aranir, eskiden aranmis filmler
cache'ten okunur. CSV'den cikan filmler "watchlist'ten cikmis" olarak
raporlanir ama cache'ten silinmez.

## Dosyalar

- `server.py` - gorsel surukle-birak arayuz (yerel web sunucusu)
- `web/` - arayuzun HTML/CSS/JS dosyalari
- `sync.py` - terminal (CLI) script
- `core.py` - JustWatch eslestirme, cache ve plan mantigi (ikisi de bunu kullanir)
- `justwatch_cache.json` - film -> platform cache'i (kendisi olusturur/gunceller)
- `last_watchlist.csv` - gorsel arayuze en son yuklenen CSV (sayfa acilista otomatik yuklenir icin)
- `plan.json` - CLI'nin urettigi en son aylik plan
- `requirements.txt` - Python bagimliliklari

## Notlar

- JustWatch'un resmi olmayan GraphQL API'sini kullanan
  `simple-justwatch-python-api` kutuphanesine dayanir. API JustWatch
  tarafindan degistirilirse script bozulabilir.
- "Hicbir platformda bulunamadi" demek, o filmin secilen ulkede JustWatch
  kataloginda abonelikle (FLATRATE) izlenebilecegi bir servis olmadigi
  anlamina gelir - kirala/satin al secenegi olabilir ama bu script sadece
  abonelikleri sayar.
- Arama sirasinda bir filmde hata olursa (agdaki sorun, rate limit, hicbir
  sonuc bulunamamasi) script durmaz; o filmi "sorunlu filmler" listesine
  ekleyip devam eder. Bu listeyi terminal ciktisinda ve `plan.json` icindeki
  `errors` alaninda gorebilirsin.
