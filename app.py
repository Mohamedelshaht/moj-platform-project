import os
import streamlit as st

st.set_page_config(page_title="MOJ Platform", page_icon="🚀", layout="wide")

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", os.getenv("ADMIN_PASSWORD", "admin123"))

st.title("MOJ Platform 🚀")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password_input = st.text_input("أدخل كلمة المرور:", type="password")
    if st.button("تسجيل الدخول"):
        if password_input == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("كلمة المرور غير صحيحة")
else:
    st.success("تم تسجيل الدخول بنجاح!")
    st.write("أهلاً بك في منصة MOJ")
