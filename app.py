import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime
import os
import re

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
            {
                "rank": 1, 
                "name": "Lillie (หมวกลิลลี่) #119/114 SM4+", 
                "set": "GX Battle Boost", 
                "price_jpy": 680000, 
                "image": "https://via.placeholder.com/220x308.png?text=Lillie",
                "backup_image": "https://via.placeholder.com/220x308.png?text=Lillie",
                "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-battle-boost/lillie-119-114" # ลิงก์ตรงของใบนี้
            },
            {
                "rank": 2, 
                "name": "Iono (นันจาโมะ) #096/071 SAR", 
                "set": "Clay Burst", 
                "price_jpy": 125000, 
                "image": "https://via.placeholder.com/220x308.png?text=Iono",
                "backup_image": "https://via.placeholder.com/220x308.png?text=Iono",
                "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-clay-burst/iono-96-071"
            },
            {
                "rank": 3, 
                "name": "Charizard ex (ลิซาร์ดอน มังกรดำ) #349/190 SAR", 
                "set": "Shiny Treasure ex", 
                "price_jpy": 48000, 
                "image": "https://via.placeholder.com/220x308.png?text=Charizard",
                "backup_image": "https://via.placeholder.com/220x308.png?text=Charizard",
                "pricecharting_url": "https://www.pricecharting.com/game/pokemon-japanese-shiny-treasure-ex/charizard-ex-349-190"
            }
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
search = st.text_input("🔍 ค้นหาเจาะจงชื่อการ์ด (เช่น Pikachu, Luffy, Iono):")

# เรียกข้อมูลการ์ดจริงที่จับคู่เรียบร้อยแล้ว
all_cards = get_verified_tcg_cards(game)

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
