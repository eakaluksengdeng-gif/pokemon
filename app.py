import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# ตั้งค่าหน้าเว็บกว้าง
st.set_page_config(page_title="Real-time Football Betting", page_icon="⚽", layout="wide")

# --- 1. ระบบจำลองฐานข้อมูลสมาชิก + คะแนนแต้มเดิมพัน ---
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {
        "admin": {"name": "ผู้ดูแลระบบ", "password": "1234", "points": 5000}
    }

if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

if "betting_history" not in st.session_state:
    st.session_state["betting_history"] = []

# --- 2. ฟังก์ชันดึงตารางแข่งจริง (พร้อมระบบสำรองที่ใช้งานได้จริง) ---
@st.cache_data(ttl=60) # ลดเวลาจำเหลือ 1 นาที เพื่อให้อัปเดตไวขึ้น
def fetch_real_matches():
    try:
        url = "https://api.football-data.org/v4/matches"
        headers = { "X-Auth-Token": "da3b6a98818a4a58b29ff2d210a4dfb7" }
        response = requests.get(url, headers=headers, timeout=5)
        
        # ถ้าดึงผ่านและได้ข้อมูลปกติ
        if response.status_code == 200:
            data = response.json()
            match_list = []
            if "matches" in data and len(data["matches"]) > 0:
                for m in data["matches"][:10]:
                    raw_time = m["utcDate"]
                    clean_time = datetime.strptime(raw_time, "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y %H:%M น.")
                    match_list.append({
                        "id": m["id"],
                        "league": m["competition"]["name"],
                        "time": clean_time,
                        "home": m["homeTeam"]["name"],
                        "away": m["awayTeam"]["name"],
                        "status": m["status"],
                        "score_home": m["score"]["fullTime"]["home"] if m["score"]["fullTime"]["home"] is not None else 0,
                        "score_away": m["score"]["fullTime"]["away"] if m["score"]["fullTime"]["away"] is not None else 0
                    })
                return match_list
        
        # ถ้า Status Code ไม่ใช่ 200 (เช่น โดนบล็อกหรือโควต้าเต็ม) ให้ส่ง Error ไปที่ระบบสำรอง
        raise Exception("API Limit reached")
        
    except Exception as e:
        # 🌟 ระบบสำรอง: ถ้า API ล่ม หรือโควต้าเต็ม จะส่งคู่นี้ไปให้เล่นทันที (สถานะ UPCOMING เพื่อให้กดแทงได้)
        return [
            {"id": 901, "league": "Premier League (Backup)", "time": "คืนนี้ 22:00 น.", "home": "Arsenal", "away": "Chelsea", "status": "UPCOMING", "score_home": 0, "score_away": 0},
            {"id": 902, "league": "La Liga (Backup)", "time": "คืนนี้ 02:00 น.", "home": "Real Madrid", "away": "Barcelona", "status": "UPCOMING", "score_home": 0, "score_away": 0},
            {"id": 903, "league": "UCL (Backup)", "time": "พรุ่งนี้ 02:00 น.", "home": "Liverpool", "away": "Bayern Munich", "status": "UPCOMING", "score_home": 0, "score_away": 0}
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

# --- 4. หน้าเล่นเกมแทงบอลจริง ---
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
    st.caption("ตารางการแข่งขันดึงข้อมูลอ้างอิงแมตช์จริงนาทิต่อนาที (มีระบบสำรองเมื่อ API เต็ม)")
    st.divider()

    # เรียกใช้งานฟังก์ชันดึงตารางแข่ง
    real_matches = fetch_real_matches()

    st.subheader("📅 รายการแข่งขันวันนี้ (เปิดรับทายผล)")
    
    # วนลูปสร้างกล่องคู่แข่งขัน
    for match in real_matches:
        # เช็คสถานะล็อกปุ่ม (ถ้าขึ้น FINISHED, IN_PLAY, LIVE จะล็อกทันที)
        is_locked = match["status"] in ["FINISHED", "IN_PLAY", "LIVE"]
        status_text = "🔴 แข่งขันแล้ว/กำลังเตะ (ปิดรับแทง)" if is_locked else "🟢 เปิดรับการทายผล"
        
        with st.expander(f"🏆 [{match['league']}] {match['home']} vs {match['away']} | เวลา: {match['time']} ({status_text})"):
            st.write(f"📊 **สกอร์ในสนาม:** {match['home']} {match['score_home']} - {match['score_away']} {match['away']}")
            
            if is_locked:
                st.warning("🔒 แมตช์นี้เริ่มแข่งขันไปแล้วหรือจบลงแล้ว ระบบทำการปิดล็อกผลทายอัตโนมัติตามสัญญาณสด")
            else:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"🏠 **เจ้าบ้าน:** {match['home']}")
                    bet_home = st.button(f"🎯 เลือกฝั่ง {match['home']}", key=f"h_{match['id']}")
                with col2:
                    bet_amount = st.number_input("ใส่จำนวนแต้มที่ต้องการเดิมพัน:", min_value=10, max_value=int(user_info['points']), value=100, step=50, key=f"a_{match['id']}")
                with col3:
                    st.write(f"✈️ **ทีมเยือน:** {match['away']}")
                    bet_away = st.button(f"🎯 เลือกฝั่ง {match['away']}", key=f"v_{match['id']}")
                
                # บันทึกแต้ม
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

    # --- 5. บอร์ดรายงานประวัติการแทงบอล ---
    st.subheader("📊 ประวัติการทายผลบอลสดของสมาชิก (Live Ledger)")
    if len(st.session_state["betting_history"]) == 0:
        st.info("ยังไม่มีข้อมูลการวางเดิมพันในแมตช์จริงของวันนี้")
    else:
        history_df = pd.DataFrame(st.session_state["betting_history"])
        st.dataframe(history_df, use_container_width=True)
