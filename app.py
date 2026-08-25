from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for,
)

from rag import manager_olustur, rag_sorgula

import sqlite3
import json

from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = "tuketici-rehber-local-secret"


# =========================================================
# SOHBET VERİTABANI
# =========================================================

def sohbet_db_hazirla():
    baglanti = sqlite3.connect("data/rag.db")
    imlec = baglanti.cursor()

    imlec.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici TEXT NOT NULL,
            soru TEXT NOT NULL,
            cevap TEXT NOT NULL,
            kaynaklar TEXT,
            tarih DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    baglanti.commit()
    baglanti.close()

def kullanici_db_hazirla():
    baglanti = sqlite3.connect("data/rag.db")
    imlec = baglanti.cursor()

    imlec.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad_soyad TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            sifre_hash TEXT NOT NULL,
            tarih DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    baglanti.commit()
    baglanti.close()
def sohbet_kaydet(
    kullanici,
    soru,
    cevap,
    kaynaklar
):
    baglanti = sqlite3.connect("data/rag.db")
    imlec = baglanti.cursor()

    imlec.execute(
        """
        INSERT INTO chat_history
        (
            kullanici,
            soru,
            cevap,
            kaynaklar
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            kullanici,
            soru,
            cevap,
            json.dumps(
                kaynaklar,
                ensure_ascii=False
            ),
        ),
    )

    baglanti.commit()
    baglanti.close()


def sohbetleri_getir(kullanici):
    baglanti = sqlite3.connect("data/rag.db")
    imlec = baglanti.cursor()

    imlec.execute(
        """
        SELECT
            id,
            soru,
            cevap,
            kaynaklar,
            tarih
        FROM chat_history
        WHERE kullanici = ?
        ORDER BY id DESC
        LIMIT 20
        """,
        (kullanici,),
    )

    kayitlar = imlec.fetchall()

    baglanti.close()

    return kayitlar


# Tabloları uygulama başlarken hazırla.
sohbet_db_hazirla()
kullanici_db_hazirla()


# =========================================================
# FOUNDRY LOCAL
# =========================================================

manager = None


def get_manager():
    global manager

    if manager is None:
        manager = manager_olustur()

    return manager


# =========================================================
# ANA SAYFA
# =========================================================

@app.route("/")
def ana_sayfa():
    if not session.get("giris_yapildi"):
        return redirect(
            url_for("giris")
        )

    return render_template(
        "index.html"
    )



# =========================================================
# GİRİŞ
# =========================================================

@app.route("/giris", methods=["GET", "POST"])
def giris():
    hata = None

    if request.method == "POST":
        eposta = request.form.get(
            "eposta",
            ""
        ).strip().lower()

        sifre = request.form.get(
            "sifre",
            ""
        ).strip()

        baglanti = sqlite3.connect("data/rag.db")
        imlec = baglanti.cursor()

        imlec.execute(
            """
            SELECT id, ad_soyad, email, sifre_hash
            FROM users
            WHERE email = ?
            """,
            (eposta,)
        )

        kullanici = imlec.fetchone()
        baglanti.close()

        if kullanici and check_password_hash(
            kullanici[3],
            sifre
        ):
            session["giris_yapildi"] = True
            session["kullanici_id"] = kullanici[0]
            session["ad_soyad"] = kullanici[1]
            session["kullanici"] = kullanici[2]

            return redirect(
                url_for("ana_sayfa")
            )

        hata = "E-posta adresi veya şifre hatalı."

    return render_template(
        "login.html",
        hata=hata
    )
# =========================================================
# KAYIT OL
# =========================================================

@app.route("/kayit", methods=["GET", "POST"])
def kayit():
    hata = None

    if request.method == "POST":
        ad_soyad = request.form.get(
            "ad_soyad",
            ""
        ).strip()

        eposta = request.form.get(
            "eposta",
            ""
        ).strip().lower()

        sifre = request.form.get(
            "sifre",
            ""
        ).strip()

        sifre_tekrar = request.form.get(
            "sifre_tekrar",
            ""
        ).strip()

        if not ad_soyad or not eposta or not sifre:
            hata = "Lütfen tüm alanları doldurun."

        elif sifre != sifre_tekrar:
            hata = "Şifreler eşleşmiyor."

        elif len(sifre) < 6:
            hata = "Şifre en az 6 karakter olmalıdır."

        else:
            try:
                sifre_hash = generate_password_hash(sifre)

                baglanti = sqlite3.connect("data/rag.db")
                imlec = baglanti.cursor()

                imlec.execute(
                    """
                    INSERT INTO users
                    (ad_soyad, email, sifre_hash)
                    VALUES (?, ?, ?)
                    """,
                    (
                        ad_soyad,
                        eposta,
                        sifre_hash
                    )
                )

                baglanti.commit()
                baglanti.close()

                return redirect(
                    url_for("giris")
                )

            except sqlite3.IntegrityError:
                hata = "Bu e-posta adresi zaten kayıtlı."

    return render_template(
        "register.html",
        hata=hata
    )
# =========================================================
# ŞİFREMİ UNUTTUM
# =========================================================

@app.route(
    "/sifremi-unuttum",
    methods=["GET", "POST"]
)
def sifremi_unuttum():
    hata = None
    basarili = None

    if request.method == "POST":
        eposta = request.form.get(
            "eposta",
            ""
        ).strip().lower()

        yeni_sifre = request.form.get(
            "yeni_sifre",
            ""
        ).strip()

        yeni_sifre_tekrar = request.form.get(
            "yeni_sifre_tekrar",
            ""
        ).strip()

        if len(yeni_sifre) < 6:
            hata = "Şifre en az 6 karakter olmalıdır."

        elif yeni_sifre != yeni_sifre_tekrar:
            hata = "Şifreler eşleşmiyor."

        else:
            baglanti = sqlite3.connect("data/rag.db")
            imlec = baglanti.cursor()

            imlec.execute(
                """
                SELECT id
                FROM users
                WHERE email = ?
                """,
                (eposta,)
            )

            kullanici = imlec.fetchone()

            if not kullanici:
                hata = "Bu e-posta adresiyle kayıtlı kullanıcı bulunamadı."

            else:
                sifre_hash = generate_password_hash(
                    yeni_sifre
                )

                imlec.execute(
                    """
                    UPDATE users
                    SET sifre_hash = ?
                    WHERE email = ?
                    """,
                    (
                        sifre_hash,
                        eposta
                    )
                )

                baglanti.commit()

                basarili = "Şifreniz başarıyla güncellendi."

            baglanti.close()

    return render_template(
        "forgot_password.html",
        hata=hata,
        basarili=basarili
    )
# =========================================================
# ÇIKIŞ
# =========================================================

@app.route("/cikis")
def cikis():
    session.clear()

    return redirect(
        url_for("giris")
    )


# =========================================================
# RAG SORU API
# =========================================================

@app.route(
    "/api/sor",
    methods=["POST"]
)
def soru_sor():
    if not session.get(
        "giris_yapildi"
    ):
        return jsonify(
            {
                "hata": "Oturum bulunamadı."
            }
        ), 401

    veri = (
        request.get_json(
            silent=True
        )
        or {}
    )

    soru = veri.get(
        "soru",
        ""
    ).strip()

    if not soru:
        return jsonify(
            {
                "hata": "Lütfen bir soru yazın."
            }
        ), 400

    try:
        sonuc = rag_sorgula(
            get_manager(),
            soru
        )

        kaynaklar = []

        for kaynak in sonuc.get(
            "kaynaklar",
            []
        ):
            temiz_ad = (
                kaynak
                .replace(".txt", "")
                .replace(".pdf", "")
            )

            parcalar = temiz_ad.split("_")

            if (
                parcalar
                and parcalar[0].isdigit()
            ):
                parcalar = parcalar[1:]

            temiz_ad = " ".join(
                parcalar
            ).title()

            kaynaklar.append(
                {
                    "dosya": kaynak,
                    "ad": temiz_ad,
                }
            )

        cevap = sonuc.get(
            "cevap",
            "Bu bilgi sağlanan belgelerde bulunamadı."
        )

        # Sohbeti SQLite'a kaydet.
        sohbet_kaydet(
            session.get(
                "kullanici",
                "kullanici"
            ),
            soru,
            cevap,
            kaynaklar
        )

        return jsonify(
            {
                "cevap": cevap,
                "kaynaklar": kaynaklar,
                "bulundu": sonuc.get(
                    "bulundu",
                    False
                ),
            }
        )

    except Exception as hata:
        print(
            "RAG HATASI:",
            hata
        )

        return jsonify(
            {
                "hata":
                    "Yanıt oluşturulurken "
                    "bir hata meydana geldi."
            }
        ), 500


# =========================================================
# SOHBET GEÇMİŞİ API
# =========================================================

@app.route("/api/gecmis")
def gecmis():
    if not session.get(
        "giris_yapildi"
    ):
        return jsonify([]), 401

    kayitlar = sohbetleri_getir(
        session.get(
            "kullanici",
            "kullanici"
        )
    )

    sonuc = []

    for (
        id_,
        soru,
        cevap,
        kaynaklar,
        tarih
    ) in kayitlar:

        sonuc.append(
            {
                "id": id_,
                "soru": soru,
                "cevap": cevap,
                "kaynaklar": json.loads(
                    kaynaklar or "[]"
                ),
                "tarih": tarih,
            }
        )

    return jsonify(sonuc)
# =========================================================
# SOHBET SİLME API
# =========================================================

@app.route("/api/gecmis/<int:sohbet_id>", methods=["DELETE"])
def sohbet_sil(sohbet_id):
    if not session.get("giris_yapildi"):
        return jsonify({
            "hata": "Oturum bulunamadı."
        }), 401

    kullanici = session.get("kullanici")

    baglanti = sqlite3.connect("data/rag.db")
    imlec = baglanti.cursor()

    imlec.execute(
        """
        DELETE FROM chat_history
        WHERE id = ? AND kullanici = ?
        """,
        (sohbet_id, kullanici)
    )

    silinen = imlec.rowcount

    baglanti.commit()
    baglanti.close()

    if silinen == 0:
        return jsonify({
            "hata": "Sohbet bulunamadı."
        }), 404

    return jsonify({
        "basarili": True
    })

# =========================================================
# UYGULAMA
# =========================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
