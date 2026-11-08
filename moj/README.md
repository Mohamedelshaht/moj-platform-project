# منصة العقل الرقمي - وزارة العدل (FastAPI + PostgreSQL)

الواجهة العربية RTL في `static/index.html`، والخلفية في `app/main.py`.
الدخول بـ JWT وكلمات المرور مشفرة (bcrypt) والبيانات في قاعدة بيانات دائمة.
البيانات الحالية تجريبية بالكامل.

## التشغيل محليًا
    pip install -r requirements.txt
    ADMIN_PASSWORD='كلمة-قوية' uvicorn app.main:app --reload
افتح http://localhost:8000 وادخل بـ `admin`. توثيق الواجهات: `/docs`.

## الاختبار
    pip install -r requirements-dev.txt && pytest

## رفعه إلى GitHub (من حسابك)
    git init && git add . && git commit -m "first commit"
    git branch -M main
    git remote add origin https://github.com/<حسابك>/moj-platform.git
    git push -u origin main

## النشر على Render
1. أنشئ حسابًا على render.com واربطه بحساب GitHub.
2. New + ← Blueprint ← اختر المستودع (يقرأ `render.yaml` وينشئ الخدمة وقاعدة PostgreSQL).
3. عند الطلب أدخل `ADMIN_PASSWORD` (كلمة مرور المدير، 10 أحرف فأكثر).
4. بعد اكتمال النشر تحصل على رابط `https://moj-platform.onrender.com`.
ملاحظة: الخطة المجانية لقاعدة Render تنتهي بعد فترة محدودة، فاستخدم خطة مدفوعة للاستمرار.

## إنشاء مستخدمين
من `/docs` ← `POST /api/users` (بصلاحية admin)، والأدوار: مدير النظام، الإدارة المركزية، مسؤول قطاع، مسؤول محافظة/مقر، مسؤول مشروعات، مسؤول شكاوى، مسؤول أزمات، اطلاع فقط.

## حدود النسخة الحالية
- البيانات تُحفظ كوثيقة JSON واحدة في جدول `state`، وليست جداول منفصلة لكل كيان.
- الصلاحيات الدقيقة لكل وحدة تُطبَّق في الواجهة، والخادم يمنع الكتابة عن دور "اطلاع فقط" فقط.
- لا توجد واجهة لإدارة المستخدمين (فقط عبر API)، ولا حدود لمحاولات الدخول.
