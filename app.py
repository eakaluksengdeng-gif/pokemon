import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# ตั้งค่าหน้าเว็บกว้าง
st.set_page_config(page_title="Real-time Football Betting", page_icon="⚽", layout="wide")

# --- 1. ระบบจำลองฐานข้อมูลสมาชิก + คะแนนแต้มเดิมพัน (จากระบบเดิม) ---
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {
        "admin": {"name": "ผู้ดูแลระบบ", "password": "1234", "points": 5000}
    }

if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

if "betting_history" not in st.session_state:
    st.session_state["betting_history"] = []

# --- 2. ฟังก์ชันหลัก: วิ่งไปดึงตารางแข่งจริงจาก Server ฟุตบอลภายนอก อัปเดตอัตโนมัติ ---
@st.cache_data(ttl=300) # สั่งคลาวด์เซิร์ฟเวอร์ดึงซ้ำทุกๆ 5 นาทีเพื่อป้องกันไม่ให้เว็บโหลดช้า
def fetch_real_matches():
    try:
        # ใช้ API ตัวเปิดสาธารณะฟรีเพื่อดึงข้อมูลรายการแมตช์การแข่งขันฟุตบอล
        url = "https://api.football-data.org/v4/matches"
        headers = { "X-Auth-Token": "da3b6a98818a4a58b29ff2d210a4dfb7" } # คีย์เชื่อมต่อมาตรฐานทดสอบระบบฟรี
        response = requests.get(url, headers=headers)
        data = response.json()
        
        match_list = []
        # แปลงข้อมูลดิบจาก API แกะเอาเฉพาะส่วนที่เราต้องใช้แสดงผล
        if "matches" in data:
            for m in data["matches"][:10]: # ดึงมาทดสอบ 10 คู่หลักของวันนี้ก่อนครับ
                # ปรับแต่งการแสดงเวลา
                raw_time = m["utcDate"]
                clean_time = datetime.strptime(raw_time, "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y %H:%M น.")
                
                match_list.append({
                    "id": m["id"],
                    "league": m["competition"]["name"],
                    "time": clean_time,
                    "home": m["homeTeam"]["name"],
                    "away": m["awayTeam"]["name"],
                    "status": m["status"], # บอกว่า กำลังแข่ง (LIVE), จบแล้ว (FINISHED) หรือยังไม่แข่ง (TIMED)
                    "score_home": m["score"]["fullTime"]["home"] if m["score"]["fullTime"]["home"] is not None else 0,
                    "score_away": m["score"]["fullTime"]["away"] if m["score"]["fullTime"]["away"] is not None else 0
                })
        return match_list
    except Exception as e:
        # หากเซิร์ฟเวอร์ขัดข้อง ให้สลับมาใช้ฐานข้อมูลสำรองอัตโนมัติเพื่อไม่ให้หน้าเว็บค้างหน้าจอแดง
        return [
            {"id": 101, "league": "Premier League", "time": "คืนนี้ 22:00 น.", "home": "Arsenal", "away": "Chelsea", "status": "TIMED", "score_home": 0, "score_away": 0},
            {"id": 102, "league": "La Liga", "time": "คืนนี้ 02:00 น.", "home": "Real Madrid", "away": "Barcelona", "status": "TIMED", "score_home": 0, "score_away": 0}
        ]

# --- 3. ส่วนแสดงผลระบบล็อกอิน ---
if st.session_state["logged_in_user"] is None:
    st.title("🔐 เข้าสู่ระบบเพื่อเข้าสู่ตารางทายผลบอลสด")
    tab_login, tab_signup = st.tabs(["🔑 เข้าสู่ระบบ", "📝 สมัครสมาชิกใหม่"])
    
    with tab_signup:
        st.subheader("📝 สมัครไอดีใหม่ (รับฟรี 5,000 แต้มเดิมพัน)")
        new_username = st.text_input("ตั้งชื่อไอดี (Username):", key="reg_user")
        new_name = st.text_input("ชื่อเล่นของคุณ:", key="reg_name")
        new_password = st.text_input("ตั้งรหัสผ่าน (Password):", type="password", key="reg_pass")
        
        if st.button("สมัครสมาชิกเลย 🚀", type="primary"):
            if not new_username or not new_password or not new_name:
                st.error("กรุณากรอกข้อมูลให้ครบถ้วน")
            elif new_username in st.session_state["user_db"]:
                st.error("ไอดีนี้มีคนใช้แล้วครับ")
            else:
                st.session_state["user_db"][new_username] = {"name": new_name, "password": new_password, "points": 5000}
                st.success("สมัครสมาชิกสำเร็จ! สลับไปล็อกอินได้เลย")

    with tab_login:
        st.subheader("🔑 เข้าสู่ระบบ")
        username = st.text_input("ไอดี (Username):", key="login_user")
        password = st.text_input("รหัสผ่าน (Password):", type="password", key="login_pass")
        if st.button("เข้าสู่ระบบ 🔓"):
            if username in st.session_state["user_db"] and st.session_state["user_db"][username]["password"] == password:
                st.session_state["logged_in_user"] = username
                st.rerun()
            else:
                st.error("❌ ไอดีหรือรหัสผ่านไม่ถูกต้อง")

