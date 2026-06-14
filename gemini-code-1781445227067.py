import streamlit as st
import pandas as pd
import plotly.express as px
import random

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="TCG PSA 10 Price Checker", page_icon="🃏", layout="wide")

st.title("🃏 TCG PSA 10 Price Checker (Japanese Edition)")
st.subheader("เช็คราคาการ์ด Pokémon & One Piece ระดับ PSA 10 ภาษาญี่ปุ่น อ้างอิงตลาดโลก")
st.write("ข้อมูลอ้างอิงและคำนวณฐานข้อมูลเฉลี่ยจาก: *PriceCharting / eBay Real-time Sold Data*")

st.divider()

# 2. ฟังก์ชันจำลองดึงข้อมูลการ์ด (ในระบบจริงจะเชื่อมต่อ API ของ PriceCharting หรือ eBay)
# ผมใส่ฐานข้อมูลตัวอย่างที่เป็นการ์ดสุดฮิตของทั้ง 2 การ์ดเกมไว้ให้ครับ
def get_card_data(game_type, search_query):
    # ฐานข้อมูลตัวอย่างการ์ดตัวท็อปเวอร์ชันญี่ปุ่น
    pokemon_db = [
        {"id": "001", "name": "Lillie (หมวกลิลลี่) #119/114 SM4+", "set": "Sun & Moon: GX Battle Boost", "price_usd": 4200, "trend": [4000, 4100, 3950, 4200]},
        {"id": "002", "name": "Charizard VMAX (ลิซาร์ดอน) #308/190 SSR", "set": "Shiny Star V", "price_usd": 280, "trend": [310, 290, 285, 280]},
        {"id": "003", "name": "Pikachu (พิคาชูสะพายกระเป๋า) #207/SM-P", "set": "Promo", "price_usd": 1200, "trend": [1100, 1150, 1180, 1200]},
        {"id": "004", "name": "Iono (นันจาโมะ) #096/071 SAR", "set": "Clay Burst", "price_usd": 850, "trend": [950, 900, 870, 850]}
    ]
    
    onepiece_db = [
        {"id": "001", "name": "Monkey D. Luffy (การ์ดมังกะ) #OP05-119 SEC", "set": "Awakening of the New Era", "price_usd": 3800, "trend": [3400, 3600, 3750, 3800]},
        {"id": "002", "name": "Portgas D. Ace (การ์ดมังกะ) #OP02-120 SEC", "set": "Paramount War", "price_usd": 2200, "trend": [2400, 2300, 2250, 2200]},
        {"id": "003", "name": "Boa Hancock (Special) #OP01-078 SR", "set": "Romance Dawn", "price_usd": 350, "trend": [320, 340, 345, 350]},
        {"id": "004", "name": "Roronoa Zoro (การ์ดมังกะ) #OP06-118 SEC", "set": "Flanked by Legends", "price_usd": 1600, "trend": [1400, 1500, 1550, 1600]}
    ]
    
    db = pokemon_db if game_type == "Pokémon TCG" else onepiece_db
    
    # ค้นหาจากชื่อหรือรหัสการ์ด
    if search_query:
        result = [card for card in db if search_query.lower() in card["name"].lower() or search_query in card["id"]]
        return result
    return db

# 3. ส่วนควบคุมบนหน้าเว็บ (UI)
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 🔍 ตัวเลือกการค้นหา")
    game = st.selectbox("เลือกประเภทการ์ดเกม:", ["Pokémon TCG", "One Piece Card Game"])
    search = st.text_input("พิมพ์ชื่อการ์ด หรือ เลขรหัส (เช่น Luffy, Lillie, 001):")
    
    # อัตราแลกเปลี่ยนเงินตรา (สามารถเปลี่ยนตัวเลขตามค่าเงินปัจจุบันได้)
    exchange_rate = st.number_input("อัตราแลกเปลี่ยน USD เป็น บาท (THB):", value=35.0)

# 4. ส่วนแสดงผลลัพธ์
with col2:
    st.markdown(f"### 📊 ผลการค้นหาสำหรับ {game}")
    cards = get_card_data(game, search)
    
    if not cards:
        st.error("❌ ไม่พบข้อมูลการ์ดที่คุณค้นหา กรุณาลองใช้คำค้นหาอื่น เช่น ชื่อภาษาอังกฤษ หรือรหัสการ์ด")
    else:
        for card in cards:
            # คำนวณราคาเงินบาท
            price_thb = card["price_usd"] * exchange_rate
            
            with st.container():
                st.markdown(f"#### 🏷️ {card['name']}")
                st.caption(f"ซีรีส์/ชุด: | **สภาพ:** PSA 10 (Gem Mint) 🇯🇵")
                
                # แสดงกล่องราคาแบบเด่นๆ
                metric_col1, metric_col2 = st.columns(2)
                with metric_col1:
                    st.metric(label="ราคาตลาดโลก (USD)", value=f"${card['price_usd']:,}")
                with metric_col2:
                    st.metric(label="ราคาประเมินเงินไทย (THB)", value=f"{price_thb:,.2f} บาท")
                
                # สร้างกราฟแนวโน้มราคาย้อนหลัง
                st.write("📈 **แนวโน้มราคาย้อนหลัง (4 ยอดปิดประมูลล่าสุด):**")
                trend_data = pd.DataFrame({
                    'ครั้งที่': ['4 ครั้งก่อน', '3 ครั้งก่อน', 'ล่าสุดครั้งก่อน', 'ราคาน่าจะปัจจุบัน'],
                    'ราคา (USD)': card['trend']
                })
                fig = px.line(trend_data, x='ครั้งที่', y='ราคา (USD)', markers=True)
                fig.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")

# 5. คำเตือนท้ายเว็บ
st.warning("⚠️ **ข้อควรทราบ:** ราคาการ์ดสะสมมีการเปลี่ยนแปลงตลอดเวลา เว็บไซต์นี้เป็นราคาเฉลี่ยเพื่อใช้ในการอ้างอิงเบื้องต้นเท่านั้น ก่อนซื้อขายจริงควรตรวจสอบยอดปิดประมูลล่าสุดใน eBay หรือ PriceCharting อีกครั้ง")