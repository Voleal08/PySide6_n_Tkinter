import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QRadioButton, QComboBox, QTextEdit, QGroupBox,
                               QMessageBox, QScrollArea, QFrame)
from PySide6.QtCore import Qt
from typing import List, Tuple, Optional
from abc import ABC, abstractmethod


class GameSolver(ABC):
    """Абстрактный класс решателя игровых задач"""

    def __init__(self, win_condition: str, win_value: int, moves: List[str]):
        self.win_condition = win_condition
        self.win_value = win_value
        self.moves = moves

    @abstractmethod
    def solve(self, *args, **kwargs) -> List[int]:
        pass

    def parse_move(self, move_str: str, heap_name: str = "Heap") -> str:
        """Парсит строку хода в выражение"""
        try:
            if move_str.startswith("+"):
                value = int(move_str[1:])
                return f"{heap_name}+{value}"
            elif move_str.startswith("*"):
                value = int(move_str[1:])
                return f"{heap_name}*{value}"
            elif move_str.startswith("-"):
                value = int(move_str[1:])
                return f"{heap_name}-{value}"
            else:
                return move_str.replace("x", heap_name).replace("X", heap_name)
        except:
            return move_str


class OneHeapSolver(GameSolver):
    """Решатель для задач с одной кучей"""

    def __init__(self, win_condition: str, win_value: int, moves: List[str]):
        super().__init__(win_condition, win_value, moves)
        self._memo = {}

    def _can_win(self, heap: int, steps: int) -> bool:
        """Рекурсивная функция проверки выигрышной позиции"""
        if (heap, steps) in self._memo:
            return self._memo[(heap, steps)]

        if eval(f"heap {self.win_condition} {self.win_value}"):
            result = steps % 2 == 0
            self._memo[(heap, steps)] = result
            return result

        if steps == 0:
            self._memo[(heap, steps)] = False
            return False

        strategies = []
        for move in self.moves:
            new_heap_expr = self.parse_move(move, "heap")
            try:
                new_heap = eval(new_heap_expr)
                strategies.append(self._can_win(new_heap, steps - 1))
            except Exception:
                continue

        if not strategies:
            result = False
        else:
            result = any(strategies) if (steps - 1) % 2 == 0 else all(strategies)

        self._memo[(heap, steps)] = result
        return result

    def solve(self, start: int, end: int, win_steps: int, lose_steps: int) -> List[int]:
        """Находит все решения в диапазоне"""
        results = []
        for s in range(start, end + 1):
            self._memo = {}
            if not self._can_win(s, lose_steps) and self._can_win(s, win_steps):
                results.append(s)
        return results


class TwoHeapsSolver(GameSolver):
    """Решатель для задач с двумя кучами"""

    def __init__(self, win_condition: str, win_value: int, moves: List[str]):
        super().__init__(win_condition, win_value, moves)
        self._memo = {}

    def _can_win(self, heap1: int, heap2: int, steps: int) -> bool:
        """Рекурсивная функция проверки выигрышной позиции"""
        if (heap1, heap2, steps) in self._memo:
            return self._memo[(heap1, heap2, steps)]

        if eval(f"heap1 + heap2 {self.win_condition} {self.win_value}"):
            result = steps % 2 == 0
            self._memo[(heap1, heap2, steps)] = result
            return result

        if steps == 0:
            self._memo[(heap1, heap2, steps)] = False
            return False

        strategies = []
        for move in self.moves:
            # Ходы для первой кучи
            new_heap1_expr = self.parse_move(move, "heap1")
            try:
                new_heap1 = eval(new_heap1_expr)
                strategies.append(self._can_win(new_heap1, heap2, steps - 1))
            except Exception:
                pass

            # Ходы для второй кучи
            new_heap2_expr = self.parse_move(move, "heap2")
            try:
                new_heap2 = eval(new_heap2_expr)
                strategies.append(self._can_win(heap1, new_heap2, steps - 1))
            except Exception:
                pass

        if not strategies:
            result = False
        else:
            result = any(strategies) if (steps - 1) % 2 == 0 else all(strategies)

        self._memo[(heap1, heap2, steps)] = result
        return result

    def solve(self, start: int, end: int, heap2_val: int, win_steps: int, lose_steps: int) -> List[int]:
        """Находит все решения в диапазоне"""
        results = []
        for s in range(start, end + 1):
            self._memo = {}
            if not self._can_win(s, heap2_val, lose_steps) and self._can_win(s, heap2_val, win_steps):
                results.append(s)
        return results


