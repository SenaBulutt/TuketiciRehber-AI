from pathlib import Path
import json
import re


DOCUMENTS_DIR = Path("data/documents")
OUTPUT_FILE = Path("data/chunks.json")

CHUNK_SIZE = 900
CHUNK_OVERLAP = 150


def metni_temizle(metin):
    """
    Gereksiz boşlukları temizler.
    """
    metin = metin.replace("\r\n", "\n")
    metin = metin.replace("\r", "\n")

    # Çok fazla boş satırı azalt.
    metin = re.sub(r"\n{3,}", "\n\n", metin)

    # Fazla boşlukları temizle.
    metin = re.sub(r"[ \t]+", " ", metin)

    return metin.strip()


def txt_oku(dosya):
    """
    TXT dosyasını UTF-8 olarak okur.
    """
    return dosya.read_text(
        encoding="utf-8"
    )


def metni_chunklara_bol(metin):
    """
    Metni belirli boyutlarda ve örtüşmeli
    parçalara ayırır.
    """

    chunklar = []

    baslangic = 0
    uzunluk = len(metin)

    while baslangic < uzunluk:
        bitis = min(
            baslangic + CHUNK_SIZE,
            uzunluk
        )

        chunk = metin[
            baslangic:bitis
        ].strip()

        if chunk:
            chunklar.append(chunk)

        if bitis >= uzunluk:
            break

        baslangic = bitis - CHUNK_OVERLAP

    return chunklar


def txt_chunklari_olustur(dosya):
    """
    Bir TXT belgesini okuyup
    RAG chunklarına dönüştürür.
    """

    metin = txt_oku(dosya)
    metin = metni_temizle(metin)

    parcalar = metni_chunklara_bol(metin)

    sonuclar = []

    for sira, parca in enumerate(
        parcalar,
        start=1
    ):
        sonuclar.append(
            {
                "kaynak": dosya.name,
                "chunk_no": sira,
                "metin": parca,
            }
        )

    return sonuclar


def main():
    DOCUMENTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    txt_dosyalari = sorted(
        DOCUMENTS_DIR.glob("*.txt")
    )

    if not txt_dosyalari:
        print(
            "data/documents klasöründe "
            "TXT dosyası bulunamadı."
        )
        return

    print(
        f"{len(txt_dosyalari)} TXT bulundu.\n"
    )

    tum_chunklar = []

    for dosya in txt_dosyalari:
        print(
            f"TXT isleniyor: {dosya.name}"
        )

        chunklar = txt_chunklari_olustur(
            dosya
        )

        tum_chunklar.extend(chunklar)

        print(
            f"-> {len(chunklar)} chunk"
        )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            tum_chunklar,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"\nToplam {len(tum_chunklar)} "
        "chunk olusturuldu."
    )

    print(
        f"Kaydedildi: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()