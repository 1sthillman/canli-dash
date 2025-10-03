import streamlit as st
import pandas as pd
import sqlite3
import requests
import io
import plotly.express as px
import plotly.graph_objects as go
import datetime
import time

# Sayfa yapılandırması
st.set_page_config(
    page_title="Canlı Futbol İstatistikleri",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Başlık ve açıklama
st.title("⚽ Canlı Futbol İstatistikleri")
st.markdown("Bu uygulama, canlı futbol maçlarının skorlarını ve istatistiklerini gösterir.")

# Veritabanı URL'i
DB_URL = "https://canli-worker.onrender.com/canli.db"

@st.cache_data(ttl=10)  # 10 saniyede bir yenile
def load_data():
    """Veritabanını indir ve DF'e yükle"""
    try:
        r = requests.get(DB_URL, timeout=15)
        r.raise_for_status()  # HTTP hataları kontrol et
        
        with open("/tmp/canli.db", "wb") as f:
            f.write(r.content)
        
        conn = sqlite3.connect("/tmp/canli.db")
        
        # Maç bazlı en son durumlar
        query = """
        SELECT *, MAX(ts) as son_guncelleme
        FROM raw
        GROUP BY mac_id
        ORDER BY ts DESC
        """
        son_durum_df = pd.read_sql(query, conn)
        
        # Tüm kayıtlar
        tum_kayitlar_df = pd.read_sql("""
            SELECT * FROM raw 
            ORDER BY ts DESC 
            LIMIT 10000
        """, conn)
        
        return son_durum_df, tum_kayitlar_df
    except Exception as e:
        st.error(f"Veri yüklenirken hata oluştu: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

# Verileri yükle
with st.spinner("Veriler yükleniyor..."):
    son_durum_df, tum_kayitlar_df = load_data()

# Yenileme butonu
if st.button("🔄 Verileri Yenile"):
    st.cache_data.clear()
    son_durum_df, tum_kayitlar_df = load_data()
    st.success("Veriler yenilendi!")

# Veri yoksa hata mesajı göster
if son_durum_df.empty:
    st.warning("Veri bulunamadı. Lütfen daha sonra tekrar deneyin.")
    st.stop()

# Son güncelleme zamanı
son_guncelleme = pd.to_datetime(son_durum_df['ts'].max())
st.info(f"Son Güncelleme: {son_guncelleme.strftime('%d.%m.%Y %H:%M:%S')}")

# Ana içerik
tab1, tab2, tab3 = st.tabs(["📊 Canlı Maçlar", "📈 İstatistikler", "📋 Tüm Kayıtlar"])

with tab1:
    # Canlı maçlar
    st.subheader("📊 Canlı Maçlar")
    
    # Filtreler
    col1, col2, col3 = st.columns(3)
    with col1:
        ligler = ["Tümü"] + sorted(son_durum_df["lig"].unique().tolist())
        secili_lig = st.selectbox("Lig Filtresi:", ligler)
    
    with col2:
        oran_durum = ["Tümü", "AÇIK", "KAPALI"]
        secili_oran = st.selectbox("Oran Durumu:", oran_durum)
    
    with col3:
        skor_filtre = st.checkbox("Sadece Gollü Maçlar")
    
    # Filtreleri uygula
    filtered_df = son_durum_df.copy()
    
    if secili_lig != "Tümü":
        filtered_df = filtered_df[filtered_df["lig"] == secili_lig]
    
    if secili_oran != "Tümü":
        filtered_df = filtered_df[filtered_df["oran"] == secili_oran]
    
    if skor_filtre:
        filtered_df = filtered_df[~filtered_df["skor"].str.contains("0-0")]
    
    # Maç sonuçlarını göster
    if not filtered_df.empty:
        # Görüntülenecek sütunları ve başlıkları belirle
        display_cols = ["tarih", "saat", "lig", "ev", "skor", "dep", "dakika", "oran"]
        display_names = ["Tarih", "Saat", "Lig", "Ev Sahibi", "Skor", "Deplasman", "Dakika", "Oran"]
        
        # Streamlit dataframe göster
        st.dataframe(
            filtered_df[display_cols].rename(columns=dict(zip(display_cols, display_names))),
            use_container_width=True,
            hide_index=True,
        )
        
        # Excel/CSV indirme
        col1, col2 = st.columns(2)
        with col1:
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 CSV İndir", data=csv, file_name=f"canli_futbol_{datetime.date.today()}.csv")
        with col2:
            excel_buffer = io.BytesIO()
            filtered_df.to_excel(excel_buffer, index=False)
            excel_data = excel_buffer.getvalue()
            st.download_button("📥 Excel İndir", data=excel_data, file_name=f"canli_futbol_{datetime.date.today()}.xlsx")
    else:
        st.warning("Filtrelenmiş veri bulunamadı.")

with tab2:
    st.subheader("📈 İstatistikler")
    
    # İstatistikler
    col1, col2 = st.columns(2)
    
    with col1:
        # Lig bazında maç sayısı
        lig_counts = son_durum_df["lig"].value_counts().reset_index()
        lig_counts.columns = ["Lig", "Maç Sayısı"]
        
        fig_lig = px.bar(
            lig_counts,
            x="Lig",
            y="Maç Sayısı",
            title="Lig Bazında Canlı Maç Sayısı",
            color="Maç Sayısı",
            color_continuous_scale="Viridis",
        )
        st.plotly_chart(fig_lig)
        
    with col2:
        # Oran durumuna göre maç sayısı
        oran_counts = son_durum_df["oran"].value_counts().reset_index()
        oran_counts.columns = ["Oran Durumu", "Maç Sayısı"]
        
        fig_oran = px.pie(
            oran_counts,
            values="Maç Sayısı",
            names="Oran Durumu",
            title="Oran Durumuna Göre Maç Dağılımı",
            color_discrete_sequence=px.colors.sequential.Viridis,
        )
        st.plotly_chart(fig_oran)
    
    # Skor dağılımı
    st.subheader("Skor Dağılımı")
    skor_counts = son_durum_df["skor"].value_counts().reset_index().head(10)
    skor_counts.columns = ["Skor", "Maç Sayısı"]
    
    fig_skor = px.bar(
        skor_counts,
        x="Skor",
        y="Maç Sayısı",
        title="En Sık Görülen Skorlar (İlk 10)",
        color="Maç Sayısı",
        color_continuous_scale="Viridis",
    )
    st.plotly_chart(fig_skor)

with tab3:
    st.subheader("📋 Tüm Kayıtlar")
    
    # Tarih filtresi
    tarih_min = pd.to_datetime(tum_kayitlar_df["ts"]).min().date()
    tarih_max = pd.to_datetime(tum_kayitlar_df["ts"]).max().date()
    
    secili_tarih = st.date_input(
        "Tarih Filtresi:",
        value=tarih_max,
        min_value=tarih_min,
        max_value=tarih_max
    )
    
    # Tarihe göre filtrele
    filtered_history = tum_kayitlar_df[pd.to_datetime(tum_kayitlar_df["ts"]).dt.date == secili_tarih]
    
    # Sonuçları göster
    if not filtered_history.empty:
        st.dataframe(filtered_history, use_container_width=True)
        
        # Toplam kayıt sayısı
        st.info(f"Toplam {len(filtered_history)} kayıt bulundu.")
        
        # İndirme butonu
        csv = filtered_history.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Tüm Kayıtları İndir (CSV)", data=csv, file_name=f"tum_kayitlar_{secili_tarih}.csv")
    else:
        st.warning(f"{secili_tarih} tarihine ait kayıt bulunamadı.")

# Footer
st.markdown("---")
st.markdown("📊 **Canlı Futbol İstatistikleri** | Render + Streamlit | Güncel veri")
