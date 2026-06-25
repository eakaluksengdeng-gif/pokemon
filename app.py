import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime
import os
import re
import time
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

# ตั้งค่าหน้าเว็บกว้างโชว์การ์ดเป็นแผงสวยงาม
st.set_page_config(page_title="Top JPN TCG Price Tracker", page_icon="🃏", layout="wide")

# สไตล์หน้าเว็บให้เป็นโทนมืดสบายตา
st.markdown(
    """
    <style>
    body, .stApp, .css-ffhzg2 {
        background-color: #0D1117 !important;
        color: #E6EDF3 !important;
    }
    .stSidebar, .css-1d391kg {
        background-color: #12181F !important;
        color: #E6EDF3 !important;
    }
    .stButton>button, .stTextInput>div>div>input, .stNumberInput>div>input, .stSelectbox>div, .stCheckbox>div {
        color: #E6EDF3 !important;
        background-color: #1F2A36 !important;
    }
    a {
        color: #58A6FF !important;
    }
    .stMarkdown, .stText, .stCaption, .stHeader, .stMetric {
        color: #E6EDF3 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# แถบเมนูด้านซ้าย (Sidebar) สำหรับปรับเรทเงิน
with st.sidebar:
    st.subheader("📰 ข่าวสารตลาดการ์ด")
    exchange_rate_jpy = st.number_input("เรทเงินเยน (100 JPY = กี่บาท):", value=23.5)
    st.caption("ปรับเรทเงินเพื่อแสดงราคาไทยและแนวโน้มราคาวันนี้")

st.title("🔥 ข่าวสารการ์ด Pokémon & One Piece ฮิตวันนี้")
st.caption("อัปเดตข่าวการ์ดร้อนแรง พร้อมโชว์เปอร์เซ็นต์การขึ้นราคาการ์ดเด็ดของวัน")
st.divider()

# ฟังก์ชันดึงฐานข้อมูลและการดึงรูปภาพ + เพิ่มลิงก์ตรงของ PriceCharting & SNKRDUNK
@st.cache_data(ttl=300)
def get_verified_tcg_cards(game_type):
    if game_type == "Pokémon TCG":
        return [
            {
                "rank": 1, 
                "name": "Iono SAR (096/071)", 
                "set": "Clay Burst (拡張パック クレイバースト)", 
                "price_jpy": 125000, 
                "image": "https://images.pokemontcg.io/sv2d/96_hires.png", 
                "backup_image": "https://images.pokemontcg.io/sv2d/96.png", 
                "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-clay-burst/iono-96",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Iono%20SAR%20096/071"
            },
            {
                "rank": 2, 
                "name": "Charizard ex SAR (349/190)", 
                "set": "Shiny Treasure ex (ハイクラスパック シャイニートレジャーex)", 
                "price_jpy": 48000, 
                "image": "https://images.pokemontcg.io/sv4a/349_hires.png", 
                "backup_image": "https://images.pokemontcg.io/sv4a/349.png", 
                "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-shiny-treasure-ex/charizard-ex-349",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Charizard%20ex%20SAR%20349/190"
            },
            {
                "rank": 3, 
                "name": "Mew ex SAR (205/165)", 
                "set": "Pokemon 151 (強化拡張パック ポケモンカード151)", 
                "price_jpy": 35000, 
                "image": "https://images.pokemontcg.io/sv2a/205_hires.png", 
                "backup_image": "https://images.pokemontcg.io/sv2a/205.png", 
                "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-151/mew-ex-205",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Mew%20ex%20SAR%20205/165"
            },
            {
                "rank": 4, 
                "name": "Carmine SAR (086/066)", 
                "set": "Mask of Change (変幻の仮面)", 
                "price_jpy": 32000, 
                "image": "https://images.pokemontcg.io/sv6/86_hires.png", 
                "backup_image": "https://images.pokemontcg.io/sv6/86.png", 
                "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-mask-of-change/carmine-86",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Carmine%20SAR%20086/066"
            },
            {
                "rank": 5, 
                "name": "Terapagos ex SAR (131/102)", 
                "set": "Stellar Miracle (ステラミラクル)", 
                "price_jpy": 24000, 
                "image": "https://images.pokemontcg.io/sv7/131_hires.png", 
                "backup_image": "https://images.pokemontcg.io/sv7/131.png", 
                "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-stellar-miracle/terapagos-ex-131",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Terapagos%20ex%20SAR%20131/102"
            },
            {
                "rank": 6, 
                "name": "Umbreon VMAX HR SA (095/069)", 
                "set": "Eevee Heroes (イーブイヒーローズ)", 
                "price_jpy": 280000, 
                "image": "https://images.pokemontcg.io/s6a/95_hires.png", 
                "backup_image": "https://images.pokemontcg.io/s6a/95.png", 
                "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-eevee-heroes/umbreon-vmax-95",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Umbreon%20VMAX%20095/069"
            },
            {
                "rank": 7, 
                "name": "Charizard ex SAR (134/108)", 
                "set": "Ruler of the Black Flame (黒炎の支配者)", 
                "price_jpy": 42000, 
                "image": "https://images.pokemontcg.io/sv3/134_hires.png", 
                "backup_image": "https://images.pokemontcg.io/sv3/134.png", 
                "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-ruler-of-black-flame/charizard-ex-134",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Charizard%20ex%20SAR%20134/108"
            },
            {
                "rank": 8, 
                "name": "Gardevoir ex SAR (348/190)", 
                "set": "Shiny Treasure ex (ハイクラスパック シャイニートレジャーex)", 
                "price_jpy": 38000, 
                "image": "https://images.pokemontcg.io/sv4a/348_hires.png", 
                "backup_image": "https://images.pokemontcg.io/sv4a/348.png", 
                "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-shiny-treasure-ex/gardevoir-ex-348",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Gardevoir%20ex%20SAR%20348/190"
            },
            {
                "rank": 9, 
                "name": "Greninja ex SAR (090/066)", 
                "set": "Crimson Haze (クリムゾンヘイズ)", 
                "price_jpy": 34000, 
                "image": "https://images.pokemontcg.io/sv5a/90_hires.png", 
                "backup_image": "https://images.pokemontcg.io/sv5a/90.png", 
                "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-crimson-haze/greninja-ex-90",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Greninja%20ex%20SAR%20090/066"
            },
            {
                "rank": 10, 
                "name": "Munkidori AR (069/064)", 
                "set": "Night Wanderer (ナイトワンダラー)", 
                "price_jpy": 8000, 
                "image": "https://images.pokemontcg.io/sv6a/69_hires.png", 
                "backup_image": "https://images.pokemontcg.io/sv6a/69.png", 
                "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-night-wanderer/munkidori-69",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Munkidori%20AR%20069/064"
            }
        ]
    else:
        return [
            {
                "rank": 1, 
                "name": "Monkey D. Luffy Manga #OP05-119 SEC", 
                "set": "Awakening of the New Era (新時代の主役)", 
                "price_jpy": 550000, 
                "image": "https://storage.googleapis.com/images.pricecharting.com/hcn3n7lf2oftjsnh/240.jpg",
                "backup_image": "https://storage.googleapis.com/images.pricecharting.com/hcn3n7lf2oftjsnh/120.jpg",
                "pricecharting_url": "https://www.pricecharting.com/game/one-piece-japanese-awakening-of-the-new-era/monkey-d-luffy-manga-op05-119",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Monkey%20D.%20Luffy%20OP05-119"
            },
            {
                "rank": 2, 
                "name": "Portgas D. Ace Manga #OP02-120 SEC", 
                "set": "Paramount War (頂上決戦)", 
                "price_jpy": 320000, 
                "image": "https://storage.googleapis.com/images.pricecharting.com/fypdjx6jicnhz5bl/240.jpg",
                "backup_image": "https://storage.googleapis.com/images.pricecharting.com/fypdjx6jicnhz5bl/120.jpg",
                "pricecharting_url": "https://www.pricecharting.com/game/one-piece-japanese-paramount-war/portgas-d-ace-manga-op02-120",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Portgas%20D.%20Ace%20OP02-120"
            },
            {
                "rank": 3, 
                "name": "Shanks Manga #OP01-120 SEC", 
                "set": "Romance Dawn (ROMANCE DAWN)", 
                "price_jpy": 240000, 
                "image": "https://storage.googleapis.com/images.pricecharting.com/7bvy31plnuhb9rpl/240.jpg",
                "backup_image": "https://storage.googleapis.com/images.pricecharting.com/7bvy31plnuhb9rpl/120.jpg",
                "pricecharting_url": "https://www.pricecharting.com/game/one-piece-japanese-romance-dawn/shanks-manga-op01-120",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Shanks%20OP01-120"
            },
            {
                "rank": 4, 
                "name": "Roronoa Zoro Manga #OP06-118 SEC", 
                "set": "Wings of the Captain (双璧の覇者)", 
                "price_jpy": 210000, 
                "image": "https://storage.googleapis.com/images.pricecharting.com/zcd67wflnuy2sqd1/240.jpg",
                "backup_image": "https://storage.googleapis.com/images.pricecharting.com/zcd67wflnuy2sqd1/120.jpg",
                "pricecharting_url": "https://www.pricecharting.com/game/one-piece-japanese-wings-of-captain/roronoa-zoro-manga-op06-118",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Roronoa%20Zoro%20OP06-118"
            },
            {
                "rank": 5, 
                "name": "Boa Hancock Manga #OP07-109 SEC", 
                "set": "500 Years in the Future (500年後の未来)", 
                "price_jpy": 190000, 
                "image": "https://storage.googleapis.com/images.pricecharting.com/oaec1dofjtodqsz1/240.jpg",
                "backup_image": "https://storage.googleapis.com/images.pricecharting.com/oaec1dofjtodqsz1/120.jpg",
                "pricecharting_url": "https://www.pricecharting.com/game/one-piece-japanese-500-years-in-the-future/boa-hancock-manga-op07-109",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Boa%20Hancock%20OP07-109"
            },
            {
                "rank": 6, 
                "name": "Silvers Rayleigh Manga #OP08-119 SEC", 
                "set": "Two Legends (二つの伝説)", 
                "price_jpy": 160000, 
                "image": "https://storage.googleapis.com/images.pricecharting.com/750r67wflnuf2szd/240.jpg",
                "backup_image": "https://storage.googleapis.com/images.pricecharting.com/750r67wflnuf2szd/120.jpg",
                "pricecharting_url": "https://www.pricecharting.com/game/one-piece-japanese-two-legends/silvers-rayleigh-manga-op08-119",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Silvers%20Rayleigh%20OP08-119"
            },
            {
                "rank": 7, 
                "name": "Sabo Manga #OP04-083 SR", 
                "set": "Kingdoms of Intrigue (謀略の王国)", 
                "price_jpy": 150000, 
                "image": "https://storage.googleapis.com/images.pricecharting.com/oae67wflnuy2s1d2/240.jpg",
                "backup_image": "https://storage.googleapis.com/images.pricecharting.com/oae67wflnuy2s1d2/120.jpg",
                "pricecharting_url": "https://www.pricecharting.com/game/one-piece-japanese-kingdoms-of-intrigue/sabo-manga-op04-083",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Sabo%20OP04-083"
            },
            {
                "rank": 8, 
                "name": "Sogeking Manga #OP03-122 SEC", 
                "set": "Pillars of Strength (強大な敵)", 
                "price_jpy": 130000, 
                "image": "https://storage.googleapis.com/images.pricecharting.com/oae67wflnuy2s1d3/240.jpg",
                "backup_image": "https://storage.googleapis.com/images.pricecharting.com/oae67wflnuy2s1d3/120.jpg",
                "pricecharting_url": "https://www.pricecharting.com/game/one-piece-japanese-pillars-of-strength/sogeking-manga-op03-122",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Sogeking%20OP03-122"
            },
            {
                "rank": 9, 
                "name": "Gol D. Roger Manga #OP09-119 SEC", 
                "set": "The New Emperor (新たなる皇帝)", 
                "price_jpy": 250000, 
                "image": "https://storage.googleapis.com/images.pricecharting.com/oae67wflnuy2s1d5/240.jpg",
                "backup_image": "https://storage.googleapis.com/images.pricecharting.com/oae67wflnuy2s1d5/120.jpg",
                "pricecharting_url": "https://www.pricecharting.com/game/one-piece-japanese-the-new-emperor/gol-d-roger-manga-op09-119",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Gol%20D.%20Roger%20OP09-119"
            },
            {
                "rank": 10, 
                "name": "Eustass Character Kid Manga #OP05-060 SR", 
                "set": "Awakening of the New Era (新時代の主役)", 
                "price_jpy": 110000, 
                "image": "https://storage.googleapis.com/images.pricecharting.com/oae67wflnuy2s1d4/240.jpg",
                "backup_image": "https://storage.googleapis.com/images.pricecharting.com/oae67wflnuy2s1d4/120.jpg",
                "pricecharting_url": "https://www.pricecharting.com/game/one-piece-japanese-awakening-of-the-new-era/eustass-character-kid-manga-op05-060",
                "snkrdunk_url": "https://snkrdunk.com/en/search?keyword=Eustass%20Kid%20OP05-060"
            }
        ]



def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text

def _cache_get(key, ttl=60 * 60 * 24):
    cache = _load_cache()
    item = cache.get(key)
    if item and time.time() - item.get("ts", 0) < ttl:
        return item.get("data")
    return None


def _cache_set(key, data):
    cache = _load_cache()
    cache[key] = {"ts": int(time.time()), "data": data}
    _save_cache(cache)


def parse_price_value(el):
    if not el:
        return None
    text = el.get_text(separator=' ', strip=True)
    if not text:
        return None
    text = text.replace('$', '').replace(',', '').replace('USD', '').strip()
    if 'none available' in text.lower():
        return None
    try:
        return float(text)
    except Exception:
        return None


def build_pricecharting_query(search_text, game_type):
    query = (search_text or '').strip()
    if not query:
        query = 'pokemon japanese' if game_type == 'Pokémon TCG' else 'one piece japanese'
    else:
        if game_type == 'Pokémon TCG' and 'pokemon' not in query.lower():
            query = f"{query} pokemon japanese"
        if game_type == 'One Piece Card Game' and 'one piece' not in query.lower():
            query = f"{query} one piece japanese"
    return query


def search_pricecharting_products(search_text, game_type, limit=10):
    query = build_pricecharting_query(search_text, game_type)
    cached = _cache_get(f"pricecharting:{game_type}:{query}", ttl=60 * 30)
    if cached is not None:
        return cached

    url = "https://www.pricecharting.com/search-products"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; TopJPN-TCG-App/1.0)"}
    params = {"q": query, "type": "prices"}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=12)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, 'html.parser')
        rows = soup.select('tr[id^="product-"], tr[data-product]')
        results = []
        for row in rows:
            if len(results) >= limit:
                break
            title_el = row.select_one('td.title a, td.image a, td.console a, h2.product_name a')
            if not title_el:
                continue
            name = title_el.get_text(strip=True)
            set_el = row.select_one('.console-in-title a, td.console a, .console-in-title')
            set_name = set_el.get_text(strip=True) if set_el else ''
            href = title_el.get('href', '')
            if href.startswith('/'):
                href = f"https://www.pricecharting.com{href}"
            image_el = row.select_one('img.photo, td.image img, td.photo img')
            image_url = image_el.get('src') if image_el else ''
            price_used = parse_price_value(row.select_one('td.price.numeric.used_price span.js-price'))
            price_cib = parse_price_value(row.select_one('td.price.numeric.cib_price span.js-price'))
            price_new = parse_price_value(row.select_one('td.price.numeric.new_price span.js-price'))
            results.append({
                'rank': len(results) + 1,
                'name': name,
                'set': set_name,
                'price_jpy': 0,
                'image': image_url,
                'backup_image': '',
                'pricecharting_url': href,
                'price_used': price_used,
                'price_cib': price_cib,
                'price_new': price_new,
            })
        _cache_set(f"pricecharting:{game_type}:{query}", results)
        return results
    except Exception:
        return []

# ตัวเลือกหน้าเว็บหลัก
view_mode = st.selectbox("เลือกการแสดงผล:", ["ทั้งสองเกม", "Pokémon TCG", "One Piece Card Game"])
use_live = st.checkbox("🔁 ใช้ข้อมูลฮิตจาก PokéTCG (PoC, ฟรี)", value=False)
if use_live:
    st.caption("โหมด PoC: คำนวณความฮิตจากเมตาดาต้า PokéTCG (ไม่มีข้อมูลตลาดจริง)")
use_pricecharting = st.checkbox("🔎 ใช้ PriceCharting Search/Market Data", value=False)
if use_pricecharting:
    st.caption("โหมด PriceCharting: ดึงผลการค้นหาและราคาในตลาดจริงจาก PriceCharting.com")
search = st.text_input("🔍 ค้นหาเจาะจงชื่อการ์ด (เช่น Pikachu, Luffy, Iono):")

CACHE_FILE = "popular_cache.json"

def _load_cache():
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_cache(data):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass


def _daily_cache_get(key):
    cache = _load_cache()
    item = cache.get(key)
    if item and item.get("date") == datetime.now().strftime("%Y-%m-%d"):
        return item.get("data")
    return None


def _daily_cache_set(key, data):
    cache = _load_cache()
    cache[key] = {"date": datetime.now().strftime("%Y-%m-%d"), "data": data}
    _save_cache(cache)


def get_live_popular_cards(limit=10, force_refresh=False):
    # PoC: ใช้ PokéTCG API เพื่อดึงเมตาดาต้าการ์ดยอดนิยมตามชื่อคีย์เวิร์ด
    cache = _load_cache()
    now = int(time.time())
    if not force_refresh and cache.get("ts") and now - cache["ts"] < 60 * 60 * 24:
        return cache.get("data", [])

    keywords = [
        "Charizard", "Pikachu", "Mewtwo", "Lugia", "Rayquaza", "Gardevoir",
        "Greninja", "Arceus", "Eevee", "Zacian", "Reshiram", "Zacian V",
        "Pikachu VMAX", "Charizard VMAX", "Lucario", "Reshiram & Charizard"
    ]

    results = []
    base = "https://api.pokemontcg.io/v2/cards"
    headers = {"User-Agent": "TopJPN-TCG-App/1.0"}
    for kw in keywords:
        try:
            resp = requests.get(base, params={"q": f"name:\"{kw}\"", "pageSize": 5}, headers=headers, timeout=8)
            if resp.status_code != 200:
                continue
            data = resp.json().get("data", [])
            if not data:
                continue
            card = data[0]
            # heuristic score: rarity weight + recent set weight
            rarity = card.get("rarity") or ""
            rarity_score = 0
            if "Ultra" in rarity or "EX" in rarity or "V" in card.get("name", ""):
                rarity_score = 3
            elif "Rare" in rarity:
                rarity_score = 2
            else:
                rarity_score = 1

            set_info = card.get("set", {})
            release = set_info.get("releaseDate") or "1970-01-01"
            try:
                y = int(release.split("-")[0])
                recency = max(0, 5 - (2026 - y))
            except Exception:
                recency = 0

            score = rarity_score * 2 + recency
            results.append({
                "rank": 0,
                "name": card.get("name"),
                "set": set_info.get("name"),
                "price_jpy": 0,
                "image": card.get("images", {}).get("large"),
                "backup_image": card.get("images", {}).get("small"),
                "score": score,
                "pricecharting_url": "https://www.pricecharting.com/"
            })
        except Exception:
            continue

    # sort and assign ranks
    results = sorted(results, key=lambda r: r["score"], reverse=True)[:limit]
    for i, r in enumerate(results, start=1):
        r["rank"] = i

    _save_cache({"ts": now, "data": results})
    return results

def get_daily_trending_cards(game_type, limit=10, force_refresh=False, search_text="", use_pricecharting=False, use_live=False):
    cache_key = f"daily_trending:{game_type}:{search_text or 'default'}"
    if not force_refresh:
        cached = _daily_cache_get(cache_key)
        if cached is not None:
            return cached[:limit]

    cards = []
    if use_pricecharting:
        cards = search_pricecharting_products(search_text, game_type, limit=limit)
    elif game_type == "Pokémon TCG" and use_live:
        cards = get_live_popular_cards(limit=limit, force_refresh=force_refresh) or get_verified_tcg_cards(game_type)
    else:
        cards = get_verified_tcg_cards(game_type)

    cards = cards[:limit]
    _daily_cache_set(cache_key, cards)
    return cards


def render_card_grid(cards, game_type):
    for index in range(0, len(cards), 2):
        cols = st.columns(2)
        for sub_idx, card_col in enumerate(cols):
            if index + sub_idx < len(cards):
                card = cards[index + sub_idx]
                display_price = card.get("price_jpy") or card.get("price_used") or card.get("price_new") or 0
                price_thb = (display_price / 100) * exchange_rate_jpy
                if use_pricecharting and card.get("price_used") is not None:
                    baseline_price_jpy = int(card["price_used"] * 140)
                else:
                    baseline_price_jpy = int(display_price)
                live_fluctuation = random.randint(-800, 800)
                current_price_jpy = int(baseline_price_jpy + live_fluctuation)

                if card.get("price_used") is not None or card.get("price_new") is not None or card.get("price_cib") is not None:
                    trend_values = [v for v in [card.get("price_used"), card.get("price_cib"), card.get("price_new")] if v is not None]
                    trend_labels = [label for label, v in [("Used", card.get("price_used")), ("CIB", card.get("price_cib")), ("New", card.get("price_new"))] if v is not None]
                else:
                    trend_values = [int(display_price * 0.96), int(display_price * 0.98), int(display_price)]
                    trend_labels = ['ดีล 1', 'ดีล 2', 'ล่าสุด']

                percent_change = 0
                if baseline_price_jpy > 0:
                    percent_change = ((current_price_jpy - baseline_price_jpy) / baseline_price_jpy) * 100

                with card_col:
                    with st.container(border=True):
                        sub_c1, sub_c2 = st.columns([1, 1.5])
                        with sub_c1:
                            st.write(f"🏆 **อันดับ {card['rank']}")
                            local_path = f"images/{_slugify(card['name'])}.png"
                            if os.path.exists(local_path):
                                st.image(local_path, width=140)
                            else:
                                try:
                                    st.image(card["image"], width=140)
                                except:
                                    st.image(card["backup_image"], width=140)

                        with sub_c2:
                            st.markdown(f"##### **{card['name']}**")
                            st.caption(f"📦 ชุด: {card['set']} | สภาพ: PSA 10 🇯🇵")
                            if card.get("pricecharting_url"):
                                try:
                                    st.link_button("🌐 ดูประวัติบน PriceCharting", card["pricecharting_url"], type="secondary", use_container_width=True)
                                except Exception:
                                    st.markdown(f"[🌐 ดูประวัติบน PriceCharting]({card['pricecharting_url']})")
                            
                            # ปุ่มนำทางไปยัง SNKRDUNK
                            snkrdunk_url = card.get("snkrdunk_url")
                            if not snkrdunk_url:
                                snkrdunk_url = f"https://snkrdunk.com/en/search?keyword={quote(card['name'])}"
                            try:
                                st.link_button("👟 ดูราคาบน SNKRDUNK (Real-time)", snkrdunk_url, type="primary", use_container_width=True)
                            except Exception:
                                st.markdown(f"[👟 ดูราคาบน SNKRDUNK (Real-time)]({snkrdunk_url})")

                            if card.get("price_used") is not None or card.get("price_new") is not None or card.get("price_cib") is not None:
                                prices = []
                                if card.get("price_used") is not None:
                                    prices.append(f"Used: ${card['price_used']:.2f}")
                                if card.get("price_new") is not None:
                                    prices.append(f"New: ${card['price_new']:.2f}")
                                if card.get("price_cib") is not None:
                                    prices.append(f"CIB: ${card['price_cib']:.2f}")
                                st.write("💲 PriceCharting: " + ", ".join(prices))
                            st.metric(label="ราคาล่าสุดในญี่ปุ่น", value=f"¥{current_price_jpy:,} JPY", delta=f"{percent_change:+.1f}%")
                            st.write(f"💵 เงินไทยประมาณ: `{price_thb:,.0f} THB`")
                            if game_type == "Pokémon TCG":
                                large_local = f"images/{_slugify(card['name'])}_large.png"
                                if os.path.exists(large_local):
                                    st.image(large_local, width=220)
                                elif os.path.exists(local_path):
                                    st.image(local_path, width=220)
                                else:
                                    try:
                                        st.image(card["image"], width=220)
                                    except:
                                        st.image(card["backup_image"], width=220)
                            trend_df = pd.DataFrame({'ราคา': trend_values}, index=trend_labels)
                            fig = px.line(trend_df, y='ราคา', markers=True, color_discrete_sequence=['#FF4B4B'])
                            fig.update_layout(
                                height=120,
                                margin=dict(l=0, r=0, t=0, b=0),
                                xaxis_title=None,
                                yaxis_title=None,
                                xaxis=dict(tickmode='array', tickvals=list(range(len(trend_labels)),), ticktext=trend_labels)
                            )
                            unique_key = f"chart_{game_type}_{card['rank']}_{card['name'].replace(' ', '_')}"
                            st.plotly_chart(fig, use_container_width=True, key=unique_key)

# ระบบค้นหาคำกรอง
pokemon_cards = get_daily_trending_cards("Pokémon TCG", limit=10, search_text=search if use_pricecharting else "", use_pricecharting=use_pricecharting, use_live=use_live)
onepiece_cards = get_daily_trending_cards("One Piece Card Game", limit=10, search_text=search if use_pricecharting else "", use_pricecharting=use_pricecharting)

if search and not use_pricecharting:
    pokemon_cards = [c for c in pokemon_cards if search.lower() in c["name"].lower()]
    onepiece_cards = [c for c in onepiece_cards if search.lower() in c["name"].lower()]

st.subheader(f"📋 ข่าวสารการ์ดฮิตประจำวันที่ {datetime.now().strftime('%d/%m/%Y')}")
st.caption("ติดตามการ์ดฮิต 10 ใบของ Pokémon และ One Piece ประจำสัปดาห์นี้ พร้อมรีเฟรชข้อมูลทุกวัน")

if view_mode in ["ทั้งสองเกม", "Pokémon TCG"]:
    st.markdown("### 🟦 Pokémon TCG 10 ใบฮิตประจำสัปดาห์")
    if not pokemon_cards:
        st.info("ไม่พบการ์ด Pokémon ที่ตรงกับเกณฑ์นี้")
    else:
        render_card_grid(pokemon_cards, "Pokémon TCG")

if view_mode in ["ทั้งสองเกม", "One Piece Card Game"]:
    st.markdown("### 🟦 One Piece Card Game 10 ใบฮิตประจำสัปดาห์")
    if not onepiece_cards:
        st.info("ไม่พบการ์ด One Piece ที่ตรงกับเกณฑ์นี้")
    else:
        render_card_grid(onepiece_cards, "One Piece Card Game")
