# -*- coding: utf-8 -*-
# HR_Pro Web v1.0 - Уеб базирана версия на HR Pro v4.7

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Конфигурация на страницата
st.set_page_config(
    page_title="HR_Pro Web",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Инициализация на session state
def init_session_state():
    if 'employees_df' not in st.session_state:
        try:
            # Опит за зареждане на съществуващ CSV файл
            if os.path.exists('employees.csv'):
                st.session_state.employees_df = pd.read_csv('employees.csv')
            else:
                # Създаване на празен DataFrame със структурата от оригиналното приложение
                st.session_state.employees_df = pd.DataFrame(columns=[
                    'ID', 'Име', 'Фирма', 'ЕГН', 'Дата на раждане',
                    'Телефон', 'Имейл', 'Адрес', 'Длъжност',
                    '№ на договор', 'Дата на договор', '№ на заповед',
                    'Дата на заповед', 'Заплата', 'Статус', 'Бележки'
                ])
        except Exception as e:
            st.error(f"Грешка при зареждане на данните: {e}")
            st.session_state.employees_df = pd.DataFrame(columns=[
                'Име', 'Фирма', 'Телефон', 'Имейл', 'Длъжност'
            ])
    
    if 'firms_list' not in st.session_state:
        st.session_state.firms_list = ["АСО", "АСО ФЛ", "СГХ1"]
    
    if 'status_list' not in st.session_state:
        st.session_state.status_list = ["Активен", "В изпитателен срок", "В отпуск", "Напускащ", "Напуснал", "Изтекъл договор"]

# Запазване на данните
def save_data():
    try:
        st.session_state.employees_df.to_csv('employees.csv', index=False, encoding='utf-8-sig')
        # Създаване на backup
        backup_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.employees_df.to_csv(f'backup_{backup_date}.csv', index=False, encoding='utf-8-sig')
        return True
    except Exception as e:
        st.error(f"Грешка при запис: {e}")
        return False

# Импорт от CSV
def import_csv(file):
    try:
        df = pd.read_csv(file)
        st.session_state.employees_df = df
        save_data()
        return True, f"Импортирани {len(df)} записа"
    except Exception as e:
        return False, str(e)

# Експорт към CSV
def export_csv():
    return st.session_state.employees_df.to_csv(index=False, encoding='utf-8-sig')

# Статистики
def show_statistics():
    if st.session_state.employees_df.empty:
        st.info("Няма данни за статистика")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Общо служители", len(st.session_state.employees_df))
    
    with col2:
        active = len(st.session_state.employees_df[st.session_state.employees_df['Статус'] == 'Активен']) if 'Статус' in st.session_state.employees_df else len(st.session_state.employees_df)
        st.metric("✅ Активни", active)
    
    with col3:
        if 'Фирма' in st.session_state.employees_df.columns:
            firms = st.session_state.employees_df['Фирма'].nunique()
        else:
            firms = 0
        st.metric("🏢 Фирми", firms)
    
    with col4:
        st.metric("📅 Дата", datetime.now().strftime("%d.%m.%Y"))
    
    st.markdown("---")
    
    # Графики
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Фирма' in st.session_state.employees_df.columns and not st.session_state.employees_df.empty:
            firm_counts = st.session_state.employees_df['Фирма'].value_counts()
            fig = px.pie(values=firm_counts.values, names=firm_counts.index, title="Разпределение по фирми")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'Статус' in st.session_state.employees_df.columns and not st.session_state.employees_df.empty:
            status_counts = st.session_state.employees_df['Статус'].value_counts()
            fig = px.bar(x=status_counts.index, y=status_counts.values, title="Статус на служителите")
            st.plotly_chart(fig, use_container_width=True)

# Страница за управление на служители
def manage_employees():
    st.subheader("👥 Управление на служители")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Списък", "➕ Добави", "✏️ Редактирай", "🗑️ Изтрий"])
    
    with tab1:
        # Търсене и филтриране
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("🔍 Търсене", placeholder="Търсене по име, фирма, телефон...")
        with col2:
            if st.button("🔄 Изчисти филтър"):
                search = ""
                st.rerun()
        
        # Филтриране
        if search:
            mask = st.session_state.employees_df.apply(
                lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1
            )
            filtered_df = st.session_state.employees_df[mask]
            st.info(f"Намерени {len(filtered_df)} резултата")
        else:
            filtered_df = st.session_state.employees_df
        
        if not filtered_df.empty:
            st.dataframe(filtered_df, use_container_width=True, height=400)
            
            # Експорт на филтрираните данни
            csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Изтегли CSV (филтрирани данни)",
                data=csv,
                file_name=f"employees_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Няма данни за показване")
    
    with tab2:
        with st.form("add_employee_form", clear_on_submit=True):
            st.markdown("### 📝 Основна информация")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Име *")
                firm = st.selectbox("Фирма *", st.session_state.firms_list)
                egc = st.text_input("ЕГН")
                birth_date = st.date_input("Дата на раждане", value=None)
                phone = st.text_input("Телефон")
            
            with col2:
                email = st.text_input("Имейл")
                position = st.text_input("Длъжност")
                salary = st.number_input("Заплата (лв.)", min_value=0, value=0, step=50)
                status = st.selectbox("Статус", st.session_state.status_list)
            
            st.markdown("### 📄 Договорна информация")
            col3, col4 = st.columns(2)
            with col3:
                contract_number = st.text_input("№ на договор")
                contract_date = st.date_input("Дата на договор", value=None)
            with col4:
                order_number = st.text_input("№ на заповед")
                order_date = st.date_input("Дата на заповед", value=None)
            
            address = st.text_area("Адрес")
            notes = st.text_area("Бележки")
            
            st.markdown("---")
            submitted = st.form_submit_button("✅ Добави служител", use_container_width=True)
            
            if submitted:
                if not name or not firm:
                    st.error("Моля, попълнете задължителните полета (Име и Фирма)")
                else:
                    new_id = len(st.session_state.employees_df) + 1
                    new_row = pd.DataFrame({
                        'ID': [new_id],
                        'Име': [name],
                        'Фирма': [firm],
                        'ЕГН': [egc],
                        'Дата на раждане': [birth_date if birth_date else ''],
                        'Телефон': [phone],
                        'Имейл': [email],
                        'Адрес': [address],
                        'Длъжност': [position],
                        '№ на договор': [contract_number],
                        'Дата на договор': [contract_date if contract_date else ''],
                        '№ на заповед': [order_number],
                        'Дата на заповед': [order_date if order_date else ''],
                        'Заплата': [salary],
                        'Статус': [status],
                        'Бележки': [notes]
                    })
                    st.session_state.employees_df = pd.concat([st.session_state.employees_df, new_row], ignore_index=True)
                    if save_data():
                        st.success(f"✅ {name} е добавен успешно!")
                        st.rerun()
    
    with tab3:
        if not st.session_state.employees_df.empty:
            employee_list = st.session_state.employees_df['Име'].tolist()
            employee_to_edit = st.selectbox("Изберете служител за редакция", employee_list)
            
            if employee_to_edit:
                employee_data = st.session_state.employees_df[st.session_state.employees_df['Име'] == employee_to_edit].iloc[0]
                
                with st.form("edit_employee_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_name = st.text_input("Име", employee_data.get('Име', ''))
                        new_firm = st.selectbox("Фирма", st.session_state.firms_list, 
                                               index=st.session_state.firms_list.index(employee_data.get('Фирма', 'АСО')) if employee_data.get('Фирма', 'АСО') in st.session_state.firms_list else 0)
                        new_phone = st.text_input("Телефон", employee_data.get('Телефон', ''))
                        new_email = st.text_input("Имейл", employee_data.get('Имейл', ''))
                    
                    with col2:
                        new_position = st.text_input("Длъжност", employee_data.get('Длъжност', ''))
                        new_salary = st.number_input("Заплата (лв.)", value=float(employee_data.get('Заплата', 0)) if employee_data.get('Заплата', 0) else 0, step=50)
                        new_status = st.selectbox("Статус", st.session_state.status_list,
                                                 index=st.session_state.status_list.index(employee_data.get('Статус', 'Активен')) if employee_data.get('Статус', 'Активен') in st.session_state.status_list else 0)
                    
                    new_contract_number = st.text_input("№ на договор", employee_data.get('№ на договор', ''))
                    new_order_number = st.text_input("№ на заповед", employee_data.get('№ на заповед', ''))
                    new_notes = st.text_area("Бележки", employee_data.get('Бележки', ''))
                    
                    if st.form_submit_button("💾 Запази промените"):
                        st.session_state.employees_df.loc[st.session_state.employees_df['Име'] == employee_to_edit, 'Име'] = new_name
                        st.session_state.employees_df.loc[st.session_state.employees_df['Име'] == new_name, 'Фирма'] = new_firm
                        st.session_state.employees_df.loc[st.session_state.employees_df['Име'] == new_name, 'Телефон'] = new_phone
                        st.session_state.employees_df.loc[st.session_state.employees_df['Име'] == new_name, 'Имейл'] = new_email
                        st.session_state.employees_df.loc[st.session_state.employees_df['Име'] == new_name, 'Длъжност'] = new_position
                        st.session_state.employees_df.loc[st.session_state.employees_df['Име'] == new_name, 'Заплата'] = new_salary
                        st.session_state.employees_df.loc[st.session_state.employees_df['Име'] == new_name, 'Статус'] = new_status
                        st.session_state.employees_df.loc[st.session_state.employees_df['Име'] == new_name, '№ на договор'] = new_contract_number
                        st.session_state.employees_df.loc[st.session_state.employees_df['Име'] == new_name, '№ на заповед'] = new_order_number
                        st.session_state.employees_df.loc[st.session_state.employees_df['Име'] == new_name, 'Бележки'] = new_notes
                        
                        if save_data():
                            st.success("✅ Промените са запазени!")
                            st.rerun()
        else:
            st.info("Няма служители за редакция")
    
    with tab4:
        if not st.session_state.employees_df.empty:
            employee_to_delete = st.selectbox("Изберете служител за изтриване", st.session_state.employees_df['Име'].tolist())
            
            if employee_to_delete:
                st.warning(f"⚠️ Сигурни ли сте, че искате да изтриете {employee_to_delete}?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Да, изтрий", use_container_width=True):
                        st.session_state.employees_df = st.session_state.employees_df[st.session_state.employees_df['Име'] != employee_to_delete]
                        if save_data():
                            st.success(f"✅ {employee_to_delete} е изтрит успешно!")
                            st.rerun()
                with col2:
                    if st.button("❌ Отказ", use_container_width=True):
                        st.rerun()
        else:
            st.info("Няма служители за изтриване")

# Страница за импорт/експорт
def import_export():
    st.subheader("💾 Импорт и Експорт на данни")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Експорт")
        if st.button("📥 Експортирай всички данни"):
            csv = export_csv()
            st.download_button(
                label="💾 Изтегли CSV файл",
                data=csv,
                file_name=f"hr_pro_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        if st.button("💾 Ръчен Backup"):
            if save_data():
                st.success(f"✅ Backup създаден успешно в {datetime.now().strftime('%H:%M:%S')}")
    
    with col2:
        st.markdown("### 📥 Импорт")
        uploaded_file = st.file_uploader("Изберете CSV файл за импорт", type=['csv'])
        
        if uploaded_file:
            try:
                df_preview = pd.read_csv(uploaded_file)
                st.write("**Предварителен преглед:**")
                st.dataframe(df_preview.head(), use_container_width=True)
                
                if st.button("✅ Импортирай данните", use_container_width=True):
                    success, message = import_csv(uploaded_file)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(f"Грешка: {message}")
            except Exception as e:
                st.error(f"Невалиден CSV файл: {e}")
    
    st.markdown("---")
    st.markdown("### 📊 Статистика на данните")
    if not st.session_state.employees_df.empty:
        st.write(f"**Общо записи:** {len(st.session_state.employees_df)}")
        st.write(f"**Колони:** {', '.join(st.session_state.employees_df.columns)}")

# Страница за настройки
def settings():
    st.subheader("⚙️ Настройки на системата")
    
    st.markdown("### ℹ️ Информация за системата")
    st.info("""
    **HR_Pro Web v1.0**
    - Базирано на HR_Pro v4.7
    - Пълна уеб версия за достъп от всякъде
    - Поддържани фирми: АСО, АСО ФЛ, СГХ1
    
    **Функционалности:**
    - ✅ Управление на служители (CRUD)
    - ✅ Търсене и филтриране
    - ✅ Статистика и графики
    - ✅ Импорт/Експорт на CSV
    - ✅ Автоматичен backup
    - ✅ Мултифирмен режим
    """)
    
    st.markdown("### 🎨 Външен вид")
    theme = st.selectbox("Тема", ["Светла", "Тъмна"])
    if theme == "Тъмна":
        st.markdown("""
        <style>
        .stApp {
            background-color: #0E1117;
            color: #FFFFFF;
        }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("### 💾 Управление на данните")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Презареждане на данните"):
            try:
                if os.path.exists('employees.csv'):
                    st.session_state.employees_df = pd.read_csv('employees.csv')
                    st.success("Данните са презаредени успешно!")
                    st.rerun()
                else:
                    st.warning("Няма запазени данни")
            except Exception as e:
                st.error(f"Грешка: {e}")
    
    with col2:
        if st.button("🗑️ Изчистване на всички данни", type="secondary"):
            st.warning("⚠️ Това действие ще изтрие ВСИЧКИ данни!")
            if st.button("Потвърди изтриване", type="primary"):
                st.session_state.employees_df = pd.DataFrame(columns=st.session_state.employees_df.columns)
                save_data()
                st.success("Всички данни са изчистени")
                st.rerun()

# Основна функция
def main():
    init_session_state()
    
    # Странично меню
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/employees.png", width=80)
        st.title("HR_Pro Web")
        st.markdown("---")
        
        menu = st.radio(
            "**Навигация**",
            ["🏠 Табло", "👥 Служители", "📈 Статистика", "💾 Импорт/Експорт", "⚙️ Настройки", "❓ Помощ"],
            index=0
        )
        
        st.markdown("---")
        st.caption(f"Версия: 1.0\nДата: {datetime.now().strftime('%d.%m.%Y')}")
    
    # Страници
    if menu == "🏠 Табло":
        st.title("🏠 HR_Pro - Уеб система за управление на човешки ресурси")
        show_statistics()
    
    elif menu == "👥 Служители":
        manage_employees()
    
    elif menu == "📈 Статистика":
        st.title("📈 Статистика и анализ")
        show_statistics()
        
        if not st.session_state.employees_df.empty:
            st.markdown("---")
            st.subheader("📊 Детайлен анализ")
            
            if 'Заплата' in st.session_state.employees_df.columns:
                fig = px.histogram(st.session_state.employees_df, x='Заплата', nbins=20, title="Разпределение на заплатите")
                st.plotly_chart(fig, use_container_width=True)
    
    elif menu == "💾 Импорт/Експорт":
        import_export()
    
    elif menu == "⚙️ Настройки":
        settings()
    
    elif menu == "❓ Помощ":
        st.title("❓ Помощ и документация")
        st.markdown("""
        ### 📖 Как да използвате HR_Pro Web
        
        **1. Добавяне на служител**
        - Отидете в "Служители" -> "Добави"
        - Попълнете информацията
        - Натиснете "Добави служител"
        
        **2. Търсене на служител**
        - Използвайте полето за търсене в списъка със служители
        
        **3. Редактиране**
        - Изберете служител от "Редактирай"
        - Променете необходимата информация
        - Запазете промените
        
        **4. Импорт/Експорт**
        - CSV формат с разделител запетая
        - UTF-8 encoding
        
        **5. Backup**
        - Автоматичен backup при всяко запазване
        - Ръчен backup от меню "Импорт/Експорт"
        """)

if __name__ == "__main__":
    main()
