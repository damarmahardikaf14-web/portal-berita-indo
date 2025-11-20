import streamlit as st
import feedparser
from bs4 import BeautifulSoup
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Portal Berita Indonesia Terlengkap",
    page_icon="🇮🇩",
    layout="wide"
)

# --- CSS UNTUK TAMPILAN MODERN ---
st.markdown("""
<style>
    .card-container {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 20px;
        height: 100%;
        transition: transform 0.2s;
    }
    .card-container:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .news-title {
        font-weight: 700;
        font-size: 16px;
        margin-bottom: 8px;
        line-height: 1.4;
        color: #ffffff; 
    }
    .news-meta {
        font-size: 12px;
        color: #aaaaaa;
        margin-bottom: 10px;
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- DATABASE SUMBER BERITA (RSS) ---
# Kita kelompokkan berdasarkan Nama Media
NEWS_SOURCES = {
    "CNN Indonesia": {
        "Terbaru": "https://www.cnnindonesia.com/nasional/rss",
        "Ekonomi": "https://www.cnnindonesia.com/ekonomi/rss",
        "Olahraga": "https://www.cnnindonesia.com/olahraga/rss",
        "Teknologi": "https://www.cnnindonesia.com/teknologi/rss",
        "Hiburan": "https://www.cnnindonesia.com/hiburan/rss"
    },
    "Antara News": {
        "Terbaru": "https://www.antaranews.com/rss/terkini.xml",
        "Ekonomi": "https://www.antaranews.com/rss/ekonomi-bisnis.xml",
        "Dunia": "https://www.antaranews.com/rss/dunia.xml",
        "Olahraga": "https://www.antaranews.com/rss/olahraga.xml",
        "Tekno": "https://www.antaranews.com/rss/tekno.xml"
    },
    "CNBC Indonesia": {
        "Market": "https://www.cnbcindonesia.com/market/rss",
        "Investment": "https://www.cnbcindonesia.com/investment/rss",
        "News": "https://www.cnbcindonesia.com/news/rss",
        "Tech": "https://www.cnbcindonesia.com/tech/rss"
    },
    "Suara.com": {
        "Nasional": "https://www.suara.com/rss/news",
        "Bisnis": "https://www.suara.com/rss/bisnis",
        "Bola": "https://www.suara.com/rss/bola",
        "Tekno": "https://www.suara.com/rss/tekno"
    },
     "Okezone": {
        "Berita": "https://sindikasi.okezone.com/index.php/rss/0/RSS12",
        "Bola": "https://sindikasi.okezone.com/index.php/rss/0/RSS12",
        "Sports": "https://sindikasi.okezone.com/index.php/rss/0/RSS2",
        "Economy": "https://sindikasi.okezone.com/index.php/rss/0/RSS11"
    }
}

# --- FUNGSI PENCARI GAMBAR CERDAS ---
def extract_image(entry):
    """Mencoba mencari gambar dari berbagai kemungkinan tag RSS"""
    # 1. Cek media_content (Standar umum)
    if 'media_content' in entry:
        return entry.media_content[0]['url']
    
    # 2. Cek media_thumbnail
    if 'media_thumbnail' in entry:
        return entry.media_thumbnail[0]['url']

    # 3. Cek links (biasanya ada type image/jpeg)
    if 'links' in entry:
        for link in entry.links:
            if link.get('type', '').startswith('image/'):
                return link['href']
            if link.get('rel') == 'enclosure' and link.get('type', '').startswith('image/'):
                return link['href']

    # 4. Cek tag <img> di dalam deskripsi HTML (Scraping manual)
    if 'summary' in entry:
        soup = BeautifulSoup(entry.summary, 'html.parser')
        img = soup.find('img')
        if img and img.get('src'):
            return img['src']
            
    # 5. Gambar Default jika tidak ketemu
    return "https://via.placeholder.com/400x200.png?text=Berita+Indonesia"

# --- FUNGSI UTAMA PENGAMBIL BERITA ---
@st.cache_data(ttl=300) # Cache data selama 5 menit agar loading cepat
def fetch_news(rss_url):
    feed = feedparser.parse(rss_url)
    news_items = []
    
    for entry in feed.entries[:20]: # Ambil maksimal 20 berita
        image = extract_image(entry)
        
        # Bersihkan tanggal
        published = entry.get('published', 'Baru saja')
        # Potong tanggal jika terlalu panjang
        if len(published) > 20: 
             published = published[:25] + "..."

        news_items.append({
            "title": entry.title,
            "link": entry.link,
            "published": published,
            "image": image,
            "source": feed.feed.get('title', 'News Source')
        })
    return news_items

# --- SIDEBAR NAVIGASI ---
with st.sidebar:
    st.title("🌐 Sumber Berita")
    
    # 1. Pilih Media
    selected_provider = st.selectbox("Pilih Media:", list(NEWS_SOURCES.keys()))
    
    # 2. Pilih Kategori (Berubah sesuai media yang dipilih)
    categories = NEWS_SOURCES[selected_provider]
    selected_category = st.radio("Kategori:", list(categories.keys()))
    
    st.divider()
    st.info("Website ini menggabungkan RSS Feed dari berbagai media terpercaya di Indonesia.")
    
    if st.button("🔄 Refresh Berita"):
        st.cache_data.clear() # Hapus cache manual

# --- HALAMAN UTAMA ---
rss_link = NEWS_SOURCES[selected_provider][selected_category]

st.title(f"{selected_provider} - {selected_category}")
st.caption(f"Update terkini dari {rss_link}")

# Loading animation
with st.spinner('Sedang mengambil berita terbaru...'):
    try:
        news_data = fetch_news(rss_link)
        
        # TAMPILAN GRID (3 Kolom)
        cols = st.columns(3)
        
        for idx, item in enumerate(news_data):
            with cols[idx % 3]:
                # Card Container
                with st.container(border=True):
                    # Gambar
                    st.image(item['image'], use_column_width=True, output_format='JPEG')
                    
                    # Judul
                    st.markdown(f"<div class='news-title'>{item['title']}</div>", unsafe_allow_html=True)
                    
                    # Tanggal
                    st.markdown(f"<div class='news-meta'>🕒 {item['published']}</div>", unsafe_allow_html=True)
                    
                    # Tombol
                    st.link_button("Baca Selengkapnya 🔗", item['link'])
                    
    except Exception as e:
        st.error(f"Maaf, gagal memuat berita dari sumber ini. Error: {e}")

# --- FOOTER ---
st.markdown("---")
st.markdown(
    """
    <style>
    .footer {text-align: center; color: grey; font-size: small;}
    </style>
    <div class="footer">
    Developed with ❤️ using Python Streamlit | Aggregator Berita Indonesia
    </div>
    """, unsafe_allow_html=True
)
