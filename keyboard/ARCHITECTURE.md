# Архитектура проекта "Виртуальная клавиатура"

## Оглавление

1. [Общая архитектура](#общая-архитектура)
2. [Структура проекта](#структура-проекта)
3. [Архитектурные паттерны](#архитектурные-паттерны)
4. [Технические решения](#технические-решения)
5. [Модули и их взаимодействие](#модули-и-их-взаимодействие)
6. [Диаграммы](#диаграммы)
7. [Особенности реализации](#особенности-реализации)

---

## Общая архитектура

Проект построен на основе **объектно-ориентированного программирования (OOP)** с применением классических паттернов проектирования. Архитектура разделена на несколько слоёв:

### Слои архитектуры

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│    (main.py, VirtualKeyboardApp)        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Management Layer                │
│         (LayoutManager)                 │
└─────────────────────────────────────────┘
                    ↓
┌──────────────────┬──────────────────────┐
│   View Layer     │   Controller Layer   │
│  (Visualizers)   │   (Controllers)      │
└──────────────────┴──────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Business Logic Layer            │
│    (Factory, Services, Config)          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         System Layer                    │
│    (Windows API, pynput, tkinter)       │
└─────────────────────────────────────────┘
```

---

## Структура проекта

### Файловая структура

```
virtual_keyboard/
├── keyboard/                   # Основной пакет приложения
│   ├── __init__.py             # Экспорт публичных классов
│   ├── config.py               # Конфигурации и константы
│   ├── visualizers.py          # Слой представления (View)
│   ├── controllers.py          # Слой управления (Controller)
│   ├── factory.py              # Фабрика компонентов
│   ├── services.py             # Системные сервисы
│   └── manager.py              # Менеджер раскладок
├── main.py                     # Точка входа
├── README.md                   # Пользовательская документация
└── ARCHITECTURE.md             # Техническая документация (этот файл)
```

### Назначение модулей

| Модуль | Назначение | Паттерн |
|--------|-----------|---------|
| `config.py` | Централизованное хранение конфигураций | Configuration Object |
| `visualizers.py` | Отрисовка GUI клавиатуры | Template Method, Strategy |
| `controllers.py` | Обработка пользовательского ввода | Template Method, Strategy |
| `factory.py` | Создание компонентов | Factory Method |
| `services.py` | Интеграция с Windows API | Service Layer |
| `manager.py` | Управление переключением раскладок | Manager Pattern |
| `main.py` | Инициализация приложения | Entry Point |

---

## Архитектурные паттерны

### 1. Factory Method (Фабричный метод)

**Местоположение**: `keyboard/factory.py`

**Назначение**: Инкапсуляция логики создания компонентов клавиатуры.

```python
class KeyboardFactory:
    @staticmethod
    def create_layout(language: Language, root: tk.Tk):
        visualizer = KeyboardFactory.create_visualizer(language, root)
        controller = KeyboardFactory.create_controller(language, visualizer)
        return visualizer, controller
```

**Преимущества**:
- Единая точка создания объектов
- Упрощение добавления новых языков
- Слабая связанность компонентов

### 2. Template Method (Шаблонный метод)

**Местоположение**: `keyboard/visualizers.py`, `keyboard/controllers.py`

**Назначение**: Определение общего алгоритма работы с возможностью переопределения шагов.

```python
class BaseKeyboardVisualizer(ABC):
    def create_keyboard(self, typed_text: str = ""):
        # Общий алгоритм (template)
        self._reset_internal_state()
        self._create_main_frame()
        self._create_title()           # Использует get_title() (hook)
        self._create_text_display(typed_text)
        self._create_keyboard_layout() # Использует get_layout() (hook)

    @abstractmethod
    def get_title(self) -> str:
        # Hook method - переопределяется в подклассах
        pass
```

**Преимущества**:
- Устранение дублирования кода
- Гибкость при добавлении новых раскладок
- Четкое разделение общей и специфичной логики

### 3. Strategy (Стратегия)

**Местоположение**: `keyboard/controllers.py`

**Назначение**: Инкапсуляция различных алгоритмов обработки символов.

```python
class EnglishKeyboardController(BaseKeyboardController):
    def process_character(self, char: str) -> str:
        # Стратегия для английского языка
        if char.isalpha():
            if self.caps_lock_on != self.shift_pressed:
                return char.upper()
        return char

class RussianKeyboardController(BaseKeyboardController):
    def process_character(self, char: str) -> str:
        # Стратегия для русского языка (с конвертацией)
        if char.isalpha():
            if self.caps_lock_on != self.shift_pressed:
                char = char.upper()
        if char in self.en_to_ru_map:
            return self.en_to_ru_map[char]
        return char
```

**Преимущества**:
- Возможность переключения алгоритмов в runtime
- Изоляция языковой логики
- Простота тестирования

### 4. Manager Pattern (Менеджер)

**Местоположение**: `keyboard/manager.py`

**Назначение**: Координация работы компонентов и управление состоянием.

```python
class LayoutManager:
    def __init__(self, root: tk.Tk):
        self.layouts: Dict[Language, Tuple[...]] = {}
        self._initialize_layouts()     # Создание всех раскладок
        self._start_monitoring()       # Запуск фоновых потоков

    def switch_layout(self):
        # Координация переключения
        current_text = self.current_controller.get_typed_text()
        self.listener.stop()
        self.current_visualizer.main_frame.destroy()
        self.current_visualizer, self.current_controller = self.layouts[self.current_language]
        self.current_controller.sync_caps_lock_state()
        # ... восстановление состояния
```

**Преимущества**:
- Централизованное управление
- Контроль жизненного цикла компонентов
- Управление многопоточностью

### 5. Service Layer (Сервисный слой)

**Местоположение**: `keyboard/services.py`

**Назначение**: Изоляция системных вызовов и внешних зависимостей.

```python
class LanguageDetector:
    @staticmethod
    def get_current_language() -> Language:
        # Изоляция Windows API
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        # ... работа с API
        return Language.RUSSIAN if lid == 0x0419 else Language.ENGLISH

class CapsLockDetector:
    @staticmethod
    def is_caps_lock_on() -> bool:
        # Изоляция Windows API
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        state = user32.GetKeyState(0x14)
        return bool(state & 1)
```

**Преимущества**:
- Платформенная изоляция
- Возможность mock-тестирования
- Единая точка интеграции с ОС

---

## Технические решения

### 1. Caps Lock: XOR логика вместо простого переключения

**Проблема**: Caps Lock может быть изменён вне приложения, что приводит к рассинхронизации.

**Решение**: Синхронизация с системным состоянием через Windows API.

```python
# Инициализация
self.caps_lock_on = CapsLockDetector.is_caps_lock_on()

# При нажатии Caps Lock
elif key_name == 'caps_lock':
    self.caps_lock_on = CapsLockDetector.is_caps_lock_on()

# При переключении раскладки
self.current_controller.sync_caps_lock_state()

# XOR логика для определения регистра
if self.caps_lock_on != self.shift_pressed:
    return char.upper()
```

**Таблица истинности**:

| Caps Lock | Shift | Результат | Пояснение |
|-----------|-------|-----------|-----------|
| OFF (0) | OFF (0) | 0 != 0 = False | строчные |
| OFF (0) | ON (1) | 0 != 1 = True | ЗАГЛАВНЫЕ |
| ON (1) | OFF (0) | 1 != 0 = True | ЗАГЛАВНЫЕ |
| ON (1) | ON (1) | 1 != 1 = False | строчные |

### 2. Многопоточность: Фоновый мониторинг раскладки

**Проблема**: Необходимо отслеживать изменение системной раскладки без блокировки GUI.

**Решение**: Использование `threading.Thread` с флагом `daemon=True`.

```python
def _start_monitoring(self):
    # Поток мониторинга раскладки
    layout_monitor_thread = threading.Thread(
        target=self._monitor_layout,
        daemon=True  # Автоматическое завершение с главным процессом
    )
    layout_monitor_thread.start()

    # Поток слушателя клавиатуры
    listener_thread = threading.Thread(
        target=self._start_listener,
        daemon=True
    )
    listener_thread.start()

def _monitor_layout(self):
    while True:
        new_language = LanguageDetector.get_current_language()
        if new_language != self.current_language:
            self.current_language = new_language
            # Безопасное обновление GUI через root.after()
            self.root.after(0, self.switch_layout)
        time.sleep(0.1)  # Опрос каждые 100 мс
```

**Ключевые моменты**:
- `daemon=True`: потоки завершаются при закрытии приложения
- `root.after(0, ...)`: безопасное взаимодействие с GUI из фонового потока
- Интервал опроса 100 мс: баланс между отзывчивостью и нагрузкой на CPU

### 3. Защита от дублирования нажатий (Russian layout)

**Проблема**: При быстром нажатии клавиш на русской раскладке могут возникать дубликаты.

**Решение**: Временная защита с порогом 50 мс.

```python
def _handle_character_key(self, key_char: str):
    current_time = time.time()

    # Проверка временного интервала
    if key_char in self.last_key_time:
        time_diff = current_time - self.last_key_time[key_char]
        if time_diff < 0.05:  # 50 мс
            return  # Игнорируем дубликат

    # Сохраняем время нажатия
    self.last_key_time[key_char] = current_time
    # ... обработка клавиши
```

**Альтернативы рассмотренные**:
- ❌ Игнорирование повторных событий от `pynput`: не работает надёжно
- ❌ Дебаунсинг на уровне GUI: слишком сложно
- ✅ **Временная защита**: простое и эффективное решение

### 4. Closure для захвата переменных в lambda

**Проблема**: Lambda-функции в `root.after()` захватывают ссылку на переменную, а не её значение.

**Неправильно**:
```python
for char in chars:
    # char изменяется в цикле!
    self.root.after(0, lambda: self.highlight_key(char))  # ❌ Все lambda получат последнее значение char
```

**Правильно**:
```python
def do_highlight(hc=highlight_char):  # ✅ Захват значения через default argument
    self.visualizer.highlight_key(hc, self.key_mapping)

self.visualizer.root.after(0, do_highlight)
```

### 5. Конвертация английских символов в русские

**Проблема**: Windows всегда отправляет английские коды клавиш, даже на русской раскладке.

**Решение**: Словарь маппинга `EN_TO_RU_MAP` с учётом регистра.

```python
EN_TO_RU_MAP = {
    # Строчные буквы
    'q': 'й', 'w': 'ц', 'e': 'у', ...,
    # Заглавные буквы
    'Q': 'Й', 'W': 'Ц', 'E': 'У', ...,
    # Специальные символы
    '[': 'х', ']': 'ъ', '{': 'Х', '}': 'Ъ', ...
}

def process_character(self, char: str) -> str:
    # 1. Применяем Caps Lock + Shift к английскому символу
    if char.isalpha():
        if self.caps_lock_on != self.shift_pressed:
            char = char.upper()

    # 2. Конвертируем в русский
    if char in self.en_to_ru_map:
        return self.en_to_ru_map[char]
    return char
```

### 6. Сохранение состояния при переключении раскладки

**Проблема**: При смене раскладки теряется набранный текст и состояние Caps Lock.

**Решение**: Явное сохранение и восстановление состояния.

```python
def switch_layout(self):
    # 1. Сохраняем текущее состояние
    current_text = self.current_controller.get_typed_text()

    # 2. Останавливаем текущую раскладку
    if self.listener:
        self.listener.stop()
    if self.current_visualizer.main_frame is not None:
        self.current_visualizer.main_frame.destroy()

    # 3. Активируем новую раскладку
    self.current_visualizer, self.current_controller = self.layouts[self.current_language]

    # 4. Восстанавливаем состояние
    self.current_controller.sync_caps_lock_state()  # Синхронизация Caps Lock
    self.current_controller.set_typed_text(current_text)  # Восстановление текста
    self.current_visualizer.create_keyboard(current_text)

    # 5. Запускаем новый listener
    self.listener = keyboard.Listener(...)
    self.listener.start()
```

### 7. Оптимизация создания GUI: избежание вложенных циклов

**Проблема**: Вложенные циклы при создании клавиатуры усложняют код.

**Решение**: List comprehension для создания плоского списка элементов.

```python
# Создание плоского списка всех элементов раскладки
layout_items = [(row_idx, col_idx, key)
                for row_idx, row in enumerate(layout)
                for col_idx, key in enumerate(row)]

# Один цикл для обработки всех элементов
for row_idx, col_idx, key in layout_items:
    # Создание row_frame по требованию
    if row_idx not in row_frames:
        row_frames[row_idx] = self._create_row_frame(...)
    # ... создание кнопки
```

**Преимущества**:
- Линейная сложность O(n) вместо O(n²)
- Упрощение логики
- Легче читать и поддерживать

---

## Модули и их взаимодействие

### Диаграмма зависимостей

```
main.py
  ↓
LayoutManager
  ↓
  ├─→ KeyboardFactory
  │     ↓
  │     ├─→ EnglishKeyboardVisualizer ←── UIConfig
  │     │                              ←── EnglishLayoutConfig
  │     ├─→ RussianKeyboardVisualizer ←── UIConfig
  │     │                              ←── RussianLayoutConfig
  │     ├─→ EnglishKeyboardController ←── CapsLockDetector
  │     └─→ RussianKeyboardController ←── CapsLockDetector
  │                                    ←── RussianLayoutConfig.EN_TO_RU_MAP
  └─→ LanguageDetector (Windows API)
```

### Поток данных

#### 1. Инициализация приложения

```
1. main.py создаёт VirtualKeyboardApp
2. VirtualKeyboardApp создаёт главное окно (tkinter)
3. VirtualKeyboardApp создаёт LayoutManager
4. LayoutManager создаёт все раскладки через KeyboardFactory
5. KeyboardFactory создаёт пары (Visualizer, Controller) для каждого языка
6. LayoutManager запускает фоновые потоки:
   - Мониторинг раскладки (опрос каждые 100 мс)
   - Слушатель клавиатуры (pynput.keyboard.Listener)
7. Visualizer отрисовывает первую раскладку
```

#### 2. Нажатие клавиши

```
1. pynput.keyboard.Listener перехватывает нажатие
2. Listener вызывает Controller.on_press(key)
3. Controller определяет тип клавиши:
   - Символьная → _handle_character_key()
   - Специальная → _handle_special_key_press()
4. Controller обрабатывает символ:
   - Применяет Caps Lock + Shift (XOR)
   - Для русской: конвертирует через EN_TO_RU_MAP
5. Controller обновляет текст:
   - Добавляет символ к typed_text
   - Вызывает Visualizer.update_text_display()
6. Controller вызывает подсветку:
   - Visualizer.highlight_key() → меняет цвет кнопки
   - root.after(200 мс) → устанавливает приглушённый цвет
```

#### 3. Переключение раскладки

```
1. Фоновый поток мониторинга:
   - LanguageDetector.get_current_language() (Windows API)
   - Сравнивает с current_language
2. При изменении:
   - root.after(0, switch_layout) → безопасный вызов из потока
3. LayoutManager.switch_layout():
   - Сохраняет current_text
   - Останавливает listener
   - Удаляет GUI старой раскладки
   - Получает новую раскладку из self.layouts[]
   - Синхронизирует Caps Lock
   - Восстанавливает текст
   - Создаёт новый GUI
   - Запускает новый listener
```

---

## Диаграммы

### UML Class Diagram (упрощённый)

```
┌─────────────────────────┐
│  VirtualKeyboardApp     │
├─────────────────────────┤
│ - root: tk.Tk           │
│ - manager: LayoutManager│
├─────────────────────────┤
│ + run()                 │
└────────────┬────────────┘
             │ создаёт
             ↓
┌─────────────────────────────────────────────────┐
│           LayoutManager                         │
├─────────────────────────────────────────────────┤
│ - current_language: Language                    │
│ - layouts: Dict[Language, (Visualizer, ...)]    │
│ - current_visualizer: BaseKeyboardVisualizer    │
│ - current_controller: BaseKeyboardController    │
│ - listener: keyboard.Listener                   │
├─────────────────────────────────────────────────┤
│ + switch_layout()                               │
│ - _monitor_layout()        # Фоновый поток      │
│ - _start_listener()        # Фоновый поток      │
└──────────┬──────────────────────────────────────┘
           │ использует
           ↓
┌──────────────────────┐
│  KeyboardFactory     │◄─────────────────┐
├──────────────────────┤                  │
│ <<static>>           │                  │
├──────────────────────┤                  │
│ + create_layout()    │                  │
│ + create_visualizer()│                  │
│ + create_controller()│                  │
└──────────┬───────────┘                  │
           │ создаёт                      │
           ↓                              │
┌──────────────────────────┐    ┌────────┴───────────────┐
│ BaseKeyboardVisualizer   │    │ BaseKeyboardController │
│ <<abstract>>             │    │ <<abstract>>           │
├──────────────────────────┤    ├────────────────────────┤
│ + create_keyboard()      │    │ + on_press()           │
│ + highlight_key()        │    │ + on_release()         │
│ + get_layout()* abstract │    │ + process_character()* │
└────────┬─────────────────┘    └──────────┬─────────────┘
         │                                  │
    ┌────┴────┐                        ┌────┴────┐
    ↓         ↓                        ↓         ↓
┌────────┐  ┌────────┐          ┌────────┐  ┌────────┐
│English │  │Russian │          │English │  │Russian │
│Visual  │  │Visual  │          │Control │  │Control │
└────────┘  └────────┘          └────────┘  └────────┘
```

### Sequence Diagram: Нажатие клавиши

```
User    Keyboard    Listener    Controller    Visualizer     GUI
 │          │          │            │              │          │
 │─ press ─→│          │            │              │          │
 │          │─ event ─→│            │              │          │
 │          │          │─ on_press ─→│             │          │
 │          │          │            │─ process ────│          │
 │          │          │            │              │          │
 │          │          │            │─ update_text ─→         │
 │          │          │            │              │─ config ─→
 │          │          │            │              │          │
 │          │          │            │─ highlight ──→          │
 │          │          │            │              │─ change ─→
 │          │          │            │              │  color   │
 │          │          │            │              │          │
 │          │          │            │              │←─ after ─│
 │          │          │            │              │  200ms   │
 │          │          │            │              │─ dim ────→
 │          │          │            │              │  color   │
```

---

## Особенности реализации

### 1. Windows API Integration

**Используемые функции**:

| Функция | DLL | Назначение | Возвращаемое значение |
|---------|-----|------------|----------------------|
| `GetForegroundWindow()` | user32 | Получить дескриптор активного окна | HWND |
| `GetWindowThreadProcessId()` | user32 | Получить ID потока окна | DWORD |
| `GetKeyboardLayout()` | user32 | Получить раскладку клавиатуры потока | HKL |
| `GetKeyState()` | user32 | Получить состояние виртуальной клавиши | SHORT |

**Пример использования**:

```python
import ctypes

# Загрузка DLL с обработкой ошибок
user32 = ctypes.WinDLL('user32', use_last_error=True)

# Определение текущей раскладки
curr_window = user32.GetForegroundWindow()
thread_id = user32.GetWindowThreadProcessId(curr_window, 0)
klid = user32.GetKeyboardLayout(thread_id)
lid = klid & 0xFFFF  # Извлечение Language ID

# 0x0419 = русский, иначе английский
if lid == 0x0419:
    return Language.RUSSIAN

# Определение состояния Caps Lock
VK_CAPITAL = 0x14
state = user32.GetKeyState(VK_CAPITAL)
is_on = bool(state & 1)  # Младший бит = toggle state
```

### 2. Tkinter GUI Architecture

**Иерархия виджетов**:

```
tk.Tk (root)
  └─ tk.Frame (main_frame)
       ├─ tk.Label (title_label)
       ├─ tk.Label (text_display)
       └─ tk.Frame (keyboard_container)
            ├─ tk.Frame (row_frame[0])  # Ряд 0: ESC, F1-F12
            │    └─ tk.Label (btn) × 13
            ├─ tk.Frame (row_frame[1])  # Ряд 1: Цифры
            │    └─ tk.Label (btn) × 14
            ├─ tk.Frame (row_frame[2])  # Ряд 2: QWERTY
            │    └─ tk.Label (btn) × 14
            ├─ tk.Frame (row_frame[3])  # Ряд 3: ASDF
            │    └─ tk.Label (btn) × 13
            ├─ tk.Frame (row_frame[4])  # Ряд 4: ZXCV
            │    └─ tk.Label (btn) × 12
            └─ tk.Frame (row_frame[5])  # Ряд 5: Пробел
                 └─ tk.Label (btn) × 8
```

**Grid Layout**: Использование `columnconfigure(weight=...)` для адаптивной ширины клавиш.

### 3. pynput Integration

**Объекты клавиш**:

```python
from pynput import keyboard

# Символьные клавиши имеют атрибут .char
key.char  # 'a', 'b', '1', '!', и т.д.

# Специальные клавиши - это экземпляры Key
keyboard.Key.shift
keyboard.Key.caps_lock
keyboard.Key.backspace
# и т.д.

# Обработка
try:
    char = key.char  # AttributeError для специальных клавиш
except AttributeError:
    key_name = str(key).replace('Key.', '')  # "shift", "caps_lock", и т.д.
```

### 4. Конфигурационные константы

**UIConfig**: Все цвета и размеры в одном месте.

```python
class UIConfig:
    # Цвета
    BG_COLOR = '#2b2b2b'           # Фон приложения
    KEY_DEFAULT_COLOR = '#404040'   # Обычная клавиша
    KEY_ACCENT_COLOR = '#5a5a5a'    # Домашний ряд (F, J)
    KEY_PRESSED_COLOR = '#00ff00'   # Нажатая клавиша
    KEY_DIM_COLOR = '#408040'       # Отпущенная клавиша

    # Размеры
    MIN_WINDOW_WIDTH = 800
    DEFAULT_WINDOW_WIDTH = 1200

    # Шрифты
    FONT_FAMILY = 'Arial'
    FONT_FAMILY_MONO = 'Courier New'
```

**LayoutConfig**: Раскладки и веса клавиш.

```python
class KeyboardLayoutConfig:
    POSITION_WEIGHTS = {
        (1, 13): 10,  # BACKSPACE - широкая
        (2, 0): 6,    # TAB - широкая
        (3, 0): 7,    # CAPS - широкая
        (3, 12): 9,   # ENTER - широкая
        (4, 0): 8,    # SHIFT левый - широкий
        (5, 3): 25,   # SPACE - очень широкий
    }
```

---

## Потенциальные улучшения

### 1. Тестирование

**Текущее состояние**: Нет автоматизированных тестов.

**Предложения**:
```python
# Unit тесты для логики
class TestCapsLockLogic(unittest.TestCase):
    def test_xor_logic_caps_on_shift_off(self):
        controller = EnglishKeyboardController(mock_visualizer)
        controller.caps_lock_on = True
        controller.shift_pressed = False
        result = controller.process_character('a')
        self.assertEqual(result, 'A')

# Mock для Windows API
class MockCapsLockDetector:
    @staticmethod
    def is_caps_lock_on():
        return True  # Для тестирования
```

### 2. Конфигурация

**Текущее состояние**: Хардкоженные константы.

**Предложения**:
- JSON/YAML конфигурационные файлы
- Пользовательские цветовые схемы
- Настройка горячих клавиш

### 3. Добавление языков

**Текущее состояние**: Только EN и RU.

**Как добавить новый язык**:

```python
# 1. Добавить в enum
class Language(Enum):
    ENGLISH = 'EN'
    RUSSIAN = 'RU'
    GERMAN = 'DE'   # Новый язык

# 2. Создать конфигурацию
class GermanLayoutConfig(KeyboardLayoutConfig):
    LAYOUT = [...]
    HOME_ROW_KEYS = ['F', 'J']

# 3. Создать визуализатор
class GermanKeyboardVisualizer(BaseKeyboardVisualizer):
    def get_layout(self):
        return GermanLayoutConfig.LAYOUT

# 4. Создать контроллер
class GermanKeyboardController(BaseKeyboardController):
    def process_character(self, char: str) -> str:
        # Логика для немецкого языка (ä, ö, ü, ß)
        pass

# 5. Обновить фабрику
class KeyboardFactory:
    @staticmethod
    def create_visualizer(language: Language, root: tk.Tk):
        if language == Language.GERMAN:
            return GermanKeyboardVisualizer(root)
        # ...
```

### 4. Производительность

**Текущие характеристики**:
- Интервал опроса раскладки: 100 мс
- Задержка подсветки: 200 мс
- Порог дублирования: 50 мс

**Возможные оптимизации**:
- Использование событий Windows вместо polling
- Аппаратное ускорение отрисовки (OpenGL)
- Кэширование виджетов

### 5. Кроссплатформенность

**Текущее состояние**: Только Windows (из-за `ctypes.WinDLL`).

**Для поддержки Linux/macOS**:
```python
import platform

class LanguageDetector:
    @staticmethod
    def get_current_language() -> Language:
        if platform.system() == 'Windows':
            return LanguageDetector._get_language_windows()
        elif platform.system() == 'Linux':
            return LanguageDetector._get_language_linux()
        elif platform.system() == 'Darwin':  # macOS
            return LanguageDetector._get_language_macos()
```

---

## Заключение

Архитектура проекта построена на принципах **SOLID**:

- **S**ingle Responsibility: Каждый класс имеет одну ответственность
- **O**pen/Closed: Легко добавлять новые языки без изменения существующего кода
- **L**iskov Substitution: Все наследники корректно заменяют базовые классы
- **I**nterface Segregation: Абстрактные методы минимальны и целевые
- **D**ependency Inversion: Зависимость от абстракций, а не от конкретных классов

Использование классических паттернов проектирования обеспечивает:
- ✅ Читаемость и поддерживаемость кода
- ✅ Простоту расширения функциональности
- ✅ Модульность и тестируемость
- ✅ Слабую связанность компонентов
 