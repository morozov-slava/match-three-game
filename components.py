import sys
import copy
import random
from abc import ABC, abstractmethod
from typing import Union

from pydantic import BaseModel


class Element:
    def __init__(self, value: object):
        self.value = value

    def __eq__(self, other_element):
        if not isinstance(other_element, Element):
            return False
        return self.value == other_element.value


class Cell:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.value = None

    # Команды
    def put(self, value: Union[Element | None]) -> None:
        self.value = value
    
    def remove(self) -> None:
        self.value = None

    # Запросы
    def is_empty(self) -> bool:
        return self.value is None
    
    def get_value(self) -> Union[Element | None]:
        return self.value


class PlayingField:
    def __init__(self, n_rows: int, n_cols: int):
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.grid = [[Cell(r, c) for c in range(n_cols)] for r in range(n_rows)]

    # Команда
    def swap_two_elements(self, row_1: int, col_1: int, row_2: int, col_2: int) -> None:
        cell_1 = self.get_cell(row_1, col_1)
        cell_2 = self.get_cell(row_2, col_2)
        value_1 = cell_1.get_value()
        value_2 = cell_2.get_value()
        cell_1.put(value_2)
        cell_2.put(value_1)

    # Запрос
    def get_cell(self, row: int, col: int) -> Cell:
        if (0 <= row < self.n_rows) and (0 <= col < self.n_cols):
            return self.grid[row][col]
        raise AssertionError("Row or col out of grid")
    
    def get_row(self, row: int) -> list[Cell]:
        if 0 <= row < self.n_rows: 
            return self.grid[row]
        raise AssertionError("Row out of grid")
    
    def get_col(self, col: int) -> list[Cell]:
        if (0 <= col < self.n_cols):
            return [x[col] for x in self.grid]
        raise AssertionError("Col out of grid")
    
    def shape(self) -> tuple:
        return (self.n_rows, self.n_cols)
    

class PlayingFieldDisplayer:
    def __init__(self, playing_field: PlayingField):
        self.playing_field = playing_field
        self.n_rows, self.n_cols = playing_field.shape()

    def display(self) -> None:
        print("   ", end="")
        for col in range(self.n_cols):
            print(f"{col:^3}", end=" ")
        print("\n" + "   " + "-" * (self.n_cols * 4))

        for row in range(self.n_rows):
            print(f"{row:<2}|", end=" ")
            for cell in self.playing_field.get_row(row):
                val = cell.get_value()
                if val is None:
                    print(" . ", end=" ")
                else:
                    print(f"{str(val.value):^3}", end=" ")
            print()





############################# COMBINATIONS ##############################

class CombinationsSettings(BaseModel):
    use_horizontal_combinations: bool
    use_vertical_combinations: bool
    

class CombinationsSettingsSetup:
    def __init__(self, settings: CombinationsSettings):
        self.settings = settings

    def setup(self):
        # TODO: доделать
        pass



class CombinationChecker(ABC):

    @abstractmethod
    def check(self, playing_field: PlayingField) -> list[Cell]:
        raise NotImplementedError("Must be implemented in child class")
    

class HorizontalElementsChecker(CombinationChecker):

    def check(self, playing_field: PlayingField) -> list[Cell]:
        n_rows, _ = playing_field.shape()
        combinations = []
        for i in range(n_rows):
            row = playing_field.get_row(i)
            cells_sequence = []
            current_cell = None
            for cell in row:
                if (current_cell is None):
                    current_cell = cell
                    cells_sequence.append(cell)
                    continue
                if cell.get_value() == current_cell.get_value():
                    cells_sequence.append(cell)
                    continue
                if len(cells_sequence) >= 3:
                    combinations.append(cells_sequence)
                cells_sequence = [cell]
                current_cell = cell
        return combinations
    

class VerticalElementsChecker(CombinationChecker):

    def check(self, playing_field: PlayingField) -> list[Cell]:
        _, n_cols = playing_field.shape()
        combinations = []
        for i in range(n_cols):
            col = playing_field.get_col(i)
            cells_sequence = []
            current_cell = None
            for cell in col:
                if (current_cell is None):
                    current_cell = cell
                    cells_sequence.append(cell)
                    continue
                if cell.get_value() == current_cell.get_value():
                    cells_sequence.append(cell)
                    continue
                if len(cells_sequence) >= 3:
                    combinations.append(cells_sequence)
                cells_sequence = [cell]
                current_cell = cell
        return combinations


