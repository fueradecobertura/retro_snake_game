import pygame
import random  # для генерации случайных чисел (позиции еды, бонусов)
import json    # для сохранения рекорда в файл

pygame.init()    #запускаем все сценарии для работы с ПО, инициализируем все модули


width = 720 # ширина
height = 480 # высота
grid_square = 24 # размер клетки поля
grid_width = width // grid_square # высчитываем ячейки в равных пропорциях для сетки поля
#если считать вручную, то grid_width = 30
grid_height = height // grid_square # grid_height = 20
fps = 60 # частота кадров в секунду

# Цвета в формате RGB
black = (0, 0, 0)  # черный цвет для фона
white = (255, 255, 255)  # белый цвет для текста
green = (0, 255, 0)  # зеленый цвет для змейки
red = (255, 0, 0)  # красный цвет для еды
blue = (0, 0, 255)  # синий цвет для бонусов
yellow = (255, 255, 0)  # желтый цвет для других бонусов
dark_gray = (64, 64, 64)  # темно-серый цвет для рамки, в которую будет биться змея

# цвета для специальных скинов
neon_green = (57, 255, 20)  # неоновый зеленый для неонового скина
neon_pink = (255, 20, 147)  # неоновый розовый для головы неоновой змейки

# цвета для желто-зеленого пиксельного скина
pixel_yellow_green = (154, 205, 50)  # желто-зеленый цвет для головы пиксельной змейки
pixel_lime = (50, 205, 50)  # лаймовый зеленый цвет для тела пиксельной змейки
pixel_dark = (107, 142, 35)  # темный желто-зеленый для текстуры

# загружаем звуки из файлов в папке sounds
eat_sound = pygame.mixer.Sound("sounds/eat.mp3")  # звук поедания еды
bonus_sound = pygame.mixer.Sound("sounds/bonus.mp3")  # звук подбора бонуса
collision_sound = pygame.mixer.Sound("sounds/collision.mp3")  # звук столкновения
menu_sound = pygame.mixer.Sound("sounds/menu.mp3")  # звук нажатия в меню


