from foundry_local_sdk import Configuration, FoundryLocalManager
from pathlib import Path
import sqlite3
import json


CHUNKS_FILE = Path("data/chunks.json")
DATABASE_FILE = Path("data/rag.db")
EMBEDDING_MODEL = "qwen3-embedding-0.6b"


def manager_olustur():
    config = Configuration(
        app_name="foundry_local_rag"
    )

    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    manager.download_and_register_eps()

    return manager


def veritabani_olustur():
    baglanti = sqlite3.connect(DATABASE_FILE)
    imlec = baglanti.cursor()

    imlec.execute(
        """
        DROP TABLE IF EXISTS documents
        """
    )

    imlec.execute(
        """
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kaynak TEXT NOT NULL,
            sayfa_no INTEGER,
            chunk_no INTEGER NOT NULL,
            metin TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
        """
    )

    baglanti.commit()

    return baglanti


def main():
    if not CHUNKS_FILE.exists():
        print("chunks.json bulunamadi.")
        print("Once python chunk_documents.py calistirin.")
        return

    with open(
        CHUNKS_FILE,
        encoding="utf-8"
    ) as dosya:
        chunklar = json.load(dosya)

    print(
        f"{len(chunklar)} chunk bulundu."
    )

    manager = manager_olustur()

    embedding_model = manager.catalog.get_model(
        EMBEDDING_MODEL
    )

    print("Embedding modeli hazirlaniyor...")

    embedding_model.download()
    embedding_model.load()

    embedding_client = (
        embedding_model.get_embedding_client()
    )

    baglanti = veritabani_olustur()
    imlec = baglanti.cursor()

    for sira, chunk in enumerate(
        chunklar,
        start=1
    ):
        metin = chunk["metin"]

        sonuc = embedding_client.generate_embedding(
            metin
        )

        embedding = sonuc.data[0].embedding

        imlec.execute(
            """
            INSERT INTO documents (
                kaynak,
                sayfa_no,
                chunk_no,
                metin,
                embedding
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                chunk["kaynak"],
                chunk.get("sayfa_no"),
                chunk["chunk_no"],
                chunk["metin"],
                json.dumps(embedding),
            )
        )

        print(
            f"\rEmbedding olusturuluyor: "
            f"{sira}/{len(chunklar)}",
            end="",
            flush=True
        )

    baglanti.commit()
    baglanti.close()

    embedding_model.unload()

    print("\n")
    print("Veritabani olusturuldu.")
    print(f"Kaydedildi: {DATABASE_FILE}")


if __name__ == "__main__":
    main()