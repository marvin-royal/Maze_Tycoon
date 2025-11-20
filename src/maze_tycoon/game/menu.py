# game/menu.py
import pygame

MENU_ITEMS = [
    "Start New Game",
    "Continue",
    "Load Game",
    "Quit",
]


def run_menu_screen() -> str:
    """
    Displays a simple vertical menu using pygame.
    Returns a string: "start", "continue", "load", or "quit".
    """
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Maze Tycoon - Main Menu")

    font = pygame.font.SysFont("arial", 32)
    clock = pygame.time.Clock()

    selected_index = 0
    running = True
    action = "quit"

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(MENU_ITEMS)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(MENU_ITEMS)
                elif event.key == pygame.K_RETURN:
                    label = MENU_ITEMS[selected_index].lower()
                    # "start new game" -> "start"
                    action = label.split()[0]
                    running = False

        screen.fill((20, 20, 20))

        for i, item in enumerate(MENU_ITEMS):
            color = (240, 240, 240) if i == selected_index else (120, 120, 120)
            text = font.render(item, True, color)
            screen.blit(text, (180, 120 + i * 40))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    return action
