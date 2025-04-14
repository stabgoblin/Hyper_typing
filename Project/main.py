import os
import time
import pygame
import pyjokes  # type: ignore
from typing import Any, Tuple
pygame.font.init()

# Window setup
WIDTH, HEIGHT = 1000, 650
# hos.environ['SDL_VIDEO_WINDOW_POS'] = '1920, 300'
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Type Racer")

# Colours
INCORRECT_TEXT_RED = (54, 33, 34)
INCORRECRT_TEXT_BG = (181, 69, 73)
TEXT_BOX_BG = (41, 38, 38)

# Fonts
FONT_MAIN = pygame.font.SysFont('courier', 45)
FONT_STATS = pygame.font.SysFont('arial', 36)
FONT_GAME_COMPLETE = pygame.font.SysFont('arial', 60)

# Assets
BG_MAIN = pygame.transform.scale(pygame.image.load("C:\\Users\\91825\\Desktop\\net-project\\Typing_Racer\\Project\\assets\\mechanicalkeyboards_bg.png"), (WIDTH, HEIGHT))

# Misc
FPS = 60


def draw(processed_game_list: list[Tuple[str, str, str]], current_time: float,
         wpm: float, current_line: int) -> None:

    WIN.blit(BG_MAIN, (0, 0))
    # draw stats rect
    stats_rect = pygame.draw.rect(
        WIN, TEXT_BOX_BG, (0, 0, WIDTH, FONT_STATS.get_height() + 10), 0)

    # draw timer
    time_text = FONT_STATS.render(
        f"Time elapsed: {round(current_time, 2)}", True, 'white')
    WIN.blit(time_text, (stats_rect.width/6,
             stats_rect.centery - FONT_STATS.get_height() / 2))

    # draw wpm
    wpm_text = FONT_STATS.render(f"WPM: {round(wpm)}", True, 'white')
    WIN.blit(wpm_text, (stats_rect.width*2/3,
             stats_rect.centery - FONT_STATS.get_height() / 2))

    # draw game text BG
    text_box_position = (50, 200)
    pygame.draw.rect(WIN, TEXT_BOX_BG, (text_box_position[0], text_box_position[1],
                                        WIDTH - 100, HEIGHT // 2), 0)

    # draw game text
    for line, (correct_text, incorrect_text, remaining_text) in enumerate(processed_game_list):
        line_spacing = line * (FONT_MAIN.get_height() +
                               2) + text_box_position[1]
        # display correct text
        correct_text_disp = FONT_MAIN.render(correct_text, True, 'green')
        WIN.blit(correct_text_disp, (text_box_position[0], line_spacing))
        # display incorrect text
        incorrect_text_disp = FONT_MAIN.render(
            incorrect_text, True, INCORRECT_TEXT_RED, INCORRECRT_TEXT_BG)
        WIN.blit(incorrect_text_disp,
                 (correct_text_disp.get_width() + text_box_position[0], line_spacing))
        # display remaining text
        remaining_text_disp = FONT_MAIN.render(remaining_text, True, 'white')
        WIN.blit(remaining_text_disp, (correct_text_disp.get_width() +
                 incorrect_text_disp.get_width() + text_box_position[0], line_spacing))

        # draw cursor
        if line == current_line:
            cursor_position_x = correct_text_disp.get_width() \
                + incorrect_text_disp.get_width() + text_box_position[0]
            # blink the cursor
            if time.time() % 1 > 0.5:
                pygame.draw.rect(WIN, 'white', pygame.Rect(
                    cursor_position_x, line_spacing, 3, FONT_MAIN.get_height()))

    pygame.display.update()


def process_game_list(game_text_lst: list[str], input_text: str) -> list[Tuple[str, str, str]]:
    processed_game_list = []
    incorrect_text_flag = False

    for line in game_text_lst:
        correct_text = ''
        incorrect_text = ''
        remaining_text = ''

        if incorrect_text_flag:
            incorrect_text = line[:len(input_text)]
        elif len(input_text):
            for i, char in enumerate(input_text[:len(line)]):
                if char != line[i]:
                    correct_text = input_text[:i]
                    incorrect_text = line[len(correct_text):len(input_text)]
                    incorrect_text_flag = True
                    break
            else:
                correct_text = input_text[:len(line)]
                incorrect_text_flag = False
        input_text = input_text[len(line):]
        remaining_text = line[len(correct_text) + len(incorrect_text):]
        processed_game_list.append(
            (correct_text, incorrect_text, remaining_text))

    return processed_game_list


def wrap_text(game_text: str) -> list[str]:
    game_text_line_list = []

    # loop until game_text is empty
    while game_text:
        i = 1

        # determine width of the line relative to the width of the window
        while FONT_MAIN.size(game_text[:i])[0] < WIDTH - 120 and i < len(game_text):
            i += 1

        # adjust index to find last space before end of line to avoid word chopping
        if i < len(game_text):
            i = game_text.rfind(' ', 0, i) + 1

        # Add the line of text to the list
        game_text_line_list.append(game_text[:i])

        # updates the string to remove the line that has been dispalyed
        game_text = game_text[i:]

    return game_text_line_list


def get_game_text() -> str:
    return pyjokes.get_joke()


def game_complete(wpm: float, current_time: float):
    WIN.blit(BG_MAIN, (0, 0))
    text_rect = pygame.draw.rect(
        WIN, TEXT_BOX_BG, (0, HEIGHT / 2, WIDTH, FONT_GAME_COMPLETE.get_height() + 10), 0)
    text_disp = FONT_GAME_COMPLETE.render(
        f'Game complete in {round(current_time, 2)} secs with {round(wpm)} wpm', True, 'white')
    WIN.blit(text_disp, text_rect)
    pygame.display.update()
    pygame.time.delay(5000)
    main()


def get_wpm(processed_game_list: list[Tuple], current_time: float) -> float:
    correct_chars = sum([len(line[0]) for line in processed_game_list])
    wpm = correct_chars / 5 / current_time * 60
    return wpm


def get_current_line(input_len: int, game_text_lst: list[str]) -> int:
    char_count = 0
    for i, line in enumerate(game_text_lst):
        char_count = char_count + len(line)
        if char_count >= input_len:
            return i
    return 0


def main() -> None:
    clock = pygame.time.Clock()

    input_text = ''
    start_time = 0.0
    current_time = 0.0
    current_line = 0
    wpm = 0.0
    game_text = get_game_text()
    game_text_lst = wrap_text(game_text)
    processed_game_list: list[Tuple[str, str, str]] = []

    run = True
    while run:
        clock.tick(FPS)

        if start_time > 0:
            current_time = time.time() - start_time
            wpm = get_wpm(processed_game_list, current_time)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if start_time == 0:
                    start_time = time.time()
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if len(input_text) < len(game_text):
                        input_text += event.unicode

        processed_game_list = process_game_list(game_text_lst, input_text)
        current_line = get_current_line(len(input_text), game_text_lst)
        draw(processed_game_list, current_time, wpm, current_line)

        # game complete check
        if input_text == game_text:
            game_complete(wpm, current_time)

    main()


if __name__ == '__main__':
    main()