import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from tensorflow.keras.models import load_model
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# إضافة مكتبة المصادقة
# ============================================================
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# ============================================================
# إعداد الصفحة
# ============================================================
st.set_page_config(
    page_title="نظام التنبؤ بالطاقة الشمسية - سوريا",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# إعداد المصادقة (Authentication)
# ============================================================

# بيانات المستخدمين المسموح لهم (يمكنك تعديلها)
hashed_passwords = stauth.Hasher(['svu2026', 'hajooz2026', 'roaa303101']).generate()

config = {
    'credentials': {
        'usernames': {
            'committee': {
                'email': 'committee@svuonline.org',
                'name': 'لجنة المناقشة',
                'password': hashed_passwords[0]
            },
            'supervisor': {
                'email': 't_mhajooz@svuonline.org',
                'name': 'د. محمد مصطفى حجوز',
                'password': hashed_passwords[1]
            },
            'roaa': {
                'email': 'roaa_303101@svuonline.org',
                'name': 'رؤى ظافر الجرف',
                'password': hashed_passwords[2]
            }
        }
    },
    'cookie': {
        'expiry_days': 30,          # مدة صلاحية الجلسة (30 يوم)
        'key': 'solar_prediction_key',
        'name': 'solar_prediction_cookie'
    },
    'preauthorized': {
        'emails': []
    }
}

# إنشاء كائن المصادقة
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# عرض واجهة تسجيل الدخول (بدون custom fields لأن الإصدار لا يدعمها)
name, authentication_status, username = authenticator.login('main')

# التحقق من حالة المصادقة
if authentication_status == False:
    st.error("❌ اسم المستخدم أو كلمة السر غير صحيحة")
    st.stop()
elif authentication_status == None:
    st.warning("🔐 الرجاء إدخال اسم المستخدم وكلمة السر للوصول إلى التطبيق")
    st.stop()
else:
    # تسجيل الدخول ناجح - نعرض رسالة ترحيب في الشريط الجانبي
    st.sidebar.success(f"✅ مرحباً {name}")
    authenticator.logout('تسجيل الخروج', 'sidebar')

# ============================================================
# باقي الكود كما هو (بدون تغيير)
# ============================================================

# تحميل الخطوط العربية CSS (كما هو)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif !important;
    }
    
    /* دعم الاتجاه من اليمين لليسار */
    .stApp {
        direction: rtl;
        text-align: right;
        background: linear-gradient(rgba(255,255,255,0.92), rgba(255,255,255,0.92)), 
                    url('https://images.unsplash.com/photo-1509391366360-2e959784a4e5?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80');
        background-size: cover;
        background-attachment: fixed;
    }
    
    /* تحسين العناوين */
    h1 {
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        color: #1e3c72 !important;
        margin-bottom: 1rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.05);
    }
    h2 {
        font-size: 2.2rem !important;
        font-weight: 600 !important;
        color: #2a5298 !important;
        margin-top: 1.5rem !important;
    }
    h3 {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        color: #333 !important;
    }
    
    /* النص العادي */
    p, li, .stMarkdown p {
        font-size: 1.1rem !important;
        line-height: 1.7 !important;
        color: #2c3e50 !important;
    }
    
    /* بطاقات إحصائية */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        text-align: center;
        margin: 10px 0;
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-card h3 {
        color: rgba(255,255,255,0.9) !important;
        font-size: 1.2rem !important;
        margin: 0;
    }
    .metric-card p {
        color: white !important;
        font-size: 2.5rem !important;
        font-weight: 700;
        margin: 5px 0 0;
    }
    
    .card1 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .card2 { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .card3 { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    .card4 { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
    
    /* التبويبات */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: rgba(255,255,255,0.8);
        backdrop-filter: blur(10px);
        padding: 10px;
        border-radius: 50px;
        margin-bottom: 20px;
        border: 1px solid rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 30px;
        background-color: transparent;
        border-radius: 50px;
        color: #495057;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white !important;
    }
    
    /* الأزرار */
    .stButton button {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s;
        width: 100%;
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
    }
    .stButton button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
    }
    
    /* حقول الإدخال */
    .stSelectbox, .stRadio, .stSlider {
        direction: rtl;
    }
    .stSelectbox label, .stRadio label, .stSlider label {
        font-size: 1.1rem !important;
        font-weight: 600;
    }
    
    /* الجداول - مهم جداً لعرض البيانات بشكل صحيح */
    .dataframe {
        font-size: 1rem !important;
        text-align: center;
        direction: ltr;
        width: 100%;
        border-collapse: collapse;
    }
    .dataframe th {
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        font-weight: 600;
    }
    .dataframe td {
        padding: 8px;
        border-bottom: 1px solid #ddd;
    }
    .dataframe tr:hover {
        background-color: #f5f5f5;
    }
    
    /* الخريطة */
    .stPlotlyChart {
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    
    /* شعار الجامعة */
    .university-logo {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .university-logo h2 {
        color: white !important;
        font-size: 2rem !important;
        margin: 10px 0;
    }
    .university-logo p {
        color: rgba(255,255,255,0.9) !important;
        font-size: 1.3rem !important;
    }
    
    /* المقاييس */
    .stMetric {
        background: rgba(255,255,255,0.8);
        backdrop-filter: blur(5px);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
    }
    .stMetric label {
        font-size: 1.1rem !important;
        font-weight: 600;
    }
    .stMetric [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700;
    }
    
    /* تنسيق حقوق النشر */
    .copyright {
        text-align: center;
        padding: 20px;
        font-size: 1.1rem;
        color: #666;
        border-top: 1px solid rgba(0,0,0,0.1);
        margin-top: 30px;
    }
    
    /* تنسيق expander */
    .streamlit-expanderHeader {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }
    
    /* تنسيق رسائل الخطأ والتحذير */
    .stAlert {
        border-radius: 15px;
        border-right: 5px solid;
        background-color: rgba(255,255,255,0.95);
        backdrop-filter: blur(10px);
        padding: 15px;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# الدوال المساعدة (كما هي)
# ============================================================
@st.cache_resource
def load_model_and_scalers(plant_name):
    model_path = f"LSTM_recursive_results/lstm_model_{plant_name}.h5"
    scalers_path = f"LSTM_recursive_results/scalers_{plant_name}.npz"
    if not os.path.exists(model_path) or not os.path.exists(scalers_path):
        return None, None, None, None
    try:
        model = load_model(model_path)
        scalers = np.load(scalers_path, allow_pickle=True)
        X_min = scalers['X_min']
        X_max = scalers['X_max']
        y_min = float(scalers['y_min'].item()) if scalers['y_min'].ndim == 0 else float(scalers['y_min'])
        y_max = float(scalers['y_max'].item()) if scalers['y_max'].ndim == 0 else float(scalers['y_max'])
        return model, X_min, X_max, y_min, y_max
    except Exception as e:
        st.error(f"خطأ في تحميل النموذج: {e}")
        return None, None, None, None

def minmax_scale_new_data(X_new, X_min, X_max):
    X_min = np.array(X_min).flatten()
    X_max = np.array(X_max).flatten()
    if X_new.shape[1] != len(X_min):
        raise ValueError(f"عدد الميزات غير متطابق: {X_new.shape[1]} != {len(X_min)}")
    range_ = X_max - X_min
    range_[range_ == 0] = 1
    return (X_new - X_min) / range_

def recursive_forecast(model, initial_sequence, future_climate, n_steps=24):
    current_seq = initial_sequence.copy()
    predictions = []
    for step in range(n_steps):
        pred_scaled = model.predict(current_seq, verbose=0)[0, 0]
        predictions.append(pred_scaled)
        new_seq = current_seq[0, 1:, :]
        climate_values = future_climate[step].reshape(1, -1)
        new_seq = np.vstack([new_seq, climate_values])
        current_seq = new_seq.reshape(1, new_seq.shape[0], -1)
    return np.array(predictions)

def inverse_scale(y_scaled, y_min, y_max):
    return y_scaled * (y_max - y_min) + y_min

# ============================================================
# دالة الخريطة (كما هي)
# ============================================================
def create_solar_map(selected_plant, plant_coords):
    syria_cities = pd.DataFrame({
        'city': ['دمشق', 'حمص', 'حلب', 'اللاذقية', 'دير الزور'],
        'lat': [33.5138, 34.7324, 36.2028, 35.5317, 35.3363],
        'lon': [36.2765, 36.7137, 37.1583, 35.7844, 40.1381],
        'ghi': [5.8, 5.7, 5.5, 5.2, 6.0],
        'capacity': ['100 MW', '60 MW', '—', '—', '—']
    })
    selected = plant_coords[selected_plant]
    
    fig = px.scatter_mapbox(
        syria_cities, 
        lat='lat', lon='lon', 
        hover_name='city',
        hover_data={'ghi': True, 'capacity': True}, 
        color='ghi',
        size=[10]*len(syria_cities), 
        color_continuous_scale='YlOrRd',
        range_color=[4.5, 6.5], 
        mapbox_style='carto-positron',
        zoom=6, 
        center={'lat': 34.8, 'lon': 38.0},
        title='خريطة الإشعاع الشمسي في سوريا (kWh/m²/يوم)'
    )
    
    # دائرة حمراء شفافة كبيرة
    fig.add_trace(go.Scattermapbox(
        lat=[selected['lat']], 
        lon=[selected['lon']],
        mode='markers',
        marker=dict(
            size=60,
            color='rgba(255, 0, 0, 0.3)',
            symbol='circle'
        ),
        hoverinfo='none',
        showlegend=False
    ))
    
    # نجمة حمراء في المركز
    fig.add_trace(go.Scattermapbox(
        lat=[selected['lat']], 
        lon=[selected['lon']],
        mode='markers',
        marker=dict(
            size=25,
            color='red',
            symbol='star'
        ),
        name=f"{selected['name']} (المحددة)",
        hovertext=f"{selected['name']} - {selected['capacity']} MW - إشعاع {selected['ghi']} kWh/m²/يوم",
        hoverinfo='text'
    ))
    
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))
    return fig

# ============================================================
# بيانات المحطات
# ============================================================
plant_options = {
    "Wadi_AlRabee": {"name": "وادي الربيع", "capacity": 100, "city": "دمشق", "lat": 33.5138, "lon": 36.2765, "ghi": 5.8},
    "Adra": {"name": "عدرا", "capacity": 10, "city": "دمشق", "lat": 33.5138, "lon": 36.2765, "ghi": 5.8},
    "Hissya": {"name": "حسياء", "capacity": 60, "city": "حمص", "lat": 34.7324, "lon": 36.7137, "ghi": 5.7}
}

# ============================================================
# الشريط الجانبي (مع إضافة زر تسجيل الخروج في أعلاه)
# ============================================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/solar-panel.png", width=80)
    st.title("☀️ نظام التنبؤ")
    st.markdown("---")
    st.markdown("### 🏭 اختر المحطة")
    selected_plant = st.selectbox(
        "المحطة",
        options=list(plant_options.keys()),
        format_func=lambda x: f"{plant_options[x]['name']} ({plant_options[x]['capacity']} MW) - {plant_options[x]['city']}"
    )
    model, X_min, X_max, y_min, y_max = load_model_and_scalers(selected_plant)
    st.markdown("---")
    st.markdown("### 📌 معلومات سريعة")
    st.info(
        f"**المحطة:** {plant_options[selected_plant]['name']}\n\n"
        f"**القدرة:** {plant_options[selected_plant]['capacity']} ميجاواط\n\n"
        f"**الموقع:** {plant_options[selected_plant]['city']}\n\n"
        f"**الإشعاع السنوي:** ≈ {plant_options[selected_plant]['ghi']} kWh/m²/يوم\n\n"
        f"**حالة النموذج:** {'✅ جاهز' if model else '❌ غير متوفر'}"
    )
    st.markdown("---")
    st.caption(f"© 2026 - رسالة ماجستير | رؤى ظافر الجرف")

# ============================================================
# التبويبات الرئيسية
# ============================================================
tabs = st.tabs([
    "🏠 الرئيسية",
    "🗺️ الخريطة الشمسية",
    "📊 تحليل البيانات",
    "🤖 التنبؤ الذكي",
    "📈 أداء النموذج",
    "ℹ️ حول المشروع"
])

# ============================================================
# التبويب 1: الرئيسية
# ============================================================
with tabs[0]:
    st.title("🌞 نظام التنبؤ بالطاقة الشمسية المتكامل")
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card card1"><h3>المحطات المدعومة</h3><p>3</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card card2"><h3>فترة البيانات</h3><p>2020-2024</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card card3"><h3>نوع النموذج</h3><p>LSTM</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card card4"><h3>الدقة (R²)</h3><p>~0.92</p></div>', unsafe_allow_html=True)
    st.markdown("---")
    with st.expander("📖 نظرة عامة على المشروع", expanded=True):
        st.markdown("""
        يهدف هذا المشروع إلى تطوير نموذج تنبؤ دقيق للطاقة الكهروضوئية في سوريا باستخدام تقنيات الذكاء الاصطناعي.
        
        **التحدي:** ندرة البيانات التشغيلية الفعلية للمحطات الشمسية في سوريا.
        
        **الحل:** منهجية مبتكرة تعتمد على:
        - بيانات مناخية عالمية من **NASA POWER** (إشعاع، حرارة، رطوبة، رياح) للفترة 2020-2024.
        - محاكاة أداء المحطات باستخدام برنامج **PVsyst** للمحطات الثلاث.
        - دمج المصادر في قاعدة بيانات موحدة ساعية.
        - تدريب نموذج **LSTM** بطبقتين للتنبؤ بإنتاج الطاقة.
        
        **النتائج:** حقق النموذج معامل تحديد R² ≈ 0.92 على بيانات الاختبار.
        """)

# ============================================================
# التبويب 2: الخريطة الشمسية
# ============================================================
with tabs[1]:
    st.title("🗺️ خريطة الإشعاع الشمسي في سوريا")
    st.markdown("---")
    st.markdown("تعرض هذه الخريطة متوسط الإشعاع الشمسي اليومي (kWh/m²/يوم) في مختلف المناطق السورية. تم تمييز موقع المحطة المختارة بدائرة حمراء ونجمة.")
    fig = create_solar_map(selected_plant, plant_options)
    st.plotly_chart(fig, use_container_width=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("الإشعاع في موقع المحطة", f"{plant_options[selected_plant]['ghi']} kWh/m²/يوم")
    with col2:
        st.metric("المعدل الوطني", "~5.6 kWh/m²/يوم", help="متوسط الإشعاع الشمسي اليومي في عموم سوريا")

# ============================================================
# التبويب 3: تحليل البيانات
# ============================================================
with tabs[2]:
    st.title("📊 تحليل البيانات الاستكشافي (EDA)")
    st.markdown("---")
    
    try:
        df = pd.read_csv("LSTM_training_dataset.csv", parse_dates=['timestamp'])
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي السجلات", f"{len(df):,}")
        with col2:
            st.metric("عدد المحطات", df['plant'].nunique())
        with col3:
            st.metric("الفترة الزمنية", f"{df['timestamp'].min().year} - {df['timestamp'].max().year}")
        st.markdown("---")
        st.subheader("📋 عينة من قاعدة البيانات")
        sample_cols = ['timestamp', 'plant', 'E_Grid'] + [c for c in df.columns if 'Glob' in c or 'T_amb' in c]
        st.dataframe(df[sample_cols].head(10), use_container_width=True)
        
        if st.button("📥 تحميل قاعدة البيانات (CSV)"):
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="⬇️ اضغط لتحميل الملف", 
                data=csv, 
                file_name="LSTM_training_dataset.csv", 
                mime="text/csv"
            )
    except:
        st.warning("لم يتم العثور على قاعدة البيانات.")
    
    st.markdown("---")
    st.subheader("📸 رسوم التحليل الاستكشافي حسب المحطة المختارة")
    
    eda_dir = "EDA_plots"
    if not os.path.exists(eda_dir):
        st.warning("⚠️ مجلد EDA_plots غير موجود.")
    else:
        all_images = [f for f in os.listdir(eda_dir) if f.endswith('.png')]
        plant_key = selected_plant
        plant_images = [img for img in all_images if img.lower().startswith(plant_key.lower())]
        
        corr_matrix_img = [img for img in all_images if 'correlation_matrix' in img.lower()]
        if corr_matrix_img:
            plant_images.extend(corr_matrix_img)
        
        if not plant_images:
            st.info(f"لا توجد صور متاحة للمحطة {plant_options[selected_plant]['name']}")
        else:
            plant_images = list(set(plant_images))
            plant_images.sort()
            
            explanations = {
                'daily_profile': {'title': 'الملف اليومي', 'desc': 'متوسط الإنتاج اليومي لكل ساعة. يظهر النمط اليومي (ذروة الظهيرة، انعدام الإنتاج ليلاً).'},
                'monthly_profile': {'title': 'الملف الشهري', 'desc': 'متوسط الإنتاج الشهري عبر السنوات. يظهر التغير الموسمي (صيف مرتفع، شتاء منخفض).'},
                'energy_distribution': {'title': 'توزيع الطاقة', 'desc': 'هيستوجرام يوضح توزيع قيم الطاقة المنتجة. التركيز عند القيم المنخفضة (ليل) وذيل طويل للقيم العالية.'},
                'energy_vs_temp': {'title': 'الطاقة مقابل درجة الحرارة', 'desc': 'علاقة الطاقة بدرجة الحرارة. غالباً ما تكون عكسية (درجات الحرارة العالية تقلل الكفاءة).'},
                'hourly_boxplot': {'title': 'مخطط الصندوق للساعات', 'desc': 'توزيع الإنتاج حسب الساعة. يظهر الوسيط والربيعات والقيم الشاذة.'},
                'correlation_matrix': {'title': 'مصفوفة الارتباط', 'desc': 'توضح قوة العلاقة بين المتغيرات المختلفة. القيم القريبة من +1 تعني ارتباط طردي قوي، ومن -1 ارتباط عكسي قوي. تساعد في اختيار الميزات الأكثر تأثيراً على الإنتاج.'},
                'energy_histogram': {'title': 'هيستوجرام الطاقة', 'desc': 'توزيع تكرار قيم الطاقة المنتجة، يوضح القيم الأكثر شيوعاً.'}
            }
            
            cols = st.columns(2)
            for i, img_file in enumerate(plant_images):
                with cols[i % 2]:
                    img_name_part = img_file.replace(plant_key+'_', '').replace('.png', '')
                    if 'correlation' in img_name_part:
                        img_type = 'correlation_matrix'
                    else:
                        matched = False
                        for key in explanations:
                            if key in img_name_part:
                                img_type = key
                                matched = True
                                break
                        if not matched:
                            img_type = img_name_part
                    
                    explanation = explanations.get(img_type, {'title': img_name_part, 'desc': ''})
                    
                    st.image(os.path.join(eda_dir, img_file), use_column_width=True)
                    st.markdown(f"**{explanation['title']}**")
                    if explanation['desc']:
                        st.markdown(f"<div class='eda-insight'>{explanation['desc']}</div>", unsafe_allow_html=True)
                    
                    if st.button(f"🔍 تكبير", key=f"expand_{i}"):
                        st.session_state['selected_image'] = img_file
                        st.session_state['show_full'] = True
                    
                    if st.session_state.get('show_full', False) and st.session_state.get('selected_image') == img_file:
                        with st.expander(f"🖼️ {img_file} - عرض كامل", expanded=True):
                            st.image(os.path.join(eda_dir, img_file), use_column_width=True)
                            with open(os.path.join(eda_dir, img_file), "rb") as f_img:
                                st.download_button(
                                    label="📥 تحميل الصورة", 
                                    data=f_img, 
                                    file_name=img_file, 
                                    mime="image/png"
                                )

# ============================================================
# التبويب 4: التنبؤ الذكي 
# ============================================================
with tabs[3]:
    st.title("🤖 التنبؤ الذكي بإنتاج الطاقة")
    st.markdown("---")
    
    if model is None:
        st.error("⚠️ النموذج غير متوفر للمحطة المختارة")
    else:
        st.success(f"✅ النموذج جاهز للمحطة: {plant_options[selected_plant]['name']}")
        
        data_source = st.radio(
            "مصدر بيانات التنبؤ:", 
            ["📁 تحميل ملف CSV جديد", "🧪 بيانات تجريبية"], 
            horizontal=True, 
            index=1
        )
        
        if data_source == "📁 تحميل ملف CSV جديد":
            uploaded_file = st.file_uploader("قم بتحميل ملف CSV يحتوي على البيانات المناخية", type=['csv'])
            if uploaded_file is not None:
                st.info("تم رفع الملف، سيتم التنبؤ بعد التأكد من البيانات...")
        else:
            st.info("سيتم استخدام آخر 48 ساعة متاحة في قاعدة البيانات كبيانات تجريبية للتنبؤ.")
            
            try:
                df_all = pd.read_csv("LSTM_training_dataset.csv", parse_dates=['timestamp'])
                df_plant = df_all[df_all['plant'] == selected_plant].sort_values('timestamp')
                
                if len(df_plant) < 48:
                    st.error(f"❌ البيانات المتاحة للمحطة {plant_options[selected_plant]['name']} أقل من 48 ساعة.")
                else:
                    # آخر 48 ساعة من البيانات
                    df_last = df_plant.tail(48)
                    
                    start_date = df_last.iloc[0]['timestamp']
                    end_date = df_last.iloc[-1]['timestamp']
                    st.info(f"📅 الفترة المستخدمة: من **{start_date.strftime('%Y-%m-%d %H:%M')}** إلى **{end_date.strftime('%Y-%m-%d %H:%M')}**")
                    
                    feature_cols = ['GlobHor', 'DiffHor', 'BeamNor', 'T_amb', 'WindVel', 'RH', 'Pressure', 'Rain']
                    X_new = df_last[feature_cols].values
                    X_scaled = minmax_scale_new_data(X_new, X_min, X_max)
                    
                    forecast_hours = st.slider(
                        "⏱️ عدد ساعات التنبؤ:", 
                        min_value=1, 
                        max_value=24, 
                        value=24, 
                        step=1
                    )
                    
                    if st.button("🚀 تشغيل التنبؤ"):
                        last_seq = X_scaled[:24].reshape(1, 24, -1)
                        future_climate = X_scaled[24:24+forecast_hours, :]
                        
                        if len(future_climate) < forecast_hours:
                            st.error("❌ لا توجد بيانات مناخية كافية للفترة المطلوبة")
                        else:
                            pred_scaled = recursive_forecast(model, last_seq, future_climate, n_steps=forecast_hours)
                            pred_energy = inverse_scale(pred_scaled, y_min, y_max)
                            actual_energy = df_last.iloc[24:24+forecast_hours]['E_Grid'].values
                            
                            absolute_errors = np.abs(pred_energy - actual_energy)
                            
                            # عرض المقاييس
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("📉 أفضل خطأ", f"{absolute_errors.min():.2f} kW")
                            with col2:
                                st.metric("📈 أقصى خطأ", f"{absolute_errors.max():.2f} kW")
                            with col3:
                                st.metric("📊 متوسط الخطأ (MAE)", f"{absolute_errors.mean():.2f} kW")
                            
                            # إنشاء جدول النتائج
                            last_timestamp = df_last.iloc[23]['timestamp']
                            forecast_timestamps = [last_timestamp + timedelta(hours=i+1) for i in range(forecast_hours)]
                            
                            results_df = pd.DataFrame({
                                'الساعة': [f"{i+1}" for i in range(forecast_hours)],
                                'التاريخ والوقت': [t.strftime('%Y-%m-%d %H:%M') for t in forecast_timestamps],
                                'الطاقة المتوقعة (kW)': [f"{x:.2f}" for x in pred_energy],
                                'الطاقة الفعلية (kW)': [f"{x:.2f}" for x in actual_energy],
                                'الخطأ المطلق (kW)': [f"{x:.2f}" for x in absolute_errors]
                            })
                            
                            # رسم بياني
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=forecast_timestamps,
                                y=pred_energy/1000,
                                mode='lines+markers',
                                name='متوقعة',
                                line=dict(color='green', width=3)
                            ))
                            fig.add_trace(go.Scatter(
                                x=forecast_timestamps,
                                y=actual_energy/1000,
                                mode='lines+markers',
                                name='فعلية',
                                line=dict(color='red', width=3, dash='dot')
                            ))
                            fig.update_layout(
                                title=f'مقارنة التوقعات مع القيم الفعلية',
                                xaxis_title='الزمن',
                                yaxis_title='الطاقة (ميجاواط)',
                                hovermode='x unified',
                                height=500
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # عرض الجدول مع تحسين التنسيق
                            with st.expander("📊 جدول الأخطاء التفصيلي", expanded=True):
                                st.dataframe(
                                    results_df,
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config={
                                        "الساعة": "الساعة",
                                        "التاريخ والوقت": "التاريخ والوقت",
                                        "الطاقة المتوقعة (kW)": "الطاقة المتوقعة (kW)",
                                        "الطاقة الفعلية (kW)": "الطاقة الفعلية (kW)",
                                        "الخطأ المطلق (kW)": "الخطأ المطلق (kW)"
                                    }
                                )
                                
                                # زر تحميل النتائج
                                csv = results_df.to_csv(index=False).encode('utf-8-sig')
                                st.download_button(
                                    label="📥 تحميل النتائج كملف CSV",
                                    data=csv,
                                    file_name=f"forecast_results_{selected_plant}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv"
                                )
            except Exception as e:
                st.error(f"خطأ في البيانات التجريبية: {str(e)}")

# ============================================================
# التبويب 5: أداء النموذج
# ============================================================
with tabs[4]:
    st.title("📈 تقييم أداء النموذج")
    st.markdown("---")
    if model is None:
        st.warning("اختر محطة أولاً")
    else:
        st.subheader(f"مقاييس الأداء للمحطة: {plant_options[selected_plant]['name']}")
        results_file = f"LSTM_recursive_results/{selected_plant}_recursive_errors_real_climate.csv"
        if os.path.exists(results_file):
            df_res = pd.read_csv(results_file)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("أفضل MAE (الساعة 1)", f"{df_res['MAE_kW_with_real_climate'].iloc[0]:.2f} kW")
            with col2:
                st.metric("أسوأ MAE (الساعة 24)", f"{df_res['MAE_kW_with_real_climate'].iloc[-1]:.2f} kW")
            with col3:
                st.metric("متوسط MAE عبر 24 ساعة", f"{df_res['MAE_kW_with_real_climate'].mean():.2f} kW")
            
            fig = px.line(
                df_res, 
                x='hour', 
                y='MAE_kW_with_real_climate', 
                title='تطور الخطأ مع أفق التنبؤ', 
                labels={'hour': 'ساعة التنبؤ', 'MAE_kW_with_real_climate': 'MAE (kW)'},
                markers=True,
                template='plotly_white'
            )
            fig.update_traces(line=dict(color='red', width=3))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد نتائج متاحة لهذه المحطة.")

# ============================================================
# التبويب 6: حول المشروع
# ============================================================
with tabs[5]:
    st.title("ℹ️ حول المشروع")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("""
        <div class="university-logo">
            <h2>SYRIAN VIRTUAL UNIVERSITY</h2>
            <p>الجامعة الافتراضية السورية</p>
        </div>
        """, unsafe_allow_html=True)
        
        if os.path.exists("svu_logo.png"):
            st.image("svu_logo.png", width=200)
    
    with col2:
        st.markdown("""
        ### مشروع ماجستير
        **بناء نموذج ذكاء اصطناعي للتنبؤ بإنتاج الطاقة الكهروضوئية في سوريا**
        
        ---
        
        **إعداد الطالبة:** رؤى ظافر الجرف  
        **إشراف:** د. محمد مصطفى حجوز  
        **الجامعة:** الجامعة الافتراضية السورية  
        **السنة:** 2026  
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 📌 تفاصيل المشروع
    
    | العنصر | الوصف |
    |--------|-------|
    | **المحطات المدروسة** | وادي الربيع (100 م.و)، عدرا (10 م.و)، حسياء (60 م.و) |
    | **مصادر البيانات** | NASA POWER (مناخ) + PVsyst (محاكاة) |
    | **الفترة الزمنية** | 2020-2024 (5 سنوات، دقة ساعية) |
    | **نوع النموذج** | LSTM بطبقتين (128 + 64 خلية) مع Dropout 0.2 |
    | **المدخلات** | الإشعاع الكلي، المباشر، المنتشر، درجة الحرارة، الرطوبة، سرعة الرياح، الضغط، الأمطار |
    | **المخرجات** | الطاقة المنتجة (كيلوواط) |
    | **التقييم** | MAE ≈ 1,200 kW (لمحطة 100 م.و)، R² ≈ 0.92 |
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 🚀 التقنيات المستخدمة
    - **Python** (Pandas, NumPy, TensorFlow/Keras, Matplotlib, Plotly)
    - **Streamlit** (واجهة المستخدم)
    - **PVsyst** (محاكاة المحطات)
    - **NASA POWER API** (البيانات المناخية)
    """)
    
    st.markdown("""
    <div class="copyright">
        © roaa_303101_MPR_S25
    </div>
    """, unsafe_allow_html=True)