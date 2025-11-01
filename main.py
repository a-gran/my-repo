"""
Главный файл для запуска виртуальной клавиатуры
Точка входа в приложение
"""

# Импортируем модуль tkinter для создания графического интерфейса
import tkinter as tk

# Импортируем класс UIConfig с настройками интерфейса из пакета keyboard
from keyboard.config import UIConfig
# Импортируем класс LayoutManager для управления раскладками клавиатуры
from keyboard.manager import LayoutManager


class VirtualKeyboardApp:
    """Главное приложение виртуальной клавиатуры"""

    def __init__(self):
        """
        Инициализация приложения
        Создаёт главное окно и запускает менеджер раскладок
        """
        # Создаём главное окно приложения
        self.root = self._create_window()
        # Создаём менеджер раскладок, передавая ему главное окно
        self.manager = LayoutManager(self.root)
        # Создаём начальную визуализацию клавиатуры
        self.manager.current_visualizer.create_keyboard()

    def _create_window(self) -> tk.Tk:
        """
        Создание главного окна приложения

        Returns:
            tk.Tk: Главное окно приложения с настроенными параметрами
        """
        # Создаём объект главного окна Tkinter
        root = tk.Tk()
        # Устанавливаем заголовок окна
        root.title("Виртуальная клавиатура")
        # Устанавливаем цвет фона окна из конфигурации
        root.configure(bg=UIConfig.BG_COLOR)
        # Делаем окно всегда поверх других окон
        root.attributes('-topmost', True)
        # Разрешаем изменение размера окна по горизонтали и вертикали
        root.resizable(True, True)
        # Устанавливаем минимальный размер окна (ширина, высота)
        root.minsize(UIConfig.MIN_WINDOW_WIDTH, UIConfig.MIN_WINDOW_HEIGHT)
        # Устанавливаем размер окна по умолчанию (ширина x высота)
        root.geometry(f"{UIConfig.DEFAULT_WINDOW_WIDTH}x{UIConfig.DEFAULT_WINDOW_HEIGHT}")
        # Возвращаем созданное и настроенное окно
        return root

    def run(self):
        """
        Запуск главного цикла приложения
        Запускает обработку событий графического интерфейса
        """
        # Запускаем главный цикл обработки событий Tkinter
        # Это блокирующий вызов - программа будет работать до закрытия окна
        self.root.mainloop()


# Точка входа в программу - выполняется только при прямом запуске файла
if __name__ == '__main__':
    # Создаём экземпляр приложения виртуальной клавиатуры
    app = VirtualKeyboardApp()
    # Запускаем приложение (входим в главный цикл)
    app.run()