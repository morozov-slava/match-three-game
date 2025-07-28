from src.components import (
    ElementGenerator,
    CombinationsCheckingPipeline,
    HorizontalElementsChecker,
    VerticalElementsChecker,
    PlayingFieldGenerator,
    GlobalGameCommands,
    MoveMaker,
    InputHandler,
    PlayingFieldDisplayer,
    has_possible_moves
)

# Constants
ELEMENTS_WEIGHTS = {
    "A": 10,
    "B": 10,
    "C": 10,
    "D": 10,
    "E": 10,
    "F": 10,
    "G": 10,
    "H": 10,
    "I": 10,
    "J": 10
}
N_FIELD_ROWS = 8
N_FIELD_COLS = 8



def main():
    element_generator = ElementGenerator(ELEMENTS_WEIGHTS)
    combinations_pipeline = CombinationsCheckingPipeline()
    combinations_pipeline.add(
        [
            HorizontalElementsChecker(),
            VerticalElementsChecker()
        ]
    )
    playing_field_generator = PlayingFieldGenerator(element_generator, combinations_pipeline)
    playing_field = playing_field_generator.generate(
        n_rows=N_FIELD_ROWS,
        n_cols=N_FIELD_COLS
    )
    move_maker = MoveMaker(playing_field)
    input_handler = InputHandler(move_maker, playing_field, element_generator, combinations_pipeline)
  
    # Выводим поле
    field_displayer = PlayingFieldDisplayer(playing_field)
    
    # Start Game
    print("Добро пожаловать в игру 'Три-в-ряд'")
    print("Для вас доступны следующие команды:")
    print("Ход: например (01 02)")
    print("'exit' - выйти из игры")
    print()
    print("Ваше игровое поле:")
    print()
    field_displayer.display() 

    while True:
        if not has_possible_moves(playing_field, combinations_pipeline):
            print("Нет возможных ходов. Игра окончена")
            GlobalGameCommands.exit_game()
        command = input("Ваш ход: ")
        if not input_handler.handle(command):
            print("Вы ввели некорректный ход. Попробуйте ещё раз")
            continue
        print()
        field_displayer.display() 




if __name__ == "__main__":
    main()





