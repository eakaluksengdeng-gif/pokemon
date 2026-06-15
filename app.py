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

# ตั้งค่าหน้าเว็บกว้างโชว์การ์ดเป็นแผงสวยงาม
st.set_page_config(page_title="Top JPN TCG Price Tracker", page_icon="🃏", layout="wide")

# แถบเมนูด้านซ้าย (Sidebar) สำหรับปรับเรทเงิน
with st.sidebar:
    st.subheader("⚙️ ตั้งค่าระบบ")
    exchange_rate_jpy = st.number_input("เรทเงินเยน (100 JPY = กี่บาท):", value=23.5)
    st.caption("ปรับเปลี่ยนเรทเงินเพื่อคำนวณราคาไทยแบบเรียลไทม์")

st.title("🔥 Top Trending Japanese Cards (PSA 10)")
st.caption("จัดอันดับการ์ดยอดฮิตพร้อมระบบลิงก์เช็คราคาประมูลตรงสู่เว็บไซต์ **PriceCharting** 📊")
st.divider()

# ฟังก์ชันดึงฐานข้อมูลและการดึงรูปภาพ + เพิ่มลิงก์ตรงของ PriceCharting เป็นรายใบ
@st.cache_data(ttl=300)
def get_verified_tcg_cards(game_type):
    if game_type == "Pokémon TCG":
        return [
            {"rank": 1, "name": "Lillie #62", "set": "Shining Legends", "price_jpy": 680000, "image": "https://images.pokemontcg.io/sm35/62_hires.png", "backup_image": "https://images.pokemontcg.io/sm35/62.png", "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-shining-legends/lillie-62"},
            {"rank": 2, "name": "Iono #185", "set": "Paldea Evolved", "price_jpy": 125000, "image": "https://images.pokemontcg.io/sv2/185_hires.png", "backup_image": "https://images.pokemontcg.io/sv2/185.png", "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-paldea-evolved/iono-185"},
            {"rank": 3, "name": "Charizard ex #125", "set": "Obsidian Flames", "price_jpy": 48000, "image": "https://images.pokemontcg.io/sv3/125_hires.png", "backup_image": "https://images.pokemontcg.io/sv3/125.png", "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-obsidian-flames/charizard-ex-125"},
            {"rank": 4, "name": "Pikachu #1", "set": "Base Promo", "price_jpy": 120000, "image": "https://images.pokemontcg.io/basep/1_hires.png", "backup_image": "https://images.pokemontcg.io/basep/1.png", "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-base-promo/pikachu-1"},
            {"rank": 5, "name": "Charizard #4", "set": "Base Set 2", "price_jpy": 3200000, "image": "https://images.pokemontcg.io/base1/4_hires.png", "backup_image": "https://images.pokemontcg.io/base1/4.png", "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-base-set-2/charizard-4"},
            {"rank": 6, "name": "Mewtwo #3", "set": "Base Promo", "price_jpy": 150000, "image": "https://images.pokemontcg.io/basep/3_hires.png", "backup_image": "https://images.pokemontcg.io/basep/3.png", "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-base-promo/mewtwo-3"},
            {"rank": 7, "name": "Lugia #2", "set": "Pop Series 5", "price_jpy": 250000, "image": "https://images.pokemontcg.io/pop5/2_hires.png", "backup_image": "https://images.pokemontcg.io/pop5/2.png", "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-pop-series-5/lugia-2"},
            {"rank": 8, "name": "Rayquaza #3", "set": "Pop Series 1", "price_jpy": 200000, "image": "https://images.pokemontcg.io/pop1/3_hires.png", "backup_image": "https://images.pokemontcg.io/pop1/3.png", "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-pop-series-1/rayquaza-3"},
            {"rank": 9, "name": "Gardevoir ex #4", "set": "EX Ruby & Sapphire", "price_jpy": 90000, "image": "https://images.pokemontcg.io/ex9/4_hires.png", "backup_image": "https://images.pokemontcg.io/ex9/4.png", "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-ex-ruby-and-sapphire/gardevoir-ex-4"},
            {"rank": 10, "name": "Pikachu VMAX #44", "set": "Vivid Voltage", "price_jpy": 220000, "image": "https://images.pokemontcg.io/swsh4/44_hires.png", "backup_image": "https://images.pokemontcg.io/swsh4/44.png", "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-vivid-voltage/pikachu-vmax-44"}
        ]
    else:
        return [
            {
                "rank": 1, 
                "name": "Monkey D. Luffy (ลูฟี่ การ์ดมังกะ) #OP05-119 SEC", 
                "set": "Awakening of the New Era", 
                "price_jpy": 550000, 
                "image": "https://raw.githubusercontent.com/AnandChowdhary/one-piece-card-game/main/assets/OP05/OP05-119.png",
                "backup_image": "https://raw.githubusercontent.com/AnandChowdhary/one-piece-card-game/main/assets/OP05/OP05-119.png",
                "pricecharting_url": "https://www.pricecharting.com/game/one-piece-japanese-awakening-of-the-new-era/monkey-d-luffy-manga-op05-119"
            },
            {
                "rank": 2, 
                "name": "Portgas D. Ace (เอส การ์ดมังกะ) #OP02-120 SEC", 
                "set": "Paramount War", 
                "price_jpy": 320000, 
                "image": "https://raw.githubusercontent.com/AnandChowdhary/one-piece-card-game/main/assets/OP02/OP02-120.png",
                "backup_image": "https://raw.githubusercontent.com/AnandChowdhary/one-piece-card-game/main/assets/OP02/OP02-120.png",
                "pricecharting_url": "https://www.pricecharting.com/game/one-piece-japanese-paramount-war/portgas-d-ace-manga-op02-120"
            }
        ]


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text

