import pygame.font


class Button:
    """Buttons for the game."""

    def __init__(self, ai_game, message):
        """Initialize button attributes."""

        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()

        # Set dimensions and properties of button
        self.width = 200
        self.height = 50
        self.button_color = (0, 135, 0)  # dark green
        self.text_color = (255, 255, 255)  # white
        self.font = pygame.font.SysFont(None, 48)  # default font, 48 size font

        # Build button's rectangle object and center it.
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center

        # Button message needs to be prepped only once.
        self._prep_message(message)

    def _prep_message(self, message):
        """Turns message into a rendered image; center text on button."""
        self.message_image = self.font.render(message, True, self.text_color)
        self.message_image_rect = self.message_image.get_rect()
        self.message_image_rect.center = self.rect.center

    def draw_button(self):
        """Draw blank button, then draw message."""
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.message_image, self.message_image_rect)

