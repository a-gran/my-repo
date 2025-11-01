"""
Модуль фабрики для создания компонентов клавиатуры
Реализует паттерн Factory для создания визуализаторов и контроллеров
"""

# Импортируем модуль tkinter для работы с графическим интерфейсом
import tkinter as tk
# Импортируем тип Tuple для аннотации возвращаемого значения (кортеж из двух элементов)
from typing import Tuple

# Импортируем перечисление языков
from .config import Language
# Импортируем базовый класс визуализатора и его реализации
from .visualizers import BaseKeyboardVisualizer, EnglishKeyboardVisualizer, RussianKeyboardVisualizer
# Импортируем базовый класс контроллера и его реализации
from .controllers import BaseKeyboardController, EnglishKeyboardController, RussianKeyboardController


class KeyboardFactory:
    """
    Фабрика для создания визуализаторов и контроллеров клавиатуры

    Реализует паттерн Factory Method для инкапсуляции логики создания
    объектов в зависимости от выбранного языка
    """

    @staticmethod
    def create_visualizer(language: Language, root: tk.Tk) -> BaseKeyboardVisualizer:
        """
        Создание визуализатора по языку

        Args:
            language: Язык клавиатуры (ENGLISH или RUSSIAN)
            root: Главное окно приложения Tkinter

        Returns:
            BaseKeyboardVisualizer: Экземпляр визуализатора для указанного языка

        Raises:
            ValueError: Если передан неподдерживаемый язык
        """
        # Проверяем, является ли язык английским
        if language == Language.ENGLISH:
            # Создаём и возвращаем визуализатор английской клавиатуры
            return EnglishKeyboardVisualizer(root)
        # Проверяем, является ли язык русским
        elif language == Language.RUSSIAN:
            # Создаём и возвращаем визуализатор русской клавиатуры
            return RussianKeyboardVisualizer(root)
        else:
            # Если язык не поддерживается, выбрасываем исключение
            raise ValueError(f"Unsupported language: {language}")

    @staticmethod
    def create_controller(language: Language, visualizer: BaseKeyboardVisualizer) -> BaseKeyboardController:
        """
        Создание контроллера по языку

        Args:
            language: Язык клавиатуры (ENGLISH или RUSSIAN)
            visualizer: Визуализатор, с которым будет работать контроллер

        Returns:
            BaseKeyboardController: Экземпляр контроллера для указанного языка

        Raises:
            ValueError: Если передан неподдерживаемый язык
        """
        # Проверяем, является ли язык английским
        if language == Language.ENGLISH:
            # Создаём и возвращаем контроллер для английской клавиатуры
            return EnglishKeyboardController(visualizer)
        # Проверяем, является ли язык русским
        elif language == Language.RUSSIAN:
            # Создаём и возвращаем контроллер для русской клавиатуры
            return RussianKeyboardController(visualizer)
        else:
            # Если язык не поддерживается, выбрасываем исключение
            raise ValueError(f"Unsupported language: {language}")

    @staticmethod
    def create_layout(language: Language, root: tk.Tk) -> Tuple[BaseKeyboardVisualizer, BaseKeyboardController]:
        """
        Создание полной раскладки (визуализатор + контроллер)

        Удобный метод для одновременного создания визуализатора и контроллера

        Args:
            language: Язык клавиатуры (ENGLISH или RUSSIAN)
            root: Главное окно приложения Tkinter

        Returns:
            Tuple[BaseKeyboardVisualizer, BaseKeyboardController]:
                Кортеж из визуализатора и контроллера для указанного языка
        """
        # Создаём визуализатор для указанного языка
        visualizer = KeyboardFactory.create_visualizer(language, root)
        # Создаём контроллер для указанного языка, передавая ему визуализатор
        controller = KeyboardFactory.create_controller(language, visualizer)
        # Возвращаем кортеж из визуализатора и контроллера
        return visualizer, controller