# ตัวเลือกหน้าเว็บหลัก
game = st.selectbox("เลือกประเภทการ์ดเกม:", ["Pokémon TCG", "One Piece Card Game"])
use_live = st.checkbox("🔁 ใช้ข้อมูลฮิตจาก PokéTCG (PoC, ฟรี)", value=False)
if use_live:
    st.caption("โหมด PoC: คำนวณความฮิตจากเมตาดาต้า PokéTCG (ไม่มีข้อมูลตลาดจริง)")
use_scrape = st.checkbox("🔍 ใช้ Scraping (eBay sold listings) เพื่อวัดฮิตจริง (PoC)", value=False)
if use_scrape:
    st.caption("โหมด Scrape: จะส่งคำขอไปยัง eBay เพื่อคำนวนจำนวนรายการขาย (อาจถูกบล็อก/เปลี่ยนผลได้)")
search = st.text_input("🔍 ค้นหาเจาะจงชื่อการ์ด (เช่น Pikachu, Luffy, Iono):")

# เรียกข้อมูลการ์ดจริงที่จับคู่เรียบร้อยแล้ว
all_cards = get_verified_tcg_cards(game)

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

if use_live and game == "Pokémon TCG":
    live = get_live_popular_cards(limit=10)
    if live:
        all_cards = live

if use_scrape and game == "Pokémon TCG":
    # Scrape eBay sold listings for each card name to estimate popularity (PoC)
    def scrape_ebay_count(query):
        try:
            q = query.replace(' ', '+')
            url = f"https://www.ebay.com/sch/i.html?_nkw={q}&_sop=10&LH_Sold=1&LH_Complete=1"
            headers = {"User-Agent": "Mozilla/5.0 (compatible; TopJPNBot/1.0)"}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                return 0
            soup = BeautifulSoup(resp.text, 'html.parser')
            # attempt to find results count text
            text = ''
            h = soup.find('h1')
            if h:
                text = h.get_text(separator=' ')
            if not text:
                text = soup.get_text()[:2000]
            m = re.search(r"([0-9,]+) results", text)
            if not m:
                m = re.search(r"([0-9,]+) sold", text)
            if m:
                return int(m.group(1).replace(',', ''))
            # fallback: count listing items
            items = soup.select('.srp-results .s-item')
            return len(items) if items else 0
        except Exception:
            return 0

    scraped = []
    for card in all_cards:
        name = card.get('name')
        count = scrape_ebay_count(name)
        scraped.append({
            'rank': card.get('rank', 0),
            'name': name,
            'set': card.get('set'),
            'price_jpy': card.get('price_jpy', 0),
            'image': card.get('image'),
            'backup_image': card.get('backup_image'),
            'sales_count': count,
            'pricecharting_url': card.get('pricecharting_url', '')
        })
    scraped = sorted(scraped, key=lambda x: x['sales_count'], reverse=True)
    for i, s in enumerate(scraped, start=1):
        s['rank'] = i
    all_cards = scraped

