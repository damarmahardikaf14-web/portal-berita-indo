import streamlit as st
import requests
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Berita Indonesia Terkini",
    page_icon="📰",
    layout="wide"
)

# --- API KEY & URL ---
# Ganti tulisan di bawah dengan API Key Anda dari NewsAPI.org
API_KEY = 'MASUKKAN_API_KEY_ANDA_DISINI' 
BASE_URL = "https://newsapi.org/v2/top-headlines"

# --- FUNGSI MENGAMBIL BERITA ---
def get_news(category='general'):
    params = {
        'country': 'id',  # Fokus berita Indonesia
        'category': category,
        'apiKey': API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status() # Cek jika ada error koneksi
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mengambil berita: {e}")
        return None

# --- UI UTAMA ---
st.title("🇮🇩 Portal Berita Indonesia")
st.markdown("Update berita terkini langsung dari sumber terpercaya.")

# --- SIDEBAR (KATEGORI) ---
with st.sidebar:
    st.header("Kategori Berita")
    category = st.selectbox(
        "Pilih Topik:",
        ('general', 'business', 'entertainment', 'health', 'science', 'sports', 'technology')
    )
    st.info("Dibuat dengan Python & Streamlit")

# --- LOGIKA TAMPILAN ---
news_data = get_news(category)

if news_data and news_data['status'] == 'ok':
    articles = news_data['articles']
    
    # Layout Grid (3 kolom)
    cols = st.columns(3)
    
    for index, article in enumerate(articles):
        # Filter: Hanya tampilkan jika ada gambar dan deskripsi agar rapi
        if article['urlToImage'] and article['description']:
            with cols[index % 3]:
                with st.container(border=True):
                    # Gambar Berita
                    st.image(article['urlToImage'], use_column_width=True)
                    
                    # Judul
                    st.subheader(article['title'])
                    
                    # Sumber & Waktu
                    pub_date = datetime.strptime(article['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
                    st.caption(f"Sumber: {article['source']['name']} | {pub_date.strftime('%d-%m-%Y %H:%M')}")
                    
                    # Deskripsi
                    st.write(article['description'])
                    
                    # Tombol Baca Selengkapnya
                    st.link_button("Baca Selengkapnya", article['url'])
else:
    st.warning("Tidak ada berita ditemukan atau API Key salah.")

# --- FOOTER ---
st.markdown("---")
st.markdown("<center>Copyright © 2024 - Portal Berita Python</center>", unsafe_allow_html=True)
