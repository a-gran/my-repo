"""
Модуль сервисов
Содержит вспомогательные сервисы для работы приложения
"""

# Импортируем модуль ctypes для работы с Windows API
import ctypes
# Импортируем класс Language с перечислением поддерживаемых языков
from .config import Language


class LanguageDetector:
    """Сервис для определения языка клавиатуры"""

    @staticmethod
    def get_current_language() -> Language:
        """
        Определение текущего языка клавиатуры в Windows

        Использует Windows API для получения текущей раскладки клавиатуры
        активного окна и определяет её язык

        Returns:
            Language: Текущий язык клавиатуры (ENGLISH или RUSSIAN)
        """
        try:
            # Загружаем библиотеку user32.dll Windows API с обработкой ошибок
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            # Получаем дескриптор (handle) окна, которое находится на переднем плане
            curr_window = user32.GetForegroundWindow()
            # Получаем ID потока, владеющего окном (0 = не получать ID процесса)
            thread_id = user32.GetWindowThreadProcessId(curr_window, 0)
            # Получаем раскладку клавиатуры для этого потока
            # klid - это Keyboard Layout ID
            klid = user32.GetKeyboardLayout(thread_id)
            # Извлекаем младшие 16 бит (Language ID) из полного KLID
            # Используем побитовую операцию AND с маской 0xFFFF
            lid = klid & 0xFFFF

            # Проверяем, является ли язык русским
            # 0x0419 - это код русского языка в Windows
            if lid == 0x0419:
                # Возвращаем перечисление RUSSIAN
                return Language.RUSSIAN
            else:
                # Для всех остальных языков возвращаем ENGLISH по умолчанию
                return Language.ENGLISH
        except Exception:
            # Если произошла любая ошибка при работе с Windows API,
            # возвращаем ENGLISH как безопасное значение по умолчанию
            return Language.ENGLISH


class CapsLockDetector:
    """Сервис для определения состояния Caps Lock"""

    @staticmethod
    def is_caps_lock_on() -> bool:
        """
        Определение состояния Caps Lock в Windows

        Использует Windows API для проверки текущего состояния
        клавиши Caps Lock

        Returns:
            bool: True если Caps Lock включен, False если выключен
        """
        try:
            # Загружаем библиотеку user32.dll Windows API с обработкой ошибок
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            # VK_CAPITAL = 0x14 (код виртуальной клавиши Caps Lock в Windows)
            # GetKeyState возвращает состояние указанной виртуальной клавиши
            # Возвращает значение типа SHORT (16 бит):
            # - старший бит = 1, если клавиша нажата
            # - младший бит = 1, если клавиша включена (toggled)
            state = user32.GetKeyState(0x14)
            # Проверяем младший бит (& 1) для определения состояния переключения
            # Преобразуем результат в булево значение
            # Если state & 1 != 0, то Caps Lock включен
            return bool(state & 1)
        except Exception:
            # Если произошла ошибка при работе с Windows API,
            # возвращаем False (Caps Lock выключен) как безопасное значение
            return False