from foundry_local_sdk import Configuration, FoundryLocalManager


def main():
    # Foundry Local SDK'yi baslat
    config = Configuration(app_name="foundry_local_rag")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    # Cihaza uygun calistirma altyapisini indir ve kaydet
    current_ep = ""

    def ep_progress(ep_name: str, percent: float):
        nonlocal current_ep

        if ep_name != current_ep:
            if current_ep:
                print()
            current_ep = ep_name

        print(
            f"\r{ep_name:<30} {percent:5.1f}%",
            end="",
            flush=True,
        )

    manager.download_and_register_eps(
        progress_callback=ep_progress
    )

    if current_ep:
        print()

    # Kucuk bir model sec
    model = manager.catalog.get_model("qwen2.5-0.5b")

    print("Model indiriliyor...")

    model.download(
        lambda progress: print(
            f"\rModel indirme: {progress:.2f}%",
            end="",
            flush=True,
        )
    )

    print()

    # Modeli bellekte yukle
    model.load()
    print("Model yuklendi.")

    # Chat istemcisini al
    client = model.get_chat_client()

    messages = [
        {
            "role": "user",
            "content": "Merhaba! Kendini kisaca tanit."
        }
    ]

    print("Model cevabi: ", end="", flush=True)

    for chunk in client.complete_streaming_chat(messages):

        if not chunk.choices:
            continue

        content = chunk.choices[0].delta.content

        if content:
            print(content, end="", flush=True)

    print()

    # Bellekten modeli kaldir
    model.unload()

    print("Model kapatildi.")

@app.route("/api/gecmis/<int:sohbet_id>", methods=["DELETE"])
def sohbet_sil(sohbet_id):
    if not session.get("giris_yapildi"):
        return jsonify({
            "hata": "Oturum bulunamadı."
        }), 401

    kullanici = session.get(
        "kullanici",
        "kullanici"
    )

    baglanti = sqlite3.connect(
        "data/rag.db"
    )

    imlec = baglanti.cursor()

    imlec.execute(
        """
        DELETE FROM chat_history
        WHERE id = ?
        AND kullanici = ?
        """,
        (
            sohbet_id,
            kullanici
        )
    )

    baglanti.commit()
    baglanti.close()

    return jsonify({
        "basarili": True
    })
if __name__ == "__main__":
    main()