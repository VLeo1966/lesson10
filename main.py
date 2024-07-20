import pygame
import random
import sys
from abc import ABC, abstractmethod

# Константы
WINDOW_SIZE = (600, 400)
SNAKE_SIZE = 20
FPS = 3

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Абстрактный класс для объектов, которые можно отрисовывать
class Drawable(ABC):
    @abstractmethod
    def draw(self, screen):
        pass

# Абстрактный класс для объектов, которые можно обновлять
class Updatable(ABC):
    @abstractmethod
    def update(self):
        pass

# Комбинированный абстрактный класс для игровых объектов, которые можно отрисовывать и обновлять
class GameObject(Drawable, Updatable):
    pass

# Главный класс игры, который управляет основным циклом игры и обработкой событий
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()
        self.running = True
        self.snake = Snake()
        self.food = Food()
        self.game_objects = [self.snake, self.food]

    # Главный цикл игры
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    # Обработка событий, таких как нажатия клавиш и выход из игры
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snake.change_direction('UP')
                elif event.key == pygame.K_DOWN:
                    self.snake.change_direction('DOWN')
                elif event.key == pygame.K_LEFT:
                    self.snake.change_direction('LEFT')
                elif event.key == pygame.K_RIGHT:
                    self.snake.change_direction('RIGHT')

    # Обновление состояния всех игровых объектов
    def update(self):
        for obj in self.game_objects:
            obj.update()
        if self.snake.check_collision():
            self.running = False
        if self.snake.eat(self.food.position):
            self.food.spawn(self.snake.body)

    # Отрисовка всех игровых объектов на экране
    def render(self):
        self.screen.fill(BLACK)
        for obj in self.game_objects:
            obj.draw(self.screen)
        pygame.display.flip()

# Класс змейки, которая управляется игроком
class Snake(GameObject):
    def __init__(self):
        self.body = [(100, 100), (80, 100), (60, 100)]
        self.direction = 'RIGHT'
        self.grow = False

    # Изменение направления движения змейки
    def change_direction(self, direction):
        if direction == 'UP' and self.direction != 'DOWN':
            self.direction = direction
        elif direction == 'DOWN' and self.direction != 'UP':
            self.direction = direction
        elif direction == 'LEFT' and self.direction != 'RIGHT':
            self.direction = direction
        elif direction == 'RIGHT' and self.direction != 'LEFT':
            self.direction = direction

    # Обновление состояния змейки (движение)
    def update(self):
        self.move()

    # Логика движения змейки и обработка прохождения через стены
    def move(self):
        head_x, head_y = self.body[0]

        if self.direction == 'UP':
            head_y -= SNAKE_SIZE
        elif self.direction == 'DOWN':
            head_y += SNAKE_SIZE
        elif self.direction == 'LEFT':
            head_x -= SNAKE_SIZE
        elif self.direction == 'RIGHT':
            head_x += SNAKE_SIZE

        # Телепортация через стены
        head_x %= WINDOW_SIZE[0]
        head_y %= WINDOW_SIZE[1]

        new_head = (head_x, head_y)
        self.body = [new_head] + self.body[:-1]

        if self.grow:
            self.body.append(self.body[-1])
            self.grow = False

    # Отрисовка змейки на экране
    def draw(self, screen):
        for segment in self.body:
            pygame.draw.rect(screen, GREEN, (*segment, SNAKE_SIZE, SNAKE_SIZE))
        self.draw_face(screen)

    # Отрисовка лица змейки
    def draw_face(self, screen):
        head_x, head_y = self.body[0]

        # Координаты глаз и рта относительно головы змейки
        if self.direction == 'UP':
            left_eye = (head_x + 5, head_y + 5)
            right_eye = (head_x + 15, head_y + 5)
            mouth_start = (head_x + 7, head_y + 15)
            mouth_end = (head_x + 13, head_y + 15)
        elif self.direction == 'DOWN':
            left_eye = (head_x + 5, head_y + 15)
            right_eye = (head_x + 15, head_y + 15)
            mouth_start = (head_x + 7, head_y + 5)
            mouth_end = (head_x + 13, head_y + 5)
        elif self.direction == 'LEFT':
            left_eye = (head_x + 5, head_y + 5)
            right_eye = (head_x + 5, head_y + 15)
            mouth_start = (head_x + 15, head_y + 7)
            mouth_end = (head_x + 15, head_y + 13)
        else:  # RIGHT
            left_eye = (head_x + 15, head_y + 5)
            right_eye = (head_x + 15, head_y + 15)
            mouth_start = (head_x + 5, head_y + 7)
            mouth_end = (head_x + 5, head_y + 13)

        pygame.draw.circle(screen, WHITE, left_eye, 3)
        pygame.draw.circle(screen, WHITE, right_eye, 3)
        pygame.draw.line(screen, RED, mouth_start, mouth_end, 2)

    # Проверка на столкновение с самой собой
    def check_collision(self):
        head = self.body[0]
        if head in self.body[1:]:
            return True
        return False

    # Логика поедания пищи
    def eat(self, food_position):
        if self.body[0] == food_position:
            self.grow = True
            return True
        return False

# Класс еды, которая появляется на игровом поле
class Food(GameObject):
    def __init__(self):
        self.position = (0, 0)
        self.spawn([])

    # Спавн еды в случайном месте, не совпадающем с телом змейки
    def spawn(self, snake_body):
        while True:
            x = random.randint(0, (WINDOW_SIZE[0] // SNAKE_SIZE) - 1) * SNAKE_SIZE
            y = random.randint(0, (WINDOW_SIZE[1] // SNAKE_SIZE) - 1) * SNAKE_SIZE
            self.position = (x, y)
            if self.position not in snake_body:
                break

    # Обновление состояния еды (не используется, но требуется для интерфейса)
    def update(self):
        pass

    # Отрисовка еды на экране
    def draw(self, screen):
        pygame.draw.rect(screen, RED, (*self.position, SNAKE_SIZE, SNAKE_SIZE))

if __name__ == "__main__":
    game = Game()
    game.run()
