import streamlit as st
import json
import os
import hashlib
import uuid

st.set_page_config(page_title="Login Sistemi", page_icon="🔐")

# ------------------ PATH DÜZƏLİŞİ ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
TOKEN_FILE = os.path.join(BASE_DIR, "device_token.json")

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

# ------------------ TOKEN ------------------
def load_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def save_token(username):
    token_data = {
        "user": username,
        "token": str(uuid.uuid4())
    }
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(token_data, f, indent=4, ensure_ascii=False)

def delete_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)

# ------------------ ŞİFRƏ HASH ------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ------------------ QEYDİYYAT ------------------
def register_page():
    st.subheader("📝 Qeydiyyat")

    username = st.text_input("İstifadəçi adı", key="reg_user")
    password = st.text_input("Şifrə", type="password", key="reg_pass")
    confirm = st.text_input("Şifrəni təsdiqlə", type="password", key="reg_confirm")

    if st.button("Hesab yarat"):
        users = load_users()

        if not username or not password:
            st.error("Bütün sahələri doldur")
        elif username in users:
            st.error("Bu istifadəçi artıq mövcuddur")
        elif password != confirm:
            st.error("Şifrələr uyğun deyil")
        else:
            users[username] = hash_password(password)
            save_users(users)
            st.success("✅ Hesab yaradıldı! İndi giriş et")

# ------------------ GİRİŞ ------------------
def login_page():
    st.subheader("🔑 Giriş")

    username = st.text_input("İstifadəçi adı", key="login_user")
    password = st.text_input("Şifrə", type="password", key="login_pass")
    remember = st.checkbox("🖥 Bu cihazı xatırla")

    if st.button("Daxil ol"):
        users = load_users()
        hashed = hash_password(password)

        if username in users and users[username] == hashed:
            st.session_state.logged_in = True
            st.session_state.user = username

            if remember:
                save_token(username)

            st.success(f"Xoş gəldin, {username}!")
            st.rerun()
        else:
            st.error("İstifadəçi adı və ya şifrə səhvdir")

# ------------------ PANEL ------------------
def dashboard():
    st.success(f"✅ Giriş edildi: {st.session_state.user}")
    st.write("Bu test panelidir — əsas proqram burada olacaq")

    if st.button("🚪 Çıxış et"):
        st.session_state.logged_in = False
        delete_token()  # <<< BU ƏN VACİB HİSSƏDİR
        st.rerun()

# ------------------ AUTO LOGIN ------------------
def auto_login():
    token_data = load_token()
    users = load_users()

    if token_data:
        user = token_data.get("user")
        if user in users:
            st.session_state.logged_in = True
            st.session_state.user = user

# ------------------ ƏSAS ------------------
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        auto_login()

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
