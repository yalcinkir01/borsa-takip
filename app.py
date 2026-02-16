import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Evrensel Portföyüm", layout="wide")

# --- 1. VARLIK KÜTÜPHANESİ (Ticker Eşleşmeleri) ---
VARLIK_TIPLERI = {
    "Borsa İstanbul (Hisse)": ".IS",
    "ABD Borsaları (Hisse)": "",
    "Kripto Paralar": "-USD",
    "Emtia & Döviz": "=X"
}

# Hızlı seçim için popüler tickerlar
POPULER_VARLIKLAR = {
    "Borsa İstanbul (Hisse)": ["THYAO", "EREGL", "ASELS", "TUPRS", "SISE", "AKBNK", "BIMAS"],
    "ABD Borsaları (Hisse)": ["AAPL", "NVDA", "TSLA", "AMZN", "MSFT", "GOOGL"],
    "Kripto Paralar": ["BTC", "ETH", "SOL", "AVAX", "XRP"],
    "Emtia & Döviz": ["GAU=TRY", "USDTRY", "EURTRY", "GC=F", "SI=F"] # GAU=TRY Gram Altın, GC=F Ons Altın
}

# --- 2. VERİ SAKLAMA ---
if 'portfoy' not in st.session_state:
    st.session_state.portfoy = []
if 'nakit' not in st.session_state:
    st.session_state.nakit = 0.0

# --- 3. YAN MENÜ: VARLIK EKLEME ---
st.sidebar.header("➕ Portföye Ekle")

kategori = st.sidebar.selectbox("Varlık Tipi", list(VARLIK_TIPLERI.keys()))
liste_tipi = st.sidebar.radio("Giriş Yöntemi", ["Listeden Seç", "Manuel Ticker Yaz"])

if liste_tipi == "Listeden Seç":
    sembol = st.sidebar.selectbox("Varlık Seç", POPULER_VARLIKLAR[kategori])
else:
    sembol = st.sidebar.text_input("Ticker Yaz (Örn: AAPL, BTC, THYAO)").upper()

adet = st.sidebar.number_input("Miktar / Adet", min_value=0.0, step=0.01)

if st.sidebar.button("Portföye Ekle"):
    # Ticker formatını ayarla
    suffix = VARLIK_TIPLERI[kategori]
    final_ticker = f"{sembol}{suffix}" if not sembol.endswith(suffix) else sembol
    
    # Portföye ekle
    st.session_state.portfoy.append({
        "kategori": kategori,
        "ticker": final_ticker,
        "adet": adet
    })
    st.sidebar.success(f"{final_ticker} başarıyla eklendi!")

# --- 4. ANA EKRAN: ÖZET VE TABLO ---
st.title("💰 Evrensel Finansal Panel")

# Üst Bilgi Kartları
if st.session_state.portfoy:
    df_list = []
    toplam_varlik_tl = st.session_state.nakit
    
    with st.spinner('Fiyatlar güncelleniyor...'):
        for item in st.session_state.portfoy:
            t = yf.Ticker(item['ticker'])
            try:
                fiyat = t.history(period="1d")['Close'].iloc[-1]
                deger = fiyat * item['adet']
                toplam_varlik_tl += deger
                
                df_list.append({
                    "Tip": item['kategori'],
                    "Varlık": item['ticker'],
                    "Miktar": item['adet'],
                    "Güncel Fiyat": f"{fiyat:,.2f}",
                    "Toplam Değer": deger
                })
            except:
                st.error(f"{item['ticker']} verisi çekilemedi.")

    # Metrikleri Göster
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Portföy Değeri", f"{toplam_varlik_tl:,.2f} TL")
    c2.metric("Nakit Bakiye", f"{st.session_state.nakit:,.2f} TL")
    c3.metric("Varlık Sayısı", len(st.session_state.portfoy))

    # Tabloyu Göster
    if df_list:
        st.subheader("Varlık Detayları")
        main_df = pd.DataFrame(df_list)
        st.dataframe(main_df.style.format({"Toplam Değer": "{:,.2f} TL"}), use_container_width=True)
else:
    st.info("Portföyünüz henüz boş. Yan menüden varlık ekleyerek başlayın.")

# --- 5. NAKİT YÖNETİMİ (ALT KISIM) ---
st.divider()
st.subheader("💵 Nakit Bakiyesi Güncelle")
yeni_nakit = st.number_input("Banka Hesabındaki Toplam Nakit (TL)", value=st.session_state.nakit)
if st.button("Nakiti Kaydet"):
    st.session_state.nakit = yeni_nakit
    st.rerun()