class CombinationsCheckingPipeline:
    # Пайплайн формируется в самом начале игры, а затем запускается после каждого хода
    def __init__(self):
        self.pipeline = []

    def add(self, checker: list[CombinationChecker]) -> None:
        self.pipeline.extend(checker)

    def run(self, playing_field: PlayingField):
        results = []
        for checker in self.pipeline:
            results.extend(checker.check(playing_field))
        return results




####### GENERATION FIELD AND ELEMENTS ######


class ElementGenerator:
    def __init__(self, values_weights: dict[str, int]):
        if sum(values_weights.values()) != 100:
            raise ValueError("Sum of probabilities must be equal 1")
        self.values_weights = values_weights

    # Команды
    def generate(self) -> Element:
        # Постусловие: генерация некоторого элемента из заданного набора по определённому правилу (логике)
        return Element(
            value=random.choices(
                list(self.values_weights.keys()), 
                weights=list(self.values_weights.values()), 
                k=1
            )[0]
        )


class PlayingFieldGenerator:
    def __init__(self, element_generator: ElementGenerator, combinations_pipeline: CombinationsCheckingPipeline):
        # Предусловия: должны совпадать предусловия для объектов PlayingField и ElementGenerator.
        # Постусловие: создан объект генерирующий объект PlayingField, все поля которого заполнены по логике ElementGenerator.
        self.element_generator = element_generator
        self.combinations_pipeline = combinations_pipeline

    def generate(self, n_rows: int, n_cols: int) -> PlayingField:
        while True:
            playing_field = PlayingField(n_rows, n_cols)
            for row in range(n_rows):
                for col in range(n_cols):
                    cell = playing_field.get_cell(row, col)
                    cell.put(self.element_generator.generate())
            # displayer = PlayingFieldDisplayer(playing_field)
            # displayer.display()
            # Нормализация поля (Уничтожение комбинаций + генерация элементов)
            playing_field = normalize_playing_field(playing_field, self.element_generator, self.combinations_pipeline)
            if has_possible_moves(playing_field, self.combinations_pipeline):
                break
        return playing_field



######### DELETE AND FILL PLAYING FIELD ###########

def remove_combination_cells(cells: list[Cell]) -> None:
    for sequence in cells:
        for cell in sequence:
            # if isinstance(cell, Cell):
            cell.remove()


# def find_top_element_not_empty_cell(empty_cell: Cell, playing_field: PlayingField):
#     n_rows, _ = playing_field.shape()
#     initial_row = empty_cell.row
#     initial_col = empty_cell.col
#     while True:
#         if initial_row >= n_rows - 1:
#             return None
#         top_cell = playing_field.get_cell(row=initial_row+1, col=initial_col)
#         if top_cell.is_empty():
#             initial_row += 1
#             continue
#         return top_cell

def find_top_element_not_empty_cell(empty_cell: Cell, playing_field: PlayingField):
    row = empty_cell.row - 1
    col = empty_cell.col
    while row >= 0:
        top_cell = playing_field.get_cell(row=row, col=col)
        if not top_cell.is_empty():
            return top_cell
        row -= 1
    return None

    

def fall_down_elements(playing_field: PlayingField, element_generator: ElementGenerator) -> None:
    n_rows, n_cols = playing_field.shape()
    for col in range(n_cols):
        for row in range(n_rows - 1, -1, -1):
            cell = playing_field.get_cell(row, col)
            if cell.is_empty():
                # Поиск первого заполненного выше
                for search_row in range(row - 1, -1, -1):
                    upper_cell = playing_field.get_cell(search_row, col)
                    if not upper_cell.is_empty():
                        cell.put(upper_cell.get_value())
                        upper_cell.remove()
                        break
                else:
                    # Если сверху нет элементов — сгенерировать новый
                    cell.put(element_generator.generate())



# def fall_down_elements(playing_field: PlayingField, element_generator: ElementGenerator) -> None:
#     # Правила: 
#     # 1. Элементы падают сверху вниз
#     # 2. Если cell.is_empty() -> падает элемент сверху (рекурсивный поиск наверх) -> если элементы закончились -> генерируем элемент и ставим его на место исходного

#     # Алгоритм падения элементов:
#     # 1. 
#     n_rows, n_cols = playing_field.shape()
#     for row in range(n_rows-1, 0, -1):   # сверху-вниз по полю
#         for col in range(n_cols):
#             cell = playing_field.get_cell(row, col)
#             if cell.is_empty():
#                 not_empty_cell = find_top_element_not_empty_cell(cell, playing_field)
#                 if not_empty_cell is None:
#                     cell.put(element_generator.generate())
#                 else:
#                     playing_field.swap_two_elements(cell.row, cell.col, not_empty_cell.row, not_empty_cell.col)


