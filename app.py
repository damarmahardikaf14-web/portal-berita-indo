import streamlit as st
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Berita Indonesia Live",
    page_icon="🇮🇩",
    layout="wide"
)

# --- CSS KHUSUS AGAR TAMPILAN LEBIH CANTIK ---
st.markdown("""
<style>
    .card-img {border-radius: 10px; margin-bottom: 10px;}
    .title-text {font-weight: bold; font-size: 18px; margin-bottom: 5px;}
    .date-text {font-size: 12px; color: #666;}
</style>
""", unsafe_allow_html=True)

# --- SUMBER BERITA (RSS CNN INDONESIA) ---
RSS_FEEDS = {
    "Nasional": "https://www.cnnindonesia.com/nasional/rss",
    "Ekonomi": "https://www.cnnindonesia.com/ekonomi/rss",
    "Olahraga": "https://www.cnnindonesia.com/olahraga/rss",
    "Teknologi": "https://www.cnnindonesia.com/teknologi/rss",
    "Hiburan": "https://www.cnnindonesia.com/hiburan/rss",
    "Gaya Hidup": "https://www.cnnindonesia.com/gaya-hidup/rss"
}

# --- FUNGSI PARSING BERITA ---
def get_news(category):
    url = RSS_FEEDS.get(category)
    feed = feedparser.parse(url)
    articles = []
    
    for entry in feed.entries:
        # Coba ambil gambar dari berbagai kemungkinan field RSS
        image_url = ""
        if 'media_content' in entry:
            image_url = entry.media_content[0]['url']
        elif 'links' in entry:
            for link in entry.links:
                if link.get('type', '').startswith('image/'):
                    image_url = link['href']
                    break
        
        # Jika gambar ada di dalam deskripsi HTML
        if not image_url and 'summary' in entry:
            soup = BeautifulSoup(entry.summary, 'html.parser')
            img_tag = soup.find('img')
            if img_tag:
                image_url = img_tag['src']

        # Bersihkan tanggal publish
        published = entry.get('published', 'Baru saja')
        
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "published": published,
            "image": image_url,
            "summary": entry.summary
        })
    return articles

# --- SIDEBAR ---
with st.sidebar:
    st.header("📰 Kanal Berita")
    selected_category = st.radio("Pilih Topik:", list(RSS_FEEDS.keys()))
    st.markdown("---")
    st.caption("Sumber: CNN Indonesia RSS")
    st.caption("Develop by Python Streamlit")

# --- HALAMAN UTAMA ---
st.title(f"🇮🇩 Berita Terkini: {selected_category}")
st.markdown("Update langsung secara *real-time*.")
st.divider()

# Ambil Berita
news_items = get_news(selected_category)

# Tampilkan dalam Grid
if news_items:
    # Buat layout 3 kolom
    cols = st.columns(3)
    
    for idx, item in enumerate(news_items):
        with cols[idx % 3]:
            with st.container(border=True):
                # Tampilkan Gambar jika ada
                if item['image']:
                    st.image(item['image'], use_column_width=True)
                
                # Judul Berita
                st.markdown(f"<div class='title-text'>{item['title']}</div>", unsafe_allow_html=True)
                
                # Tanggal
                st.markdown(f"<div class='date-text'>📅 {item['published']}</div>", unsafe_allow_html=True)
                
                # Tombol Baca
                st.link_button("Baca Selengkapnya 🔗", item['link'])
else:
    st.error("Gagal memuat berita. Cek koneksi internet.")

# --- FOOTER ---
st.markdown("---")
st.markdown("<center>Dibuat dengan ❤️ menggunakan Python</center>", unsafe_allow_html=True)
