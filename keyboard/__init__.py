"""
Пакет виртуальной клавиатуры
Содержит все модули для работы приложения
"""

# Импортируем основные классы конфигурации
from .config import Language, UIConfig
# Импортируем базовый класс визуализатора и его реализации для разных языков
from .visualizers import BaseKeyboardVisualizer, EnglishKeyboardVisualizer, RussianKeyboardVisualizer
# Импортируем базовый класс контроллера и его реализации для разных языков
from .controllers import BaseKeyboardController, EnglishKeyboardController, RussianKeyboardController
# Импортируем фабрику для создания компонентов клавиатуры
from .factory import KeyboardFactory
# Импортируем сервисы для определения языка и состояния Caps Lock
from .services import LanguageDetector, CapsLockDetector
# Импортируем менеджер для управления переключением между раскладками
from .manager import LayoutManager

# Список всех публичных объектов, доступных при импорте пакета
# Это определяет, что будет доступно при "from keyboard import *"
__all__ = [
    # Перечисление поддерживаемых языков
    'Language',
    # Класс с настройками пользовательского интерфейса
    'UIConfig',
    # Базовый класс для всех визуализаторов клавиатуры
    'BaseKeyboardVisualizer',
    # Визуализатор английской раскладки клавиатуры
    'EnglishKeyboardVisualizer',
    # Визуализатор русской раскладки клавиатуры
    'RussianKeyboardVisualizer',
    # Базовый класс для всех контроллеров клавиатуры
    'BaseKeyboardController',
    # Контроллер для обработки ввода с английской раскладки
    'EnglishKeyboardController',
    # Контроллер для обработки ввода с русской раскладки
    'RussianKeyboardController',
    # Фабрика для создания визуализаторов и контроллеров
    'KeyboardFactory',
    # Сервис для определения текущего языка системной раскладки
    'LanguageDetector',
    # Сервис для определения состояния клавиши Caps Lock
    'CapsLockDetector',
    # Менеджер для автоматического переключения между раскладками
    'LayoutManager',
]

# Версия пакета в формате semver (major.minor.patch)
__version__ = '2.0.0'
# Информация об авторе пакета
__author__ = 'Virtual Keyboard Team'