# def normalize_playing_field(
#         playing_field: PlayingField, 
#         generator: ElementGenerator, 
#         combinations_pipeline: CombinationsCheckingPipeline
#     ):
#         combinations = combinations_pipeline.run(playing_field)
#         remove_combination_cells(combinations)
#         fall_down_elements(playing_field, generator)
#         return playing_field

def normalize_playing_field(
        playing_field: PlayingField, 
        generator: ElementGenerator, 
        combinations_pipeline: CombinationsCheckingPipeline
    ):
    while True:
        combinations = combinations_pipeline.run(playing_field)
        if not combinations:
            break
        remove_combination_cells(combinations)
        fall_down_elements(playing_field, generator)
    return playing_field



######## CHECK AVAILABLE MOVES ########


def has_possible_moves(playing_field: PlayingField, combinations_pipeline: CombinationsCheckingPipeline) -> True:
    n_rows, n_cols = playing_field.shape()
    
    current_row = 0
    current_col = 0
    while True:
        if current_row >= n_rows:
            break
        # Двигаемся по полю и проверям все возможные перестановки
        pf = copy.deepcopy(playing_field)
        # top swap
        if current_row + 1 < n_rows:
            pf = copy.deepcopy(playing_field)
            pf.swap_two_elements(row_1=current_row, col_1=current_col, row_2=current_row+1, col_2=current_col)
            if len(combinations_pipeline.run(pf)):
                return True
        # bottom swap
        if current_row - 1 >= 0:
            pf = copy.deepcopy(playing_field)
            pf.swap_two_elements(row_1=current_row, col_1=current_col, row_2=current_row-1, col_2=current_col)
            if len(combinations_pipeline.run(pf)):
                return True
        # left swap
        if current_col - 1 >= 0:
            pf = copy.deepcopy(playing_field)
            pf.swap_two_elements(row_1=current_row, col_1=current_col, row_2=current_row, col_2=current_col-1)
            if len(combinations_pipeline.run(pf)):
                return True
        # right swap
        if current_col + 1 < n_cols:
            pf = copy.deepcopy(playing_field)
            pf.swap_two_elements(row_1=current_row, col_1=current_col, row_2=current_row, col_2=current_col+1)
            if len(combinations_pipeline.run(pf)):
                return True
        
        if current_col + 1 >= n_cols:
            current_row += 1
            current_col = 0
            continue
        current_col += 1

    return False



################## INPUT HANDLER ##################


class MoveMaker:
    def __init__(self, playing_field: PlayingField):
        self.playing_field = playing_field

    def move(self, command: str) -> tuple[int, int, int, int]:
        parts = command.strip().split()
        if len(parts) != 2 or len(parts[0]) != 2 or len(parts[1]) != 2:
            raise ValueError("Команда должна быть в формате 'XY ZW', где X,Y,Z,W - координаты")
        row_1, col_1 = int(parts[0][0]), int(parts[0][1])
        row_2, col_2 = int(parts[1][0]), int(parts[1][1])
        return row_1, col_1, row_2, col_2



class GlobalGameCommands:

    @staticmethod
    def exit_game() -> None:
        print("Выполняю выход из игры")
        sys.exit()



class InputHandler:
    def __init__(self, move_maker: MoveMaker, playing_field: PlayingField, element_generator: ElementGenerator,
                 combinations_pipeline: CombinationsCheckingPipeline):
        self.move_maker = move_maker
        self.playing_field = playing_field
        self.element_generator = element_generator
        self.combinations_pipeline = combinations_pipeline

        self.available_commands = {
            "exit": GlobalGameCommands.exit_game,
        }

    def handle(self, command: str):
        func = self.available_commands.get(command, None)
        if func is None:
            try:
                row_1, col_1, row_2, col_2 = self.move_maker.move(command)
                self.playing_field.swap_two_elements(row_1, col_1, row_2, col_2)
                combinations = self.combinations_pipeline.run(self.playing_field)
                if all(len(sublist) == 0 for sublist in combinations):
                    self.playing_field.swap_two_elements(row_2, col_2, row_1, col_1)
                    print("Данный ход недоступен (не создаёт комбинации)")
                    return False
                playing_field = normalize_playing_field(self.playing_field, self.element_generator, self.combinations_pipeline)
                return True
            except BaseException:
                return False
        else:
            func()

