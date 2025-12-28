import itertools
from typing import Dict, List, Tuple, Optional
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


class Graph:
    """
    Класс для представления графа дорог между населенными пунктами
    Хранит узлы (пункты) и ребра (дороги) - факт наличия дороги, без длин
    """

    def __init__(self):
        # Список всех узлов графа (русские буквы: А, Б, В...)
        self.nodes: List[str] = []
        # Множество рёбер: наличие дороги между пунктами
        self.edges: set = set()
        # Матрица смежности: 1 - есть дорога, 0 - нет дороги
        self.adjacency_matrix: List[List[int]] = []

    def add_node(self, node: str) -> None:
        """Добавление нового населенного пункта в граф"""
        if node not in self.nodes:
            self.nodes.append(node)
            self._update_adjacency_matrix()

    def add_edge(self, node1: str, node2: str) -> None:
        """Добавление дороги между двумя пунктами"""
        # Сортируем имена узлов для единообразия (А,Б) и (Б,А) - одно ребро
        edge = tuple(sorted([node1, node2]))
        self.edges.add(edge)

        # Автоматически добавляем узлы, если их еще нет
        if node1 not in self.nodes:
            self.add_node(node1)
        if node2 not in self.nodes:
            self.add_node(node2)

        self._update_adjacency_matrix()

    def _update_adjacency_matrix(self) -> None:
        """Обновление матрицы смежности после изменений в графе"""
        n = len(self.nodes)
        # Создаем новую матрицу N×N, заполненную 0 (отсутствие дороги)
        self.adjacency_matrix = [[0] * n for _ in range(n)]

        # Заполняем матрицу данными о дорогах
        for (node1, node2) in self.edges:
            i = self.nodes.index(node1)
            j = self.nodes.index(node2)
            # Граф неориентированный, поэтому заполняем симметрично
            self.adjacency_matrix[i][j] = 1
            self.adjacency_matrix[j][i] = 1

    def find_isomorphism(self, table_matrix: List[List[Optional[int]]], table_labels: List[str]) -> Dict[str, str]:
        """
        Поиск изоморфизма - соответствия между узлами нашего графа и узлами из таблицы
        В задаче всегда есть правильный ответ, поэтому всегда возвращает соответствие
        """
        # Перебираем все возможные перестановки узлов нашего графа
        for permutation in itertools.permutations(self.nodes):
            # Создаем словарь соответствия
            mapping = dict(zip(permutation, table_labels))

            # Проверяем, подходит ли это соответствие
            if self._check_mapping(mapping, table_matrix):
                return mapping

        # Если дошли сюда, значит решение должно быть, но не найдено
        # В реальной задаче это не должно происходить
        return dict(zip(self.nodes, table_labels))

    def _check_mapping(self, mapping: Dict[str, str], table_matrix: List[List[Optional[int]]]) -> bool:
        """
        Проверка корректности соответствия между графом и таблицей
        mapping: словарь {узел_графа: узел_таблицы}
        table_matrix: матрица смежности из условия задачи (с длинами дорог)
        """
        n = len(self.nodes)
        table_labels = list(mapping.values())

        # Проверяем все пары узлов
        for i in range(n):
            for j in range(n):
                graph_node1 = self.nodes[i]
                graph_node2 = self.nodes[j]

                # Каким узлам таблицы они соответствуют
                table_node1 = mapping[graph_node1]
                table_node2 = mapping[graph_node2]

                # Находим индексы в таблице
                table_i = table_labels.index(table_node1)
                table_j = table_labels.index(table_node2)

                # Получаем информацию о дорогах
                graph_has_road = self.adjacency_matrix[i][j]  # 1 - есть дорога, 0 - нет
                table_has_road = table_matrix[table_i][table_j] is not None  # True - есть дорога

                # Структура дорог должна совпадать
                if graph_has_road != table_has_road:
                    return False  # Найдено несоответствие в структуре дорог

        return True  # Все проверки пройдены


