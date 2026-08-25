# Microsoft Foundry Local RAG Asistanı

Microsoft Foundry Local kullanılarak geliştirilen, tamamen yerel çalışan
doküman tabanlı bir Retrieval-Augmented Generation (RAG) soru-cevap
uygulamasıdır.

Sistem, kullanıcı sorularını yerel bilgi tabanındaki Microsoft Foundry
Local dokümanlarıyla eşleştirir ve yalnızca ilgili doküman parçalarını
yerel dil modeline bağlam olarak gönderir.

## Projenin Amacı

Bu projenin amacı;

- Retrieval-Augmented Generation (RAG) mimarisini öğrenmek,
- Microsoft Foundry Local ile cihaz üzerinde yapay zekâ modeli çalıştırmak,
- metin embeddingleri üretmek,
- cosine similarity ile semantik arama gerçekleştirmek,
- SQLite kullanarak yerel bilgi tabanı oluşturmak,
- kaynak temelli ve daha güvenilir cevaplar üretmek,
- tamamen yerel çalışan bir yapay zekâ uygulaması geliştirmektir.

## Kullanılan Teknolojiler

- Python
- Microsoft Foundry Local SDK
- Qwen3 Embedding 0.6B
- Qwen3.5 0.8B
- SQLite
- Streamlit
- Retrieval-Augmented Generation (RAG)
- Cosine Similarity

## Sistem Mimarisi

```text
Kullanıcı Sorusu
       ↓
Query Embedding
       ↓
SQLite Bilgi Tabanı
       ↓
Cosine Similarity
       ↓
En İlgili 3 Chunk
       ↓
Benzerlik Eşiği Kontrolü
       ↓
Foundry Local LLM
       ↓
Kaynak Temelli Türkçe Cevap
```

RAG sistemi üç temel aşamadan oluşmaktadır:

1. **Retrieve:** Kullanıcı sorusuyla en alakalı doküman parçaları bulunur.
2. **Augment:** Bulunan parçalar LLM'e bağlam olarak eklenir.
3. **Generate:** Yerel dil modeli yalnızca bu bağlama dayanarak cevap üretir.

## Bilgi Tabanı

Projede Microsoft Foundry Local ile ilgili 5 doküman kullanılmaktadır.

Dokümanlar:

- What is Foundry Local?
- Get Started
- Build a RAG Application
- SDK Reference
- Model Catalog

Dokümanlar küçük parçalara (**chunk**) ayrılmıştır.

Her chunk için Qwen3 Embedding 0.6B modeli kullanılarak embedding
vektörü üretilmiş ve metin ile birlikte SQLite veritabanında saklanmıştır.

## Embedding ve Semantic Search

Embedding, metinlerin anlamsal özelliklerini sayısal vektörler ile temsil eder.

Kullanıcının sorusu da aynı embedding modeli kullanılarak vektöre dönüştürülür.

Soru vektörü ile veritabanındaki doküman vektörleri
**cosine similarity** kullanılarak karşılaştırılır.

Bu sayede kelimeler birebir aynı olmasa bile anlamsal olarak benzer
doküman parçaları bulunabilir.

## Retrieval

Her kullanıcı sorgusunda:

1. Soru embedding'e dönüştürülür.
2. SQLite veritabanındaki embeddingler okunur.
3. Cosine similarity hesaplanır.
4. Sonuçlar benzerlik skoruna göre sıralanır.
5. En alakalı 3 chunk seçilir.
6. Bu parçalar cevap üretimi için yerel LLM'e gönderilir.

Streamlit arayüzünde kullanıcı retrieval sonuçlarının:

- kaynak dosyasını,
- chunk numarasını,
- benzerlik skorunu

görüntüleyebilir.

## Güvenli Fallback

Sistemde `0.35` cosine similarity eşik değeri kullanılmaktadır.

En iyi retrieval sonucunun benzerlik skoru `0.35` değerinin altında kalırsa
soru bilgi tabanıyla yeterince ilişkili kabul edilmez.

Bu durumda yerel LLM çağrılmaz ve sistem:

> Bu bilgi sağlanan belgelerde bulunamadı.

cevabını döndürür.

Bu kontrol, modelin kendi genel bilgisini kullanarak kaynak dışı cevap
üretmesini ve hallucination riskini azaltmak amacıyla eklenmiştir.

## Yerel LLM

Cevap üretiminde Microsoft Foundry Local üzerinden:

`Qwen3.5 0.8B`

modeli kullanılmaktadır.

