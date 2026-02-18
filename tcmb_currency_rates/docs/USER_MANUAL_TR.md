# TCMB Döviz Kurları – Kullanım Kılavuzu (Türkçe)

## 1. Giriş

**TCMB Currency Rates** modülü, Odoo 19’u Türkiye Cumhuriyet Merkez Bankası (TCMB) günlük döviz kuru servisine bağlar. Resmi kurlar indirilir, modülün kendi tablosunda saklanır ve istenen kurlar Odoo muhasebe kurlarına aktarılabilir. Güncel kurları elle veya zamanlanmış görevle güncelleyebilir; geçmiş tarihler için tarih aralığı ile toplu import yapabilirsiniz.

---

## 2. TCMB Nerede Bulunur?

- **Ana menü**: **Muhasebe** → **Yapılandırma** → **TCMB Kurları**
- **Paralar**: **Muhasebe** → **Yapılandırma** → **Paralar** (TCMB butonu ve sütunları)
- **Ayarlar**: **Muhasebe** → **Yapılandırma** → **Ayarlar** → Faturalandırma bölümü → **TCMB Döviz Kurları**
- **Zamanlanmış işlem**: **Ayarlar** → **Teknik** → **Otomasyon** → **Zamanlanmış İşlemler** → TCMB günlük güncelleme

---

## 3. TCMB Kurları Menüsü (Muhasebe > Yapılandırma > TCMB Kurları)

### 3.1 Cron’u düzelt (manuel çalıştırmaları kaydet)

- **Ne yapar**: Zamanlanmış işlemin kodunu güncelleyerek, TCMB cron’unu manuel veya otomatik çalıştırdığınızda her çalışmanın **Çalışma Geçmişi**nde ve chatter’da kayıt oluşturmasını sağlar.
- **Ne zaman kullanılır**: Zamanlanmış işlemi manuel çalıştırdığınızda Çalışma Geçmişi’nde kayıt görünmüyorsa **bir kez** çalıştırın (özellikle Odoo 18+ ve yükseltme sonrası).
- **Erişim**: Muhasebe yöneticisi.
- **Sonuç**: Başarı mesajı; bir sonraki manuel veya otomatik cron çalışması Çalışma Geçmişi’ne yazılır.

---

### 3.2 TCMB’den güncelle

- **Ne yapar**: **Bugünün** kurlarını TCMB’den çeker, **Döviz Kurları** listesine kaydeder, **TCMB Oto** işaretli paraları Odoo **Paralar** ile eşitler ve **Çalışma Geçmişi**ne chatter’lı kayıt ekler.
- **Ne zaman kullanılır**: Zamanlanmış çalışmayı beklemeden bugünün kurlarını yenilemek için.
- **Erişim**: TCMB menüsüne erişebilen kullanıcılar.
- **Sonuç**: Bildirim (Başarılı / Türkiye tatilinde atlandı / Hata). Çalışma **Çalışma Geçmişi**nde görünür.

---

### 3.3 Döviz kurları

- **Ne yapar**: **TCMB döviz kurları** listesini açar (tarih, para, döviz/banknot kurları, Odoo’ya senkron durumu).
- **Üst buton**: **TCMB’den güncelle** – yukarıdaki menü ile aynı; çalışma Çalışma Geçmişi’ne yazılır.
- **Sütunlar**: Kullanılan kur türü, Tarih, Para Kodu/Adı, Birim, Döviz Alış/Satış, Banknot kurları, Etkin kur, Odoo’ya senkron.
- **Filtreler**: Para, tarih, Senkron / Senkron değil.
- **Form**: Tek bir kurun detayı; Odoo’ya senkron edilmemişse (ve TCMB Oto işaretliyse) **Odoo’ya senkron** butonu görünür.
- **Not**: Listeden kur eklenemez/düzenlenemez; veriler TCMB veya **Geçmiş içe aktar** sihirbazından gelir.

---

### 3.4 Tarihi Odoo’ya senkron et

- **Ne yapar**: Mevcut TCMB verisinden **tek bir tarih** seçip Odoo **Paralar**a senkron eden sihirbaz. Sadece **TCMB Oto** işaretli paralar güncellenir.
- **Ne zaman kullanılır**: Geçmiş import yaptıktan sonra belirli bir tarihi (örn. 1 Şubat) muhasebe kurlarına yansıtmak için.
- **Erişim**: Yönetici.
- **Adımlar**: Sihirbazı açın → **Kur tarihi** seçin → **Senkron et**.
- **Not**: O tarih için TCMB verisi önceden olmalı (örn. **Geçmiş içe aktar** ile).

---

### 3.5 Geçmiş içe aktar

