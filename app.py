import streamlit as st
import pandas as pd

# ตั้งค่าหน้าเว็บกว้างสวยงาม
st.set_page_config(page_title="Football Betting System", page_icon="⚽", layout="wide")

# --- 1. ระบบจำลองฐานข้อมูลสมาชิก + คะแนนแต้มเดิมพัน (Points) ---
if "user_db" not in st.session_state:
    # เริ่มต้นมีไอดี admin (รหัส 1234) ให้แต้มฟรี 1,000 แต้มไว้ลองแทงครับ
    st.session_state["user_db"] = {
        "admin": {"name": "ผู้ดูแลระบบ", "password": "1234", "points": 1000}
    }

if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

# ระบบจำลองประวัติการแทงบอล
if "betting_history" not in st.session_state:
    st.session_state["betting_history"] = []

# --- 2. หน้าแรก: ระบบล็อกอิน / สมัครสมาชิก ---
if st.session_state["logged_in_user"] is None:
    st.title("🔐 เข้าสู่ระบบ / สมัครสมาชิกเพื่อเข้าแทงบอล")
    tab_login, tab_signup = st.tabs(["🔑 เข้าสู่ระบบ", "📝 สมัครสมาชิกใหม่"])
    
    with tab_signup:
        st.subheader("📝 สมัครไอดีใหม่ (รับฟรี 1,000 แต้ม)")
        new_username = st.text_input("ตั้งชื่อไอดี (Username):", key="reg_user")
        new_name = st.text_input("ชื่อเล่นของคุณ:", key="reg_name")
        new_password = st.text_input("ตั้งรหัสผ่าน (Password):", type="password", key="reg_pass")
        
        if st.button("สมัครสมาชิกเลย 🚀", type="primary"):
            if not new_username or not new_password or not new_name:
                st.error("❌ กรุณากรอกข้อมูลให้ครบถ้วน")
            elif new_username in st.session_state["user_db"]:
                st.error("❌ ไอดีนี้มีคนใช้แล้วครับ")
            else:
                # บันทึกไอดีใหม่ และแจกแต้มตั้งต้น 1000
                st.session_state["user_db"][new_username] = {
                    "name": new_name,
                    "password": new_password,
                    "points": 1000
                }
                st.success("🎉 สมัครสมาชิกสำเร็จ! สลับไปที่แท็บเข้าสู่ระบบได้เลย")

    with tab_login:
        st.subheader("🔑 เข้าสู่ระบบ")
        username = st.text_input("ไอดี (Username):", key="login_user")
        password = st.text_input("รหัสผ่าน (Password):", type="password", key="login_pass")
        if st.button("เข้าสู่ระบบ 🔓"):
            if username in st.session_state["user_db"] and st.session_state["user_db"][username]["password"] == password:
                # จำว่าใครล็อกอินอยู่ (จำคีย์ username ไว้ดึงแต้ม)
                st.session_state["logged_in_user"] = username
                st.rerun()
            else:
                st.error("❌ ไอดีหรือรหัสผ่านไม่ถูกต้อง")

# --- 3. หน้าเล่นเกมทายผลบอล (หลังล็อกอินสำเร็จ) ---
else:
    current_user = st.session_state["logged_in_user"]
    user_info = st.session_state["user_db"][current_user]

    # แถบเมนูด้านซ้าย (Sidebar) โชว์โปรไฟล์และคะแนน
    with st.sidebar:
        st.markdown(f"### 👤 โปรไฟล์: {user_info['name']}")
        st.markdown(f"### 💰 แต้มของคุณ: `{user_info['points']:,}` คะแนน")
        st.divider()
        if st.button("ออกจากระบบ 🚪"):
            st.session_state["logged_in_user"] = None
            st.rerun()

    st.title("⚽ ระบบตารางแข่งและทายผลบอลออนไลน์")
    st.caption("ระบบดึงตารางอัตโนมัติและบันทึกประวัติการวางเดิมพันตามรายชื่อไอดี")
    st.divider()

    # ข้อมูลตารางแข่งฟุตบอลวันนี้ (ในระบบจริงจะใช้คำสั่งดึงจาก API-Football อัตโนมัติ)
    # ผมเตรียมข้อมูลแมตช์หยุดโลกไว้ให้ 3 คู่ครับ
    matches = [
        {"id": 1, "time": "21:00 น.", "league": "พรีเมียร์ลีก", "home": "แมนฯ ยูไนเต็ด", "away": "เชลซี", "odds": "แมนฯ ยูฯ ต่อ 0.5"},
        {"id": 2, "time": "23:30 น.", "league": "พรีเมียร์ลีก", "home": "ลิเวอร์พูล", "away": "แมนฯ ซิตี้", "odds": "เสมอ ลิเวอร์พูล"},
        {"id": 3, "time": "02:00 น.", "league": "ลาลีกา", "home": "เรอัล มาดริด", "away": "บาร์เซโลน่า", "odds": "มาดริด ต่อ 0.5/1"},
    ]

    # ส่วนแสดงตารางแข่งและปุ่มกดแทงบอล
    st.subheader("📅 รายการแข่งขันและราคาต่อรองวันนี้")
    
    for match in matches:
        with st.expander(f"⏰ {match['time']} | [{match['league']}] {match['home']} vs {match['away']} ({match['odds']})"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"🏠 **ทีมเหย้า:** {match['home']}")
                bet_home = st.button(f"🎯 แทง {match['home']}", key=f"home_{match['id']}")
            
            with col2:
                st.write("⚖️ **ราคาต่อรองกลาง**")
                st.info(match['odds'])
                # ช่องให้กรอกจำนวนแต้มที่จะแทง
                bet_amount = st.number_input("ใส่จำนวนแต้มที่ต้องการเดิมพัน:", min_value=10, max_value=user_info['points'], value=100, step=50, key=f"amt_{match['id']}")
                
            with col3:
                st.write(f"✈️ **ทีมเยือน:** {match['away']}")
                bet_away = st.button(f"🎯 แทง {match['away']}", key=f"away_{match['id']}")
            
            # กลไกบันทึกเมื่อผู้ใช้กดปุ่มแทง
            if bet_home or bet_away:
                selected_team = match['home'] if bet_home else match['away']
                
                # หักคะแนนผู้ใช้จริงในฐานข้อมูล
                st.session_state["user_db"][current_user]["points"] -= bet_amount
                
                # บันทึกประวัติการแทง
                st.session_state["betting_history"].append({
                    "ผู้เล่น": user_info['name'],
                    "คู่แข่งขัน": f"{match['home']} vs {match['away']}",
                    "ทีมที่เลือก": selected_team,
                    "จำนวนแต้มที่แทง": bet_amount
                })
                st.success(f"✔️ บันทึกการทายผลสำเร็จ! แทงทีม {selected_team} จำนวน {bet_amount} แต้มเรียบร้อย")
                st.rerun() # รีเฟรชหน้าเว็บเพื่ออัปเดตแต้มล่าสุดในแถบซ้ายมือ

    st.divider()

    # --- 4. ตารางแสดงประวัติการทายผลบอลของคนในเว็บ ---
    st.subheader("📊 ตารางบันทึกการทายผลบอลล่าสุด (Live Bet)")
    if len(st.session_state["betting_history"]) == 0:
        st.write("ยังไม่มีใครวางเดิมพันในวันนี้")
    else:
        # แปลงประวัติเป็นตาราง Dataframe มาโชว์แบบหน้าเว็บที่คุณส่งมาเลยครับ
        history_df = pd.DataFrame(st.session_state["betting_history"])
        st.dataframe(history_df, use_container_width=True)