class Snake:
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width  # сохраняем ширину поля в клетках
        self.grid_height = grid_height  # сохраняем высоту поля в клетках
        self.reset()  # сбрасываем состояние игры в первоначальное состояние

    def reset(self):  # сбрасываем змейку в первоначальное состояние
        # тело змейки - это список координат клеток, который начинается с одной клетки в центре поля
        self.body = [(5, 5)] # чтобы при переходе между уровнями змейка стартовала из независимой части поля и не умирала сразу
        # начальное направление движения (1, 0) вправо
        self.direction = (1, 0)
        # Количество сегментов сетки, которые нужно добавить при следующем движении
        self.grow_pending = 3  # начальная длина змейки
        # количество очков в игре(съеденных сегментов сетки)
        self.score = 0

    def move(self, use_portals=True, border_walls=None, inner_walls=None):   # двигаем змейку вперед на 1 клетку

        if border_walls is None:
            border_walls = []
        if inner_walls is None:
            inner_walls = []

        # получаем координаты головы змейки
        head_x, head_y = self.body[0]
        # получаем направление движения змеййки (dx - изменение по х, dy - изменение по y)
        dx, dy = self.direction
        # вычисляем новые координаты головы
        new_head = ((head_x + dx), (head_y + dy))

        # проверяем, выходит ли змейка за границы поля
        if not use_portals:
            # если используем режим без порталов и змейка выходит за границы - игра заканчивается
            if (new_head[0] < 0 or new_head[0] >= self.grid_width or
                    new_head[1] < 0 or new_head[1] >= self.grid_height):
                return False  # возвращаем false, т.е. у нас движение не удалось, поэтому конец игры
            if new_head in border_walls:
                return False  # столкновение с рамкой в режиме границ
        else: # для режима с порталами(змейка переползает через границу и появляется с противоположной стороны)
            # используем оператор %, чтобы "зациклить" координаты
            new_head = (new_head[0] % self.grid_width, new_head[1] % self.grid_height)

        # проверка столкновения со стенами(серыми)
        if new_head in inner_walls:
            return False

        # проверяем столкновение змейки с самой собой, не ударяется ли голова о её тело
        if new_head in self.body:
            return False  # возвращаем false и игра заканчивается

        # добавляем новую голову в начало списка
        self.body.insert(0, new_head)

        # если змейка должна расти, уменьшаем счетчик роста
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            # если не должна расти, удаляем последний сегмент (хвост)
            self.body.pop()

        return True  # возвращаем true - движение успешно

    def change_direction(self, new_direction): # изменяет направление движения змейки
        dx, dy = self.direction # текущее направление
        new_dx, new_dy = new_direction # новое направление

        # запрещаем разворот на 180 градусов, чтобы змейка не поползла прямо в противоположном направлении
        if (dx, dy) != (-new_dx, -new_dy):
            self.direction = new_direction

    def grow(self, amount=1, play_sound=True):
        # увеличиваем змейку на указанное количество сегментов
        self.grow_pending += amount  # увеличиваем счетчик роста
        self.score += 10 * amount  # увеличиваем счет (по 10 очков за сегмент)
        if play_sound:  # воспроизводим звук поедания
            eat_sound.play()

    # отрисовываем змейку с выбранным скином
    def draw(self, screen, skin="basic"):
        if skin == "basic":
            self.draw_basic(screen)  # базовый скин
        elif skin == "neon":
            self.draw_neon(screen)  # неоновый скин
        elif skin == "pixel":
            self.draw_pixel(screen)  # пиксельный скин

    # отрисовываем базовый скин змейки
    def draw_basic(self, screen):
        for segment in self.body: # проходимся циклом по каждому сегменту змейки
            x, y = segment # берем координаты текущего сегмента
            # рисуем прямоугольник для сегмента змейки, выбираем цвета, переводим координаты сетки в пиксели
            pygame.draw.rect(screen, green, (x * grid_square, y * grid_square, grid_square, grid_square))

    # отрисовываем неоновую змейку
    def draw_neon(self, screen):
        for i, segment in enumerate(self.body):  # цикл проходит по сегментам с их индексами
        # enumerate добавляет номер i к каждому сегменту (0, 1, 2, ...)
            x, y = segment # извлекаем координаты x и y текущего сегмента
            if i == 0: # проверяем, является ли этот сегмент первым (головой змейки), если да, то красим голову в розовый
                pygame.draw.rect(screen, neon_pink, (x * grid_square, y * grid_square, grid_square, grid_square))
            else:
                pygame.draw.rect(screen, neon_green, (x * grid_square, y * grid_square, grid_square, grid_square))
            # рисуем прямоугольники неоново-зеленого цвета для тела, белый контур вокруг сегмента с толщиной линии в 2 пикселя
            pygame.draw.rect(screen, white, (x * grid_square, y * grid_square, grid_square, grid_square), 2)

    # отрисовываем пиксельный скин
    def draw_pixel(self, screen):
        for i, segment in enumerate(self.body):
            x, y = segment
            if i == 0:
                # рисуем голову змейки желто-зеленым цветом
                pygame.draw.rect(screen, pixel_yellow_green,(x * grid_square, y * grid_square, grid_square, grid_square))
                # рисуем левый глаз черного цвета, с отступом в 6 пикселей, глаз 4х4
                pygame.draw.rect(screen, black, (x * grid_square + 6, y * grid_square + 6, 4, 4))
                # правый глаз
                pygame.draw.rect(screen, black, (x * grid_square + 14, y * grid_square + 6, 4, 4))
            else:
                # рисуем тело змейки лаймовым цветом
                pygame.draw.rect(screen, pixel_lime, (x * grid_square, y * grid_square, grid_square, grid_square))
                # рисуем пиксельную структуру для змейки, просто смещаем клеточки с разными оттенками зеленого, текстурный пиксель 8х8
                pygame.draw.rect(screen, pixel_dark, (x * grid_square + 2, y * grid_square + 2, 8, 8))
                pygame.draw.rect(screen, pixel_dark, (x * grid_square + 14, y * grid_square + 14, 8, 8))


