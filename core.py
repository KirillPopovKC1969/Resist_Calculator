import json
import os
import sys
from scipy.optimize import brentq

def load_library():
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    filepath = os.path.join(base_path, "library.json")
    
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_thickness(resist_data, rpm):
    if rpm < resist_data["min_rpm"] or rpm > resist_data["max_rpm"]:
        return None, f"Ошибка: скорость вне рабочего диапазона ({resist_data['min_rpm']} - {resist_data['max_rpm']} об/мин)."
    
    a, b, c, d, e = resist_data["coeffs"]
    
    thickness = a*(rpm**4) + b*(rpm**3) + c*(rpm**2) + d*rpm + e
    
    if thickness <= 0:
        return None, "Ошибка: расчет дал отрицательную или нулевую толщину. Проверьте коэффициенты."

    return round(thickness, 1), "Успешно"

def calculate_rpm_for_thickness(resist_data, target_thickness):
    # Проверяем, влезает ли желаемая толщина в диапазон этого резиста
    min_thickness, _ = calculate_thickness(resist_data, resist_data["max_rpm"])
    max_thickness, _ = calculate_thickness(resist_data, resist_data["min_rpm"])
    
    if target_thickness < min_thickness or target_thickness > max_thickness:
        return None, f"Ошибка: желаемая толщина ({target_thickness} нм) вне возможностей этого резиста. Диапазон: от {min_thickness} до {max_thickness} нм."

    # Создаем функцию, которая равна нулю, когда мы нашли нужную скорость
    def equation(rpm):
        thickness, _ = calculate_thickness(resist_data, rpm)
        return thickness - target_thickness

    try:
        # xtol=0.1 означает точность поиска по скорости 0.1 об/мин
        optimal_rpm = brentq(equation, resist_data["min_rpm"], resist_data["max_rpm"], xtol=0.1)
        return round(optimal_rpm), "Успешно"
    except Exception as e:
        return None, "Ошибка: не удалось подобрать скорость."
