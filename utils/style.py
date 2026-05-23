# Цвета согласно руководству по стилю
MAIN_BG = "#FFFFFF"
SECONDARY_BG = "#7FFF00"
ACCENT_BG = "#00FA9A"
DISCOUNT_HIGH_BG = "#2E8B57"
STOCK_ZERO_BG = "#ADD8E6"  # голубой

def get_button_style(color):
    return f"background-color: {color}; padding: 5px; border: none; border-radius: 3px;"

# Общий стиль для кнопок
BUTTON_STYLE = """
    QPushButton {
        background-color: #7FFF00;
        padding: 5px;
        border: none;
        border-radius: 3px;
    }
    QPushButton:hover {
        background-color: #6acf00;
    }
    QPushButton:pressed {
        background-color: #5aaf00;
    }
"""

ACCENT_BUTTON_STYLE = """
    QPushButton {
        background-color: #00FA9A;
        padding: 5px;
        border: none;
        border-radius: 3px;
    }
    QPushButton:hover {
        background-color: #00e089;
    }
"""