Daha büyük modeller daha kaliteli cevaplar üretebilse de bu projede
yerel çalışma performansı ve donanım kullanımı dikkate alınarak küçük
bir model tercih edilmiştir.

Modelden:

- yalnızca verilen kaynakları kullanması,
- kaynak dışı bilgi üretmemesi,
- kısa ve anlaşılır Türkçe cevap vermesi

system prompt ile istenmektedir.

## Kullanıcı Arayüzü

Proje için Streamlit tabanlı bir kullanıcı arayüzü geliştirilmiştir.

Arayüz üzerinden kullanıcı:

- soru sorabilir,
- oluşturulan RAG cevabını görebilir,
- kullanılan kaynakları inceleyebilir,
- retrieval sonuçlarını görüntüleyebilir,
- chunk numaralarını görebilir,
- cosine similarity skorlarını inceleyebilir.

Ayrıca bilgi tabanı dışında kalan sorular için sistem güvenli fallback
mesajı göstermektedir.

## Proje Yapısı

```text
foundry_local_rag/
│
├── data/
│   ├── documents/
│   ├── chunks.json
│   └── rag.db
│
├── tests/
│   ├── test_cases.json
│   └── test_results.md
│
├── experiments/
│
├── build_database.py
├── chunk_documents.py
├── rag.py
├── streamlit_app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Kurulum

Projeyi bilgisayarınıza klonlayın:

```bash
git clone <REPOSITORY_URL>
cd foundry_local_rag
```

### Sanal Ortam Oluşturma

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows kullanılıyorsa:

```bash
.venv\Scripts\activate
```

### Bağımlılıkları Yükleme

```bash
python -m pip install -r requirements.txt
```

## Bilgi Tabanını Oluşturma

Dokümanlar `data/documents/` klasöründe bulunmaktadır.

Önce dokümanları chunk'lara ayırın:

```bash
python chunk_documents.py
```

Ardından chunk embeddinglerini üretip SQLite veritabanına kaydedin:

```bash
python build_database.py
```

Bu işlem sonucunda yerel RAG bilgi tabanı oluşturulur.

## Uygulamayı Çalıştırma

### Streamlit Arayüzü

```bash
streamlit run streamlit_app.py
```

Komut çalıştırıldıktan sonra uygulama tarayıcıda açılır.

### Terminal Sürümü

Arayüz kullanmadan terminal üzerinden çalıştırmak için:

```bash
python rag.py
```

## Örnek Sorular

Bilgi tabanında bulunan örnekler:

```text
Foundry Local nedir ve ne işe yarar?

Foundry Local hangi donanımlardan yararlanabilir?

Model kataloğu ne işe yarar?

Foundry Local için Python sürümü ne olmalıdır?