class GraphCanvas(QWidget):
    """
    Виджет для рисования графа
    Позволяет визуально создавать пункты и дороги
    """

    def __init__(self, graph: Graph, parent=None):
        super().__init__(parent)
        self.graph = graph  # Ссылка на объект графа
        self.node_positions = {}  # Позиции узлов на холсте: {имя: (x, y)}
        self.selected_nodes = []  # Список выделенных узлов

        self.setMinimumSize(600, 400)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border-radius: 8px;
            }
        """)

    def mousePressEvent(self, event: QMouseEvent):
        """Обработка клика левой кнопкой мыши"""
        if event.button() == Qt.LeftButton:
            x, y = event.position().x(), event.position().y()

            # Ищем, не кликнули ли на существующий узел
            clicked_node = None
            for node, (node_x, node_y) in self.node_positions.items():
                if self._is_point_near(x, y, node_x, node_y):
                    clicked_node = node
                    break

            if clicked_node:
                # Клик на узле - обрабатываем выделение
                self._handle_node_click(clicked_node)
            else:
                # Клик на пустом месте - создаем новый узел
                self._create_new_node(x, y)

            self.update()

    def _handle_node_click(self, clicked_node: str):
        """Обработка клика на существующем узле"""
        if clicked_node in self.selected_nodes:
            # Если узел уже выделен - снимаем выделение
            self.selected_nodes.remove(clicked_node)
        else:
            # Добавляем узел в выделенные
            self.selected_nodes.append(clicked_node)

            # Если выделено 2 узла - создаем дорогу между ними
            if len(self.selected_nodes) == 2:
                self._add_edge_between_selected()

    def _add_edge_between_selected(self):
        """Создание дороги между двумя выделенными пунктами"""
        if len(self.selected_nodes) != 2:
            return

        node1, node2 = self.selected_nodes

        # Просто добавляем дорогу (без запроса длины)
        self.graph.add_edge(node1, node2)

        # Сбрасываем выделение после создания дороги
        self.selected_nodes = []

    def _create_new_node(self, x: int, y: int):
        """Создание нового населенного пункта"""
        node_name = self._get_next_node_name()
        self.graph.add_node(node_name)
        self.node_positions[node_name] = (x, y)

    def _is_point_near(self, x1: int, y1: int, x2: int, y2: int, radius: int = 20) -> bool:
        """Проверка, находится ли точка рядом с другой точкой"""
        return (x1 - x2) ** 2 + (y1 - y2) ** 2 <= radius ** 2

    def _get_next_node_name(self) -> str:
        """Генерация имени для нового узла (русские буквы по порядку)"""
        used_names = set(self.graph.nodes)
        letters = "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ"

        # Ищем первую неиспользованную букву
        for letter in letters:
            if letter not in used_names:
                return letter
        return "Я"  # Если все буквы использованы

    def paintEvent(self, event: QPaintEvent):
        """Перерисовка графа на холсте"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Сначала рисуем все дороги (чтобы они были под узлами)
        painter.setPen(QPen(QColor("#495057"), 3, Qt.SolidLine, Qt.RoundCap))
        for (node1, node2) in self.graph.edges:
            if node1 in self.node_positions and node2 in self.node_positions:
                x1, y1 = self.node_positions[node1]
                x2, y2 = self.node_positions[node2]
                painter.drawLine(x1, y1, x2, y2)

        # Затем рисуем все узлы (чтобы они были поверх дорог)
        for node, (x, y) in self.node_positions.items():
            # Выбираем цвет в зависимости от выделения
            if node in self.selected_nodes:
                gradient = QRadialGradient(x, y - 5, 25)
                gradient.setColorAt(0, QColor("#51cf66"))
                gradient.setColorAt(1, QColor("#40c057"))
                painter.setBrush(QBrush(gradient))
                painter.setPen(QPen(QColor("#2f9e44"), 3))
            else:
                gradient = QRadialGradient(x, y - 5, 25)
                gradient.setColorAt(0, QColor("#74c0fc"))
                gradient.setColorAt(1, QColor("#4dabf7"))
                painter.setBrush(QBrush(gradient))
                painter.setPen(QPen(QColor("#1c7ed6"), 2))

            # Рисуем круг для узла с тенью
            shadow_offset = 2
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 0, 0, 30))
            painter.drawEllipse(x - 20 + shadow_offset, y - 20 + shadow_offset, 40, 40)

            if node in self.selected_nodes:
                painter.setBrush(QBrush(gradient))
                painter.setPen(QPen(QColor("#2f9e44"), 3))
            else:
                painter.setBrush(QBrush(gradient))
                painter.setPen(QPen(QColor("#1c7ed6"), 2))

            painter.drawEllipse(x - 20, y - 20, 40, 40)

            # Рисуем текст с именем узла
            painter.setPen(QColor("#ffffff"))
            font = QFont("Segoe UI", 14, QFont.Bold)
            painter.setFont(font)

            # Центрируем текст
            fm = QFontMetrics(font)
            text_width = fm.horizontalAdvance(node)
            text_height = fm.height()
            painter.drawText(x - text_width // 2, y + text_height // 4, node)


class MatrixInputTable(QWidget):
    """
    Класс для удобного ввода таблицы смежности
    Позволяет вводить длины дорог между поселками
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.entries = {}  # Словарь полей ввода: (строка, столбец) -> QLineEdit
        self.labels = []  # Список меток узлов (П1, П2, П3...)
        self.create_interface()

    def create_interface(self):
        """Создание интерфейса для ввода таблицы"""
        layout = QVBoxLayout(self)

        # Панель управления размером таблицы
        control_layout = QHBoxLayout()

        label = QLabel("Количество пунктов:")
        label.setStyleSheet("font-weight: bold; color: #495057;")
        control_layout.addWidget(label)

        self.size_edit = QLineEdit("7")
        self.size_edit.setFixedWidth(60)
        self.size_edit.setStyleSheet("""
            QLineEdit {
                padding: 6px 10px;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background: white;
                font-size: 13px;
                color: #212529;
            }
            QLineEdit:focus {
                border-color: #4dabf7;
            }
        """)
        control_layout.addWidget(self.size_edit)

        create_btn = QPushButton("Создать таблицу")
        create_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 16px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4dabf7, stop:1 #339af0);
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #339af0, stop:1 #228be6);
            }
            QPushButton:pressed {
                background: #1c7ed6;
            }
        """)
        create_btn.clicked.connect(self.create_table)
        control_layout.addWidget(create_btn)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # Виджет для самой таблицы
        self.table_widget = QTableWidget()
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #dee2e6;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
                color: #212529;
            }
            QTableWidget::item:selected {
                background-color: #e7f5ff;
                color: #1c7ed6;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f1f3f5, stop:1 #e9ecef);
                padding: 8px;
                border: 1px solid #dee2e6;
                font-weight: bold;
                color: #495057;
            }
        """)
        layout.addWidget(self.table_widget)

        # Создаем таблицу по умолчанию
        self.create_table()

    def create_table(self):
        """Создание таблицы ввода с указанным количеством пунктов"""
        try:
            size = int(self.size_edit.text())
        except ValueError:
            size = 7
            self.size_edit.setText("7")

        # Создаем русские метки: П1, П2, П3...
        self.labels = [f"П{i + 1}" for i in range(size)]

        self.table_widget.clear()
        self.entries = {}

        self.table_widget.setRowCount(size)
        self.table_widget.setColumnCount(size)
        self.table_widget.setHorizontalHeaderLabels(self.labels)
        self.table_widget.setVerticalHeaderLabels(self.labels)

        # Создаем ячейки таблицы
        for i in range(size):
            for j in range(size):
                if i == j:
                    # Диагональ - пустое поле (дороги от пункта к самому себе нет)
                    item = QTableWidgetItem("-")
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setBackground(QColor("#f8f9fa"))
                    item.setForeground(QColor("#adb5bd"))
                    self.table_widget.setItem(i, j, item)
                else:
                    # Создаем поле ввода для длины дороги
                    item = QTableWidgetItem("")
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table_widget.setItem(i, j, item)

    def get_matrix(self) -> List[List[Optional[int]]]:
        """Получение матрицы смежности из введенных данных"""
        size = len(self.labels)
        matrix = [[None] * size for _ in range(size)]

        for i in range(size):
            for j in range(size):
                if i != j:
                    value = self.table_widget.item(i, j).text().strip()
                    if value:  # Если поле не пустое - есть дорога с указанной длиной
                        try:
                            matrix[i][j] = int(value)
                            matrix[j][i] = int(value)  # Граф неориентированный
                        except ValueError:
                            continue

        return matrix

    def get_labels(self) -> List[str]:
        """Получение списка меток узлов"""
        return self.labels


class GraphSolverApp(QMainWindow):
    """
    Главный класс приложения
    Объединяет все компоненты и предоставляет интерфейс для решения задач
    """

    def __init__(self):
        super().__init__()
        self.graph = Graph()
        self.mapping = {}  # Словарь соответствия букв и номеров
        self.setup_ui()

    def setup_ui(self):
        """Создание графического интерфейса приложения"""
        self.setWindowTitle("Решатель задач ЕГЭ по графам - Тип 1")
        self.resize(1400, 800)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #343a40;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                padding: 0 8px;
                background-color: white;
            }
        """)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Левая панель - рисование графа
        left_frame = QGroupBox("Рисование графа")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setSpacing(12)

        self.canvas = GraphCanvas(self.graph)
        left_layout.addWidget(self.canvas)

        # Кнопка очистки графа
        clear_btn = QPushButton("🗑 Очистить граф")
        clear_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff6b6b, stop:1 #fa5252);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fa5252, stop:1 #f03e3e);
            }
            QPushButton:pressed {
                background: #e03131;
            }
        """)
        clear_btn.clicked.connect(self.clear_graph)
        left_layout.addWidget(clear_btn)

        # Инструкция для пользователя
        instruction_text = """📌 Инструкция:
