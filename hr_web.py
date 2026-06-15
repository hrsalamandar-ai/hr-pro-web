import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="HR_Pro Web", layout="wide")

st.title("🏢 HR_Pro - Управление на човешки ресурси")

# Странично меню
menu = st.sidebar.radio("Навигация", ["📊 Табло", "👥 Служители", "📈 Статистика", "💾 Импорт/Експорт"])

# Инициализация на данните
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

# Функция за зареждане на CSV
def load_csv(file):
    try:
        # Пробваме с различни разделители
        content = file.getvalue().decode('utf-8-sig')
        
        # Опит с автоматично откриване
        try:
            df = pd.read_csv(io.StringIO(content), sep=None, engine='python')
        except:
            # Опит със запетая
            try:
                df = pd.read_csv(io.StringIO(content), sep=',')
            except:
                # Опит с точка и запетая
                df = pd.read_csv(io.StringIO(content), sep=';')
        
        if df.empty:
            st.error("Няма данни в CSV файла")
            return None
            
        st.success(f"✅ Успешно заредени {len(df)} записа")
        return df
    except Exception as e:
        st.error(f"Грешка при зареждане: {str(e)}")
        return None

# Страница за импорт
if menu == "💾 Импорт/Експорт":
    st.header("💾 Импорт на данни от CSV")
    
    uploaded_file = st.file_uploader("Изберете CSV файл", type=['csv'])
    
    if uploaded_file:
        # Показване на предварителен преглед
        try:
            content = uploaded_file.getvalue().decode('utf-8-sig')
            st.text_area("Предварителен преглед (първи 500 символа)", content[:500], height=150)
        except:
            pass
        
        if st.button("✅ Импортирай данните"):
            df = load_csv(uploaded_file)
            if df is not None:
                st.session_state.df = df
                st.rerun()
    
    if not st.session_state.df.empty:
        st.write(f"📊 Текущо заредени: {len(st.session_state.df)} записа")

# Страница за таблица
elif menu == "👥 Служители":
    if not st.session_state.df.empty:
        st.dataframe(st.session_state.df, use_container_width=True)
    else:
        st.info("Все още няма заредени данни. Отидете на 'Импорт/Експорт' и качете CSV файл.")

# Страница за статистика
elif menu == "📈 Статистика":
    if not st.session_state.df.empty:
        st.write(f"Общ брой: {len(st.session_state.df)}")
        if 'Фирма' in st.session_state.df.columns:
            st.bar_chart(st.session_state.df['Фирма'].value_counts())
    else:
        st.info("Няма данни за статистика")

# Табло
elif menu == "📊 Табло":
    if not st.session_state.df.empty:
        st.metric("Общ брой служители", len(st.session_state.df))
    else:
        st.info("Качете CSV файл за да започнете")
