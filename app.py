import streamlit as st
import yfinance as yf
import pandas as pd

# Sayfa Ayarları (Tam ekran ve Türkçe başlık)
st.set_page_config(page_title="Borsa İzleme Paneli", layout="wide")

# --- ⚙️ VERİ ÇEKME FONKSİYONLARI ---
# Sayfa her açıldığında butona basmadan çalışması için doğrudan çağırıyoruz
@st.cache_data(ttl=600) # Verileri 10 dakikada bir günceller, bilgisayarı yormaz
def verileri_getir(hisse_listesi):
    sonuclar = []
    for hisse in hisse_listesi:
        h = yf.Ticker(hisse)
        d = h.history(period="2d")
        if len(d) > 1:
            guncel = d['Close'].iloc[-1]
            onceki = d['Close'].iloc[-2]
            degisim = ((guncel - onceki) / onceki) * 100
            sonuclar.append({"Hisse": hisse, "Fiyat": guncel, "Değişim": degisim})
    return pd.DataFrame(sonuclar)

# --- 🏠 PORTFÖYÜN (Burayı dilediğin gibi güncelle) ---
# Format: "Hisse Kodu": [Adet, Alış Maliyeti]
benim_cüzdanım = {
    "THYAO.IS": [100, 275.50],
    "ASELS.IS": [500, 48.20],
    "TUPRS.IS": [40, 162.00],
    "EREGL.IS": [250, 41.80],
    "SASA.IS": [1000, 38.50]
}

# --- ⬅️ BANA GÖRE SOL: MENÜ SÜTUNU ---
with st.sidebar:
    st.header("📌 Menü")
    sayfa_secimi = st.radio(
        "Gitmek istediğiniz alan:",
        ["💰 Cüzdanım", "📊 Teknik Analiz", "⚙️ Ayarlar"]
    )
    st.write("---")
    st.caption("Veriler 13 Şubat 2026 Midas teknik raporu ve canlı borsa verileriyle harmanlanmıştır.")

# --- 🏗️ ANA EKRAN DÜZENİ (ORTA VE SAĞ) ---
# Orta alan %75, Sağ alan %25 yer kaplayacak şekilde bölüyoruz
orta_sutun, sag_sutun = st.columns([3, 1])

# --- 🏛️ ORTA BÖLÜM: İŞLEM ALANI ---
with orta_sutun:
    if sayfa_secimi == "💰 Cüzdanım":
        st.header("💰 Gerçek Zamanlı Portföy Durumum")
        
        tablo_verisi = []
        toplam_deger = 0
        
        # Cüzdandaki hisseleri canlı hesapla
        for hisse, bilgi in benim_cüzdanım.items():
            h = yf.Ticker(hisse)
            guncel_fiyat = h.history(period="1d")['Close'].iloc[-1]
            adet, maliyet = bilgi[0], bilgi[1]
            anlik_deger = adet * guncel_fiyat
            toplam_deger += anlik_deger
            kar_zarar = anlik_deger - (adet * maliyet)
            
            tablo_verisi.append({
                "Hisse": hisse,
                "Adet": adet,
                "Maliyet": f"{maliyet:.2f} TL",
                "Güncel": f"{guncel_fiyat:.2f} TL",
                "Durum": f"{kar_zarar:,.2f} TL"
            })
        
        st.metric("Toplam Cüzdan Değeri", f"{toplam_deger:,.2f} TL")
        st.table(pd.DataFrame(tablo_verisi))

    elif sayfa_secimi == "📊 Teknik Analiz":
        st.header("📈 Hisse Grafikleri")
        secilen = st.selectbox("Grafiğini görmek istediğiniz hisse:", list(benim_cüzdanım.keys()))
        grafik_verisi = yf.Ticker(secilen).history(period="1mo")
        st.line_chart(grafik_verisi['Close'])

# --- 🚀 BANA GÖRE SAĞ: EN ÇOK YÜKSELENLER ---
with sag_sutun:
    st.subheader("🔥 Günün Yıldızları")
    # Takip listesindeki en çok yükselenleri bulalım
    piyasa_verisi = verileri_getir(["AKSEN.IS", "KCHOL.IS", "BIMAS.IS", "SISE.IS", "PGSUS.IS", "EKGYO.IS"])
    if not piyasa_verisi.empty:
        yukselenler = piyasa_verisi.sort_values(by="Değişim", ascending=False).head(10)
        for _, row in yukselenler.iterrows():
            st.write(f"**{row['Hisse']}**")
            st.write(f"{row['Fiyat']:.2f} TL | %{row['Değişim']:.2f}")
            st.write("---")
