import sys
from time import sleep

import pygame

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard


class AlienInvasion:
    """General class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game and create game resources."""

        # Initialize background settings and clock (for framerate).
        pygame.init()
        self.clock = pygame.time.Clock()

        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width,
                                               self.settings.screen_height))
        self.bg_color = (230, 230, 230)
        pygame.display.set_caption("Alien Invasion!")

        # Create scoreboard for statistics
        self.stats = GameStats(self)
        self.scoreboard = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()

        self.aliens = pygame.sprite.Group()
        self._create_fleet()

        # Start game in inactive state
        self.game_active = False

        # Make the play button
        self.play_button = Button(self, "Play")

    def run_game(self):
        """Start main loop for the game."""

        while True:

            # Always check for events, in case user wants to quit.
            self._check_events()

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            # Allow screen to update, so player can start new game.
            self._update_screen()
            self.clock.tick(60)  # 60 FPS

    def _check_events(self):
        """Responds to keyboard and mouse events."""
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_position = pygame.mouse.get_pos()
                self._check_play_button(mouse_position)

            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)

            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_play_button(self, mouse_position):
        """Start new game when player clicks Play button."""

        button_clicked = self.play_button.rect.collidepoint(mouse_position)
        if button_clicked and not self.game_active:

            # Reset game settings
            self.settings.initialize_dynamic_settings()

            # Hide mouse cursor
            pygame.mouse.set_visible(False)

            # Reset game statistics
            self.stats.reset_stats()
            self.scoreboard.prep_score()
            self.scoreboard.prep_level()
            self.scoreboard.prep_ships()
            self.game_active = True

            # Remove bullets and aliens
            self.bullets.empty()
            self.aliens.empty()

            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()

    def _check_keyup_events(self, event):
        """Respond to key presses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False

        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _check_keydown_events(self, event):
        """Respond to key presses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True

        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True

        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

        elif event.key == pygame.K_q:
            sys.exit()

    def _fire_bullet(self):
        """Create a new bullet and add to bullets group."""

        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Update position of bullets, remove old bullets."""
        self.bullets.update()

        # Delete bullets that go beyond top of screen.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""

        # Remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(self.bullets,
                                                self.aliens,
                                                True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.stats.score += self.settings.alien_points
            self.scoreboard.prep_score()
            self.scoreboard.check_high_score()

        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Increase level
            self.stats.level += 1
            self.qscoreboard.prep_level()

    def _ship_hit(self):
        """Respond to ship being destroyed by alien."""

        if self.stats.ships_remaining > 0:
            # Decrement number of ships remaining and update scoreboard.
            self.stats.ships_remaining -= 1
            self.scoreboard.prep_ships()

            # Remove remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()

            # Create new fleet and center ship
            self._create_fleet()
            self.ship.center_ship()

            # Pause game so player can prepare
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)

    def _create_fleet(self):
        """Create fleet of aliens."""

        # Create alien; keep adding aliens until now room left in row.
        # Spacing between aliens is one alien width and one line height.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        current_x, current_y = alien_width, alien_height

        while current_y < (self.settings.screen_height - 3 * alien_height):

            while current_x < (self.settings.screen_width - 2 * alien_width):
                self.create_alien(current_x, current_y)
                current_x += 2 * alien_width

            # Finished row; reset x value, increment y value
            current_x = alien_width
            current_y += 2 * alien_height

    def create_alien(self, x_position, y_position):
        """Create an alien and place it in fleet."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        """Respond if alien fleet touches edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop entire fleet and change fleet's direction."""

        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _check_if_aliens_hit_bottom_of_screen(self):
        """Check if aliens have reached bottom of screen."""

        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                self._ship_hit()
                break

    def _update_aliens(self):
        """Check if fleet is at an edge, then update positions."""

        self._check_fleet_edges()
        self.aliens.update()

        # Looks for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        self._check_if_aliens_hit_bottom_of_screen()

    def _update_screen(self):
        """Update images on screen, then flip to new screen"""

        self.screen.fill(self.settings.bg_color)

        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        self.ship.blitme()

        self.aliens.draw(self.screen)

        # Draw score information
        self.scoreboard.show_score()

        # Draw play button if game inactive
        if not self.game_active:
            self.play_button.draw_button()

        pygame.display.flip()


if __name__ == "__main__":
    # Make an instance of the game and run game.
    alien_invasion = AlienInvasion()
    alien_invasion.run_game()
