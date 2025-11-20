# game/hud.py
import pygame


def draw_hud(screen, game_state, run_result):
    font = pygame.font.SysFont("consolas", 20)

    lines = [
        f"Day: {game_state.day}",
        f"Credits: {game_state.credits}",
        f"Solver: {run_result.get('solver', '?')}",
        f"Steps: {run_result.get('steps', '?')}",
        f"Path: {run_result.get('path_length', '?')}",
    ]

    y = 10
    for line in lines:
        text = font.render(line, True, (250, 250, 250))
        screen.blit(text, (10, y))
        y += 22
