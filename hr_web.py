import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

st.set_page_config(page_title="HR_Pro Web", layout="wide")

# Инициализация
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

# Функция за зареждане на CSV
def load_csv(file):
    try:
        content = file.getvalue().decode('utf-8-sig')
        # Опит с автоматично откриване на разделителя
        try:
            df = pd.read_csv(io.StringIO(content), sep=None, engine='python')
        except:
            try:
                df = pd.read_csv(io.StringIO(content), sep=',')
            except:
                df = pd.read_csv(io.StringIO(content), sep=';')
        return df
    except Exception as e:
        st.error(f"Грешка: {e}")
        return None

# Странично меню
st.sidebar.title("🏢 HR_Pro Web")
menu = st.sidebar.radio(
    "Навигация",
    ["📊 Табло", "👥 Служители", "📈 Статистика", "💾 Импорт/Експорт", "⚙️ Настройки"]
)

# ==================== ТАБЛО ====================
if menu == "📊 Табло":
    st.title("🏠 Табло")
    
    if not st.session_state.df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Общо служители", len(st.session_state.df))
        with col2:
            if 'Фирма' in st.session_state.df.columns:
                st.metric("🏢 Брой фирми", st.session_state.df['Фирма'].nunique())
        with col3:
            st.metric("📅 Дата", datetime.now().strftime("%d.%m.%Y"))
        
        st.info("✅ Данните са заредени успешно!")
    else:
        st.info("📂 Все още няма заредени данни. Отидете на 'Импорт/Експорт' за да качите CSV файл.")

# ==================== СЛУЖИТЕЛИ С ТЪРСАЧКА ====================
elif menu == "👥 Служители":
    st.title("👥 Управление на служители")
    
    if not st.session_state.df.empty:
        # ТЪРСАЧКА
        st.subheader("🔍 Търсене")
        search = st.text_input("Търсене по име, ЕГН, фирма или телефон", placeholder="Въведете текст...")
        
        # Филтриране
        if search:
            mask = st.session_state.df.astype(str).apply(
                lambda row: row.str.contains(search, case=False, na=False).any(), axis=1
            )
            filtered_df = st.session_state.df[mask]
            st.info(f"📊 Намерени {len(filtered_df)} резултата")
        else:
            filtered_df = st.session_state.df
        
        # Показване на таблица
        st.subheader("📋 Списък със служители")
        st.dataframe(filtered_df, use_container_width=True, height=500)
        
        # Експорт на филтрираните данни
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Изтегли CSV (филтрирани данни)", csv, "employees_export.csv", "text/csv")
    else:
        st.info("Няма заредени данни. Моля, качете CSV файл от 'Импорт/Експорт'.")

# ==================== СТАТИСТИКА ====================
elif menu == "📈 Статистика":
    st.title("📈 Статистика и анализ")
    
    if not st.session_state.df.empty:
        st.write(f"**Общ брой служители:** {len(st.session_state.df)}")
        
        if 'Фирма' in st.session_state.df.columns:
            st.subheader("📊 Разпределение по фирми")
            firm_counts = st.session_state.df['Фирма'].value_counts()
            fig = px.pie(values=firm_counts.values, names=firm_counts.index, title="Служители по фирми")
            st.plotly_chart(fig, use_container_width=True)
        
        if 'Статус' in st.session_state.df.columns:
            st.subheader("📈 Разпределение по статус")
            status_counts = st.session_state.df['Статус'].value_counts()
            st.bar_chart(status_counts)
    else:
        st.info("Няма данни за статистика")

# ==================== ИМПОРТ/ЕКСПОРТ ====================
elif menu == "💾 Импорт/Експорт":
    st.title("💾 Импорт и Експорт на данни")
    
    # Импорт
    st.subheader("📥 Импорт от CSV")
    uploaded_file = st.file_uploader("Изберете CSV файл", type=['csv'])
    
    if uploaded_file:
        if st.button("✅ Импортирай данните"):
            df = load_csv(uploaded_file)
            if df is not None and not df.empty:
                st.session_state.df = df
                st.success(f"✅ Успешно импортирани {len(df)} записа!")
                st.rerun()
    
    # Експорт
    if not st.session_state.df.empty:
        st.subheader("📤 Експорт на данни")
        csv = st.session_state.df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Изтегли CSV файл", csv, "hr_export.csv", "text/csv")
        
        st.info(f"📊 Текущо заредени: {len(st.session_state.df)} записа")

# ==================== НАСТРОЙКИ ====================
elif menu == "⚙️ Настройки":
    st.title("⚙️ Настройки")
    
    if not st.session_state.df.empty:
        if st.button("🗑️ Изчисти всички данни"):
            st.session_state.df = pd.DataFrame()
            st.success("Данните са изчистени!")
            st.rerun()
    
    st.info("""
    **HR_Pro Web v1.0**
    
    - Базирано на HR_Pro v4.7
    - Поддържа CSV файлове с разделители: запетая (,) или точка и запетая (;)
    - Търсене във всички колони
    - Експорт на филтрирани данни
    """)
