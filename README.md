# TüketiciRehber AI

TüketiciRehber AI, **Microsoft Foundry Local** ve **Retrieval-Augmented Generation (RAG)** kullanılarak geliştirilmiş yerel bir tüketici hakları bilgi asistanıdır.

Uygulama, T.C. Ticaret Bakanlığı tüketici bilgilendirme içeriklerinden ilgili bölümleri bulur ve kullanıcının sorusuna bu kaynaklara dayanarak cevap üretir. Model ve RAG işlemleri yerel ortamda çalışır.

## Nasıl Çalışır?

1. Resmî tüketici bilgilendirme belgeleri küçük metin parçalarına (chunk) ayrılır.
2. `qwen3-embedding-0.6b` modeli ile her parça için embedding oluşturulur.
3. Metinler ve embedding'ler **SQLite** veritabanında saklanır.
4. Kullanıcının sorusu da embedding'e dönüştürülür.
5. **Cosine Similarity** ile soruya en yakın belge parçaları bulunur.
6. İlgili parçalar `qwen3.5-0.8b` modeline bağlam olarak verilir.
7. Model yalnızca getirilen kaynaklara dayanarak cevap üretir.
8. Yeterli bilgi bulunamazsa sistem güvenli bir fallback cevabı döndürür.

## Kullanılan Teknolojiler

- Python
- Microsoft Foundry Local
- Foundry Local SDK
- RAG
- `qwen3-embedding-0.6b`
- `qwen3.5-0.8b`
- SQLite
- Cosine Similarity
- Flask
- HTML / CSS / JavaScript

## Kurulum

Projeyi klonlayın:

```bash
git clone https://github.com/SenaBulutt/TuketiciRehber-AI.git
cd TuketiciRehber-AI
```

Sanal ortam oluşturun ve aktif edin:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Bağımlılıkları yükleyin:

```bash
pip install -r requirements.txt
```

Bilgi tabanını oluşturun:

```bash
python chunk_documents.py
python build_database.py
```

Uygulamayı başlatın:

```bash
python app.py
```

Ardından tarayıcıdan:

```text
http://127.0.0.1:5000
```

adresine gidin.

> İlk çalıştırmada Foundry Local modellerinin indirilmesi nedeniyle başlatma işlemi biraz zaman alabilir.

## Test

Projede cevaplanabilir, cevaplanamayan ve uç durum soruları için test senaryoları bulunmaktadır.

- `tests/test_cases.json` — test soruları
- `tests/test_results.md` — test sonuçları

## Sınırlamalar

- Sistem yalnızca bilgi tabanına eklenen tüketici kaynaklarına dayanır.
- Retrieval başarısı embedding modeli ve belge parçalama yapısından etkilenebilir.
- Kaynaklarda yeterli bilgi bulunmadığında sistem cevap üretmek yerine fallback mesajı verir.
- Uygulama profesyonel hukuki danışmanlık amacı taşımaz.

## Kaynaklar

Bilgi tabanı T.C. Ticaret Bakanlığı tüketici bilgilendirme içeriklerinden oluşturulmuştur.

Projenin RAG mimarisi ve Foundry Local entegrasyonu geliştirilirken Microsoft Foundry Local ve Microsoft Learn dokümantasyonlarından yararlanılmıştır.
