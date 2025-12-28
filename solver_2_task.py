from tkinter import *
from tkinter import ttk
from tkinter.ttk import Treeview
from itertools import permutations
import numpy as np

window = Tk()  # Создание главного окна приложения


class Formule:
    def __init__(self, form):
        self.form = form
        # Замена логических символов на операторы Python
        if '∨' in self.form: self.form = self.form.replace('∨', ' or ')
        if '∧' in self.form: self.form = self.form.replace('∧', ' and ')
        if '¬' in self.form: self.form = self.form.replace('¬', ' not ')
        if '≡' in self.form: self.form = self.form.replace('≡', ' == ')
        if '→' in self.form: self.form = self.form.replace('→', ' <= ')

        self.spisok = []  # Список для хранения переменных формулы
        peremennie = ['x', 'y', 'z', 'w', 'u', 'F']  # Возможные переменные
        # Добавление переменных, которые есть в формуле
        for i in peremennie:
            if i in form: self.spisok.append(i)

        self.tablitsa = []  # Таблица истинности

    def print_table(self):
        # Генерация всех возможных комбинаций значений переменных
        for x in (0, 1):
            for y in (0, 1):
                for z in (0, 1):
                    for w in (0, 1):
                        for u in (0, 1):
                            peremennye = [x, y, z, w, u]
                            # Берем только нужные переменные
                            noviy_spisok = peremennye[:len(self.spisok)]
                            # Вычисляем значение формулы и добавляем результат
                            noviy_spisok.append(int(eval(self.form)))
                            # Добавляем строку в таблицу, если ее еще нет
                            if noviy_spisok not in self.tablitsa:
                                self.tablitsa.append(noviy_spisok)
        self.draw_table()  # Отрисовка таблицы

    def draw_table(self):
        # Создание виджета Treeview для отображения таблицы
        derevo = ttk.Treeview(columns=self.spisok + ['F'], show='headings', height=16)
        derevo.pack(anchor='w')
        peremennie = self.spisok + ["F"]  # Заголовки столбцов
        # Настройка заголовков
        for p in peremennie:
            derevo.heading(p, text=p)
        # Заполнение таблицы данными
        for l in self.tablitsa:
            derevo.insert('', END, values=l)


class Entry_table:
    def __init__(self, n, formule):
        self.n = n  # Количество столбцов
        self.formule = formule  # Объект формулы
        self.rows = 1  # Начальное количество строк
        self.entries = []  # Список для хранения виджетов Entry
        self.entry_frame = None  # Фрейм для размещения полей ввода

    def draw_button(self):
        # Кнопка для решения задачи
        self.solve_but = Button(window, text="Решить", command=self.solve)
        self.solve_but.pack(anchor='se')
        # Кнопка для добавления новых строк
        self.but = Button(window, text='Добавить ряд', command=self.draw_table)
        self.but.pack(anchor='se')

    def draw_table(self):
        # Очистка предыдущих полей ввода
        for i in self.entries:
            for j in i:
                j.destroy()
        if self.entry_frame:
            self.entry_frame.destroy()
            self.entry_frame = None

        self.entries = []
        self.entry_frame = Frame(window)
        self.entry_frame.pack(anchor='ne')
        # Создание новой таблицы полей ввода
        for r in range(self.rows):
            row_entries = []
            for c in range(self.n):
                entry = Entry(self.entry_frame, width=5)
                entry.grid(row=r, column=c)
                row_entries.append(entry)
            self.entries.append(row_entries)
        self.rows += 1  # Увеличение счетчика строк

    def get_matrix(self):
        # Получение матрицы значений из полей ввода
        matrix = [[None for i in range(len(self.entries[0]))] for j in range(len(self.entries))]
        for i in range(len(self.entries)):
            for j in range(len(self.entries[i])):
                entry = self.entries[i][j]
                text = None if entry.get() == '' else int(entry.get())
                matrix[i][j] = text
        return matrix

    def solve(self):
        matrix = self.get_matrix()  # Получение введенной матрицы
        true_table = self.formule.tablitsa  # Таблица истинности формулы

        solver = Solver(matrix, true_table)
        ans, row_perm, col_perm = solver.solve()  # Поиск решения

        cols = np.array(self.formule.spisok + ["F"])
        # Формирование ответа - порядок столбцов
        answer = "".join(cols[list(col_perm)].tolist())

        ans_label = Label(window, text=f"Ответ: {answer}")
        ans_label.pack(anchor="se")


class Solver:
    def __init__(self, matrix, true_table):
        self.matrix = np.array(matrix)  # Входная матрица (частично заполненная)
        self.true_table = np.array(true_table)  # Полная таблица истинности

    def check_ans(self, ans):
        # Проверка соответствия кандидата на решение входной матрице
        for y in range(len(self.matrix)):
            for x in range(len(self.matrix[0])):
                # None означает, что ячейка не заполнена
                if self.matrix[y, x] != ans[y, x] and self.matrix[y, x] is not None:
                    return False
        return True

    def solve(self):
        n_rows, n_cols = len(self.true_table), len(self.true_table[0])
        k = len(self.matrix)  # Количество строк во входной матрице

        # Генерация всех возможных перестановок строк и столбцов
        row_perms = list(permutations(range(n_rows), k))
        col_perms = list(permutations(range(n_cols - 1)))  # -1 т.к. последний столбец F фиксирован

        # Перебор всех комбинаций перестановок столбцов и строк
        for col_perm in col_perms:
            # Создание новой таблицы с переставленными столбцами
            new_table = self.true_table[:, tuple(list(col_perm) + [len(self.matrix[0]) - 1])]

            for row_perm in row_perms:
                pos_ans = new_table[row_perm, :]  # Кандидат на решение
                if self.check_ans(pos_ans):
                    return pos_ans, row_perm, col_perm  # Найдено решение
        return None, None, None  # Решение не найдено


def main():
    text = entry.get()  # Получение формулы из поля ввода
    a = Formule(text)  # Создание объекта формулы
    a.print_table()  # Построение и отображение таблицы истинности

    # Создание интерфейса для ввода частичной таблицы
    b = Entry_table(len(a.tablitsa[0]), a)
    b.draw_button()


# Создание элементов интерфейса
entry = ttk.Entry(width=50)  # Поле для ввода формулы
entry.pack(side=BOTTOM)
knopka = ttk.Button(text="Продолжить", command=main)  # Кнопка для запуска
knopka.pack(side=BOTTOM)

window.mainloop()  # Запуск главного цикла приложения