import os
import streamlit as st

# ضبط إعدادات الصفحة بدون إيموجي
st.set_page_config(page_title="MOJ Platform", layout="wide")

# كلمة المرور
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", os.getenv("ADMIN_PASSWORD", "admin123"))

# نظام تسجيل الدخول
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("MOJ Platform")
    password_input = st.text_input("أدخل كلمة المرور:", type="password")
    if st.button("تسجيل الدخول"):
        if password_input == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("كلمة المرور غير صحيحة")
else:
    # الشريط الجانبي
    st.sidebar.title("منصة MOJ")
    st.sidebar.success("تم تسجيل الدخول بنجاح")
    
    # واجهة التطبيق والوظائف الرئيسية
    st.title("لوحة التحكم والتحليل - MOJ Platform")
    st.write("أهلاً بك! تم ربط الواجهة بنجاح، ويمكنك هنا عرض أدوات مشروعك ووظائفه.")