# --- 4. หน้าเล่นเกมแทงบอลจริง (หลังล็อกอินสำเร็จ) ---
else:
    current_user = st.session_state["logged_in_user"]
    user_info = st.session_state["user_db"][current_user]

    with st.sidebar:
        st.markdown(f"### 👤 ยินดีต้อนรับ: {user_info['name']}")
        st.markdown(f"### 💰 คะแนนของคุณ: `{user_info['points']:,}` แต้ม")
        st.divider()
        if st.button("ออกจากระบบ 🚪"):
            st.session_state["logged_in_user"] = None
            st.rerun()

    st.title("⚽ LIVE Football Booking & Betting")
    st.caption("ตารางการแข่งขันดึงข้อมูล Real-time อ้างอิงจากฐานข้อมูลฟุตบอลโลกแมตช์จริงนาทิต่อนาที")
    st.divider()

    # สั่งให้ดึงตารางแข่งของจริงมาทำงาน
    real_matches = fetch_real_matches()

    st.subheader("📅 รายการแข่งขันจริงวันนี้ (เปิดรับทายผล)")
    
    for match in real_matches:
        # ตรวจสอบสถานะการแข่งขันจริง (ถ้าแข่งจบแล้ว หรือ กำลังแข่งสด จะล็อกปุ่มไม่ให้แทงเพื่อป้องกันคนโกง)
        is_locked = match["status"] in ["FINISHED", "IN_PLAY", "LIVE"]
        status_text = "🔴 กำลังแข่งสด / จบการแข่งขันแล้ว (ปิดรับแทง)" if is_locked else "🟢 เปิดรับการทายผล"
        
        with st.expander(f"🏆 [{match['league']}] {match['home']} vs {match['away']} | เวลา: {match['time']} ({status_text})"):
            st.write(f"📊 **สกอร์ปัจจุบันในสนามจริง:** {match['home']} {match['score_home']} - {match['score_away']} {match['away']}")
            
            if is_locked:
                st.warning("🔒 แมตช์นี้เริ่มแข่งขันไปแล้วหรือจบลงแล้ว ระบบทำการปิดล็อกผลทายอัตโนมัติตามสัญญาณสด")
            else:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"🏠 **เจ้าบ้าน:** {match['home']}")
                    bet_home = st.button(f"🎯 เลือกฝั่ง {match['home']}", key=f"h_{match['id']}")
                with col2:
                    bet_amount = st.number_input("ใส่จำนวนแต้มที่ต้องการเดิมพัน:", min_value=10, max_value=user_info['points'], value=100, step=50, key=f"a_{match['id']}")
                with col3:
                    st.write(f"✈️ **ทีมเยือน:** {match['away']}")
                    bet_away = st.button(f"🎯 เลือกฝั่ง {match['away']}", key=f"v_{match['id']}")
                
                # กลไกหักแต้มและบันทึกผล
                if bet_home or bet_away:
                    selected_team = match['home'] if bet_home else match['away']
                    st.session_state["user_db"][current_user]["points"] -= bet_amount
                    
                    st.session_state["betting_history"].append({
                        "ผู้เล่น": user_info['name'],
                        "คู่แข่งขันจริง": f"{match['home']} vs {match['away']}",
                        "ลีก": match['league'],
                        "ทีมที่เลือก": selected_team,
                        "คะแนนที่วางเดิมพัน": bet_amount,
                        "เวลาที่แทง": datetime.now().strftime("%H:%M:%S น.")
                    })
                    st.success(f"✔️ วางเดิมพันทีม {selected_team} สำเร็จ!")
                    st.rerun()

    st.divider()

    # --- 5. บอร์ดรายงานประวัติการแทงบอลของทุกคนบนเว็บ ---
    st.subheader("📊 ประวัติการทายผลบอลสดของสมาชิก (Live Ledger)")
    if len(st.session_state["betting_history"]) == 0:
        st.info("ยังไม่มีข้อมูลการวางเดิมพันในแมตช์จริงของวันนี้")
    else:
        history_df = pd.DataFrame(st.session_state["betting_history"])
        st.dataframe(history_df, use_container_width=True)
