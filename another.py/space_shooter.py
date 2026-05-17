import arcade
import random
import math

# space shooter game 


# =========================================================
# SETTINGS
# =========================================================

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "SPACE SHOOTER"

PLAYER_SPEED = 6
BULLET_SPEED = 14
ENEMY_SPEED = 2
SHOOTER_SPEED = 1.5
BOSS_SPEED = 1

PLAYER_SCALE = 0.6
ENEMY_SCALE = 0.5
BULLET_SCALE = 0.4

NORMAL_SHOOT_INTERVAL = 0.2
RAPID_SHOOT_INTERVAL = 0.08

POWERUP_DURATION = 8

# =========================================================
# PLAYER
# =========================================================

class Player(arcade.Sprite):

    def __init__(self):

        super().__init__(
            ":resources:images/space_shooter/playerShip1_blue.png",
            PLAYER_SCALE
        )

        self.center_x = SCREEN_WIDTH // 2
        self.center_y = 100

        self.health = 100
        self.max_health = 100

        self.rapid_fire = False
        self.shield = False

        self.power_timer = 0

# =========================================================
# BULLET
# =========================================================

class Bullet(arcade.Sprite):

    def __init__(self, x, y, angle):

        super().__init__(
            ":resources:images/space_shooter/laserBlue01.png",
            BULLET_SCALE
        )

        self.center_x = x
        self.center_y = y

        self.angle = angle

        radians = math.radians(angle)

        self.change_x = math.cos(radians) * BULLET_SPEED
        self.change_y = math.sin(radians) * BULLET_SPEED


class EnemyBullet(arcade.Sprite):

    def __init__(self, x, y, angle):

        super().__init__(
            ":resources:images/space_shooter/laserRed01.png",
            BULLET_SCALE
        )

        self.center_x = x
        self.center_y = y

        self.angle = angle

        radians = math.radians(angle)

        self.change_x = math.cos(radians) * (BULLET_SPEED * 0.5)
        self.change_y = math.sin(radians) * (BULLET_SPEED * 0.5)

# =========================================================
# ENEMY
# =========================================================

class Enemy(arcade.Sprite):

    def __init__(self):

        super().__init__(
            ":resources:images/space_shooter/playerShip3_orange.png",
            ENEMY_SCALE
        )

        self.center_x = random.randint(50, SCREEN_WIDTH - 50)
        self.center_y = SCREEN_HEIGHT + 50

        self.health = 20
        self.max_health = 20

    def update_enemy(self, player):

        angle = math.atan2(
            player.center_y - self.center_y,
            player.center_x - self.center_x
        )

        self.angle = math.degrees(angle)
        self.center_x += math.cos(angle) * ENEMY_SPEED
        self.center_y += math.sin(angle) * ENEMY_SPEED

# =========================================================
# SHOOTER ENEMY
# =========================================================

class ShooterEnemy(arcade.Sprite):

    def __init__(self):

        super().__init__(
            ":resources:images/space_shooter/playerShip2_orange.png",
            ENEMY_SCALE
        )

        self.center_x = random.randint(50, SCREEN_WIDTH - 50)
        self.center_y = SCREEN_HEIGHT + 50

        self.health = 40
        self.max_health = 40

        self.shoot_timer = 0

    def update_enemy(self, player, delta_time):

        dx = player.center_x - self.center_x
        dy = player.center_y - self.center_y

        angle = math.atan2(dy, dx)
        self.angle = math.degrees(angle)

        self.center_x += math.cos(angle) * SHOOTER_SPEED
        self.center_y += math.sin(angle) * SHOOTER_SPEED

        self.shoot_timer += delta_time

        if self.shoot_timer >= 2.0:
            self.shoot_timer = 0
            return True

        return False

# =========================================================
# BOSS
# =========================================================

class BossEnemy(arcade.Sprite):

    def __init__(self):

        super().__init__(
            ":resources:images/space_shooter/playerShip1_orange.png",
            1.3
        )

        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT - 100

        self.health = 500
        self.max_health = 500

        self.shoot_timer = 0

    def update_enemy(self, player, delta_time):

        dx = player.center_x - self.center_x
        dy = player.center_y - self.center_y

        angle = math.atan2(dy, dx)
        self.angle = math.degrees(angle)

        self.center_x += math.cos(angle) * BOSS_SPEED
        self.center_y += math.sin(angle) * BOSS_SPEED

        self.shoot_timer += delta_time

        if self.shoot_timer >= 1.5:
            self.shoot_timer = 0
            return True

        return False