class Food:

    def __init__(self):
        self.position = (0, 0)  # Позиция еды на поле
        self.spawn()  # Сразу размещаем еду на поле

    # размещаем еду в случайной свободной клетке
    def spawn(self, snake_body=None, walls=None):
        if snake_body is None:
            snake_body = []  # если тело змейки не передано, используем пустой список
        if walls is None:
            walls = []  # если стены не переданы, используем пустой список

        # используем бесконечный цикл для поиска свободной клетки
        while True:
            # генерируем случайные координаты в пределах игрового поля
            self.position = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
            # если клетка свободна (не в змейке и не в стене), выходим из цикла
            if self.position not in snake_body and self.position not in walls:
                break  # выходим из цикла, тк нашли свободную клетку

    def draw(self, screen): # отрисовываем еду на экране
        x, y = self.position
        # рисуем еду как красный прямоугольник
        pygame.draw.rect(screen, red, (x * grid_square, y * grid_square, grid_square, grid_square))


class Bonus:

    def __init__(self):
        self.position = (0, 0)  # позиция бонуса
        self.active = False  # активность бонуса
        self.type = None  # тип бонуса ("+2" или "slow")
        self.timer = 0  # таймер видимости бонуса на поле
        self.active_effect = None  # активный эффект змейки
        self.effect_timer = 0  # таймер действия эффекта змейки

    def spawn(self, snake_body, walls=None): # создаем бонус в случайной свободной клетке

        if walls is None:
            walls = []  # если стены не переданы, используем пустой список

        # 10% шанс появления бонуса при каждом вызове метода
        if random.random() < 0.1:
            # случайно выбираем тип бонуса из двух вариантов
            self.type = random.choice(["+2", "slow"])
            self.active = True  # активируем бонус

            # ищем свободную клетку для бонуса
            while True:
                self.position = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
                # если клетка свободна (не занята змейкой и не является стеной), выходим из цикла
                if self.position not in snake_body and self.position not in walls:
                    break

            self.timer = 300  # устанавливаем таймер (300 кадров = 5 секунд при 60 FPS)

    def update(self): # обновляем состояние бонуса(уменьшаем таймер)
        if self.active:
            self.timer -= 1  # уменьшаем таймер на 1 каждый кадр
            if self.timer <= 0:
                self.active = False  # если время вышло, делаем бонус неактивным

        # обновляем таймер активного эффекта
        if self.effect_timer > 0:
            self.effect_timer -= 1
            if self.effect_timer <= 0:  # эффект закончился
                self.active_effect = None  # сбрасываем эффект

    # применяем эффект бонуса к змейке
    def apply_effect(self, effect_type):

        self.active_effect = effect_type
        # эффект замедления длится 600 тиков (примерно 10 секунд при 60 FPS)
        if effect_type == "slow":
            self.effect_timer = 600
        # для "+2" таймер эффекта не нужен, так как это мгновенные очки

    def draw(self, screen): # отрисовываем бонус на экране
        if self.active:
            x, y = self.position
            # выбираем цвет в зависимости от типа бонуса
            color = yellow if self.type == "+2" else blue
            # рисуем бонус
            pygame.draw.rect(screen, color, (x * grid_square, y * grid_square, grid_square, grid_square))