class MoveFieldManager:
    """Управляет полями ввода ходов"""

    def __init__(self, parent_widget):
        self.parent_widget = parent_widget
        self.move_fields = []

    def add_field(self, default_value: str = "") -> None:
        """Добавляет поле для ввода хода"""
        frame = QWidget()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 2, 0, 2)

        entry = QLineEdit()
        entry.setText(default_value)
        entry.setFixedWidth(200)
        layout.addWidget(entry)

        remove_btn = QPushButton("×")
        remove_btn.setFixedWidth(30)
        remove_btn.clicked.connect(lambda: self.remove_field(frame))
        layout.addWidget(remove_btn)

        layout.addStretch()

        self.parent_widget.layout().addWidget(frame)
        self.move_fields.append((frame, entry))

    def remove_field(self, frame) -> None:
        """Удаляет поле для ввода хода"""
        for i, (f, entry) in enumerate(self.move_fields):
            if f == frame:
                self.move_fields.pop(i)
                self.parent_widget.layout().removeWidget(frame)
                frame.deleteLater()
                break

    def get_moves(self) -> List[str]:
        """Возвращает список всех ходов"""
        moves = []
        for frame, entry in self.move_fields:
            move_str = entry.text().strip()
            if move_str:
                moves.append(move_str)
        return moves

    def clear_all(self) -> None:
        """Очищает все поля"""
        for frame, entry in self.move_fields:
            self.parent_widget.layout().removeWidget(frame)
            frame.deleteLater()
        self.move_fields.clear()


class ProblemInputValidator:
    """Валидатор входных данных"""

    @staticmethod
    def validate_int(value: str, field_name: str) -> Tuple[bool, Optional[int]]:
        """Проверяет целочисленное значение"""
        try:
            return True, int(value)
        except ValueError:
            return False, None

    @staticmethod
    def validate_range(start: str, end: str) -> Tuple[bool, Optional[Tuple[int, int]]]:
        """Проверяет диапазон значений"""
        try:
            start_val = int(start)
            end_val = int(end)
            if start_val <= end_val:
                return True, (start_val, end_val)
            return False, None
        except ValueError:
            return False, None

    @staticmethod
    def validate_win_condition(condition: str) -> bool:
        """Проверяет условие победы"""
        return condition in [">=", "==", ">", "<", "<="]


class ResultsDisplay:
    """Управление отображением результатов"""

    def __init__(self, text_widget):
        self.text_widget = text_widget

    def clear(self) -> None:
        """Очищает поле результатов"""
        self.text_widget.clear()

    def show_loading(self) -> None:
        """Показывает сообщение о загрузке"""
        self.clear()
        self.text_widget.append("Вычисление...")
        QApplication.processEvents()

    def show_results(self, results: List[int]) -> None:
        """Отображает результаты вычислений"""
        self.clear()
        if results:
            self.text_widget.append(f"Найдено значений: {len(results)}")
            self.text_widget.append(f"Результаты: {results}")
            self.text_widget.append(f"Минимальное: {min(results)}")
            self.text_widget.append(f"Максимальное: {max(results)}")
        else:
            self.text_widget.append("Решения не найдены")

    def show_error(self, error_message: str) -> None:
        """Отображает сообщение об ошибке"""
        self.clear()
        self.text_widget.append(f"Ошибка: {error_message}")


