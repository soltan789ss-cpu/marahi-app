import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date

# --- ضبط إعدادات الصفحة ---
st.set_page_config(
    page_title="نظام مراحي لإدارة الحلال",
    page_icon="🐐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- إضافة تنسيقات CSS الاحترافية ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"], div[data-testid="stAppViewContainer"],
    h1, h2, h3, h4, h5, h6, label, p, span, div, input, textarea, select, button {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    input, textarea, select, div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"], div[role="combobox"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 8px !important;
    }
    
    div[data-baseweb="input"] > div, 
    div[data-baseweb="textarea"] > div,
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 2px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="textarea"] > div:focus-within {
        border-color: #2E7D32 !important;
        box-shadow: 0 0 0 2px rgba(46, 125, 50, 0.2) !important;
    }
    
    input, textarea, div[data-baseweb="select"] span {
        color: #000000 !important;
        font-size: 16px !important;
        font-weight: 700 !important;
    }
    
    ::placeholder, input::placeholder, textarea::placeholder {
        color: #64748B !important;
        opacity: 1 !important;
        font-weight: 600 !important;
    }
    
    label, div[data-testid="stWidgetLabel"] p {
        font-size: 16px !important;
        font-weight: 800 !important;
        color: #0F172A !important;
    }

    .stat-card {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.06);
        border-right: 6px solid #e07a5f;
        margin-bottom: 15px;
    }
    .stat-title {
        font-size: 18px;
        color: #475569;
        font-weight: 700;
    }
    .stat-value {
        font-size: 32px;
        font-weight: 800;
        color: #0F172A;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: 800;
        font-size: 17px;
        height: 50px;
        background-color: #2E7D32;
        color: #FFFFFF !important;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1B5E20;
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- إنشاء وتجهيز قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('marahi_web.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    role TEXT)''')
                    
    c.execute('''CREATE TABLE IF NOT EXISTS pens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pen_name TEXT UNIQUE,
                    notes TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS livestock (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag_number TEXT UNIQUE,
                    tag_color TEXT,
                    secondary_id TEXT,
                    breed TEXT,
                    sex TEXT,
                    birth_date TEXT,
                    age_status TEXT,
                    weight REAL,
                    price REAL,
                    purpose TEXT,
                    status TEXT,
                    pen_id TEXT,
                    is_alive INTEGER DEFAULT 1)''')

    c.execute('''CREATE TABLE IF NOT EXISTS vaccinations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT,
                    medicine_name TEXT,
                    dose_size TEXT,
                    vacc_date TEXT,
                    target_type TEXT,
                    target_value TEXT,
                    notes TEXT)''')

    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
        c.execute("INSERT INTO users (username, password, role) VALUES ('user', 'user123', 'user')")
    
    c.execute("SELECT * FROM pens WHERE pen_name='حظيرة 1'")
    if not c.fetchone():
        c.execute("INSERT INTO pens (pen_name, notes) VALUES ('حظيرة 1', 'الحظيرة الرئيسية')")
        
    conn.commit()
    conn.close()

init_db()

# --- حفظ الجلسة وتثبيتها عند Refresh عبر Query Params الرسمية ---
query_params = st.query_params

if 'logged_in' not in st.session_state:
    if "user" in query_params and "role" in query_params:
        st.session_state['logged_in'] = True
        st.session_state['username'] = query_params["user"]
        st.session_state['user_role'] = query_params["role"]
    else:
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.session_state['user_role'] = None

# --- شاشة تسجيل الدخول ---
def login_screen():
    st.title("🔒 تسجيل الدخول - نظام مراحي")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("اسم المستخدم", placeholder="ادخل اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password", placeholder="ادخل كلمة المرور")
            submit = st.form_submit_button("دخول")
            
            if submit:
                conn = sqlite3.connect('marahi_web.db')
                c = conn.cursor()
                c.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
                user = c.fetchone()
                conn.close()
                
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.session_state['user_role'] = user[0]
                    
                    # حفظ الجلسة في عنوان URL لضمان عدم الخروج عند Refresh
                    st.query_params["user"] = username
                    st.query_params["role"] = user[0]
                    
                    st.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

if not st.session_state['logged_in']:
    login_screen()
else:
    st.sidebar.title(f"مرحباً بك، {st.session_state['username']}")
    st.sidebar.write(f"الصلاحية: **{'مدير النظام' if st.session_state['user_role'] == 'admin' else 'مستخدم عادي'}**")
    
    menu = st.sidebar.radio("الانتقال إلى:", [
        "الرئيسية والإحصائيات",
        "إضافة رأس جديد",
        "سجل التطعيمات والصيدلية",
        "إدارة الحظائر",
        "تصدير التقارير (Excel)",
        "إدارة المستخدمين"
    ])
    
    if st.sidebar.button("تسجيل الخروج"):
        st.query_params.clear()
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = None
        st.session_state['username'] = None
        st.rerun()

    conn = sqlite3.connect('marahi_web.db')
    df_pens_all = pd.read_sql_query("SELECT pen_name FROM pens", conn)
    pen_options = df_pens_all['pen_name'].tolist() if not df_pens_all.empty else ["حظيرة 1"]
    conn.close()

    # --- 1. الرئيسية والإحصائيات ---
    if menu == "الرئيسية والإحصائيات":
        st.header("📊 لوحة التحكم الرئيسية")
        today_str = datetime.now().strftime("%Y-%m-%d")
        st.caption(f"تاريخ اليوم: **{today_str}**")
        
        conn = sqlite3.connect('marahi_web.db')
        df = pd.read_sql_query("SELECT * FROM livestock WHERE is_alive=1", conn)
        conn.close()
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-card"><div class="stat-title">إجمالي الحلال</div><div class="stat-value">{len(df)} رأس</div></div>', unsafe_allow_html=True)
        with c2:
            females = len(df[df['sex'] == 'أنثى']) if not df.empty else 0
            st.markdown(f'<div class="stat-card"><div class="stat-title">الإناث</div><div class="stat-value">{females}</div></div>', unsafe_allow_html=True)
        with c3:
            males = len(df[df['sex'] == 'ذكر']) if not df.empty else 0
            st.markdown(f'<div class="stat-card"><div class="stat-title">الذكور</div><div class="stat-value">{males}</div></div>', unsafe_allow_html=True)
        with c4:
            bham = len(df[df['age_status'] == 'بهم']) if not df.empty else 0
            st.markdown(f'<div class="stat-card"><div class="stat-title">البهم</div><div class="stat-value">{bham}</div></div>', unsafe_allow_html=True)
            
        st.subheader("📋 قائمة الحلال المسجل")
        if not df.empty:
            display_df = df[['tag_number', 'tag_color', 'breed', 'sex', 'age_status', 'status', 'pen_id']]
            display_df.columns = ['رقم الحلال', 'لون الرقم', 'النوع', 'الجنس', 'السن', 'الحالة', 'الحظيرة']
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("لا يوجد حلال مسجل حالياً.")

    # --- 2. إضافة رأس جديد ---
    elif menu == "إضافة رأس جديد":
        st.header("➕ إضافة رأس جديد إلى المراح")
        
        with st.form("add_livestock_form"):
            col1, col2 = st.columns(2)
            with col1:
                tag_number = st.text_input("رقم الحلال (الأساسي)*", placeholder="مثال: 101")
                tag_color = st.selectbox("لون الرقم", ["أصفر", "أزرق", "أحمر", "أخضر", "أبيض"])
                secondary_id = st.text_input("الرقم الثانوي (اختياري)", placeholder="مثال: A-12")
                breed = st.selectbox("النوع", ["نعيمي", "نجدي", "حري", "عارضي", "سواكني", "آخر"])
                sex = st.selectbox("الجنس", ["أنثى", "ذكر"])
                birth_date = st.date_input("تاريخ الولادة", value=date.today())
                
            with col2:
                age_status = st.selectbox("السن", ["بهم", "جذع/جذعة", "ثني/ثنية", "رباع", "سديس", "جامع"])
                purpose = st.selectbox("الغرض", ["تربية", "تسمين"])
                status = st.selectbox("الحالة الحالية", ["غير منتجة", "منتجة", "مقرعة", "دافع", "غير دافع", "قريب ولادة", "مرضعة", "تسمين"])
                pen_id = st.selectbox("الحظيرة", pen_options)
                weight = st.number_input("الوزن (كجم)", value=0.0)
                price = st.number_input("السعر / التكلفة (ريال)", value=0.0)
                
            submit_add = st.form_submit_button("حفظ وإضافة")
            
            if submit_add:
                if not tag_number:
                    st.error("يرجى إدخال رقم الحلال الأساسي!")
                else:
                    try:
                        conn = sqlite3.connect('marahi_web.db')
                        c = conn.cursor()
                        c.execute('''INSERT INTO livestock 
                            (tag_number, tag_color, secondary_id, breed, sex, birth_date, age_status, weight, price, purpose, status, pen_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (tag_number, tag_color, secondary_id, breed, sex, str(birth_date), age_status, weight, price, purpose, status, pen_id))
                        conn.commit()
                        conn.close()
                        st.success(f"تمت إضافة الرأس رقم ({tag_number}) بنجاح!")
                    except sqlite3.IntegrityError:
                        st.error("رقم الحلال هذا مسجل مسبقاً، يرجى التأكد من الرقم.")

    # --- 3. سجل التطعيمات والصيدلية ---
    elif menu == "سجل التطعيمات والصيدلية":
        st.header("💉 إضافة سجل تطعيم أو علاج جديد")
        
        conn = sqlite3.connect('marahi_web.db')
        df_tags = pd.read_sql_query("SELECT tag_number FROM livestock WHERE is_alive=1", conn)
        tag_list = df_tags['tag_number'].tolist() if not df_tags.empty else []
        conn.close()

        with st.form("add_vaccine_form"):
            col1, col2 = st.columns(2)
            with col1:
                source = st.radio("مصدر العلاج", ["من الصيدلية", "خارج الصيدلية"], horizontal=True)
                medicine_name = st.text_input("اسم العلاج / التطعيم*", placeholder="مثال: تطعيم معوي، قلاعية...")
                dose_size = st.text_input("حجم الجرعة", placeholder="مثال: 2 مل")
                vacc_date = st.date_input("تاريخ الجرعة", value=date.today())
                
            with col2:
                target_type = st.selectbox("تخصيص الجرعة إلى:", ["كل الحلال", "حظيرة معينة", "رأس معين"])
                
                target_value = "الكل"
                if target_type == "حظيرة معينة":
                    target_value = st.selectbox("اختر الحظيرة", pen_options)
                elif target_type == "رأس معين":
                    if tag_list:
                        target_value = st.selectbox("اختر رقم الحلال", tag_list)
                    else:
                        target_value = st.text_input("اكتب رقم الحلال", placeholder="أدخل رقم الرأس")
                        
                notes = st.text_area("ملاحظات إضافية (اختياري)", placeholder="اكتب أي ملاحظات هنا...")
                
            submit_vacc = st.form_submit_button("تأكيد وحفظ التطعيم")
            
            if submit_vacc:
                if not medicine_name:
                    st.error("يرجى إدخال اسم العلاج أو التطعيم!")
                else:
                    conn = sqlite3.connect('marahi_web.db')
                    c = conn.cursor()
                    c.execute('''INSERT INTO vaccinations 
                        (source, medicine_name, dose_size, vacc_date, target_type, target_value, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        (source, medicine_name, dose_size, str(vacc_date), target_type, target_value, notes))
                    conn.commit()
                    conn.close()
                    st.success("تم تسجيل الجرعة / التطعيم بنجاح!")

        st.markdown("---")
        st.subheader("📋 سجل التطعيمات والعلاجات السابقة")
        conn = sqlite3.connect('marahi_web.db')
        df_vacc = pd.read_sql_query("SELECT source, medicine_name, dose_size, vacc_date, target_type, target_value, notes FROM vaccinations ORDER BY id DESC", conn)
        conn.close()
        
        if not df_vacc.empty:
            df_vacc.columns = ['المصدر', 'العلاج/التطعيم', 'الجرعة', 'التاريخ', 'التخصيص', 'المستهدف', 'ملاحظات']
            st.dataframe(df_vacc, use_container_width=True)
        else:
            st.info("لا توجد تطعيمات مسجلة سابقاً.")

    # --- 4. إدارة الحظائر ---
    elif menu == "إدارة الحظائر":
        st.header("🏠 إدارة الحظائر وتوزيع الحلال")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("➕ إضافة حظيرة جديدة")
            with st.form("add_pen_form"):
                new_pen_name = st.text_input("اسم/رقم الحظيرة الجديدة", placeholder="مثال: حظيرة 2، حظيرة الولادة")
                pen_notes = st.text_input("ملاحظات عن الحظيرة", placeholder="تفاصيل الملاحظات")
                add_pen_btn = st.form_submit_button("إضافة الحظيرة")
                
                if add_pen_btn:
                    if new_pen_name:
                        try:
                            conn = sqlite3.connect('marahi_web.db')
                            c = conn.cursor()
                            c.execute("INSERT INTO pens (pen_name, notes) VALUES (?, ?)", (new_pen_name, pen_notes))
                            conn.commit()
                            conn.close()
                            st.success(f"تمت إضافة ({new_pen_name}) بنجاح!")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("اسم هذه الحظيرة مسجل مسبقاً.")
                    else:
                        st.error("يرجى كتابة اسم أو رقم الحظيرة.")

        with col2:
            st.subheader("📊 توزيع الحلال على الحظائر")
            selected_pen = st.selectbox("اختر الحظيرة لاستعراض الحلال الموجود فيها:", pen_options)
            
            conn = sqlite3.connect('marahi_web.db')
            df_pen_animals = pd.read_sql_query("SELECT tag_number, tag_color, breed, sex, age_status, status FROM livestock WHERE pen_id=? AND is_alive=1", conn, params=(selected_pen,))
            conn.close()
            
            st.caption(f"عدد الحلال داخل **{selected_pen}**: **{len(df_pen_animals)}** رأس")
            if not df_pen_animals.empty:
                df_pen_animals.columns = ['رقم الحلال', 'لون الرقم', 'النوع', 'الجنس', 'السن', 'الحالة']
                st.dataframe(df_pen_animals, use_container_width=True)
            else:
                st.info("لا يوجد حلال مسجل في هذه الحظيرة حالياً.")

    # --- 5. تصدير التقارير ---
    elif menu == "تصدير التقارير (Excel)":
        st.header("📥 تصدير تقارير إكسل")
        conn = sqlite3.connect('marahi_web.db')
        df = pd.read_sql_query("SELECT * FROM livestock WHERE is_alive=1", conn)
        conn.close()
        
        if not df.empty:
            file_name = f"تقرير_حلال_مراحي_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
            df.to_excel(file_name, index=False)
            
            with open(file_name, "rb") as file:
                st.download_button(
                    label="⬇️ تحميل تقرير الحلال الكامل (Excel)",
                    data=file,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("لا توجد بيانات متاحة للتصدير.")

    # --- 6. إدارة المستخدمين ---
    elif menu == "إدارة المستخدمين":
        if st.session_state['user_role'] != 'admin':
            st.warning("⚠️ هذه الصفحة مخصصة لمدير النظام فقط.")
        else:
            st.header("⚙️ إدارة حسابات المستخدمين والصلاحيات")
            with st.form("new_user_form"):
                new_username = st.text_input("اسم المستخدم الجديد", placeholder="ادخل اسم المستخدم")
                new_password = st.text_input("كلمة المرور", type="password", placeholder="ادخل كلمة المرور")
                new_role = st.selectbox("الصلاحية", ["user", "admin"], format_func=lambda x: "مستخدم عادي" if x == 'user' else "مدير النظام")
                add_user_btn = st.form_submit_button("إنشاء الحساب")
                
                if add_user_btn:
                    if new_username and new_password:
                        try:
                            conn = sqlite3.connect('marahi_web.db')
                            c = conn.cursor()
                            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (new_username, new_password, new_role))
                            conn.commit()
                            conn.close()
                            st.success(f"تم إنشاء حساب للمستخدم ({new_username}) بنجاح!")
                        except sqlite3.IntegrityError:
                            st.error("اسم المستخدم هذا مسجل مسبقاً.")