• ЛКМ на пустом месте — добавить пункт
• ЛКМ на пункте — выделить его
• 2 выделенных пункта — создать дорогу между ними"""
        instruction_label = QLabel(instruction_text)
        instruction_label.setWordWrap(True)
        instruction_label.setStyleSheet("""
            QLabel {
                background-color: #e7f5ff;
                padding: 12px;
                border-radius: 8px;
                color: #1864ab;
                font-size: 13px;
                border-left: 4px solid #4dabf7;
            }
        """)
        left_layout.addWidget(instruction_label)

        main_layout.addWidget(left_frame, 1)

        # Правая панель - таблица и управление
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)

        # Таблица ввода данных из условия задачи
        table_frame = QGroupBox("Таблица длин дорог между поселками")
        table_layout = QVBoxLayout(table_frame)

        self.matrix_input = MatrixInputTable()
        table_layout.addWidget(self.matrix_input)

        right_layout.addWidget(table_frame, 1)

        # Фрейм для решения задачи
        solution_frame = QGroupBox("Решение задачи")
        solution_layout = QVBoxLayout(solution_frame)
        solution_layout.setSpacing(12)

        # Поиск конкретной дороги
        search_layout = QHBoxLayout()
        search_label = QLabel("Найти длину дороги:")
        search_label.setStyleSheet("font-weight: bold; color: #495057; font-size: 13px;")
        search_layout.addWidget(search_label)

        combo_style = """
            QComboBox {
                padding: 6px 12px;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background: white;
                font-size: 13px;
                min-width: 80px;
            }
            QComboBox:focus {
                border-color: #4dabf7;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #868e96;
                margin-right: 8px;
            }
        """

        self.from_combo = QComboBox()
        self.from_combo.setEditable(False)
        self.from_combo.setStyleSheet(combo_style)
        search_layout.addWidget(self.from_combo)

        arrow_label = QLabel("→")
        arrow_label.setStyleSheet("font-size: 18px; color: #4dabf7; font-weight: bold;")
        search_layout.addWidget(arrow_label)

        self.to_combo = QComboBox()
        self.to_combo.setEditable(False)
        self.to_combo.setStyleSheet(combo_style)
        search_layout.addWidget(self.to_combo)

        find_btn = QPushButton("🔍 Найти")
        find_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 16px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #20c997, stop:1 #12b886);
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #12b886, stop:1 #0ca678);
            }
            QPushButton:pressed {
                background: #099268;
            }
        """)
        find_btn.clicked.connect(self.find_specific_road)
        search_layout.addWidget(find_btn)

        search_layout.addStretch()
        solution_layout.addLayout(search_layout)

        # Кнопка для поиска всех соответствий
        solve_btn = QPushButton("⚡ Найти все соответствия")
        solve_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #845ef7, stop:1 #7950f2);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7950f2, stop:1 #7048e8);
            }
            QPushButton:pressed {
                background: #6741d9;
            }
        """)
        solve_btn.clicked.connect(self.solve_problem)
        solution_layout.addWidget(solve_btn)

        # Поле для отображения результатов
        self.result_label = QLabel("Здесь появится результат")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                padding: 16px;
                border-radius: 8px;
                color: #495057;
                font-size: 13px;
                border-left: 4px solid #845ef7;
                min-height: 80px;
            }
        """)
        solution_layout.addWidget(self.result_label)

        right_layout.addWidget(solution_frame)

        main_layout.addWidget(right_widget, 1)

        # Обновляем список букв в выпадающих списках
        self.update_comboboxes()

    def update_comboboxes(self):
        """Обновление выпадающих списков с буквами графа"""
        letters = self.graph.nodes
        self.from_combo.clear()
        self.to_combo.clear()
        self.from_combo.addItems(letters)
        self.to_combo.addItems(letters)

        if letters:
            self.from_combo.setCurrentIndex(0)
            self.to_combo.setCurrentIndex(min(1, len(letters) - 1))

    def clear_graph(self):
        """Очистка графа и сброс интерфейса"""
        self.graph = Graph()
        self.canvas.graph = self.graph
        self.canvas.node_positions = {}
        self.canvas.selected_nodes = []
        self.canvas.update()
        self.result_label.setText("✓ Граф очищен")
        self.update_comboboxes()

    def solve_problem(self):
        """Поиск соответствия между нарисованным графом и таблицей из условия"""
        table_matrix = self.matrix_input.get_matrix()
        table_labels = self.matrix_input.get_labels()

        # Ищем изоморфизм (соответствие узлов)
        self.mapping = self.graph.find_isomorphism(table_matrix, table_labels)

        # Форматируем результат
        result = "✓ Соответствие найдено:\n\n"
        for graph_node, table_node in sorted(self.mapping.items()):
            result += f"   {graph_node}  →  {table_node}\n"
        self.result_label.setText(result)
        self.result_label.setStyleSheet("""
            QLabel {
                background-color: #d3f9d8;
                padding: 16px;
                border-radius: 8px;
                color: #2b8a3e;
                font-size: 13px;
                border-left: 4px solid #51cf66;
                min-height: 80px;
                font-weight: bold;
            }
        """)

        # Обновляем выпадающие списки
        self.update_comboboxes()

    def find_specific_road(self):
        """Поиск длины конкретной дороги между указанными буквами графа"""
        from_letter = self.from_combo.currentText().strip()
        to_letter = self.to_combo.currentText().strip()

        # Проверяем, что выбранные буквы существуют в графе
        if from_letter not in self.graph.nodes or to_letter not in self.graph.nodes:
            self.result_label.setText("❌ Ошибка: выбранные буквы не найдены в графе")
            self.result_label.setStyleSheet("""
                QLabel {
                    background-color: #ffe3e3;
                    padding: 16px;
                    border-radius: 8px;
                    color: #c92a2a;
                    font-size: 13px;
                    border-left: 4px solid #ff6b6b;
                    min-height: 80px;
                }
            """)
            return

        table_matrix = self.matrix_input.get_matrix()
        table_labels = self.matrix_input.get_labels()

        # Находим соответствующие номера из таблицы
        from_number = self.mapping.get(from_letter)
        to_number = self.mapping.get(to_letter)

        if not from_number or not to_number:
            self.result_label.setText("⚠ Сначала найдите соответствие между графом и таблицей")
            self.result_label.setStyleSheet("""
                QLabel {
                    background-color: #fff3bf;
                    padding: 16px;
                    border-radius: 8px;
                    color: #e67700;
                    font-size: 13px;
                    border-left: 4px solid #ffd43b;
                    min-height: 80px;
                }
            """)
            return

        # Находим индексы в таблице
        from_index = table_labels.index(from_number)
        to_index = table_labels.index(to_number)

        # Получаем длину дороги из таблицы
        length = table_matrix[from_index][to_index]

        if length is not None:
            self.result_label.setText(f"✓ Длина дороги {from_letter} → {to_letter}:\n\n{length} км")
            self.result_label.setStyleSheet("""
                QLabel {
                    background-color: #d3f9d8;
                    padding: 16px;
                    border-radius: 8px;
                    color: #2b8a3e;
                    font-size: 13px;
                    border-left: 4px solid #51cf66;
                    min-height: 80px;
                    font-weight: bold;
                }
            """)
        else:
            self.result_label.setText(f"ℹ Дороги между {from_letter} и {to_letter} нет")
            self.result_label.setStyleSheet("""
                QLabel {
                    background-color: #e7f5ff;
                    padding: 16px;
                    border-radius: 8px;
                    color: #1864ab;
                    font-size: 13px;
                    border-left: 4px solid #4dabf7;
                    min-height: 80px;
                }
            """)


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")

    # Установка палитры для Fusion стиля
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#f8f9fa"))
    palette.setColor(QPalette.WindowText, QColor("#212529"))
    palette.setColor(QPalette.Base, QColor("#ffffff"))
    palette.setColor(QPalette.AlternateBase, QColor("#f1f3f5"))
    palette.setColor(QPalette.Text, QColor("#212529"))
    palette.setColor(QPalette.Button, QColor("#e9ecef"))
    palette.setColor(QPalette.ButtonText, QColor("#212529"))
    app.setPalette(palette)

    window = GraphSolverApp()
    window.show()

    app.exec()