class GameTheorySolverApp(QMainWindow):
    """Основной класс приложения"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Решатель теории игр для ЕГЭ")
        self.setGeometry(100, 100, 800, 600)

        self.validator = ProblemInputValidator()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        self.setup_ui()

    def setup_ui(self) -> None:
        """Создает пользовательский интерфейс"""
        self.create_type_selection()
        self.create_win_conditions()
        self.create_moves_section()
        self.create_start_values()
        self.create_query_section()
        self.create_buttons()
        self.create_results_section()

        self.initialize_defaults()

    def create_type_selection(self) -> None:
        """Создает секцию выбора типа задачи"""
        group_box = QGroupBox("Тип задачи")
        layout = QHBoxLayout()

        self.one_heap_radio = QRadioButton("1 куча")
        self.one_heap_radio.setChecked(True)
        self.one_heap_radio.toggled.connect(self.on_problem_type_change)
        layout.addWidget(self.one_heap_radio)

        self.two_heaps_radio = QRadioButton("2 кучи")
        self.two_heaps_radio.toggled.connect(self.on_problem_type_change)
        layout.addWidget(self.two_heaps_radio)

        layout.addStretch()
        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    def create_win_conditions(self) -> None:
        """Создает секцию условий победы"""
        group_box = QGroupBox("Условие победы")
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Победа при:"))

        self.win_condition = QComboBox()
        self.win_condition.addItems([">=", "==", ">", "<", "<="])
        self.win_condition.setFixedWidth(60)
        layout.addWidget(self.win_condition)

        layout.addWidget(QLabel("Значение:"))

        self.win_value = QLineEdit("202")
        self.win_value.setFixedWidth(100)
        layout.addWidget(self.win_value)

        layout.addStretch()
        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    def create_moves_section(self) -> None:
        """Создает секцию ввода ходов"""
        group_box = QGroupBox("Возможные ходы")
        main_layout = QVBoxLayout()

        self.moves_widget = QWidget()
        self.moves_layout = QVBoxLayout(self.moves_widget)
        self.moves_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.moves_widget)

        self.move_manager = MoveFieldManager(self.moves_widget)

        button_layout = QHBoxLayout()
        add_move_btn = QPushButton("Добавить ход")
        add_move_btn.clicked.connect(lambda: self.move_manager.add_field())
        button_layout.addWidget(add_move_btn)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)
        group_box.setLayout(main_layout)
        self.main_layout.addWidget(group_box)

    def create_start_values(self) -> None:
        """Создает секцию начальных значений"""
        group_box = QGroupBox("Начальные значения")
        main_layout = QVBoxLayout()

        # Диапазон поиска
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("Диапазон поиска:"))

        self.range_start = QLineEdit("1")
        self.range_start.setFixedWidth(50)
        range_layout.addWidget(self.range_start)

        range_layout.addWidget(QLabel("до"))

        self.range_end = QLineEdit("201")
        self.range_end.setFixedWidth(50)
        range_layout.addWidget(self.range_end)

        range_layout.addStretch()
        main_layout.addLayout(range_layout)

        # Вторая куча
        self.second_heap_widget = QWidget()
        second_heap_layout = QHBoxLayout(self.second_heap_widget)
        second_heap_layout.setContentsMargins(0, 0, 0, 0)

        second_heap_layout.addWidget(QLabel("Вторая куча:"))

        self.second_heap_value = QLineEdit("2")
        self.second_heap_value.setFixedWidth(50)
        second_heap_layout.addWidget(self.second_heap_value)

        second_heap_layout.addStretch()

        main_layout.addWidget(self.second_heap_widget)
        self.second_heap_widget.hide()

        group_box.setLayout(main_layout)
        self.main_layout.addWidget(group_box)

    def create_query_section(self) -> None:
        """Создает секцию запроса"""
        group_box = QGroupBox("Запрос")
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Выигрыш за:"))

        self.win_steps = QLineEdit("2")
        self.win_steps.setFixedWidth(50)
        layout.addWidget(self.win_steps)

        layout.addWidget(QLabel("ходов,"))

        layout.addWidget(QLabel("проигрыш за:"))

        self.lose_steps = QLineEdit("1")
        self.lose_steps.setFixedWidth(50)
        layout.addWidget(self.lose_steps)

        layout.addWidget(QLabel("ходов"))

        layout.addStretch()
        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    def create_buttons(self) -> None:
        """Создает панель кнопок"""
        layout = QHBoxLayout()

        solve_btn = QPushButton("Решить")
        solve_btn.clicked.connect(self.solve)
        layout.addWidget(solve_btn)

        clear_btn = QPushButton("Очистить")
        clear_btn.clicked.connect(self.clear)
        layout.addWidget(clear_btn)

        examples_btn = QPushButton("Примеры")
        examples_btn.clicked.connect(self.show_examples)
        layout.addWidget(examples_btn)

        layout.addStretch()
        self.main_layout.addLayout(layout)

    def create_results_section(self) -> None:
        """Создает секцию результатов"""
        group_box = QGroupBox("Результат")
        layout = QVBoxLayout()

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

        self.results_display = ResultsDisplay(self.result_text)

    def initialize_defaults(self) -> None:
        """Инициализирует значения по умолчанию"""
        self.move_manager.add_field("+1")
        self.move_manager.add_field("+4")
        self.move_manager.add_field("*3")
        self.on_problem_type_change()

    def on_problem_type_change(self) -> None:
        """Обрабатывает изменение типа задачи"""
        if self.two_heaps_radio.isChecked():
            self.second_heap_widget.show()
        else:
            self.second_heap_widget.hide()

    def solve(self) -> None:
        """Основной метод решения задачи"""
        try:
            # Валидация входных данных
            if not self.validate_inputs():
                return

            # Получение параметров
            moves = self.move_manager.get_moves()
            if not moves:
                QMessageBox.critical(self, "Ошибка", "Добавьте хотя бы один ход")
                return

            win_cond = self.win_condition.currentText()
            win_val = int(self.win_value.text())
            start = int(self.range_start.text())
            end = int(self.range_end.text())
            win_steps = int(self.win_steps.text())
            lose_steps = int(self.lose_steps.text())

            # Создание решателя и вычисление
            self.results_display.show_loading()

            if self.one_heap_radio.isChecked():
                solver = OneHeapSolver(win_cond, win_val, moves)
                results = solver.solve(start, end, win_steps, lose_steps)
            else:
                heap2_val = int(self.second_heap_value.text())
                solver = TwoHeapsSolver(win_cond, win_val, moves)
                results = solver.solve(start, end, heap2_val, win_steps, lose_steps)

            self.results_display.show_results(results)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при вычислениях: {str(e)}")
            self.results_display.show_error(str(e))

    def validate_inputs(self) -> bool:
        """Проверяет корректность входных данных"""
        # Проверка условия победы
        if not self.validator.validate_win_condition(self.win_condition.currentText()):
            QMessageBox.critical(self, "Ошибка", "Некорректное условие победы")
            return False

        # Проверка числовых значений
        fields = [
            (self.win_value, "Значение победы"),
            (self.range_start, "Начало диапазона"),
            (self.range_end, "Конец диапазона"),
            (self.win_steps, "Ходы для выигрыша"),
            (self.lose_steps, "Ходы для проигрыша")
        ]

        for field, name in fields:
            valid, value = self.validator.validate_int(field.text(), name)
            if not valid:
                QMessageBox.critical(self, "Ошибка", f"Некорректное значение: {name}")
                return False

        # Проверка диапазона
        valid, range_vals = self.validator.validate_range(
            self.range_start.text(), self.range_end.text())
        if not valid:
            QMessageBox.critical(self, "Ошибка", "Некорректный диапазон поиска")
            return False

        # Для двух куч
        if self.two_heaps_radio.isChecked():
            valid, value = self.validator.validate_int(
                self.second_heap_value.text(), "Вторая куча")
            if not valid:
                QMessageBox.critical(self, "Ошибка", "Некорректное значение второй кучи")
                return False

        return True

    def clear(self) -> None:
        """Очищает результаты"""
        self.results_display.clear()

    def show_examples(self) -> None:
        """Показывает примеры задач"""
        examples = """Примеры задач:

1. Одна куча:
   - Победа при >= 202
   - Ходы: +1, +4, *3
   - Запрос: выигрыш за 2 хода, проигрыш за 1 ход

2. Две кучи:
   - Победа при >= 142  
   - Ходы: +2, *2 (для любой кучи)
   - Вторая куча: 2
   - Запрос: выигрыш за 2 хода, проигрыш за 1 ход

Формат ходов:
   +N - добавить N
   *N - умножить на N
   -N - вычесть N
   x*2+1 - произвольное выражение"""

        msg = QMessageBox(self)
        msg.setWindowTitle("Примеры задач")
        msg.setText(examples)
        msg.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameTheorySolverApp()
    window.show()
    sys.exit(app.exec())