import streamlit as st
import json
import os
import hashlib

st.set_page_config(page_title="Login Sistemi", page_icon="🔐")

USERS_FILE = "users.json"

# ------------------ USER YÜKLƏ ------------------
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

# ------------------ ŞİFRƏ HASH ------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ------------------ QEYDİYYAT ------------------
def register_page():
    st.subheader("📝 Qeydiyyat")

    username = st.text_input("İstifadəçi adı", key="reg_user")
    password = st.text_input("Şifrə", type="password", key="reg_pass")
    confirm = st.text_input("Şifrəni təsdiqlə", type="password", key="reg_confirm")

    if st.button("Hesab yarat", key="reg_btn"):
        users = load_users()

        if not username or not password:
            st.error("Bütün sahələri doldur")
        elif username in users:
            st.error("Bu istifadəçi artıq mövcuddur")
        elif password != confirm:
            st.error("Şifrələr uyğun deyil")
        elif len(password) < 4:
            st.error("Şifrə minimum 4 simvol olmalıdır")
        else:
            users[username] = hash_password(password)
            save_users(users)
            st.success("✅ Hesab yaradıldı! İndi giriş et")

# ------------------ GİRİŞ ------------------
def login_page():
    st.subheader("🔑 Giriş")

    username = st.text_input("İstifadəçi adı", key="login_user")
    password = st.text_input("Şifrə", type="password", key="login_pass")

    if st.button("Daxil ol", key="login_btn"):
        users = load_users()
        hashed = hash_password(password)

        if username in users and users[username] == hashed:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success(f"Xoş gəldin, {username}!")
            st.rerun()
        else:
            st.error("İstifadəçi adı və ya şifrə səhvdir")

# ------------------ PANEL ------------------
def dashboard():
    st.success(f"✅ Giriş edildi: {st.session_state.user}")
    st.write("Bu test panelidir — əsas proqram burada olacaq")

    if st.button("Çıxış et", key="logout_btn"):
        st.session_state.logged_in = False
        st.rerun()

# ------------------ ƏSAS ------------------
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    st.title("🔐 İstifadəçi Sistemi (Müstəqil Test)")

    if st.session_state.logged_in:
        dashboard()
    else:
        tab1, tab2 = st.tabs(["Giriş", "Qeydiyyat"])
        with tab1:
            login_page()
        with tab2:
            register_page()

if __name__ == "__main__":
    main()
