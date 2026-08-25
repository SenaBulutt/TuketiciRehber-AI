import sqlite3
import json


def main():
    baglanti = sqlite3.connect("rag_test.db")
    imlec = baglanti.cursor()

    imlec.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
        """
    )

    ornek_metin = "Embedding, metinleri sayısal vektörlere dönüştürür."
    ornek_embedding = [0.12, 0.45, 0.78, 0.33]

    imlec.execute(
        """
        INSERT INTO documents (content, embedding)
        VALUES (?, ?)
        """,
        (
            ornek_metin,
            json.dumps(ornek_embedding),
        ),
    )

    baglanti.commit()

    imlec.execute(
        """
        SELECT id, content, embedding
        FROM documents
        """
    )

    kayitlar = imlec.fetchall()

    print("Veritabanindaki kayitlar:")

    for kayit in kayitlar:
        print(kayit)

    baglanti.close()


if __name__ == "__main__":
    main()