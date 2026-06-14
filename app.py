import streamlit as st
import pandas as pd
import plotly.express as px

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="TCG Member Web", page_icon="🃏", layout=wide)

# --- 1. ระบบฐานข้อมูลสมาชิกชั่วคราว (จำลองระบบสมัครไอดี) ---
# ระบบจะเก็บไอดีที่สมัครไว้ใน Session State ตราบใดที่ยังไม่ปิดแท็บเว็บ
if "user_db" not in st.session_state:
    # ใส่ไอดีตัวอย่างไว้ให้ก่อน 1 ไอดี (username: admin, password: 1234)
    st.session_state["user_db"] = {"admin": {"name": "ผู้ดูแลระบบ", "password": "1234"}}

if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

# --- 2. ส่วนหน้าจอเข้าใช้งาน (ล็อกอิน / สมัครสมาชิก) ---
if st.session_state["logged_in_user"] is None:
    st.title("🔐 กรุณาเข้าสู่ระบบก่อนใช้งาน")
    
    # สร้างแท็บให้เลือกระหว่าง ล็อกอิน กับ สมัครสมาชิก
    tab_login, tab_signup = st.tabs(["🔑 เข้าสู่ระบบ", "📝 สมัครสมาชิกใหม่"])
    
    # หน้าสมัครสมาชิก
    with tab_signup:
        st.subheader("สร้างไอดีของคุณ")
        new_username = st.text_input("ตั้งชื่อไอดี (Username):", key="reg_user")
        new_name = st.text_input("ชื่อของคุณ (Display Name):", key="reg_name")
        new_password = st.text_input("ตั้งรหัสผ่าน (Password):", type="password", key="reg_pass")
        
        if st.button("ยืนยันการสมัครสมาชิก", type="primary"):
            if not new_username or not new_password or not new_name:
                st.error("❌ กรุณากรอกข้อมูลให้ครบทุกช่องครับ")
            elif new_username in st.session_state["user_db"]:
                st.error("❌ ชื่อไอดีนี้มีผู้ใช้งานแล้ว กรุณาเปลี่ยนใหม่ครับ")
            else:
                # บันทึกไอดีใหม่ลงฐานข้อมูลจำลอง
                st.session_state["user_db"][new_username] = {
                    "name": new_name,
                    "password": new_password
                }
                st.success("🎉 สมัครสมาชิกสำเร็จแล้ว! คุณสามารถไปที่แท็บ 'เข้าสู่ระบบ' ได้เลย")

    # หน้าล็อกอิน
    with tab_login:
        st.subheader("กรอกข้อมูลเพื่อเข้าสู่ระบบ")
        username = st.text_input("ชื่อไอดี (Username):", key="login_user")
        password = st.text_input("รหัสผ่าน (Password):", type="password", key="login_pass")
        
        if st.button("เข้าสู่ระบบ"):
            # ตรวจสอบไอดีและรหัสผ่าน
            if username in st.session_state["user_db"] and st.session_state["user_db"][username]["password"] == password:
                st.session_state["logged_in_user"] = st.session_state["user_db"][username]["name"]
                st.rerun() # สั่งรีเฟรชหน้าเว็บเพื่อเข้าสู่หน้าหลัก
            else:
                st.error("❌ ชื่อไอดีหรือรหัสผ่านไม่ถูกต้อง")

# --- 3. หน้าเนื้อหาเว็บหลัก (แสดงหลังจากล็อกอินสำเร็จแล้วเท่านั้น) ---
else:
    # แถบเมนูด้านข้างสำหรับแสดงชื่อผู้ใช้และปุ่มออกจากระบบ
    with st.sidebar:
        st.write(f"สวัสดีครับคุณ **{st.session_state['logged_in_user']}** 😊")
        if st.button("ออกจากระบบ (Log out)"):
            st.session_state["logged_in_user"] = None
            st.rerun()

    # โค้ดเว็บเช็คราคาการ์ดเดิมของคุณ
    st.title("🃏 TCG PSA 10 Price Checker")
    st.write(f"ยินดีต้อนรับคุณ {st.session_state['logged_in_user']} เข้าสู่ระบบข้อมูลการ์ดระดับพรีเมียม")
    
    # (ฟังก์ชันจำลองดึงข้อมูลการ์ดและการแสดงผลกราฟจากโค้ดเดิมจะอยู่ตรงนี้)
    game = st.selectbox("เลือกประเภทการ์ดเกม:", ["Pokémon TCG", "One Piece Card Game"])
    search = st.text_input("พิมพ์ชื่อการ์ดที่ต้องการค้นหา:")
    st.info(f"ระบบกำลังแสดงผลข้อมูลสำหรับสมาชิกทีกำลังเปิดดูข้อมูล {game}...")
