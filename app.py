import streamlit as st
import core

# Настройка страницы
st.set_page_config(page_title="Resist Recipe Calculator", page_icon="🔬", layout="centered")

# Загружаем базу
db = core.load_library()

st.title("Калькулятор параметров резиста")
st.markdown("Выберите марку резиста и укажите скорость центрифугирования")

# --- БЛОК ВВОДА ---
col1, col2 = st.columns(2)

with col1:
    resist_key = st.selectbox(
        "Марка резиста:", 
        list(db.keys()),
        format_func=lambda x: db[x]["name"]
    )

# Получаем данные выбранного резиста, чтобы узнать его диапазон скоростей
resist = db[resist_key]
min_rpm = resist["min_rpm"]
max_rpm = resist["max_rpm"]

with col2:
    # Ползунок автоматически подстраивается под выбранный резист
    rpm = st.number_input(
        f"Скорость вращения (об/мин) [{min_rpm} - {max_rpm}]:", 
        min_value=min_rpm, 
        max_value=max_rpm, 
        value=min_rpm + (max_rpm - min_rpm) // 2, # По умолчанию ставим середину диапазона
        step=100
    )

if st.button("Рассчитать", type="primary", use_container_width=True):
    thickness, msg = core.calculate_thickness(resist, rpm)
    
    if thickness:
        st.success(f"### Толщина пленки: **{thickness} нм**")
        
        st.markdown("---")
        st.markdown("Технологические параметры")
        
        st.info(f"""
        **1. Нанесение**
        * **Резист:** {resist['name']}
        * **Скорость:** {rpm} об/мин
        * *Рекомендуется: {rpm} об/мин (40-45 с).*
        
        **2. Запекание**
        * **Температура:** {resist['bake_temp']} °C
        * **Время:** {resist['bake_time']} секунд
        
        **3. Проявление**
        * **Проявитель:** {resist['developer']}
        * **Время:** {resist['develop_time']}
        * *Рекомендуется проявление в чистом IPA на 30 секунд.*
        """)
    else:
        st.error(msg)
