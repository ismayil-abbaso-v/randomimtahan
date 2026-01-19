import streamlit as st
import json
import bcrypt
import os

st.set_page_config(page_title="İstifadəçi Girişi", page_icon="🔐")

USERS_FILE = "users.json"

# ---------------- FAYL YOXLA ----------------
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ---------------- ŞİFRƏ ----------------
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# ---------------- QEYDİYYAT ----------------
def register_page():
    st.subheader("📝 Qeydiyyat")

    username = st.text_input("İstifadəçi adı")
    password = st.text_input("Şifrə", type="password")
    confirm = st.text_input("Şifrəni təsdiqlə", type="password")

    if st.button("Hesab yarat"):
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
            st.success("Hesab yaradıldı! İndi giriş et")

# ---------------- GİRİŞ ----------------
def login_page():
    st.subheader("🔑 Giriş")

    username = st.text_input("İstifadəçi adı")
    password = st.text_input("Şifrə", type="password")

    if st.button("Daxil ol"):
        users = load_users()

        if username in users and check_password(password, users[username]):
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
            st.success(f"Xoş gəldin, {username}!")
            st.rerun()
        else:
            st.error("İstifadəçi adı və ya şifrə səhvdir")

# ---------------- PANEL ----------------
def dashboard():
    st.success(f"✅ Sistemə giriş edildi: {st.session_state['user']}")
    st.write("Bura sənin əsas proqramunun test sahəsi olacaq")

    if st.button("Çıxış et"):
        st.session_state["logged_in"] = False
        st.rerun()

# ---------------- ƏSAS ----------------
def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    st.title("🔐 İstifadəçi Sistemi (Test)")

    if st.session_state["logged_in"]:
        dashboard()
    else:
        tab1, tab2 = st.tabs(["Giriş", "Qeydiyyat"])
        with tab1:
            login_page()
        with tab2:
            register_page()

if __name__ == "__main__":
    main()
