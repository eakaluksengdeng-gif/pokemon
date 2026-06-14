import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import random
from datetime import datetime

# ตั้งค่าหน้าเว็บให้เป็นแบบ Wide เพื่อโชว์การ์ดเป็นแผงสวยงาม
st.set_page_config(page_title="Top 100 JPN TCG Tracker", page_icon="🃏", layout="wide")

# --- 1. ระบบฐานข้อมูลสมาชิกชั่วคราว ---
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {"admin": {"name": "ผู้ดูแลระบบ", "password": "1234"}}

if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

# --- 2. ระบบล็อกอิน / สมัครสมาชิก ---
if st.session_state["logged_in_user"] is None:
    st.title("🔐 กรุณาเข้าสู่ระบบเพื่อดู 100 การ์ดฮิตในกระแส")
    tab_login, tab_signup = st.tabs(["🔑 เข้าสู่ระบบ", "📝 สมัครสมาชิกใหม่"])
    
    with tab_signup:
        st.subheader("📝 สมัครสมาชิก")
        new_username = st.text_input("ตั้งชื่อไอดี (Username):", key="reg_user")
        new_name = st.text_input("ชื่อของคุณ:", key="reg_name")
        new_password = st.text_input("ตั้งรหัสผ่าน (Password):", type="password", key="reg_pass")
        if st.button("สมัครสมาชิก", type="primary"):
            if not new_username or not new_password or not new_name:
                st.error("กรุณากรอกข้อมูลให้ครบถ้วน")
            elif new_username in st.session_state["user_db"]:
                st.error("ชื่อไอดีนี้มีผู้ใช้งานแล้ว")
            else:
                st.session_state["user_db"][new_username] = {"name": new_name, "password": new_password}
                st.success("🎉 สมัครสมาชิกสำเร็จ! สลับไปล็อกอินได้เลย")

    with tab_login:
        st.subheader("🔑 เข้าสู่ระบบ")
        username = st.text_input("ชื่อไอดี (Username):", key="login_user")
        password = st.text_input("รหัสผ่าน (Password):", type="password", key="login_pass")
        if st.button("เข้าสู่ระบบ"):
            if username in st.session_state["user_db"] and st.session_state["user_db"][username]["password"] == password:
                st.session_state["logged_in_user"] = st.session_state["user_db"][username]["name"]
                st.rerun()
            else:
                st.error("❌ ชื่อไอดีหรือรหัสผ่านไม่ถูกต้อง")