# =========================================================
# POWERUP
# =========================================================

class PowerUp(arcade.Sprite):

    def __init__(self, power_type, x, y):

        image = ":resources:images/items/gemBlue.png"

        if power_type == "rapid":
            image = ":resources:images/items/gemRed.png"

        elif power_type == "shield":
            image = ":resources:images/items/gemYellow.png"

        super().__init__(image, 0.5)

        self.power_type = power_type

        self.center_x = x
        self.center_y = y

        self.change_y = -2

# =========================================================
# MAIN GAME
# =========================================================

class SpaceShooter(arcade.Window):

    def __init__(self):

        super().__init__(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_TITLE
        )

        arcade.set_background_color(arcade.color.BLACK)

        # Player
        self.player = Player()

        # Lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.powerup_list = arcade.SpriteList()

        self.player_list.append(self.player)

        # Game
        self.score = 0
        self.game_over = False

        # Timers
        self.enemy_timer = 0
        self.shooter_timer = 0
        self.boss_timer = 0

        # Controls
        self.left = False
        self.right = False
        self.up = False
        self.down = False

        # Stars
        self.stars = []

        for i in range(200):

            self.stars.append([
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.randint(1, 3),
                random.uniform(1, 5)
            ])

        # Particles
        self.particles = []

        # Sounds
        self.shoot_sound = arcade.load_sound(
            ":resources:sounds/laser1.wav"
        )

        self.explosion_sound = arcade.load_sound(
            ":resources:sounds/explosion2.wav"
        )

        # Mouse
        self.mouse_x = SCREEN_WIDTH // 2
        self.mouse_y = SCREEN_HEIGHT // 2

        # Shooting state
        self.shoot_pressed = False
        self.shoot_timer = 0.0

        # Reload button
        self.restart_button = {
            "left": SCREEN_WIDTH - 170,
            "bottom": 20,
            "width": 140,
            "height": 40
        }

    # =====================================================
    # DRAW
    # =====================================================

    def on_draw(self):

        self.clear()

        # Background stars
        for star in self.stars:

            arcade.draw_circle_filled(
                star[0],
                star[1],
                star[2],
                arcade.color.WHITE
            )

        # Sprites
        self.player_list.draw()
        self.enemy_list.draw()
        self.bullet_list.draw()
        self.enemy_bullet_list.draw()
        self.powerup_list.draw()

        # Particles
        for particle in self.particles:

            arcade.draw_circle_filled(
                particle["x"],
                particle["y"],
                3,
                arcade.color.ORANGE_RED
            )

        # Player shield
        if self.player.shield:

            arcade.draw_circle_outline(
                self.player.center_x,
                self.player.center_y,
                45,
                arcade.color.CYAN,
                4
            )

        # Player health bar
        bar_width = 200
        health_width = bar_width * self.player.health / self.player.max_health

        arcade.draw_lrbt_rectangle_filled(
            20,
            20 + bar_width,
            SCREEN_HEIGHT - 34,
            SCREEN_HEIGHT - 16,
            arcade.color.DARK_RED
        )
        arcade.draw_lrbt_rectangle_filled(
            20,
            20 + max(0, health_width),
            SCREEN_HEIGHT - 34,
            SCREEN_HEIGHT - 16,
            arcade.color.GREEN
        )
        arcade.draw_lrbt_rectangle_outline(
            20,
            20 + bar_width,
            SCREEN_HEIGHT - 34,
            SCREEN_HEIGHT - 16,
            arcade.color.WHITE
        )
        arcade.draw_text(
            f"HEALTH: {self.player.health}",
            20,
            SCREEN_HEIGHT - 45,
            arcade.color.WHITE,
            14,
            bold=True
        )

        # Score
        arcade.draw_text(
            f"SCORE: {self.score}",
            20,
            SCREEN_HEIGHT - 80,
            arcade.color.CYAN,
            20,
            bold=True
        )

        # Enemy health bars
        for enemy in self.enemy_list:

            if hasattr(enemy, "max_health"):

                health_ratio = enemy.health / enemy.max_health

                health_bar_width = 100 * health_ratio
                arcade.draw_lrbt_rectangle_filled(
                    enemy.center_x - health_bar_width / 2,
                    enemy.center_x + health_bar_width / 2,
                    enemy.top + 6,
                    enemy.top + 14,
                    arcade.color.RED
                )

        # Game over
        if self.game_over:

            arcade.draw_text(
                "GAME OVER",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                arcade.color.RED,
                60,
                anchor_x="center"
            )

            button = self.restart_button
            arcade.draw_lrbt_rectangle_filled(
                button["left"],
                button["left"] + button["width"],
                button["bottom"],
                button["bottom"] + button["height"],
                arcade.color.DARK_BLUE
            )
            arcade.draw_lrbt_rectangle_outline(
                button["left"],
                button["left"] + button["width"],
                button["bottom"],
                button["bottom"] + button["height"],
                arcade.color.WHITE,
                border_width=2
            )
            arcade.draw_text(
                "Reload",
                button["left"] + button["width"] / 2,
                button["bottom"] + button["height"] / 2 - 10,
                arcade.color.WHITE,
                18,
                anchor_x="center"
            )

    # =====================================================
    # UPDATE
    # =====================================================

    def on_update(self, delta_time):

        if self.game_over:
            return

        # Stars movement
        for star in self.stars:

            star[1] -= star[3]

            if star[1] < 0:

                star[0] = random.randint(0, SCREEN_WIDTH)
                star[1] = SCREEN_HEIGHT

        # Player movement
        if self.left:
            self.player.center_x -= PLAYER_SPEED

        if self.right:
            self.player.center_x += PLAYER_SPEED

        if self.up:
            self.player.center_y += PLAYER_SPEED

        if self.down:
            self.player.center_y -= PLAYER_SPEED

        # Keep player inside screen
        self.player.center_x = max(
            30,
            min(SCREEN_WIDTH - 30, self.player.center_x)
        )

        self.player.center_y = max(
            30,
            min(SCREEN_HEIGHT - 30, self.player.center_y)
        )

        # Spawn enemies
        self.enemy_timer += delta_time
        self.shooter_timer += delta_time
        self.boss_timer += delta_time

        if self.enemy_timer > 1.5:

            self.enemy_list.append(Enemy())
            self.enemy_timer = 0

        if self.shooter_timer > 4:

            self.enemy_list.append(ShooterEnemy())
            self.shooter_timer = 0

        if self.score > 300 and self.boss_timer > 20:

            self.enemy_list.append(BossEnemy())
            self.boss_timer = 0

        # Enemy updates
        for enemy in self.enemy_list:

            if isinstance(enemy, BossEnemy):

                if enemy.update_enemy(self.player, delta_time):
                    self.fire_enemy_bullet(enemy)

            elif isinstance(enemy, ShooterEnemy):

                if enemy.update_enemy(self.player, delta_time):
                    self.fire_enemy_bullet(enemy)

            else:

                enemy.update_enemy(self.player)

        # Automatic shooting while mouse button is held
        if self.shoot_pressed:
            self.shoot_timer += delta_time
            interval = RAPID_SHOOT_INTERVAL if self.player.rapid_fire else NORMAL_SHOOT_INTERVAL
            if self.shoot_timer >= interval:
                self.fire_bullet()
                self.shoot_timer = 0.0

        # Bullet updates
        self.bullet_list.update()
        self.enemy_bullet_list.update()

        # Bullet cleanup
        for bullet in list(self.bullet_list):
            if (bullet.bottom > SCREEN_HEIGHT or bullet.top < 0 or
                    bullet.right < 0 or bullet.left > SCREEN_WIDTH):
                bullet.remove_from_sprite_lists()

        for bullet in list(self.enemy_bullet_list):
            if (bullet.bottom > SCREEN_HEIGHT or bullet.top < 0 or
                    bullet.right < 0 or bullet.left > SCREEN_WIDTH):
                bullet.remove_from_sprite_lists()

        # Bullet collisions
        for bullet in self.bullet_list:

            hit_list = arcade.check_for_collision_with_list(
                bullet,
                self.enemy_list
            )

            if hit_list:

                bullet.remove_from_sprite_lists()

                for enemy in hit_list:

                    enemy.health -= 10

                    self.create_explosion(
                        enemy.center_x,
                        enemy.center_y
                    )

                    if enemy.health <= 0:

                        self.spawn_powerup(
                            enemy.center_x,
                            enemy.center_y
                        )

                        enemy.remove_from_sprite_lists()

                        self.score += 20

                        arcade.play_sound(
                            self.explosion_sound
                        )

        # Enemy collision
        hit_enemies = arcade.check_for_collision_with_list(
            self.player,
            self.enemy_list
        )

        for enemy in hit_enemies:

            if not self.player.shield:

                self.player.health -= 10

            enemy.remove_from_sprite_lists()

        # Powerup collection
        # Player hit by enemy bullets
        for bullet in list(self.enemy_bullet_list):
            if arcade.check_for_collision(bullet, self.player):
                if not self.player.shield:
                    self.player.health -= 10
                bullet.remove_from_sprite_lists()

        powerups = arcade.check_for_collision_with_list(
            self.player,
            self.powerup_list
        )

        for powerup in powerups:

            if powerup.power_type == "rapid":

                self.player.rapid_fire = True

            elif powerup.power_type == "shield":

                self.player.shield = True

            elif powerup.power_type == "health":

                self.player.health = min(
                    100,
                    self.player.health + 30
                )

            self.player.power_timer = POWERUP_DURATION

            powerup.remove_from_sprite_lists()

        # Power timer
        if self.player.power_timer > 0:

            self.player.power_timer -= delta_time

        else:

            self.player.rapid_fire = False
            self.player.shield = False

        # Update particles
        for particle in self.particles:

            particle["x"] += particle["dx"]
            particle["y"] += particle["dy"]

            particle["life"] -= 1

        self.particles = [
            p for p in self.particles
            if p["life"] > 0
        ]

        # Game over
        if self.player.health <= 0:

            self.game_over = True

    # =====================================================
    # EXPLOSION
    # =====================================================

    def create_explosion(self, x, y):

        for i in range(25):

            self.particles.append({

                "x": x,
                "y": y,

                "dx": random.uniform(-4, 4),
                "dy": random.uniform(-4, 4),

                "life": random.randint(20, 40)

            })

    # =====================================================
    # POWERUPS
    # =====================================================

    def spawn_powerup(self, x, y):

        if random.random() < 0.25:

            power_type = random.choice([
                "rapid",
                "shield",
                "health"
            ])

            self.powerup_list.append(
                PowerUp(power_type, x, y)
            )

    # =====================================================
    # RESET

    def reset(self):

        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.powerup_list = arcade.SpriteList()

        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = 1000
        self.player.health = 1000
        self.player.rapid_fire = True
        self.player.shield = True
        self.player.power_timer = 0

        self.score = 0
        self.game_over = False
        self.enemy_timer = 0
        self.shooter_timer = 0
        self.boss_timer = 0

        self.player.angle = 0

    # =====================================================
    # SHOOTING
    # =====================================================

    def fire_bullet(self):

        angle = math.degrees(

            math.atan2(
                self.mouse_y - self.player.center_y,
                self.mouse_x - self.player.center_x
            )

        )

        self.player.angle = angle

        bullet = Bullet(
            self.player.center_x,
            self.player.center_y,
            angle
        )

        self.bullet_list.append(bullet)

        arcade.play_sound(self.shoot_sound)

    def fire_enemy_bullet(self, enemy):

        angle = math.degrees(
            math.atan2(
                self.player.center_y - enemy.center_y,
                self.player.center_x - enemy.center_x
            )
        )

        bullet = EnemyBullet(
            enemy.center_x,
            enemy.center_y,
            angle
        )

        self.enemy_bullet_list.append(bullet)

    # =====================================================
    # INPUT
    # =====================================================

    def on_key_press(self, key, modifiers):

        if key == arcade.key.W:
            self.up = True

        elif key == arcade.key.S:
            self.down = True

        elif key == arcade.key.A:
            self.left = True

        elif key == arcade.key.D:
            self.right = True

    def on_key_release(self, key, modifiers):

        if key == arcade.key.W:
            self.up = False

        elif key == arcade.key.S:
            self.down = False

        elif key == arcade.key.A:
            self.left = False

        elif key == arcade.key.D:
            self.right = False

    def on_mouse_motion(self, x, y, dx, dy):

        self.mouse_x = x
        self.mouse_y = y

        angle = math.degrees(
            math.atan2(
                y - self.player.center_y,
                x - self.player.center_x
            )
        )
        self.player.angle = angle

    def on_mouse_press(self, x, y, button, modifiers):

        if self.game_over:
            button = self.restart_button
            if (button["left"] <= x <= button["left"] + button["width"] and
                    button["bottom"] <= y <= button["bottom"] + button["height"]):
                self.reset()
                return

        self.shoot_pressed = True
        self.shoot_timer = 0.0
        self.fire_bullet()

    def on_mouse_release(self, x, y, button, modifiers):
        self.shoot_pressed = False

# =========================================================
# MAIN
# =========================================================

def main():

    game = SpaceShooter()

    arcade.run()

if __name__ == "__main__":
    main()
