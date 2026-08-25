from foundry_local_sdk import Configuration, FoundryLocalManager
import math


def cosine_similarity(v1, v2):
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))

    return dot_product / (norm1 * norm2)


def main():
    config = Configuration(app_name="foundry_local_rag")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    manager.download_and_register_eps()

    embedding_model = manager.catalog.get_model("qwen3-embedding-0.6b")

    print("Embedding modeli indiriliyor...")
    embedding_model.download()

    embedding_model.load()
    print("Embedding modeli yuklendi.")

    client = embedding_model.get_embedding_client()

    belgeler = [
        "Foundry Local modelleri cihaz üzerinde çalıştırır.",
        "SQLite hafif ve yerel bir veritabanıdır.",
        "RAG, ilgili belgeleri bulup modele bağlam olarak verir.",
        "Embedding, metinleri sayısal vektörlere dönüştürür.",
    ]

    belge_vektorleri = []

    for belge in belgeler:
        sonuc = client.generate_embedding(belge)
        belge_vektorleri.append(sonuc.data[0].embedding)

    sorgu = "Metinleri vektöre çeviren yapı nedir?"

    sorgu_sonucu = client.generate_embedding(sorgu)
    sorgu_vektoru = sorgu_sonucu.data[0].embedding

    skorlar = []

    for belge, vektor in zip(belgeler, belge_vektorleri):
        skor = cosine_similarity(sorgu_vektoru, vektor)
        skorlar.append((belge, skor))

    skorlar.sort(key=lambda x: x[1], reverse=True)

    print("\nSorgu:")
    print(sorgu)

    print("\nEn benzer sonuc:")
    print(skorlar[0][0])

    print("\nBenzerlik skoru:")
    print(skorlar[0][1])

    embedding_model.unload()


if __name__ == "__main__":
    main()