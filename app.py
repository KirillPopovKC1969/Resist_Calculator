import streamlit as st
import core

st.set_page_config(page_title="Resist Recipe Calculator", page_icon="🔬", layout="centered")

db = core.load_library()

st.title("Калькулятор параметров резиста")

# --- ВЫБОР РЕЖИМА РАБОТЫ ---
mode = st.radio(
    "Что вы хотите рассчитать?",
    ["Толщину через скорость", "Скорость через толщину"],
    horizontal=True
)

col1, col2 = st.columns(2)

with col1:
    resist_key = st.selectbox(
        "Марка резиста:", 
        list(db.keys()),
        format_func=lambda x: db[x]["name"]
    )

resist = db[resist_key]
min_rpm = resist["min_rpm"]
max_rpm = resist["max_rpm"]

# --- ЛОГИКА В ЗАВИСИМОСТИ ОТ РЕЖИМА ---
if mode == "Толщину через скорость":
    with col2:
        rpm = st.number_input(
            f"Скорость вращения (об/мин) [{min_rpm} - {max_rpm}]:", 
            min_value=min_rpm, max_value=max_rpm, 
            value=min_rpm + (max_rpm - min_rpm) // 2, step=100
        )
    
    if st.button("Рассчитать рецепт", type="primary", use_container_width=True):
        thickness, msg = core.calculate_thickness(resist, rpm)
        if thickness:
            st.session_state['final_rpm'] = rpm
            st.session_state['final_thickness'] = thickness
        else:
            st.error(msg)

else: # Режим "Скорость через толщину"
    with col2:
        # Вычисляем границы толщин для этого резиста
        thickness_at_min_rpm, _ = core.calculate_thickness(resist, min_rpm)
        thickness_at_max_rpm, _ = core.calculate_thickness(resist, max_rpm)
        
        # Выводим подсказку для пользователя
        st.info(f"Для этого резиста доступна толщина от **{thickness_at_max_rpm}** до **{thickness_at_min_rpm}** нм.")
        
        # Ставим значение по умолчанию (середину диапазона), чтобы было удобнее
        default_thickness = int((thickness_at_min_rpm + thickness_at_max_rpm) / 2)
        
        target_thickness = st.number_input(
            "Желаемая толщина (нм):", 
            min_value=1, max_value=20000, value=default_thickness, step=10
        )
    
    if st.button("Подобрать скорость", type="primary", use_container_width=True):
        rpm, msg = core.calculate_rpm_for_thickness(resist, target_thickness)
        if rpm:
            st.session_state['final_rpm'] = rpm
            exact_thickness, _ = core.calculate_thickness(resist, rpm)
            st.session_state['final_thickness'] = exact_thickness
        else:
            st.error(msg)

# --- ВЫВОД РЕЗУЛЬТАТА (общий для обоих режимов) ---
if 'final_rpm' in st.session_state:
    st.success(f"### Необходимая скорость: **{st.session_state['final_rpm']} об/мин**")
    st.info(f"Расчетная толщина пленки: {st.session_state['final_thickness']} нм")
    
    st.markdown("---")
    st.markdown("Технологические параметры")
    
    st.info(f"""
    **1. Нанесение**
    * **Резист:** {resist['name']}
    * **Скорость:** {st.session_state['final_rpm']} об/мин
    * *Рекомендуется: {st.session_state['final_rpm']} об/мин (40-45 с).*
    
    **2. Запекание**
    * **Температура:** {resist['bake_temp']} °C
    * **Время:** {resist['bake_time']} секунд
    
    **3. Проявление**
    * **Проявитель:** {resist['developer']}
    * **Время:** {resist['develop_time']}
    * *Рекомендуется после проявителя промыть образец в чистом IPA в течение 30 секунд для остановки реакции.*
    """)
