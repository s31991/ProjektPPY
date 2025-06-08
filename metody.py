
import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
LIGHT_ORANGE = (255, 200, 100)
def draw_shadow(surface, rect, offset=3, alpha=100):
    """Rysuje cień pod prostokątem z określonym przesunięciem i przezroczystością"""
    shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    shadow_color = (*BLACK, alpha)
    pygame.draw.rect(shadow_surface, shadow_color, (0, 0, rect.width, rect.height))
    surface.blit(shadow_surface, (rect.x + offset, rect.y + offset))


def draw_text_with_background(surface, text, font, pos, text_color=WHITE, bg_color=(0, 0, 0, 180), padding=10):
    """Rysuje tekst z półprzezroczystym tłem"""
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect()

    bg_rect = pygame.Rect(pos[0] - padding, pos[1] - padding,
                          text_rect.width + 2 * padding, text_rect.height + 2 * padding)

    draw_shadow(surface, bg_rect, 2, 120)

    bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, bg_color, (0, 0, bg_rect.width, bg_rect.height))
    surface.blit(bg_surface, bg_rect.topleft)

    surface.blit(text_surface, pos)
    return text_rect


def create_gradient_surface(width, height, color1, color2, vertical=True):
    """Tworzy powierzchnię z gradientem między dwoma kolorami"""
    surface = pygame.Surface((width, height))

    if vertical:
        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
    else:
        for x in range(width):
            ratio = x / width
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (x, 0), (x, height))

    return surface