- **Ne yapar**: **Tarih aralığı** için TCMB kurlarını içe aktarır. Veri TCMB’nin geçmiş adreslerinden (`YYYYMM/DDMMYYYY.xml`) alınır. Hafta sonları ve resmi tatiller atlanabilir, zaten içe aktarılmış tarihler atlanabilir ve isteğe bağlı olarak içe aktarılan tarihler Odoo Paralar’a senkron edilebilir.
- **Ne zaman kullanılır**: Geçmiş kurları doldurmak için (raporlama, geçmiş faturalar).
- **Erişim**: Yönetici.
- **Alanlar**:
  - **Başlangıç tarihi** / **Bitiş tarihi**: İçe aktarılacak aralık (16 Nisan 1996 sonrası).
  - **Hafta sonu ve tatilleri atla**: İşaretliyse hafta sonları ve Türkiye resmi tatillerinde istek atılmaz (varsayılan: açık).
  - **Zaten içe aktarılmış tarihleri atla**: İşaretliyse daha önce TCMB verisi alınmış tarihler tekrar çekilmez (varsayılan: açık).
  - **Odoo paralarına senkron et**: İşaretliyse her tarih içe aktarıldıktan sonra, **TCMB Oto** işaretli paralar Odoo Paralar’a yansıtılır (varsayılan: açık).
- **İşlemler**: **İçe aktar** (işlemi başlatır; başarıda sihirbaz kapanır), **Kapat** (iptal).
- **Sonuç**: Oluşturulan/güncellenen/atlanan adetleri gösteren bildirim; veriler **Döviz kurları**nda ve isteğe bağlı **Paralar**da.

---

### 3.6 Çalışma geçmişi

- **Ne yapar**: Her TCMB güncelleme **çalışmasının** (zamanlanmış veya manuel) kaydını listeler. Her kayıtta chatter’da sonuç (başarılı/atlandı/hata ve ayrıntı) yer alır.
- **Sütunlar**: Çalışma tarihi, Çalışma türü (Zamanlanmış / Manuel), Sonuç (Başarılı / Atlanan / Hata), Oluşturulan güncellemeler, Güncellenen güncellemeler, TCMB kur tarihi, Ayrıntılar.
- **Form**: Tüm detaylar ve chatter (çalışma sonucu mesajları).
- **Erişim**: Muhasebe kullanıcıları okuyabilir; yöneticiler tam yetkili.
- **Kullanım**: Denetim izi ve sorun giderme (örn. çalışmanın neden atlandığı veya hata verdiği).

---

## 4. Paralar (Muhasebe > Yapılandırma > Paralar)

- **TCMB’den güncelle** (buton): **TCMB Kurları** → **TCMB’den güncelle** ile aynı; çalışma Çalışma Geçmişi’ne yazılır.
- **TCMB Oto** (sütun): Bu parayı TCMB senkronuna dahil etmek için işaretleyin. Sadece işaretli paraların Odoo kuru TCMB’den güncellenir. Varsayılan: kapalı.
- **Son TCMB senkron** (sütun): Son “TCMB’den güncelle” (veya eşdeğeri) çalışmasının tamamlandığı an; **gg.aa.yyyy ss:dd** (24 saat), kullanıcı saat diliminde.
- **Form**: TCMB grubunda **TCMB’den otomatik güncelle** alanı listedeki TCMB Oto ile aynıdır.

---

## 5. Ayarlar (Muhasebe > Yapılandırma > Ayarlar)

**Faturalandırma** bölümünde **TCMB Döviz Kurları** bloğu:

- **Odoo senkronu için TCMB kuru**: Paralar’a hangi TCMB kurunun yansıtılacağı – **Döviz alış**, **Döviz satış** (varsayılan), **Banknot alış**, **Banknot satış**.
- **Hata durumunda yeniden dene**: **Yeniden deneme sayısı** (örn. 3) ve **Yeniden deneme aralığı (dakika)** (örn. 5). İstek başarısız olursa bu kadar kez bu aralıkla tekrar denenir; hepsi başarısız olursa hata gösterilir.
- **Türkiye tatil günlerini atla**: İşaretliyse Türkiye resmi tatillerinde TCMB isteği atılmaz (TCMB kapalı). Manuel/cron çalıştırmalarında “Atlandı” görünür.

Ayarları kaydetmek, kur türü değiştiğinde Odoo Paralar’ı **mevcut** TCMB verisinden yeniden senkron eder (yeni istek atılmaz).

---

## 6. Zamanlanmış işlem (Cron)