Embedding nedir ve RAG sisteminde ne işe yarar?
```

Bilgi tabanında bulunmayan örnek:

```text
Türkiye'nin başkenti neresidir?
```

Beklenen cevap:

```text
Bu bilgi sağlanan belgelerde bulunamadı.
```

## Testler

Sistem farklı sorgu türleri ile test edilmiştir.

Testlerde:

- bilgi tabanında bulunan sorular,
- bilgi tabanında bulunmayan sorular,
- boş sorgular,
- retrieval doğruluğu,
- kaynak seçimi,
- benzerlik eşik değeri,
- cevap üretimi

kontrol edilmiştir.

Test sonuçları:

`tests/test_results.md`

### Test Özeti

| Test | Durum |
|---|---|
| Foundry Local nedir ve ne işe yarar? | ✅ Başarılı |
| Embedding nedir ve RAG sisteminde ne işe yarar? | ✅ Başarılı |
| Foundry Local hangi donanımlardan yararlanabilir? | ✅ Başarılı |
| Model kataloğu ne işe yarar? | ✅ Başarılı |
| Foundry Local için Python sürümü ne olmalıdır? | ✅ Başarılı |
| Türkiye'nin başkenti neresidir? | ✅ Fallback başarılı |
| Bugün hava nasıl? | ✅ Fallback başarılı |
| Boş sorgu | ✅ Başarılı |

## Performans ve Tasarım Kararları

Projenin tamamen yerel çalışması nedeniyle performans önemli bir tasarım
kriteri olarak ele alınmıştır.

Bu nedenle:

- küçük bir cevap modeli kullanılmıştır,
- retrieval için yalnızca en alakalı 3 chunk seçilmektedir,
- doküman embeddingleri önceden hesaplanıp SQLite içinde saklanmaktadır,
- doküman embeddingleri her soruda yeniden oluşturulmamaktadır,
- düşük benzerlik skorlarında LLM gereksiz yere çağrılmamaktadır.

Bu yaklaşım yerel cihaz kaynaklarının daha kontrollü kullanılmasını sağlar.

## Öğrendiklerim

Bu proje kapsamında;

- RAG mimarisinin Retrieve, Augment ve Generate aşamalarını,
- embeddinglerin metinleri sayısal vektörlerle temsil ettiğini,
- semantic search mantığını,
- cosine similarity ile vektör benzerliği hesaplamayı,
- dokümanları chunk'lara ayırmayı,
- chunk boyutunun retrieval kalitesi üzerindeki etkisini,
- SQLite içinde metin ve embedding saklamayı,
- Microsoft Foundry Local SDK kullanımını,
- yapay zekâ modellerini tamamen cihaz üzerinde çalıştırmayı,
- embedding modeli ile LLM arasındaki farkı,
- prompt engineering ile model davranışını sınırlandırmayı,
- similarity threshold kullanarak kaynak dışı soruları engellemeyi,
- kaynak temelli cevap üretmenin hallucination riskini azaltmadaki önemini,
- Streamlit kullanarak yerel bir yapay zekâ uygulamasına kullanıcı arayüzü geliştirmeyi

öğrendim.

## Karşılaşılan Zorluklar

Proje geliştirme sürecinde bazı teknik zorluklarla karşılaşılmıştır.

Bunlardan bazıları:

- Foundry Local SDK içerisindeki embedding metodunun doğru kullanımının bulunması,
- küçük yerel modellerin Türkçe cevap kalitesinin sınırlı olması,
- bazı modellerin cihaz kaynaklarını fazla kullanması,
- model çıktılarında tekrar problemlerinin görülmesi,
- kaynak dışı sorularda modelin kendi genel bilgisini kullanarak cevap üretmesi.

Bu problemlere;

- doğru SDK metotlarının kullanılması,
- daha küçük ve uygun model seçimi,
- token ve temperature ayarlarının düzenlenmesi,
- prompt iyileştirmeleri,
- `0.35` similarity threshold eklenmesi

ile çözüm geliştirilmiştir.

## Sınırlamalar

Projenin mevcut sürümünde bazı sınırlamalar bulunmaktadır:

- Bilgi tabanı yalnızca 5 kısa dokümandan oluşmaktadır.
- Retrieval işlemi küçük veri setine uygun olarak brute-force cosine similarity ile yapılmaktadır.
- Daha büyük veri setlerinde özel bir vector database kullanılması daha uygun olabilir.
- Küçük yerel LLM nedeniyle bazı Türkçe cevaplarda dil kalitesi daha büyük modellere göre sınırlı olabilir.
- İlk model yükleme işlemi cihaz donanımına bağlı olarak zaman alabilir.
- Sistem yalnızca bilgi tabanına eklenen dokümanlardaki bilgiler için tasarlanmıştır.

## Gelecekte Yapılabilecek Geliştirmeler

- Daha büyük bir doküman koleksiyonu eklemek,
- PDF ve farklı dosya türlerini otomatik yüklemek,
- gelişmiş vector database kullanmak,
- reranking eklemek,
- model ve embedding caching mekanizmasını geliştirmek,
- sohbet geçmişi desteği eklemek,
- kaynak metnin ilgili bölümünü doğrudan kullanıcıya göstermek,
- farklı embedding ve LLM modellerini karşılaştırmak

gelecekte yapılabilecek geliştirmeler arasındadır.

## Kaynaklar

Bu proje geliştirilirken aşağıdaki kaynaklardan yararlanılmıştır:

- Microsoft Foundry Local resmi dokümantasyonu
- Microsoft Learn – Build a RAG Application
- Microsoft Learn – Foundry Local Get Started
- Microsoft Learn – Prompt Engineering
- Microsoft Tech Community – Building Your First Local RAG Application with Foundry Local

## Sonuç

Bu proje ile Microsoft Foundry Local kullanılarak tamamen cihaz üzerinde
çalışan, doküman tabanlı ve kaynak temelli bir RAG soru-cevap sistemi
geliştirilmiştir.

Proje kapsamında doküman işleme, embedding üretimi, SQLite veri yönetimi,
semantic retrieval, prompt engineering, yerel LLM kullanımı, güvenli
fallback mekanizması ve Streamlit kullanıcı arayüzü tek bir uygulama
altında birleştirilmiştir.