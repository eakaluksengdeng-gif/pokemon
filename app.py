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

    # แก้ไขคลังลิงก์รูปภาพใหม่ (ใช้รูปจากแหล่งเปิดที่ไม่บล็อกเว็บเรา)
    def get_snkrdunk_data(game_type, search_query):
        pokemon_db = [
            {
                "name": "Lillie (หมวกลิลลี่) #119/114 SM4+", 
                "set": "GX Battle Boost", 
                "price_jpy": 650000, 
                "image": "https://images.pokemontcg.io/sm4plus/119.png", # ลิงก์แบบบีบอัด ไม่โดนบล็อก
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
                "image": "
