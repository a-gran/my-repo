"""
Модуль менеджера раскладок
Управляет переключением между раскладками клавиатуры
"""

# Импортируем модуль tkinter для работы с графическим интерфейсом
import tkinter as tk
# Импортируем модуль threading для работы с потоками
import threading
# Импортируем модуль time для работы с задержками
import time
# Импортируем типы для аннотации: Dict (словарь), Tuple (кортеж), Optional (может быть None)
from typing import Dict, Tuple, Optional
# Импортируем модуль keyboard из pynput для прослушивания нажатий клавиш
from pynput import keyboard

# Импортируем перечисление языков
from .config import Language
# Импортируем базовый класс визуализатора
from .visualizers import BaseKeyboardVisualizer
# Импортируем базовый класс контроллера
from .controllers import BaseKeyboardController
# Импортируем фабрику для создания компонентов
from .factory import KeyboardFactory
# Импортируем сервис для определения языка клавиатуры
from .services import LanguageDetector


class LayoutManager:
    """Менеджер для переключения между раскладками"""

    def __init__(self, root: tk.Tk):
        """
        Инициализация менеджера раскладок

        Args:
            root: Главное окно приложения Tkinter
        """
        # Сохраняем ссылку на главное окно приложения
        self.root = root
        # Устанавливаем текущий язык по умолчанию (английский)
        self.current_language = Language.ENGLISH
        # Создаём словарь для хранения всех раскладок
        # Ключ - язык, значение - кортеж (визуализатор, контроллер)
        self.layouts: Dict[Language, Tuple[BaseKeyboardVisualizer, BaseKeyboardController]] = {}
        # Ссылка на текущий визуализатор (изначально None)
        self.current_visualizer: Optional[BaseKeyboardVisualizer] = None
        # Ссылка на текущий контроллер (изначально None)
        self.current_controller: Optional[BaseKeyboardController] = None
        # Ссылка на слушателя клавиатуры pynput (изначально None)
        self.listener: Optional[keyboard.Listener] = None

        # Инициализируем все раскладки (английская и русская)
        self._initialize_layouts()
        # Запускаем мониторинг изменения раскладки и слушателя клавиш
        self._start_monitoring()

    def _initialize_layouts(self):
        """
        Инициализация всех раскладок

        Создаёт визуализаторы и контроллеры для всех поддерживаемых языков
        и сохраняет их в словаре для быстрого переключения
        """
        # Проходимся по всем языкам из перечисления Language
        for lang in Language:
            # Создаём визуализатор и контроллер для текущего языка с помощью фабрики
            visualizer, controller = KeyboardFactory.create_layout(lang, self.root)
            # Сохраняем созданную пару в словарь с ключом = язык
            self.layouts[lang] = (visualizer, controller)

        # Устанавливаем текущие визуализатор и контроллер для языка по умолчанию
        # Берём их из словаря layouts по ключу current_language
        self.current_visualizer, self.current_controller = self.layouts[self.current_language]

    def _start_monitoring(self):
        """
        Запуск мониторинга раскладки и слушателя клавиатуры

        Создаёт и запускает два фоновых потока:
        1. Поток для отслеживания изменения системной раскладки
        2. Поток для прослушивания нажатий клавиш
        """
        # Создаём поток для мониторинга раскладки
        # target - функция, которая будет выполняться в потоке
        # daemon=True - поток завершится при завершении главной программы
        layout_monitor_thread = threading.Thread(target=self._monitor_layout, daemon=True)
        # Запускаем поток мониторинга раскладки
        layout_monitor_thread.start()

        # Создаём поток для слушателя клавиатуры
        listener_thread = threading.Thread(target=self._start_listener, daemon=True)
        # Запускаем поток слушателя клавиатуры
        listener_thread.start()

    def _monitor_layout(self):
        """
        Мониторинг изменения раскладки клавиатуры

        Бесконечный цикл, который каждые 100мс проверяет текущую
        системную раскладку и переключает виртуальную клавиатуру
        при обнаружении изменений
        """
        # Бесконечный цикл мониторинга
        while True:
            try:
                # Получаем текущий язык системной раскладки
                new_language = LanguageDetector.get_current_language()
                # Проверяем, изменился ли язык
                if new_language != self.current_language:
                    # Обновляем текущий язык на новый
                    self.current_language = new_language
                    # Планируем переключение раскладки в главном потоке GUI
                    # after(0, ...) - выполнить в главном потоке как можно скорее
                    self.root.after(0, self.switch_layout)
                # Делаем паузу 100 миллисекунд перед следующей проверкой
                time.sleep(0.1)
            except Exception:
                # При любой ошибке просто делаем паузу и продолжаем
                # Не прерываем работу мониторинга
                time.sleep(0.1)

    def switch_layout(self):
        """
        Переключение раскладки

        Выполняет переключение между раскладками:
        1. Сохраняет текущий набранный текст
        2. Останавливает слушателя клавиш
        3. Удаляет визуализацию старой раскладки
        4. Активирует новую раскладку
        5. Восстанавливает текст
        6. Запускает слушателя для новой раскладки
        """
        # Сохраняем текущий набранный текст из контроллера
        current_text = self.current_controller.get_typed_text()

        # Останавливаем текущий слушатель клавиатуры, если он существует
        if self.listener:
            # Вызываем метод stop() для остановки слушателя
            self.listener.stop()

        # Удаляем графический фрейм текущего визуализатора
        if self.current_visualizer.main_frame is not None:
            # Уничтожаем фрейм (удаляем из интерфейса)
            self.current_visualizer.main_frame.destroy()
            # Обнуляем ссылку на фрейм
            self.current_visualizer.main_frame = None

        # Переключаемся на новую раскладку из словаря layouts
        # Получаем визуализатор и контроллер для нового языка
        self.current_visualizer, self.current_controller = self.layouts[self.current_language]

        # Синхронизируем состояние Caps Lock с системным перед использованием контроллера
        # Это важно, чтобы состояние Caps Lock было корректным после переключения
        self.current_controller.sync_caps_lock_state()

        # Передаём сохранённый текст новому контроллеру
        self.current_controller.set_typed_text(current_text)

        # Создаём визуализацию клавиатуры с сохранённым текстом
        self.current_visualizer.create_keyboard(current_text)

        # Создаём новый слушатель клавиатуры с обработчиками из нового контроллера
        self.listener = keyboard.Listener(
            # Обработчик нажатия клавиши
            on_press=self.current_controller.on_press,
            # Обработчик отпускания клавиши
            on_release=self.current_controller.on_release
        )
        # Запускаем слушателя клавиатуры
        self.listener.start()

    def _start_listener(self):
        """
        Запуск первого слушателя клавиатуры

        Создаёт и запускает начальный слушатель клавиатуры
        для текущей раскладки после небольшой задержки
        """
        # Делаем паузу 500 миллисекунд, чтобы дать время на инициализацию GUI
        time.sleep(0.5)
        # Создаём слушателя клавиатуры с обработчиками текущего контроллера
        self.listener = keyboard.Listener(
            # Обработчик нажатия клавиши
            on_press=self.current_controller.on_press,
            # Обработчик отпускания клавиши
            on_release=self.current_controller.on_release
        )
        # Запускаем слушателя
        self.listener.start()
        # Ждём завершения работы слушателя (блокирующий вызов)
        # Слушатель будет работать до остановки программы
        self.listener.join()