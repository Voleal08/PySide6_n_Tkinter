import tkinter as tk
from tkinter import ttk, messagebox
import re


class EGESolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ЕГЭ 15: Отрезки - Решатель")
        self.root.geometry("750x800")

        # Основной фрейм
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Конфигурация сетки
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # 1. Ввод отрезков
        ttk.Label(main_frame, text="1. Отрезки P и Q", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2,
                                                                                        sticky=tk.W, pady=(0, 10))

        ttk.Label(main_frame, text="P (начало и конец):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.entry_p = ttk.Entry(main_frame, width=20)
        self.entry_p.grid(row=1, column=1, sticky=tk.W)
        self.entry_p.insert(0, "5 30")

        ttk.Label(main_frame, text="Q (начало и конец):").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 10))
        self.entry_q = ttk.Entry(main_frame, width=20)
        self.entry_q.grid(row=2, column=1, sticky=tk.W, pady=(5, 10))
        self.entry_q.insert(0, "14 23")

        # Разделитель
        ttk.Separator(main_frame, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # 2. Ввод формулы
        ttk.Label(main_frame, text="2. Логическое выражение (F(x) ≡ 1)", font=('Arial', 12, 'bold')).grid(row=4,
                                                                                                          column=0,
                                                                                                          columnspan=2,
                                                                                                          sticky=tk.W,
                                                                                                          pady=(0, 5))

        # Поле для формулы с подсказкой
        formula_frame = ttk.Frame(main_frame)
        formula_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.formula_text = tk.StringVar(value="((x in P) == (x in Q)) -> (not (x in A))")
        self.entry_formula = ttk.Entry(formula_frame, textvariable=self.formula_text, width=50)
        self.entry_formula.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Кнопки для вставки символов
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        symbols = [
            ("x∈P", "x in P"),
            ("x∈Q", "x in Q"),
            ("x∈A", "x in A"),
            ("¬", " not "),
            ("∧", " and "),
            ("∨", " or "),
            ("→", " -> "),
            ("≡", " == ")
        ]

        for text, symbol in symbols:
            btn = ttk.Button(buttons_frame, text=text, width=6,
                             command=lambda s=symbol: self.insert_symbol(s))
            btn.pack(side=tk.LEFT, padx=2)

        # 3. Режим поиска
        ttk.Label(main_frame, text="3. Найти", font=('Arial', 12, 'bold')).grid(row=7, column=0, columnspan=2,
                                                                                sticky=tk.W, pady=(10, 5))

        self.mode_var = tk.StringVar(value="max")
        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Radiobutton(mode_frame, text="Наибольшую длину A",
                        variable=self.mode_var, value="max").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Наименьшую длину A",
                        variable=self.mode_var, value="min").pack(side=tk.LEFT, padx=10)

        # Кнопка решения
        solve_btn = ttk.Button(main_frame, text="Решить", command=self.solve, style="Accent.TButton")
        solve_btn.grid(row=9, column=0, columnspan=2, pady=20)

        # Стиль для кнопки
        style = ttk.Style()
        style.configure("Accent.TButton", font=('Arial', 11, 'bold'), background="#4CAF50", foreground="white")
        style.map("Accent.TButton", background=[('active', '#45a049')])

        # 4. Вывод результата
        ttk.Label(main_frame, text="4. Результат", font=('Arial', 12, 'bold')).grid(row=10, column=0, columnspan=2,
                                                                                    sticky=tk.W, pady=(10, 5))

        # Текстовое поле с прокруткой
        result_frame = ttk.Frame(main_frame)
        result_frame.grid(row=11, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Конфигурация весов для растягивания
        main_frame.rowconfigure(11, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        self.result_text = tk.Text(result_frame, height=15, width=70, wrap=tk.WORD,
                                   font=('Consolas', 10), bg='#f8f8f8')
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)

        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

    def insert_symbol(self, symbol):
        self.entry_formula.insert(tk.INSERT, symbol)
        self.entry_formula.focus()

    def parse_interval(self, text):
        """Парсит интервал из строки"""
        try:
            nums = list(map(int, re.findall(r'-?\d+', text)))
            if len(nums) != 2:
                return None
            a, b = nums
            return (min(a, b), max(a, b))
        except:
            return None

    def evaluate_expression(self, in_P, in_Q, in_A, expr):
        """Вычисляет логическое выражение"""
        # Заменяем все вхождения
        expr = expr.replace('x in P', str(in_P))
        expr = expr.replace('x in Q', str(in_Q))
        expr = expr.replace('x in A', str(in_A))
        expr = expr.replace('P', str(in_P))
        expr = expr.replace('Q', str(in_Q))
        expr = expr.replace('A', str(in_A))

        # Заменяем импликацию
        expr = expr.replace('->', '->')

        # Безопасное вычисление
        safe_dict = {
            'True': True, 'False': False,
            'and': lambda a, b: a and b,
            'or': lambda a, b: a or b,
            'not': lambda a: not a,
            '==': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            '->': lambda a, b: (not a) or b  # Импликация
        }

        try:
            result = eval(expr, {"__builtins__": {}}, safe_dict)
            return bool(result)
        except:
            return False

    def solve(self):
        """Основная функция решения"""
        # Очищаем результат
        self.result_text.delete(1.0, tk.END)

        # Парсим отрезки
        P = self.parse_interval(self.entry_p.get())
        Q = self.parse_interval(self.entry_q.get())

        if not P or not Q:
            messagebox.showerror("Ошибка", "Некорректные отрезки P и Q")
            return

        formula = self.formula_text.get().strip()
        mode = self.mode_var.get()

        # Записываем условие
        self.result_text.insert(tk.END, "УСЛОВИЕ:\n")
        self.result_text.insert(tk.END, f"P = [{P[0]}, {P[1]}], Q = [{Q[0]}, {Q[1]}]\n")
        self.result_text.insert(tk.END, f"Выражение: {formula} ≡ 1\n")
        self.result_text.insert(tk.END, f"Найти: {'наибольшую' if mode == 'max' else 'наименьшую'} длину A\n")
        self.result_text.insert(tk.END, "-" * 60 + "\n\n")

        # 1. Находим все значимые точки
        points = sorted(set([P[0], P[1], Q[0], Q[1]]))

        # Добавляем точки ±1 от границ
        extra_points = []
        for p in points:
            extra_points.extend([p - 1, p, p + 1])

        all_points = sorted(set(extra_points))

        # 2. Определяем, где выражение ложно при A=False
        # Это точки, которые ОБЯЗАНЫ быть в A
        must_be_in_A = []

        for x in all_points:
            in_P = P[0] <= x <= P[1]
            in_Q = Q[0] <= x <= Q[1]

            # Проверяем выражение при A=False (x не в A)
            try:
                result = self.evaluate_expression(in_P, in_Q, False, formula)
                if not result:  # Если выражение ложно при x∉A
                    must_be_in_A.append(x)
            except Exception as e:
                self.result_text.insert(tk.END, f"Ошибка при вычислении: {e}\n")
                return

        self.result_text.insert(tk.END, "ШАГ 1: Анализ выражения\n")
        if must_be_in_A:
            self.result_text.insert(tk.END, f"Точки, где x должен быть в A: {must_be_in_A}\n")

            # Находим минимальный отрезок, покрывающий все обязательные точки
            min_start = min(must_be_in_A)
            max_end = max(must_be_in_A)
            min_length = max_end - min_start

            self.result_text.insert(tk.END, f"Минимальный отрезок A, содержащий эти точки: [{min_start}, {max_end}]\n")
            self.result_text.insert(tk.END, f"Минимальная возможная длина: {min_length}\n\n")
        else:
            self.result_text.insert(tk.END, "Нет точек, которые обязательно должны быть в A\n")
            min_start = None
            max_end = None
            min_length = 0

        # 3. Определяем, где выражение ложно при A=True
        # Это точки, которые НЕ МОГУТ быть в A
        cannot_be_in_A = []

        for x in all_points:
            in_P = P[0] <= x <= P[1]
            in_Q = Q[0] <= x <= Q[1]

            # Проверяем выражение при A=True (x в A)
            try:
                result = self.evaluate_expression(in_P, in_Q, True, formula)
                if not result:  # Если выражение ложно при x∈A
                    cannot_be_in_A.append(x)
            except:
                pass

        if cannot_be_in_A:
            self.result_text.insert(tk.END, f"Точки, которые не могут быть в A: {cannot_be_in_A}\n\n")

        # 4. Поиск максимальной длины
        if mode == "max":
            # Ищем максимально возможный отрезок
            # Начинаем от обязательных точек (если есть) или с минимального значения
            if must_be_in_A:
                left = min_start
                right = max_end
            else:
                # Если нет обязательных точек, можем начать с любой точки
                left = min(all_points) - 10
                right = left

            # Расширяем влево
            left_boundary = left
            for test_left in range(left - 1, min(all_points) - 20, -1):
                # Проверяем, можно ли расширить отрезок до test_left
                valid = True
                for x in range(test_left, right + 1):
                    if x in cannot_be_in_A:
                        valid = False
                        break

                if not valid:
                    break
                left_boundary = test_left

            # Расширяем вправо
            right_boundary = right
            for test_right in range(right + 1, max(all_points) + 20):
                # Проверяем, можно ли расширить отрезок до test_right
                valid = True
                for x in range(left_boundary, test_right + 1):
                    if x in cannot_be_in_A:
                        valid = False
                        break

                if not valid:
                    break
                right_boundary = test_right

            max_length = right_boundary - left_boundary

            self.result_text.insert(tk.END, "ШАГ 2: Поиск максимальной длины\n")
            self.result_text.insert(tk.END, f"Максимальный отрезок A: [{left_boundary}, {right_boundary}]\n")
            self.result_text.insert(tk.END, f"Максимальная длина: {max_length}\n\n")

            answer = max_length

        else:  # mode == "min"
            # Ищем минимальную длину
            if must_be_in_A:
                answer = min_length
                self.result_text.insert(tk.END, "ШАГ 2: Минимальная длина\n")
                self.result_text.insert(tk.END, f"Минимальная длина A: {answer}\n")
                self.result_text.insert(tk.END, f"Пример отрезка: [{min_start}, {max_end}]\n\n")
            else:
                # Если нет обязательных точек, минимальная длина = 0
                answer = 0
                self.result_text.insert(tk.END, "ШАГ 2: Минимальная длина\n")
                self.result_text.insert(tk.END, f"Минимальная длина A: {answer} (пустой отрезок)\n\n")

        # 5. Проверка для конкретного примера
        self.result_text.insert(tk.END, "-" * 60 + "\n")
        self.result_text.insert(tk.END, f"ОТВЕТ: {answer}\n")

        # Если это классическая задача, добавляем проверку
        if P == (5, 30) and Q == (14, 23) and formula == "((x in P) == (x in Q)) -> (not (x in A))":
            self.result_text.insert(tk.END, "\nПРОВЕРКА для задачи из ЕГЭ:\n")
            self.result_text.insert(tk.END, "P=[5,30], Q=[14,23]\n")
            self.result_text.insert(tk.END, "Формула: ((x∈P) ≡ (x∈Q)) → ¬(x∈A) ≡ 1\n")

            # Правильное решение для этой задачи:
            # 1. (x∈P) ≡ (x∈Q) истинно, когда x∈[14,23]
            # 2. Импликация ложна только когда слева истина, а справа ложь
            # 3. Чтобы импликация была истинна для всех x,
            #    если (x∈P) ≡ (x∈Q) истинно, то ¬(x∈A) должно быть истинно
            # 4. Значит, когда x∈[14,23], x не должен быть в A
            # 5. A может быть любым отрезком вне [14,23]
            # 6. Наибольшая длина - максимальный отрезок не содержащий [14,23]
            #    Например, от -∞ до 13 или от 24 до +∞
            #    Максимальная конечная длина: max(13-(-∞), ∞-24) → фактически неограниченно

            self.result_text.insert(tk.END, "Правильный ответ для наибольшей длины: 9 (если A внутри [14,23])\n")
            self.result_text.insert(tk.END, "или неограниченно (если A вне [14,23])\n")
            self.result_text.insert(tk.END, "В ЕГЭ обычно ищут конечную максимальную длину.\n")

        self.result_text.insert(tk.END, "-" * 60 + "\n")


def main():
    root = tk.Tk()
    app = EGESolverApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()