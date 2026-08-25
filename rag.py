from foundry_local_sdk import Configuration, FoundryLocalManager
import sqlite3
import json
import math


ESIK_SKOR = 0.42
EMBEDDING_MODEL = "qwen3-embedding-0.6b"
CHAT_MODEL = "qwen3.5-0.8b"


def cosine_similarity(v1, v2):
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def manager_olustur():
    """
    Foundry Local yöneticisini hazırlar.
    """

    config = Configuration(
        app_name="foundry_local_rag"
    )

    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    manager.download_and_register_eps()

    return manager


def ilgili_chunklari_bul(manager, sorgu, limit=3):
    """
    Kullanıcının sorusuna en benzer belge parçalarını bulur.
    """

    embedding_model = manager.catalog.get_model(
        EMBEDDING_MODEL
    )

    embedding_model.download()
    embedding_model.load()

    embedding_client = embedding_model.get_embedding_client()

    # Kullanıcının sorusunu vektöre dönüştür.
    sorgu_sonucu = embedding_client.generate_embedding(sorgu)
    sorgu_vektoru = sorgu_sonucu.data[0].embedding

    # SQLite bilgi tabanını aç.
    baglanti = sqlite3.connect("data/rag.db")
    imlec = baglanti.cursor()

    imlec.execute(
        """
        SELECT kaynak, sayfa_no, chunk_no, metin, embedding
        FROM documents
        """
    )

    kayitlar = imlec.fetchall()
    sonuclar = []

    # Sorgu ile bütün kayıtların cosine similarity skorunu hesapla.
    for kaynak, sayfa_no, chunk_no, metin, embedding_json in kayitlar:
        belge_vektoru = json.loads(embedding_json)

        skor = cosine_similarity(
            sorgu_vektoru,
            belge_vektoru
        )

        sonuclar.append(
            {
                "kaynak": kaynak,
                "sayfa_no": sayfa_no,
                "chunk_no": chunk_no,
                "metin": metin,
                "skor": skor,
            }
        )

    baglanti.close()
    embedding_model.unload()

    # En yüksek benzerlik skorundan en düşüğe sırala.
    sonuclar.sort(
        key=lambda sonuc: sonuc["skor"],
        reverse=True
    )

    return sonuclar[:limit]


def cevap_uret(manager, soru, chunklar):
    """
    Bulunan belge parçalarını LLM'e context olarak verir
    ve oluşturulan cevabı string olarak döndürür.
    """

    context_parcalari = []

    for sonuc in chunklar:
        kaynak_adi = (
            sonuc["kaynak"]
            .replace(".txt", "")
            .replace(".pdf", "")
        )

        parcalar = kaynak_adi.split("_")

        if parcalar and parcalar[0].isdigit():
            parcalar = parcalar[1:]

        kaynak_adi = " ".join(parcalar).title()

        context_parcalari.append(
            f"""
KONU: {kaynak_adi}

{sonuc["metin"]}
"""
        )

    context = "\n".join(context_parcalari)

    sistem_mesaji = """
Sen TüketiciRehber AI adlı tüketici hakları bilgi asistanısın.

Yalnızca sana verilen T.C. Ticaret Bakanlığı içeriklerini kullanarak
kullanıcının sorusuna doğru, kısa ve anlaşılır cevap ver.

KURALLAR:

1. Önce kullanıcının hangi tüketici konusunu sorduğunu belirle.
2. Sorunun konusuyla doğrudan ilgili KONU altındaki bilgileri kullan.
3. Farklı tüketici işlemlerine ait bilgileri birbirine karıştırma.
4. Örneğin bir süre başka bir işlem için geçerliyse, onu kullanıcının
   sorduğu işlem için kullanma.
5. Kullanıcı özellikle "yenilenmiş ürün" demiyorsa yalnızca bu konuya
   özgü hükümleri genel internet alışverişi için kullanma.
6. Kaynaklarda açıkça bulunmayan hiçbir bilgiyi ekleme veya tahmin etme.
7. Kendi genel bilgini ve internet bilgisini kullanma.
8. Sorunun doğrudan cevabını ilk cümlede ver.
9. Cevabı kısa tut; mümkünse 1-3 cümle kullan.
10. Aynı bilgiyi tekrarlama.
11. Süre, tutar, tarih ve diğer sayısal değerleri kaynakta yazıldığı
    şekliyle koru.
12. Dosya adı, TXT, PDF, chunk, skor, embedding, belge parçası,
    kaynak metin veya sistem gibi teknik ifadeleri kullanıcıya yazma.
13. "Verilen içerikte", "yukarıdaki metinde", "belgeler incelendiğinde"
    gibi ifadelerle cevap başlatma.
14. Cevabı tamamlanmış bir cümleyle bitir.
15. Sorunun cevabı verilen içeriklerde açıkça bulunmuyorsa yalnızca:

Bu bilgi sağlanan tüketici kaynaklarında bulunamadı.

yaz.

Sadece kullanıcıya gösterilecek nihai cevabı üret.
"""

    kullanici_mesaji = f"""
Aşağıdaki içerikler bilgi kaynağıdır:

{context}

Kullanıcının sorusu:
{soru}

Soruyu yalnızca verilen içeriklere dayanarak cevapla.
"""

    chat_model = manager.catalog.get_model(
        CHAT_MODEL
    )

    def indirme_durumu(progress):
        print(
            f"\rModel indirme: {progress:.2f}%",
            end="",
            flush=True
        )

    chat_model.download(indirme_durumu)
    chat_model.load()

    chat_client = chat_model.get_chat_client()

    chat_client.settings.temperature = 0.0
    chat_client.settings.max_tokens = 250

    messages = [
        {
            "role": "system",
            "content": sistem_mesaji,
        },
        {
            "role": "user",
            "content": kullanici_mesaji,
        },
    ]

    cevap_parcalari = []

    for chunk in chat_client.complete_streaming_chat(messages):
        if not chunk.choices:
            continue

        content = chunk.choices[0].delta.content

        if content:
            cevap_parcalari.append(content)

    chat_model.unload()

    return "".join(cevap_parcalari).strip()


