from foundry_local_sdk import Configuration, FoundryLocalManager
import sqlite3
import json
import math


def cosine_similarity(v1, v2):
    dot_product = sum(a * b for a, b in zip(v1, v2))

    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def main():
    # Foundry Local'i başlat
    config = Configuration(app_name="foundry_local_rag")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    manager.download_and_register_eps()

    # Embedding modelini hazırla
    embedding_model = manager.catalog.get_model("qwen3-embedding-0.6b")

    print("Embedding modeli hazirlaniyor...")
    embedding_model.download()
    embedding_model.load()

    print("Embedding modeli yuklendi.")

    client = embedding_model.get_embedding_client()

    # Kullanıcıdan soru al
    sorgu = input("\nSorunuzu yazin: ")

    # Soruyu embedding'e dönüştür
    sorgu_sonucu = client.generate_embedding(sorgu)
    sorgu_vektoru = sorgu_sonucu.data[0].embedding

    # SQLite veritabanını aç
    baglanti = sqlite3.connect("data/rag.db")
    imlec = baglanti.cursor()

    imlec.execute(
        """
        SELECT kaynak, chunk_no, metin, embedding
        FROM documents
        """
    )

    kayitlar = imlec.fetchall()

    sonuclar = []

    # Sorguyu bütün chunk embeddingleriyle karşılaştır
    for kaynak, chunk_no, metin, embedding_json in kayitlar:

        belge_vektoru = json.loads(embedding_json)

        skor = cosine_similarity(
            sorgu_vektoru,
            belge_vektoru
        )

        sonuclar.append(
            {
                "kaynak": kaynak,
                "chunk_no": chunk_no,
                "metin": metin,
                "skor": skor
            }
        )

    # En yüksek benzerlik skorundan en düşüğe sırala
    sonuclar.sort(
        key=lambda sonuc: sonuc["skor"],
        reverse=True
    )

    # İlk 3 sonucu göster
    print("\n--- EN ILGILI 3 BELGE PARCASI ---")

    for sira, sonuc in enumerate(sonuclar[:3], start=1):

        print(f"\n{sira}. SONUC")
        print(f"Kaynak: {sonuc['kaynak']}")
        print(f"Chunk: {sonuc['chunk_no']}")
        print(f"Benzerlik: {sonuc['skor']:.4f}")
        print("Metin:")
        print(sonuc["metin"])

    baglanti.close()

    embedding_model.unload()

    print("\nArama tamamlandi.")


if __name__ == "__main__":
    main()