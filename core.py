import json
import os
import sys

def load_library():
    if getattr(sys, 'frozen', False):
        # Если это собранный .exe:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        # Если запуск из исходников в VS Code:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    filepath = os.path.join(base_path, "library.json")
    
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_thickness(resist_data, rpm):
    # 1. Проверка диапазона скоростей
    if rpm < resist_data["min_rpm"] or rpm > resist_data["max_rpm"]:
        return None, f"Ошибка: скорость вне рабочего диапазона ({resist_data['min_rpm']} - {resist_data['max_rpm']} об/мин)."
    
    a, b, c, d, e = resist_data["coeffs"]
    
    thickness = a*(rpm**4) + b*(rpm**3) + c*(rpm**2) + d*rpm + e
    
    if thickness <= 0:
        return None, "Ошибка: расчет дал отрицательную или нулевую толщину. Проверьте коэффициенты."

    return round(thickness, 1), "Успешно"

#def calculate_develop_time(resist_data, thickness):
    # t = k*d + b (линейная интерполяция)
    # Если коэффициентов нет, возвращаем заглушку
#    k = resist_data.get("dev_k")
#    b = resist_data.get("dev_b")
    
#    if k is not None and b is not None:
#        time = k * thickness + b
#        return round(time, 0)
#    return None