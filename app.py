import streamlit as st
import core
import os
os.environ["WEBVIEW2_USER_DATA_FOLDER"] = os.path.join(os.getenv('TEMP'), 'ebl_calc_profile')

# Настройка страницы
st.set_page_config(page_title="EBL Recipe Calculator", page_icon="🔬", layout="centered")

# Загружаем базу
db = core.load_library()

st.title("🔬 Калькулятор рецептов ЭЛЛ")
st.markdown("Выберите марку резиста и укажите скорость центрифуги, чтобы получить полный технологический рецепт.")

# --- БЛОК ВВОДА ---
col1, col2 = st.columns(2)

with col1:
    resist_key = st.selectbox(
        "Выберите резист:", 
        list(db.keys()),
        format_func=lambda x: db[x]["name"]
    )

with col2:
    rpm = st.number_input(
        "Скорость вращения (об/мин):", 
        min_value=100, 
        max_value=10000, 
        value=3000, 
        step=100
    )

# --- БЛОК РАСЧЕТА ---
if st.button("Рассчитать рецепт", type="primary", use_container_width=True):
    resist = db[resist_key]
    
    thickness, msg = core.calculate_thickness(resist, rpm)
    
    if thickness:
        # Вывод толщины
        st.success(f"### Рассчитанная толщина пленки: **{thickness} нм**")
        
        # Вывод полного рецепта
        st.markdown("---")
        st.markdown("#### 📋 Технологическая карта")
        
        st.info(f"""
        **1. Нанесение (Spin Coating)**
        * **Резист:** {resist['name']}
        * **Скорость:** {rpm} об/мин
        * *Рекомендуется: 500 об/мин (5 с) для растекания, затем {rpm} об/мин (40-45 с).*
        
        **2. Запекание (Soft Bake)**
        * **Температура:** {resist['bake_temp']} °C
        * **Время:** {resist['bake_time']} секунд (на горячей плите)
        
        **3. Проявление (Development)**
        * **Проявитель:** {resist['developer']}
        * **Время:** {resist['develop_time']}
        * *Рекомендуется остановить проявление в чистом IPA на 30 секунд.*
        """)
    else:
        st.error(msg)