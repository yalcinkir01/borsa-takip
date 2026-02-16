import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Pro Portföy Yönetimi", layout="wide")

# --- 1. VERİ KAYNAKLARI (TÜM ŞİRKET LİSTELERİ) ---
@st.cache_data # Listeleri her seferinde çekmemesi için önbelleğe alıyoruz
def sirket_listelerini_getir():
    # BIST Listesi (Sadeleştirilmiş Tickerlar)
    bist_url = "https://raw.githubusercontent.com/atabolat/bist-hisse-listesi/main/bist_hisse_listesi.csv"
    try:
        bist_df = pd.read_csv(bist_url)
        bist_list = bist_df['Ticker'].tolist()
    except:
        bist_list = ["THYAO", "EREGL", "ASELS", "AKBNK", "TUPRS"] # Hata durumunda yedek

    # ABD Borsaları (S&P 500 Örneği - 500 Dev Şirket)
    sp500_url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    try:
        sp500_df = pd.read_csv(sp500_url)
        # "Symbol" ve "Name" sütunlarını birleştirip liste yapıyoruz
        sp500_list = (sp500_df['Symbol'] + " - " + sp500_df['Name']).tolist()
    except:
        sp500_list = ["AAPL - Apple", "NVDA - Nvidia", "TSLA - Tesla", "MSFT - Microsoft"]

    # Kripto Paralar (En popüler 100)
    kripto_list = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOT", "LINK", "DOGE"]

    return bist_list, sp500_list, kripto_list

bist_full, sp500_full, kripto_full = sirket_listelerini_getir()

# --- 2. VERİ SAKLAMA ---
if 'portfoy' not in st.session_state:
    st.session_state.portfoy = []
if 'nakit' not in st.session_state:
    st.session_state.nakit = 0.0

# --- 3. YAN MENÜ: AKILLI DROPDOWN SİSTEMİ ---
st.sidebar.header("🚀 Portföy Yönetimi")

kategori = st.sidebar.selectbox("Borsa Seçin", 
    ["Borsa İstanbul (BIST)", "ABD Borsaları (S&P 500)", "Kripto Paralar", "Emtia & Döviz"])

# Seçilen kategoriye göre açılır listeyi doldur
if kategori == "Borsa İstanbul (BIST)":
    secilen_raw = st.sidebar.selectbox("Şirket Seçin", options=bist_full)
    ticker = f"{secilen_raw}.IS"
elif kategori == "ABD Borsaları (S&P 500)":
    secilen_raw = st.sidebar.selectbox("Şirket Seçin", options=sp500_full)
    ticker = secilen_raw.split(" - ")[0] # Sadece Ticker kısmını al (Örn: AAPL)
elif kategori == "Kripto Paralar":
    secilen_raw = st.sidebar.selectbox("Coin Seçin", options=kripto_full)
    ticker = f"{secilen_raw}-USD"
else: # Emtia
    secilen_raw = st.sidebar.selectbox("Varlık Seçin", ["GAU=TRY (Gram Altın)", "USDTRY=X (Dolar)", "GC=F (Ons Altın)"])
    ticker = secilen_raw.split(" (")[0]

adet = st.sidebar.number_input("Miktar / Adet", min_value=0.0, step=0.01)

if st.sidebar.button("Ekle / Güncelle"):
    # Eğer zaten varsa güncelle, yoksa ekle
    exists = False
    for item in st.session_state.portfoy:
        if item['ticker'] == ticker:
            item['adet'] = adet
            exists = True
    if not exists:
        st.session_state.portfoy.append({"kategori": kategori, "ticker": ticker, "adet": adet})
    st.sidebar.success(f"{ticker} kaydedildi.")

# --- 4. GÖRSEL ANALİZ VE TABLO ---
st.title("📊 Finansal Durum Raporu")

if st.session_state.portfoy:
    df_list = []
    toplam_varlik_tl = st.session_state.nakit
    
    with st.spinner('Canlı veriler borsadan çekiliyor...'):
        for item in st.session_state.portfoy:
            t = yf.Ticker(item['ticker'])
            try:
                hist = t.history(period="1d")
                fiyat = hist['Close'].iloc[-1]
                deger = fiyat * item['adet']
                toplam_varlik_tl += deger
                
                df_list.append({
                    "Kategori": item['kategori'],
                    "Varlık": item['ticker'],
                    "Adet": item['adet'],
                    "Güncel Fiyat": round(fiyat, 2),
                    "Toplam Değer (TL)": round(deger, 2)
                })
            except:
                continue

    # Özet Kartları
    c1, c2 = st.columns(2)
    c1.metric("Toplam Portföy (Nakit Dahil)", f"{toplam_varlik_tl:,.2f} TL")
    c2.metric("Nakit Bakiye", f"{st.session_state.nakit:,.2f} TL")

    # Detaylı Tablo
    st.subheader("Varlıklarım")
    st.dataframe(pd.DataFrame(df_list), use_container_width=True)
else:
    st.info("Portföyünüz şu an boş. Yan menüden borsa seçip şirket eklemeye başlayın.")

# --- 5. AYARLAR ---
with st.expander("⚙️ Veri Ayarları"):
    yeni_nakit = st.number_input("Nakit Bakiyeni Güncelle", value=st.session_state.nakit)
    if st.button("Kaydet"):
        st.session_state.nakit = yeni_nakit
        st.rerun()