- **Nerede**: **Ayarlar** → **Teknik** → **Otomasyon** → **Zamanlanmış İşlemler**.
- **Ad**: Örn. “TCMB: Günlük Kur Güncellemesi (15:15)” veya değiştirdiyseniz “(15:30)”.
- **Ne yapar**: **TCMB’den güncelle** ile aynı mantığı çalıştırır (bugünü çek, Odoo’ya senkron et, Çalışma Geçmişi kaydı oluştur). Çalışma türü Çalışma Geçmişi’nde **Zamanlanmış** olur.
- **Manuel çalıştırma**: Zamanlanmış işlemi açın → **Manuel çalıştır**. **Cron’u düzelt** bir kez çalıştırıldıysa bu çalışma Çalışma Geçmişi’nde görünür.
- **Düzenleme**: Çalışma saati (örn. 15:30), aralık veya aktif/pasif değiştirilebilir.

---

## 7. Özellik özeti

| Özellik | Açıklama |
|--------|----------|
| **Günlük güncelleme** | Bugünün TCMB kurlarını çek; TCMB Oto işaretli paraları Odoo’ya senkron et. |
| **Geçmiş içe aktarma** | Tarih aralığı import (16 Nisan 1996 sonrası); isteğe bağlı Odoo senkronu; hafta sonu/tatil ve zaten import edilmiş tarihler atlanabilir. |
| **Tek tarih senkronu** | Zaten import edilmiş bir tarihi Odoo Paralar’a yansıt (Tarihi Odoo’ya senkron et sihirbazı). |
| **Çalışma geçmişi** | Tüm çalıştırmalar (zamanlanmış ve manuel) chatter ile kayıt altında. |
| **Cron düzeltme** | Zamanlanmış/manuel cron çalışmalarının kayda alınması için tek tıkla güncelleme (Cron’u düzelt menüsü). |
| **Kur türü** | Odoo’ya hangi TCMB kurunun (döviz/banknot alış/satış) yansıtılacağı seçilir. |
| **Para bazlı** | Sadece TCMB Oto işaretli paralar Odoo’ya senkron edilir. |
| **Yeniden deneme** | İstek hatalarında ayarlanabilir yeniden deneme ve gecikme. |
| **Tatil atlama** | Türkiye resmi tatillerinde isteğe bağlı atlama. |
| **Çoklu şirket** | TCMB kurları ve Çalışma Geçmişi ilgili yerlerde şirket bazlıdır. |

---

## 8. Tipik iş akışları

1. **İlk kullanım**: Paralar’da kullanacağınız paralarda (örn. USD, EUR) **TCMB Oto**’yu açın. İsteğe bağlı Ayarlar’da **Türkiye tatil atlama** ve **Yeniden dene** ayarlarını yapın. Bir kez **TCMB’den güncelle** çalıştırın (menüden veya Paralar’dan). **Çalışma Geçmişi** ve **Döviz kurları**nı kontrol edin.
2. **Günlük**: Zamanlanmış işleme bırakın veya **TCMB’den güncelle**’yi manuel çalıştırın. Gerekirse **Son TCMB senkron** ve **Çalışma Geçmişi**ne bakın.
3. **Geçmiş**: **Geçmiş içe aktar**’ı açın, tarih aralığını girin, **Odoo paralarına senkron et** ve **Zaten içe aktarılmış tarihleri atla**yı ihtiyaca göre bırakın, **İçe aktar**’a tıklayın. İçe aktarma sırasında senkron etmediyseniz tek bir tarih için **Tarihi Odoo’ya senkron et** kullanın.
4. **Cron kayda yazmıyorsa**: TCMB menüsünden **Cron’u düzelt**’i bir kez çalıştırın, ardından zamanlanmış işlemi manuel çalıştırıp Çalışma Geçmişi’nde kayıt oluştuğunu doğrulayın.

---

## 9. Sorun giderme

- **Manuel cron çalışması Çalışma Geçmişi’nde yok**: **Cron’u düzelt (manuel çalıştırmaları kaydet)**’i bir kez çalıştırın (Odoo 18+).
- **“TCMB cron bulunamadı”**: TCMB zamanlanmış işleminin var olduğundan emin olun (modül kurulumu/yükseltme). Cron düzeltme, adı 15:15, 15:30 veya “TCMB%” ile bulur.
- **Paralar’da kur yok**: İlgili para için **TCMB Oto**’yu açın; **TCMB’den güncelle** veya ilgili tarih için **Tarihi Odoo’ya senkron et** çalıştırın.
- **Tatil / atlama**: Türkiye resmi tatillerinde **Türkiye tatil atlama** açıksa çalıştırmalar “Atlandı” gösterir; istek atılmaz.
- **Hatalar**: Çalışma Geçmişi chatter’ı ve ekrandaki mesajı inceleyin; sorun geçiciyse (örn. ağ) Ayarlar’da **Yeniden dene** ve **Yeniden deneme aralığı**nı ayarlayın.

---

*TCMB Currency Rates for Odoo 19 – Kullanım Kılavuzu (Türkçe). Sürüm 19.0.1.0.13.*
