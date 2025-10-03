# Canlı Futbol İstatistikleri Dashboard

Bu repo, canlı futbol maçlarının skorlarını ve oranlarını gösteren Streamlit uygulamasını içerir. Bu uygulama, [canli-worker](https://github.com/1sthillman/canli-worker) servisiyle birlikte çalışır.

## 📊 Özellikler

- **Canlı Maç İstatistikleri**: Anlık skorlar ve oran durumları
- **Filtre Seçenekleri**: Lig, oran durumu ve skor filtreleri
- **İstatistikler**: Grafiksel analizler
- **Veri İndirme**: CSV ve Excel formatlarında
- **Otomatik Güncelleme**: 10 saniyede bir

## 🔧 Kurulum

1. Gereksinimleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

2. Uygulamayı çalıştırın:
   ```bash
   streamlit run streamlit_app.py
   ```

## 🌐 Streamlit Cloud Deployment

Bu repo Streamlit Cloud'a bağlanarak otomatik olarak deploy edilebilir:

1. [Streamlit Cloud](https://streamlit.io/cloud)'a giriş yapın
2. "New app" butonuna tıklayın
3. GitHub repo olarak "1sthillman/canli-dash" seçin
4. Main file olarak "streamlit_app.py" yazın
5. "Deploy!" butonuna tıklayın

## 📋 Notlar

- Uygulama, verileri "https://canli-worker.onrender.com/canli.db" adresindeki SQLite veritabanından çeker.
- Bu reponun yanında çalışan bir [canli-worker](https://github.com/1sthillman/canli-worker) servisine ihtiyaç vardır.
