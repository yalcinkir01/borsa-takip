import streamlit as st
import yfinance as yf
import pandas as pd

# Sayfa Genişlik Ayarı
st.set_page_config(page_title="Borsa Portföy Yöneticisi", layout="wide")

# --- 💾 VERİ SAKLAMA ÜNİTESİ (Session State) ---
# Sayfa yenilense bile verilerin kaybolmaması için bir hafıza alanı oluşturuyoruz
if "cuzdan" not in st.session_state:
    st.session_state.cuzdan = [] # Başlangıçta cüzdan boş

# --- ⬅️ BANA GÖRE SOL: YÖNETİM VE EKLEME ÜNİTESİ ---
with st.sidebar:
    st.header("⚙️ Portföy Yönetimi")
    
    # 1. Sayfa Seçimi
    sayfa = st.radio("İşlem Seçin:", ["💰 Cüzdanım", "📉 Grafik Analiz"])
    st.write("---")
    
    # 2. VERİ EKLEME ÜNİTESİ
    st.subheader("➕ Yeni Hisse Ekle")
    yeni_hisse = st.text_input("Hisse Kodu (Örn: THYAO.IS):").upper()
    yeni_adet = st.number_input("Adet:", min_value=0, value=0, step=1)
    yeni_maliyet = st.number_input("Alış Maliyeti (TL):", min_value=0.0, value=0.0, step=0.1)
    
    if st.button("Portföye Ekle"):
        if yeni_hisse and yeni_adet > 0:
            # Listeye ekle
            st.session_state.cuzdan.append({
                "Hisse": yeni_hisse,
                "Adet": yeni_adet,
                "Maliyet": yeni_maliyet
            })
            st.success(f"{yeni_hisse} başarıyla eklendi!")
        else:
            st.error("Lütfen tüm alanları doğru doldurun.")

    st.write("---")
    if st.button("🗑️ Cüzdanı Sıfırla"):
        st.session_state.cuzdan = []
        st.rerun()

# --- 🏗️ ANA EKRAN DÜZENİ ---
orta_sutun, sag_sutun = st.columns([3, 1])

# --- 🏛️ ORTA BÖLÜM: İŞLEM VE GÖSTERİM ALANI ---
with orta_sutun:
    if sayfa == "💰 Cüzdanım":
        st.header("📋 Portföyümün Güncel Durumu")
        
        if len(st.session_state.cuzdan) == 0:
            st.info("Cüzdanınız şu an boş. Sol menüden hisse ekleyerek başlayabilirsiniz.")
        else:
            tablo_listesi = []
            toplam_maliyet_genel = 0
            toplam_deger_genel = 0
            
            for kalem in st.session_state.cuzdan:
                with st.spinner(f"{kalem['Hisse']} verisi alınıyor..."):
                    h = yf.Ticker(kalem['Hisse'])
                    guncel = h.history(period="1d")['Close'].iloc[-1]
                    
                    t_maliyet = kalem['Adet'] * kalem['Maliyet']
                    t_deger = kalem['Adet'] * guncel
                    k_z = t_deger - t_maliyet
                    
                    toplam_maliyet_genel += t_maliyet
                    toplam_deger_genel += t_deger
                    
                    tablo_listesi.append({
                        "Hisse": kalem['Hisse'],
                        "Adet": kalem['Adet'],
                        "Maliyet": f"{kalem['Maliyet']:.2f} TL",
                        "Güncel": f"{guncel:.2f} TL",
                        "Kâr/Zarar": f"{k_z:,.2f} TL",
                        "Değişim %": f"%{((guncel - kalem['Maliyet']) / kalem['Maliyet'] * 100):.2f}"
                    })
            
            # Özet Kartları
            c1, c2, c3 = st.columns(3)
            c1.metric("Toplam Maliyet", f"{toplam_maliyet_genel:,.2f} TL")
            c2.metric("Güncel Değer", f"{toplam_deger_genel:,.2f} TL")
            c3.metric("Net Durum", f"{(toplam_deger_genel - toplam_maliyet_genel):,.2f} TL")
            
            # Detaylı Tablo
            st.table(pd.DataFrame(tablo_listesi))

    elif sayfa == "📉 Grafik Analiz":
        st.header("📊 Teknik Görünüm")
        if len(st.session_state.cuzdan) > 0:
            secilen = st.selectbox("İncelemek istediğiniz hisse:", [x['Hisse'] for x in st.session_state.cuzdan])
            grafik_verisi = yf.Ticker(secilen).history(period="1mo")
            st.line_chart(grafik_verisi['Close'])
        else:
            st.warning("Grafik görmek için önce cüzdana hisse eklemelisiniz.")

# --- 🚀 BANA GÖRE SAĞ: EN ÇOK YÜKSELENLER (BIST 30 Örneği) ---
with sag_sutun:
    st.subheader("🔥 BIST Trend")
    # Takip edilecek popüler hisseler
    populer = ["THYAO.IS", "ASELS.IS", "TUPRS.IS", "EREGL.IS", "KCHOL.IS", "BIMAS.IS"]
    
    for p_hisse in populer:
        ph = yf.Ticker(p_hisse)
        p_d = ph.history(period="2d")
        if len(p_d) > 1:
            anlik = p_d['Close'].iloc[-1]
            onceki = p_d['Close'].iloc[-2]
            yuzde = ((anlik - onceki) / onceki) * 100
            
            st.write(f"**{p_hisse.split('.')[0]}**")
            color = "green" if yuzde >= 0 else "red"
            st.markdown(f"{anlik:.2f} TL | <span style='color:{color}'>%{yuzde:.2f}</span>", unsafe_allow_html=True)
            st.write("---")