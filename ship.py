import pygame.image
from pygame.sprite import Sprite


class Ship(Sprite):
    """A class to manage the game's ship and starting position."""

    def __init__(self, ai_game):
        """Initialize the ship and set its starting points."""
        super().__init__()

        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        # Load the ship image and get its rectangle.
        self.image = pygame.image.load("images/ship.bmp")
        self.rect = self.image.get_rect()

        # Start each new ship at the bottom-center of the screen.
        self.rect.midbottom = self.screen_rect.midbottom

        # Store a float for the ship's exact horizontal position
        self.x = float(self.rect.x)

        # Movement flags; start with a ship that's not moving.
        self.moving_right = False
        self.moving_left = False

    def center_ship(self):
        """Center ship at bottom of screen."""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)

    def update(self):
        """Update the ship's position based on the movement flag"""

        # Check ship's position, so as not to go out of bounds,
        # then update ship's x value, not the rectangle.
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed

        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        # Update rectangle object from self.x
        self.rect.x = self.x

    def blitme(self):
        """Draw ship at its current location."""
        self.screen.blit(self.image, self.rect)