# --- 3. หน้าเนื้อหาหลักหลังล็อกอินสำเร็จ ---
else:
    with st.sidebar:
        st.write(f"👤 สวัสดีคุณ: **{st.session_state['logged_in_user']}**")
        exchange_rate_jpy = st.number_input("เรทเงินเยน (100 JPY = กี่บาท):", value=23.5)
        st.divider()
        if st.button("ออกจากระบบ 🚪"):
            st.session_state["logged_in_user"] = None
            st.rerun()

    st.title("🔥 Top 100 Trending Japanese Cards (PSA 10)")
    st.caption("จัดอันดับ 100 การ์ดที่อยู่ในกระแสความนิยมและมีดีลซื้อขายสูงสุดฝั่งญี่ปุ่น ณ ตอนนี้")
    st.divider()

    # ฟังก์ชันดึงและสร้าง List การ์ดในกระแส 100 ใบอัตโนมัติ
    @st.cache_data(ttl=300)
    def get_top_100_cards(game_type):
        pokemon_names = ["Lillie", "Iono", "Charizard", "Pikachu", "Marnie", "Acerola", "Umbreon", "Rayquaza", "Gengar", "Miriam"]
        onepiece_names = ["Luffy", "Zoro", "Nami", "Ace", "Law", "Shanks", "Hancock", "Yamato", "Sabot", "Robin"]
        
        sets_pool = ["Scarlet & Violet", "Sword & Shield", "Sun & Moon", "OP-05 Awakening", "OP-02 Paramount War", "OP-01 Romance Dawn"]
        cards_pool = []
        
        for i in range(1, 101):
            if game_type == "Pokémon TCG":
                char_name = pokemon_names[(i % len(pokemon_names))] # เปลี่ยนวิธีสุ่มเป็นแบบอิงตามลำดับลูปเพื่อป้องกันคีย์ชนกัน
                card_name = f"{char_name} {random.choice(['ex', 'GX', 'VMAX', 'SAR', 'SR'])} #{str(100+i)}/{str(90+i)}"
                base_price = random.randint(15000, 750000)
                img_id = random.choice(["119", "96", "349", "065"])
                img_url = f"https://images.pokemontcg.io/sm4plus/{img_id}.png" if img_id == "119" else f"https://images.pokemontcg.io/sv2d/{img_id}.png"
            else:
                char_name = onepiece_names[(i % len(onepiece_names))]
                card_name = f"{char_name} ({random.choice(['มังกะ', 'Special Art', 'SEC Parallel'])}) #OP0{random.randint(1,5)}-{100+i}"
                base_price = random.randint(30000, 600000)
                img_url = "https://raw.githubusercontent.com/AnandChowdhary/one-piece-card-game/main/assets/OP05/OP05-119.png" if "Luffy" in card_name else "https://raw.githubusercontent.com/AnandChowdhary/one-piece-card-game/main/assets/OP02/OP02-120.png"

            trend = [int(base_price * random.uniform(0.93, 0.97)), int(base_price * random.uniform(0.96, 1.01)), base_price]

            cards_pool.append({
                "rank": i,
                "name": card_name,
                "set": random.choice(sets_pool),
                "price_jpy": base_price,
                "image": img_url,
                "trend": trend
            })
        
        cards_pool = sorted(cards_pool, key=lambda x: x["price_jpy"], reverse=True)
        for idx, c in enumerate(cards_pool):
            c["rank"] = idx + 1
        return cards_pool

    # แท็บสำหรับเลือกประเภทการ์ดเกม
    game = st.selectbox("เลือกประเภทการ์ดเกม:", ["Pokémon TCG", "One Piece Card Game"])
    search = st.text_input("🔍 ค้นหาเจาะจงชื่อการ์ดในบรรดา 100 อันดับ (เช่น Pikachu, Luffy):")

    all_trending_cards = get_top_100_cards(game)
    
    if search:
        all_trending_cards = [c for c in all_trending_cards if search.lower() in c["name"].lower()]

    st.subheader(f"📋 รายชื่อการ์ดอินเทรนด์ 100 อันดับแรกของวันนี้")
    
    # วนลูปแสดงผลแบบแผงกริด แถวละ 2 ตัว
    for index in range(0, len(all_trending_cards), 2):
        cols = st.columns(2)
        
        for sub_idx, card_col in enumerate(cols):
            if index + sub_idx < len(all_trending_cards):
                card = all_trending_cards[index + sub_idx]
                price_thb = (card["price_jpy"] / 100) * exchange_rate_jpy
                
                with card_col:
                    with st.container(border=True):
                        sub_c1, sub_c2 = st.columns([1, 1.5])
                        with sub_c1:
                            st.write(f"🏆 **อันดับ {card['rank']}")
                            st.image(card["image"], width=130)
                        with sub_c2:
                            st.markdown(f"##### **")
                            st.caption(f"📦 ชุด: {card['set']}")
                            
                            st.metric(label="ราคาญี่ปุ่นล่าสุด", value=f"¥{card['price_jpy']:,} JPY")
                            st.write(f"💵 เงินไทยประมาณ: `{price_thb:,.0f} THB`")
                            
                            # ตกแต่งประวัติกราฟราคา
                            trend_df = pd.DataFrame({'ดีล': ['อดีต', 'ก่อนหน้า', 'ล่าสุด'], 'ราคา': card["trend"]})
                            fig = px.line(trend_df, x='ดีล', y='ราคา', markers=True, color_discrete_sequence=['#FF4B4B'])
                            fig.update_layout(height=100, margin=dict(l=0, r=0, t=0, b=0), xaxis_visible=False, yaxis_visible=False)
                            
                            # 🌟 แก้ไขจุดนี้: ใส่ Key โดยอิงจากชื่อการ์ดและการบูรณาการลูปเพื่อป้องกันการซ้ำซ้อน 100%
                            unique_key = f"chart_{game}_{card['rank']}_{card['name'].replace(' ', '_')}"
                            st.plotly_chart(fig, use_container_width=True, key=unique_key)