class Game:
    def __init__(self): # создаем объекты класса

        # создаем игровое окно
        self.screen = pygame.display.set_mode((width, height))
        # создаем заголовок
        pygame.display.set_caption("Retro Snake Game")
        # создаем часы, чтобы отслеживать время, fps там
        self.clock = pygame.time.Clock()

        # инициализируем шрифты
        self.initialize_fonts()

        # создаем объекты
        self.snake = Snake(grid_width, grid_height)
        self.food = Food()
        self.bonus = Bonus()

        # настраиваем игру
        self.game_speed = 10  # интервал между движениями змейки (в кадрах в секунду)
        self.frame_counter = 0  # счетчик кадров для контроля движения
        self.game_over = False  # флаг окончания игры
        self.paused = False  # флаг паузы
        self.use_portals = False  # режим порталов (False = есть границы)
        self.current_skin = "basic"  # текущий выбранный скин
        self.current_level = 0  # текущий уровень (индекс в списке уровней)

        # создаем уровни и загружаем стены текущего уровня
        self.levels = self.create_levels()  # создаем 5 уровней
        self.border_walls, self.inner_walls = self.levels[self.current_level]  # разделяем стены
        self.all_walls = self.border_walls + self.inner_walls  # список стен для отрисовки

        self.load_settings()  # загружаем сохраненные настройки

    def initialize_fonts(self):
        try:
            # загружаем шрифт undertale из папки fonts
            undertale_font_path = "fonts/undertale.ttf"
            self.main_font = pygame.font.Font(undertale_font_path, 30)
            self.small_font = pygame.font.Font(undertale_font_path, 20)
            self.tiny_font = pygame.font.Font(undertale_font_path, 18)
        except FileNotFoundError:
            # если шрифт не найден — используем системный
            self.main_font = pygame.font.SysFont("courier", 36, bold=True)
            self.small_font = pygame.font.SysFont("courier", 24)
            self.tiny_font = pygame.font.SysFont("courier", 18)

        # создаем рамку из стен по краям игрового поля
    def create_border_walls(self):  # создаем рамку по краям экрана

        walls = []  # создаем пустой список для хранения координат стен

        # строим верхнюю и нижнюю границы(проходим по всем координатам х
        for x in range(grid_width):
            walls.append((x, 0))  # для верхней границы, это при y = 0
            walls.append((x, grid_height - 1))  # нижняя граница, можно было поставить (х, 19), но проще не считать и написать grid_height - 1

        # левую и правую границы(проходим по координатам у)
        for y in range(1, grid_height - 1):  # проходим по у (кроме углов)
            walls.append((0, y))  # для левой границы, при х = 0
            walls.append((grid_width - 1, y))  # для правой границы

        return walls  # возвращаем список координат стен

    # создаем 5 уровней(карточек)
    def create_levels(self):
        levels = []

        # Уровень 1: Только рамка
        level1_border = self.create_border_walls()  # создаем рамку
        level1_inner = []  # нет внутренних препятствий
        levels.append((level1_border, level1_inner))  # сохраняем как кортеж (рамка, внутренние)

        # Уровень 2: Рамка + плюсик в центре поля
        level2_border = self.create_border_walls()
        level2_inner = []  # список для внутренних препятствий
        center_x = grid_width // 2  # находим центр по х (15)
        center_y = grid_height // 2  # находим центр по у (10)
        for i in range(-3, 4):  # создаем линии длиной 7 клеток
            level2_inner.append((center_x + i, center_y))  # горизонтальная линия плюсик
            level2_inner.append((center_x, center_y + i))  # вертикальная линия плюсик
        levels.append((level2_border, level2_inner))  # сохраняем как кортеж

        # Уровень 3: Рамка + квадраты в 4 углах
        level3_border = self.create_border_walls()
        level3_inner = []
        for i in range(4):  # создаем квадраты 4x4 клетки
            for j in range(4):
                level3_inner.append((2 + i, 2 + j))  # верхний левый угол
                level3_inner.append((grid_width - 6 + i, 2 + j))  # верхний правый
                level3_inner.append((2 + i, grid_height - 6 + j))  # нижний левый
                level3_inner.append((grid_width - 6 + i, grid_height - 6 + j))  # нижний правый
        levels.append((level3_border, level3_inner))

        # Уровень 4: Рамка + лабиринт из стен
        level4_border = self.create_border_walls()
        level4_inner = []
        for i in range(5, 15):  # создаем вертикальные стены
            level4_inner.append((10, i))  # левая
            level4_inner.append((20, i))  # правая
        for i in range(10, 20):  # создаем горизонтальные стены
            level4_inner.append((i, 8))  # верхняя
            level4_inner.append((i, 12))  # нижняя
        levels.append((level4_border, level4_inner))

        # Уровень 5: Рамка + случайные препятствия
        level5_border = self.create_border_walls()
        level5_inner = []
        for _ in range(20):  # создаем 20 случайных блоков
            x = random.randint(3, grid_width - 4)  # Случайная х координата (не у края)
            y = random.randint(3, grid_height - 4)  # Случайная у координата
            if (x, y) not in level5_inner:
                level5_inner.append((x, y))  # добавляем стену в случайную позицию
        levels.append((level5_border, level5_inner))

        return levels  # возвращаем список кортежей (рамка, внутренние препятствия)

    # сохраняем текущие настройки в файл
    def load_settings(self):
        try:
            with open("highscore.json", "r") as f:
                data = json.load(f)
                self.high_score = data.get("high_score", 0)  # получаем рекорд или 0
                self.current_skin = data.get("skin", "basic")  # получаем скин
        except:
            self.high_score = 0  # устанавливаем рекорд в 0 при ошибке
            self.current_skin = "basic"  # устанавливаем базовый скин

    # сохраняем текущие настройки в файл
    def save_settings(self):
        try:
            with open("highscore.json", "w") as f:  # открываем файл для записи
                json.dump({  # сохраняем словарь в формате json
                    "high_score": self.high_score,  # сохраняем рекорд
                    "skin": self.current_skin  # сохраняем выбранный скин
                }, f)
        except:
            pass  # игнорируем ошибку

    # настраиваем нажатия клавиш(движения змейки, переключение режима игры, пауза, перезапуск, выход из игры и тд)
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # если пользователь закрыл окно (нажал крестик), выходим из игры
                return False
            # настраиваем нажатия клавиш
            elif event.type == pygame.KEYDOWN:
                # KEYDOWN - событие нажатия клавиши, работает только когда его капсом пишем
                if event.key == pygame.K_ESCAPE:
                    # ESC переключает паузу (вкл/выкл)
                    self.paused = not self.paused
                    menu_sound.play()  # воспроизводим звук меню
                elif event.key == pygame.K_r:
                    # R - перезапуск игры
                    self.reset_game()
                    menu_sound.play()
                elif event.key == pygame.K_p:
                    # P - переключение режима порталов/рамки
                    self.use_portals = not self.use_portals
                    self.reset_game()  # перезапускаем игру при смене режима
                    menu_sound.play()
                elif event.key == pygame.K_s:
                    # S - переключение скинов
                    skins = ["basic", "neon", "pixel"]  # список доступных скинов
                    current_index = skins.index(self.current_skin)  # находим индекс текущего скина
                    self.current_skin = skins[(current_index + 1) % len(skins)]  # переключаем на следующий скин
                    self.save_settings()  # сохраняем новый скин
                    menu_sound.play()  # воспроизводим звук меню
                elif event.key == pygame.K_l:
                    # Клавиша L - переключение уровней
                    self.current_level = (self.current_level + 1) % len(self.levels)  # переключаем уровень
                    self.border_walls, self.inner_walls = self.levels[self.current_level]  # Обновляем стены
                    self.all_walls = self.border_walls + self.inner_walls  # загружаем стены нового уровня
                    self.reset_game()  # перезапускаем игру
                    menu_sound.play()  # воспроизводим звук меню
                elif not self.paused and not self.game_over:
                    # управление змейкой(только если игра не на паузе и не окончена)
                    # стрелками вверх, вниз, влево, вправо
                    if event.key == pygame.K_UP:
                        self.snake.change_direction((0, -1))  # вверх (уменьшаем у)
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction((0, 1))  # вниз (увеличиваем у)
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction((-1, 0))  # влево (уменьшаем х)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction((1, 0))  # право (увеличиваем х)

        return True  # возвращаем True, чтобы продолжить игру

    def update(self): # обновляем состояние игры(настраиваем её логику)
        # если игра на паузе или окончена, не обновляем состояние
        if self.paused or self.game_over:
            return

        # увеличиваем счетчик кадров, без него змейка будет просто стоять на месте
        self.frame_counter += 1
        # если достигли нужного количества кадров для движения змейки, сбрасываем счетчик
        if self.frame_counter >= self.game_speed:
            self.frame_counter = 0

            # настраиваем движение змейки с учетом выбранного режима (портала или рамки)
            if not self.snake.move(self.use_portals, self.border_walls, self.inner_walls):
                # если змейка столкнулась со стеной или с собой, заканчиваем игру
                self.game_over = True
                collision_sound.play()  # Воспроизводим звук столкновения
                self.save_high_score()  # сохраняем рекорд
                return

            # проверка съедания еды
            if self.snake.body[0] == self.food.position:
                self.snake.grow(1)  #если голова змейки находится на клетке с едой, увеличиваем змейку на 1 сегмент
                self.food.spawn(self.snake.body, self.all_walls)  # c помощью spawn создаем новую еду в свободном месте
                # ускоряем игру (уменьшаем интервал между движениями)
                if self.game_speed > 5:  # минимальная скорость - 5 кадров между движениями
                    self.game_speed -= 0.5  # ускоряем на 0.5 кадра(уменьшаем интервал)

            # проводим проверку съедания бонусов
            if self.bonus.active and self.snake.body[0] == self.bonus.position:
                bonus_sound.play()  # воспроизводим звук бонуса
                # если голова змейки находится на клетке с активным бонусом, увеличиваем на 2 сегмента
                if self.bonus.type == "+2":
                    self.snake.grow(2)
                elif self.bonus.type == "slow":
                    self.game_speed += 3  # замедляем игру (увеличиваем интервал)
                    self.bonus.apply_effect("slow")  # применяем эффект замедления
                self.bonus.active = False  # Делаем бонус неактивным после использования

            # спавн бонусов (1% шанс получить бонус каждый кадр движения)
            if not self.bonus.active and random.random() < 0.01:
                self.bonus.spawn(self.snake.body, self.all_walls)

            # обновляем состояние бонуса (уменьшаем таймер)
            self.bonus.update()

    def draw(self): #отрисовываем объекты игры на экране
        # делаем экран черным
        self.screen.fill(black)

        # Отрисовка стен
        for wall in self.all_walls:
            x, y = wall
            # Рисуем темно-серые прямоугольники для стен
            # Используем dark_gray вместо gray для более непрозрачного вида
            pygame.draw.rect(self.screen, dark_gray, (x * grid_square, y * grid_square, grid_square, grid_square))

        # Отрисовка игровых объектов поверх фона и стен
        self.snake.draw(self.screen,self.current_skin)  # Змейка
        self.food.draw(self.screen)  # Еда
        if self.bonus.active:
            self.bonus.draw(self.screen)  # Бонус (если активен)

        # Создаем текстовые элементы HUD
        score_text = self.main_font.render(f"SCORE: {self.snake.score}", True, white)  # счет
        length_text = self.main_font.render(f"LENGTH: {len(self.snake.body)}", True, white)  # длина змейки
        high_score_text = self.main_font.render(f"BEST: {self.high_score}", True, white)  # рекорд
        mode_text = self.small_font.render(f"MODE: {'PORTALS' if self.use_portals else 'BORDERS'}", True, white)  # режим
        skin_text = self.small_font.render(f"SKIN: {self.current_skin.upper()}", True, white)  # скин
        level_text = self.small_font.render(f"LEVEL: {self.current_level + 1}/5", True, white)  # уровень

        # отображаем текст на экране
        self.screen.blit(score_text, (10, 10))  # счет в верхнем левом углу
        self.screen.blit(length_text, (10, 50))  # длина ниже счета
        self.screen.blit(high_score_text, (10, 90))  # рекорд ниже длины
        self.screen.blit(mode_text, (10, 130))  # режим игры
        self.screen.blit(skin_text, (10, 160))  # текущий скин
        self.screen.blit(level_text, (10, 190))  # уровень

        # отображаем информацию об активном бонусе
        if self.bonus.active_effect:
            effect_name = "SLOWDOWN" if self.bonus.active_effect == "slow" else "BONUS"  # название эффекта бонуса
            time_left = self.bonus.effect_timer // 60  # оставшееся время в секундах
            bonus_text = self.small_font.render(f"ACTIVE: {effect_name} ({time_left}s)", True, yellow)  # текст бонуса
            self.screen.blit(bonus_text, (10, 220))

        # отображаем текущую скорость игры
        speed_text = self.tiny_font.render(f"SPEED: {10 - self.game_speed:.1f}", True, white)
        self.screen.blit(speed_text, (10, 250))

        # подсказки по управлению (внизу экрана)
        control_text = self.tiny_font.render("P - CHANGE MODE  R - RESTART  ESC - PAUSE S-SKIN L-LEVEL", True, white)
        self.screen.blit(control_text, (10, height - 30))  # слева внизу

        # если игра на паузе, отображаем сообщение, что на паузе
        if self.paused:
            # создаем два текста для паузы
            pause_text = self.main_font.render("PAUSED", True, white)
            continue_text = self.small_font.render("Press ESC to continue", True, white)

            # вычисляем позиции для центрирования текста
            text_rect = pause_text.get_rect(center=(width // 2, height // 2 - 20))
            continue_rect = continue_text.get_rect(center=(width // 2, height // 2 + 20))

            # отображаем текст паузы и подсказку
            self.screen.blit(pause_text, text_rect)
            self.screen.blit(continue_text, continue_rect)

        # Если игра окончена, отображаем сообщение game over
        if self.game_over:
            # создаем два текста для окончания игры
            game_over_text = self.main_font.render("GAME OVER", True, white)
            restart_text = self.small_font.render("Press R to restart", True, white)

            # вычисляем положение текста по центру
            text_rect = game_over_text.get_rect(center=(width // 2, height // 2 - 20))
            restart_rect = restart_text.get_rect(center=(width // 2, height // 2 + 20))

            # отображаем текст
            self.screen.blit(game_over_text, text_rect)
            self.screen.blit(restart_text, restart_rect)

        # обновляем экран и показываем все, что нарисовали в этом кадре
        pygame.display.flip()

    # сбрасываем игру в первоначальное состояние
    def reset_game(self):
        self.snake.reset()  # сбрасываем змейку (позиция, длина, счет)
        self.food.spawn(self.snake.body, self.all_walls)  # размещаем новую еду
        self.bonus.active = False  # делаем бонусы неактивными
        self.bonus.active_effect = None  # убираем активный эффект
        self.bonus.effect_timer = 0  # сбрасываем таймер эффекта
        self.game_speed = 10  # сбрасываем скорость игры к начальной
        self.frame_counter = 0  # также счетчик кадров
        self.game_over = False  # и флаг окончания игры
        self.paused = False  # и флаг паузы

    # сохраняем текущий счет в лучший, если он побит
    def save_high_score(self):
        if self.snake.score > self.high_score:  # если текущий счет больше рекорда
            self.high_score = self.snake.score  # обновляем рекорд
            self.save_settings()  # сохраняем в файл

    # игровой цикл
    def run(self):
        running = True
        while running:
            # обрабатываем события (нажатия клавиш и тд)
            running = self.handle_events()
            # также состояние игры
            self.update()
            # отрисовываем все объекты
            self.draw()
            # контролируем fps (задержку для поддержания 60 кадров в секунду)
            self.clock.tick(fps)

        # завершаем pygame при выходе из цикла
        pygame.quit()


# запускаем игру
if __name__ == "__main__":
    # создаем экземпляр игры и запускаем его
    game = Game()
    game.run()
