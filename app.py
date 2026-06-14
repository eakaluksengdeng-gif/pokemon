import streamlit as st
import pandas as pd
import plotly.express as px

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="SNKRDUNK PSA 10 Price", page_icon="🇯🇵", layout="wide")

# --- 1. ระบบฐานข้อมูลสมาชิกชั่วคราว ---
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {"admin": {"name": "ผู้ดูแลระบบ", "password": "1234"}}

if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

# --- 2. หน้าแรก: ระบบล็อกอิน / สมัครสมาชิก ---
if st.session_state["logged_in_user"] is None:
    st.title("🔐 กรุณาเข้าสู่ระบบเพื่อดูราคา SNKRDUNK JP")
    tab_login, tab_signup = st.tabs(["🔑 เข้าสู่ระบบ", "📝 สมัครสมาชิกใหม่"])
    
    with tab_signup:
        st.subheader("สร้างไอดีของคุณ")
        new_username = st.text_input("ตั้งชื่อไอดี (Username):", key="reg_user")
        new_name = st.text_input("ชื่อของคุณ (Display Name):", key="reg_name")
        new_password = st.text_input("ตั้งรหัสผ่าน (Password):", type="password", key="reg_pass")
        
        if st.button("ยืนยันการสมัครสมาชิก", type="primary"):
            if not new_username or not new_password or not new_name:
                st.error("❌ กรุณากรอกข้อมูลให้ครบช่องครับ")
            elif new_username in st.session_state["user_db"]:
                st.error("❌ ชื่อไอดีนี้มีผู้ใช้งานแล้ว")
            else:
                st.session_state["user_db"][new_username] = {"name": new_name, "password": new_password}
                st.success("🎉 สมัครสมาชิกสำเร็จ! ไปที่แท็บเข้าสู่ระบบได้เลย")

    with tab_login:
        st.subheader("กรอกข้อมูลเพื่อเข้าสู่ระบบ")
        username = st.text_input("ชื่อไอดี (Username):", key="login_user")
        password = st.text_input("รหัสผ่าน (Password):", type="password", key="login_pass")
        if st.button("เข้าสู่ระบบ"):
            if username in st.session_state["user_db"] and st.session_state["user_db"][username]["password"] == password:
                st.session_state["logged_in_user"] = st.session_state["user_db"][username]["name"]
                st.rerun()
            else:
                st.error("❌ ชื่อไอดีหรือรหัสผ่านไม่ถูกต้อง")

# --- 3. หน้าเนื้อหาเว็บหลัก ---
else:
    with st.sidebar:
        st.write(f"ผู้ใช้งาน: **{st.session_state['logged_in_user']}** 👤")
        exchange_rate_jpy = st.number_input("เรทเงินเยนปัจจุบัน (100 JPY = กี่บาท):", value=23.5)
        if st.button("ออกจากระบบ (Log out)"):
            st.session_state["logged_in_user"] = None
            st.rerun()

    st.title("📈 SNKRDUNK JP - PSA 10 Price Tracker")
    st.caption("ดึงข้อมูลและแสดงรูปภาพอ้างอิงตามมาตรฐานตลาดซื้อขายการ์ดอันดับ 1 ของญี่ปุ่น (SNKRDUNK)")
    st.divider()

    # ฐานข้อมูลตัวอย่าง - ตรวจสอบเครื่องหมายคำพูดเรียบร้อยทุกจุด
    def get_snkrdunk_data(game_type, search_query):
        pokemon_db = [
            {
                "name": "Lillie (หมวกลิลลี่) #119/114 SM4+", 
                "set": "GX Battle Boost", 
                "price_jpy": 650000, 
                "image": "https://images.pokemontcg.io/sm4plus/119.png",
                "trend": [600000, 620000, 640000, 650000]
            },
            {
                "name": "Iono (นันจาโมะ) #096/071 SAR", 
                "set": "Clay Burst", 
                "price_jpy": 130000, 
                "image": "https://images.pokemontcg.io/sv2d/96.png",
                "trend": [150000, 140000, 135000, 130000]
            },
            {
                "name": "Charizard ex (ลิซาร์ดอน) #349/190 SAR", 
                "set": "Shiny Treasure ex", 
                "price_jpy": 45000, 
                "image": "https://images.pokemontcg.io/sv4a/349.png",
                "trend": [42000, 43000, 44000, 45000]
            }
        ]
        
        onepiece_db = [
            {
                "name": "Monkey D. Luffy (ลูฟี่การ์ดมังกะ) #OP05-119 SEC", 
                "set": "Awakening of the New Era", 
                "price_jpy": 580000, 
                "image": "https://raw.githubusercontent.com/AnandChowdhary/one-piece-card-game/main/assets/OP05/OP05-119.png",
                "trend": [520000, 550000, 565000, 580000]
            },
            {
                "name": "Portgas D. Ace (เอสการ์ดมังกะ) #OP02-120 SEC", 
                "set": "Paramount War", 
                "price_jpy": 340000, 
                "image": "https://raw.githubusercontent.com/AnandChowdhary/one-piece-card-game/main/assets/OP02/OP02-120.png",
                "trend": [360000, 350000, 345000, 340000]
            }
        ]
        
        db = pokemon_db if game_type == "Pokémon TCG" else onepiece_db
        if search_query:
            return [card for card in db if search_query.lower() in card["name"].lower()]
        return db

    # ส่วนค้นหา
    col_ctrl1, col_ctrl2 = st.columns([1, 2])
    with col_ctrl1:
        game = st.selectbox("เลือกประเภทการ์ดเกม:", ["Pokémon TCG", "One Piece Card Game"])
    with col_ctrl2:
        search = st.text_input("🔍 พิมพ์ชื่อการ์ดที่ต้องการค้นหา (เช่น Luffy, Lillie):")

    st.subheader(f"📋 รายการการ์ดจาก SNKRDUNK JP ({game})")
    cards = get_snkrdunk_data(game, search)

    if not cards:
        st.error("❌ ไม่พบข้อมูลการ์ดใบนี้ในระบบฐานข้อมูล")
    else:
        for card in cards:
            price_thb = (card["price_jpy"] / 100) * exchange_rate_jpy
            card_col1, card_col2 = st.columns([1, 2])
            
            with card_col1:
                # แสดงรูปภาพการ์ด
                st.image(card["image"], caption=card["name"], width=250)
                
            with card_col2:
                st.markdown(f"### ✨ {card['name']}")
                st.markdown(f"ชุดซีรีส์: | **สถานะ:** PSA 10 Gem Mint 🇯🇵")
                
                m1, m2 = st.columns(2)
                with m1:
                    st.metric(label="ราคาล่าสุดบน SNKRDUNK JP", value=f"¥{card['price_jpy']:,} JPY")
                with m2:
                    st.metric(label="คิดเป็นเงินไทยโดยประมาณ", value=f"{price_thb:,.2f} THB")
                
                st.write("📊 **ประวัติราคายอดปิดล่าสุดบนแอป (SNKRDUNK History):**")
                trend_df = pd.DataFrame({
                    'ดีลล่าสุด': ['ดีลที่ 4', 'ดีลที่ 3', 'ดีลก่อนหน้า', 'ล่าสุดวันนี้'],
                    'ราคา (YEN)': card["trend"]
                })
                fig = px.line(trend_df, x='ดีลล่าสุด', y='ราคา (YEN)', markers=True, color_discrete_sequence=['#FF4B4B'])
                fig.update_layout(height=200, margin=dict(l=0, r=0, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)
                
            st.divider()
