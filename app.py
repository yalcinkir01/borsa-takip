import yfinance as yf
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import sqlite3
import pandas as pd

app = FastAPI()

# VERİTABANI: Hem Nakit hem Hisse senedi tutacak şekilde güncellendi
def init_db():
    conn = sqlite3.connect('cuzdan.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS varliklar 
                      (id INTEGER PRIMARY KEY, isim TEXT, miktar REAL, tip TEXT, ticker TEXT)''')
    # İlk başta nakit bakiyeni tanımlayalım (id=1 her zaman Nakit olsun)
    cursor.execute("INSERT OR IGNORE INTO varliklar (id, isim, miktar, tip) VALUES (1, 'Nakit Bakiye', 0, 'Nakit')")
    conn.commit()
    conn.close()

# 1. BORSA VERİSİ ÇEKME FONKSİYONU
def get_bist_price(ticker):
    try:
        # BIST hisseleri için sonuna .IS ekliyoruz (örn: THYAO.IS)
        hisse = yf.Ticker(f"{ticker.upper()}.IS")
        fiyat = hisse.history(period="1d")['Close'].iloc[-1]
        return round(fiyat, 2)
    except:
        return 0

# 2. ŞİRKET LİSTESİ (Dropdown için en popülerleri ekledim, listeyi genişletebilirsin)
BIST_COMPANIES = {
    "THYAO": "Türk Hava Yolları", "EREGL": "Erdemir Demir Çelik",
    "ASELS": "Aselsan", "AKBNK": "Akbank", "SISE": "Şişecam",
    "KOCHL": "Koç Holding", "TUPRS": "Tüpraş", "BIMAS": "BİM Mağazalar",
    "SASAS": "Sasa Polyester", "HEKTS": "Hektaş", "ISCTR": "İş Bankası (C)"
}

# 3. ANA ARAYÜZ (Dropdown ve Cüzdan Görünümü)
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    conn = sqlite3.connect('cuzdan.db')
    df = pd.read_sql_query("SELECT * FROM varliklar", conn)
    conn.close()

    nakit = df[df['tip'] == 'Nakit']['miktar'].iloc[0]
    hisseler_html = ""
    toplam_hisse_degeri = 0

    for _, row in df[df['tip'] == 'Hisse'].iterrows():
        fiyat = get_bist_price(row['ticker'])
        deger = fiyat * row['miktar']
        toplam_hisse_degeri += deger
        hisseler_html += f"<li>{row['isim']} ({row['ticker']}): {row['miktar']} Adet | Fiyat: {fiyat} TL | Toplam: {round(deger, 2)} TL</li>"

    # Dropdown (Açılır Liste) oluşturma
    options = "".join([f'<option value="{k}">{v} ({k})</option>' for k, v in BIST_COMPANIES.items()])

    return f"""
    <html>
        <head><title>Kişisel Cüzdan</title></head>
        <body style="font-family: sans-serif; padding: 20px;">
            <h1>Cüzdan Özeti</h1>
            <h2 style="color: green;">Net Varlık: {round(nakit + toplam_hisse_degeri, 2)} TL</h2>
            <p>Nakit Bakiyesi: <b>{nakit} TL</b></p>
            <h3>Hisselerim:</h3>
            <ul>{hisseler_html}</ul>
            <hr>
            <h3>Hisse Ekle (Dropdown Listeden Seç)</h3>
            <form action="/hisse-ekle" method="get">
                <select name="ticker">{options}</select>
                <input type="number" name="adet" placeholder="Adet" step="0.01">
                <button type="submit">Ekle</button>
            </form>
        </body>
    </html>
    """

# 4. HİSSE EKLEME ENDPOINT'İ
@app.get("/hisse-ekle")
def add_stock(ticker: str, adet: float):
    isim = BIST_COMPANIES.get(ticker, ticker)
    conn = sqlite3.connect('cuzdan.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO varliklar (isim, miktar, tip, ticker) VALUES (?, ?, 'Hisse', ?)", (isim, adet, ticker))
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"{ticker} portföye eklendi."}

# 5. BANKA BİLDİRİMİ İŞLEME (Önceki Adımdaki gibi çalışır)
@app.post("/bildirim-isle")
async def process_notif(request: Request):
    # ... (Önceki kodun aynısı buraya gelecek, nakit bakiyeyi güncelleyecek)
    pass

if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)