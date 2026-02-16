import streamlit as st
import yfinance as yf
import pandas as pd

# Sayfa Genişliği ve Başlık
st.set_page_config(page_title="Cüzdanım", layout="centered")

# --- 1. ŞİRKET LİSTESİ (Açılır Liste İçin) ---
# Buraya istediğin şirketleri ekle
BIST_SIRKETLERI = {
    "THYAO": "Türk Hava Yolları", "EREGL": "Erdemir", "ASELS": "Aselsan",
    "AKBNK": "Akbank", "SISE": "Şişecam", "TUPRS": "Tüpraş",
    "BIMAS": "BİM Mağazalar", "SASAS": "Sasa Polyester", "HEKTS": "Hektaş"
}

# --- 2. CÜZDAN VERİLERİ (Session State - Uygulama Açıkken Veriyi Tutar) ---
if 'nakit' not in st.session_state:
    st.session_state.nakit = 0.0
if 'hisseler' not in st.session_state:
    st.session_state.hisseler = {}

# --- 3. ANA EKRAN TASARIMI ---
st.title("📱 Kişisel Cüzdan Paneli")

# NAKİT BÖLÜMÜ
st.subheader("Banka Bakiyesi")
col1, col2 = st.columns([2, 1])
yeni_nakit = col1.number_input("Güncel Nakit Bakiyeni Gir (TL)", value=st.session_state.nakit)
if col2.button("Bakiyeyi Güncelle"):
    st.session_state.nakit = yeni_nakit
    st.success("Bakiye Kaydedildi!")

st.divider()

# BORSA / HİSSE EKLEME (Senin İstediğin Dropdown)
st.subheader("Portföye Hisse Ekle")
secilen_hisse = st.selectbox("Şirket Seçin", options=list(BIST_SIRKETLERI.keys()), 
                             format_func=lambda x: f"{BIST_SIRKETLERI[x]} ({x})")
adet = st.number_input("Adet", min_value=0.0, step=1.0)

if st.button("Hisseleri Portföye Ekle"):
    st.session_state.hisseler[secilen_hisse] = adet
    st.success(f"{secilen_hisse} portföye eklendi.")

st.divider()

# --- 4. HESAPLAMA VE ÖZET ---
st.subheader("Varlıklarımın Durumu")

if st.session_state.hisseler:
    veriler = []
    toplam_borsa_tl = 0
    
    for ticker, miktar in st.session_state.hisseler.items():
        if miktar > 0:
            # BIST verisini yfinance ile çek
            hisse_data = yf.Ticker(f"{ticker}.IS")
            son_fiyat = hisse_data.history(period="1d")['Close'].iloc[-1]
            toplam_deger = son_fiyat * miktar
            toplam_borsa_tl += toplam_deger
            
            veriler.append({
                "Hisse": ticker,
                "Adet": miktar,
                "Fiyat": f"{son_fiyat:.2f} TL",
                "Toplam": f"{toplam_deger:,.2f} TL"
            })
    
    if veriler:
        st.table(pd.DataFrame(veriler))
        
        # Göstergeler (Metrikler)
        m1, m2 = st.columns(2)
        m1.metric("Toplam Nakit", f"{st.session_state.nakit:,.2f} TL")
        m2.metric("Toplam Borsa", f"{toplam_borsa_tl:,.2f} TL")
        
        st.info(f"💰 **Genel Toplam Varlık: {st.session_state.nakit + toplam_borsa_tl:,.2f} TL**")
else:
    st.write("Henüz hisse eklenmedi.")