def rag_sorgula(manager, soru, limit=3):
    """
    Streamlit ve terminal tarafından kullanılabilen
    ana RAG fonksiyonudur.
    """

    soru = soru.strip()

    if not soru:
        return {
            "cevap": "Lütfen bir soru yazın.",
            "kaynaklar": [],
            "chunklar": [],
            "bulundu": False,
        }

    chunklar = ilgili_chunklari_bul(
        manager,
        soru,
        limit
    )

    # En iyi sonuç bile yeterince benzer değilse
    # modeli çağırmadan güvenli fallback döndür.
    if not chunklar or chunklar[0]["skor"] < ESIK_SKOR:
        return {
        "cevap": "Bu bilgi sağlanan tüketici kaynaklarında bulunamadı.",
        "kaynaklar": [],
        "chunklar": chunklar,
        "bulundu": False,
    }

    cevap = cevap_uret(
        manager,
        soru,
        chunklar
    )

    kaynaklar = []

    for sonuc in chunklar:
        if sonuc["kaynak"] not in kaynaklar:
            kaynaklar.append(
                sonuc["kaynak"]
            )

    return {
        "cevap": cevap,
        "kaynaklar": kaynaklar,
        "chunklar": chunklar,
        "bulundu": True,
    }


def main():
    """
    Terminal / CLI sürümü.
    """

    manager = manager_olustur()

    print(
        "\n=== TuketiciRehber AI ==="
    )

    soru = input(
        "\nSorunuzu yazin: "
    )

    print("\nIlgili belgeler araniyor...")

    sonuc = rag_sorgula(
        manager,
        soru
    )

    print("\n--- RAG CEVABI ---\n")
    print(sonuc["cevap"])

    if sonuc["kaynaklar"]:
        print("\n--- KULLANILAN KAYNAKLAR ---")

        for kaynak in sonuc["kaynaklar"]:
            print(f"- {kaynak}")

    if sonuc["chunklar"]:
        print("\n--- BENZERLIK SONUCLARI ---")

        for sira, chunk in enumerate(
            sonuc["chunklar"],
            start=1
        ):
            print(
                f"{sira}. "
                f"{chunk['kaynak']} "
                f"(sayfa {chunk['sayfa_no']}, "
                f"chunk {chunk['chunk_no']}, "
                f"skor {chunk['skor']:.4f})"
        )


if __name__ == "__main__":
    main()