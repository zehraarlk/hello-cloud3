from flask import Flask, render_template_string, request
import os
import psycopg2

# 1. Flask uygulama tanımı düzeltildi: _name_ -> __name__
app = Flask(__name__)

# Veritabanı URL'si, ortam değişkeninden çekilmeye çalışılır. 
# Eğer bulunamazsa, sağlanan varsayılan URL kullanılır.
# Not: Bu URL'yi doğrudan kodda tutmak yerine, Render gibi servislerde 
# bir "Environment Variable" olarak tanımlamak en iyi uygulamadır.
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://hello_cloud3_db_shnf_user:HDmlcDFdWqYi93D97IC0UsbDfFjdmf5B@dpg-d5bsiuh5pdvs73bsa830-a/hello_cloud3_db_shnf"
)

HTML = """
<!doctype html>
<html>
<head>
    <title>Buluttan Selam! 👋</title>
    <style>
        body { font-family: Arial; text-align: center; padding: 50px; background: #eef2f3; }
        h1 { color: #333; }
        form { margin: 20px auto; }
        input { padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 6px; }
        button { padding: 10px 15px; background: #4CAF50; color: white; border: none; border-radius: 6px; cursor: pointer; transition: background 0.3s; }
        button:hover { background: #45a049; }
        ul { list-style: none; padding: 0; max-width: 300px; margin: 15px auto; }
        li { background: white; margin: 5px auto; padding: 10px; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <h1>Buluttan Selam! ☁️</h1>
    <p>Adını yaz, selamını bırak</p>
    <form method="POST">
        <input type="text" name="isim" placeholder="Adını yaz" required maxlength="50">
        <button type="submit">Gönder</button>
    </form>
    <h3>Son 10 Ziyaretçi:</h3>
    <ul>
        {% for ad in isimler %}
            <li>{{ ad }}</li>
        {% endfor %}
    </ul>
    <div style="position: fixed; bottom: 10px; right: 10px; font-size: 14px; color: #555;">
    Zehra Aralık
    </div>
</body>
</html>
"""

def connect_db():
    """PostgreSQL veritabanına bağlantı kurar."""
    conn = psycopg2.connect(DATABASE_URL)
    return conn


@app.route("/", methods=["GET", "POST"])
def index():
    conn = None
    try:
        conn = connect_db()
        cur = conn.cursor()
        
        # Tablo yoksa oluştur
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ziyaretciler (
                id SERIAL PRIMARY KEY, 
                isim TEXT NOT NULL
            )
        """)
        conn.commit()

        if request.method == "POST":
            isim = request.form.get("isim")
            if isim:
                # Veri ekleme (SQL Enjeksiyonundan korunmak için parametreli sorgu)
                cur.execute("INSERT INTO ziyaretciler (isim) VALUES (%s)", (isim,))
                conn.commit()

        # En son 10 ziyaretçiyi çekme
        cur.execute("SELECT isim FROM ziyaretciler ORDER BY id DESC LIMIT 10")
        isimler = [row[0] for row in cur.fetchall()]
        
        cur.close()
        
        return render_template_string(HTML, isimler=isimler)
    
    except Exception as e:
        # Hata durumunda loglama ve kullanıcıya genel bir mesaj gösterme
        print(f"Veritabanı Hatası Oluştu: {e}")
        return render_template_string("<h1>Bir veritabanı hatası oluştu.</h1><p>Lütfen daha sonra tekrar deneyin.</p>", isimler=[])
    
    finally:
        # Bağlantı her durumda kapatılır
        if conn:
            conn.close()


# 2. Uygulama çalıştırma kontrolü düzeltildi: _name_ == "_main_" -> __name__ == "__main__"
if __name__ == "__main__":
    # debug=True, geliştirme sırasında hataları tarayıcıda görmenizi sağlar.
    app.run(host="0.0.0.0", port=5000, debug=True)