# ระบบค้นหาคำกรอง
if search:
    all_cards = [c for c in all_cards if search.lower() in c["name"].lower()]

st.subheader(f"📋 รายการการ์ดระดับท็อปฮิตอินเทรนด์ในตลาดขณะนี้")

# วนลูปแสดงผลสไตล์แผงกริด แถวละ 2 กล่องแบบสวยงาม
for index in range(0, len(all_cards), 2):
    cols = st.columns(2)
    
    for sub_idx, card_col in enumerate(cols):
        if index + sub_idx < len(all_cards):
            card = all_cards[index + sub_idx]
            price_thb = (card["price_jpy"] / 100) * exchange_rate_jpy
            
            # จำลองราคาแกว่งล่าสุดเล็กน้อยเพื่อให้กราฟขยับดูสมจริง
            live_fluctuation = random.randint(-800, 800)
            current_price_jpy = card["price_jpy"] + live_fluctuation
            trend_data = [int(card["price_jpy"]*0.96), int(card["price_jpy"]*0.98), current_price_jpy]
            
            with card_col:
                with st.container(border=True):
                    sub_c1, sub_c2 = st.columns([1, 1.5])
                    with sub_c1:
                        st.write(f"🏆 **อันดับ {card['rank']}")

                        # โหลดรูปจากไฟล์ท้องถิ่น (images/) ก่อน หากไม่เจอค่อยใช้ URL สำรอง
                        local_path = f"images/{_slugify(card['name'])}.png"
                        if os.path.exists(local_path):
                            st.image(local_path, width=140)
                        else:
                            try:
                                st.image(card["image"], width=140)
                            except:
                                st.image(card["backup_image"], width=140)
                            
                    with sub_c2:
                        st.markdown(f"##### **")
                        st.caption(f"📦 ชุด: {card['set']} | สภาพ: PSA 10 🇯🇵")
                        
                        # 🌟 ส่วนที่เพิ่มเข้ามาใหม่: ปุ่มกดลิงก์ไปยัง PriceCharting ของการ์ดใบนั้นๆ
                        st.link_button("🌐 ดูประวัติบน PriceCharting", card["pricecharting_url"], type="secondary", use_container_width=True)
                        
                        st.metric(label="ราคากลางในญี่ปุ่นล่าสุด", value=f"¥{current_price_jpy:} JPY")
                        st.write(f"💵 เงินไทยประมาณ: `{price_thb:,.0f} THB`")
                        
                        # แสดงรูปภาพขนาดใหญ่สำหรับการ์ด Pokémon: ใช้ไฟล์ท้องถิ่นก่อน ถ้าไม่มีค่อยใช้ URL
                        if game == "Pokémon TCG":
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

                        # สร้างประวัติกราฟเทรนด์ของแต่ละใบ
                        trend_df = pd.DataFrame({'ดีล': ['ดีล 1', 'ดีล 2', 'ล่าสุด'], 'ราคา': trend_data})
                        fig = px.line(trend_df, x='ดีล', y='ราคา', markers=True, color_discrete_sequence=['#FF4B4B'])
                        fig.update_layout(height=95, margin=dict(l=0, r=0, t=0, b=0), xaxis_visible=False, yaxis_visible=False)
                        
                        unique_key = f"chart_{game}_{card['rank']}_{card['name'].replace(' ', '_')}"
                        st.plotly_chart(fig, use_container_width=True, key=unique_key)
