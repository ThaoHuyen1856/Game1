# khai báo các thư viện cần sử dụng
import pygame
import random
from time import sleep
from os import walk
pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()


# Thiết lập kích thước màn hình
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
def loadImage(path):
    return pygame.image.load(path).convert_alpha()


# Đặt tên và icon
pygame.display.set_caption('Last mile delivery')
icon = loadImage(r'C:\assets\shipper.png')
pygame.display.set_icon(icon)
# Tạo Background
bg = loadImage(r'C:\assets\bg.png')
# Các hình ảnh
h0 = loadImage(r'C:\assets\house0.png')
t0 = loadImage(r'C:\assets\tree0.png')
h1 = loadImage(r'C:\assets\house1.png')
t1 = loadImage(r'C:\assets\tree1.png')
h2 = loadImage(r'C:\assets\house2.png')
jump_obstacle_img = loadImage(r'C:\assets\jump.png')
duck_obstacle_img = loadImage(r'C:\assets\chim.png')
stop_obstacle_img = loadImage(r'C:\assets\den.png')
start_screen_bg = pygame.image.load(r"C:\assets\start_screen_bg.png").convert()
fuel_img = loadImage(r"C:\assets\fuel.png")
water_img = loadImage(r"C:\assets\water.png")
tip_img = loadImage(r"C:\assets\tip.PNG")


# Tải âm thanh
audio = {}
for _, __, sound_files in walk(r"C:\audio"):
    for sound_file in sound_files:
        if sound_file.endswith(".wav"):
            key = sound_file.replace(".wav", "")
            audio[key] = pygame.mixer.Sound(r"C:\audio\\" + sound_file)


# Phát nhạc nền
if "bg_music" in audio:
    audio["bg_music"].play(-1)
else:
    print("Không tìm thấy file bg_music.wav trong thư mục C:\\audio")
# Khởi tạo vị trí di chuyển nền
bg_x, bg_y = 0, 10
x_def = 5
x_def_hold = x_def


# Biến trò chơi
score = 0
level = 1
items_collected = 0
player_y = 450
player_velocity_y = 0
is_jumping = False
is_ducking = False
is_stopped = False
result = "lose"


# Người chơi
player_img = loadImage(r'C:\assets\pl.PNG')
player_img = pygame.transform.scale(player_img, (100, 100))
player_rect = player_img.get_rect(topleft=(200, player_y))


# Font chữ
font = pygame.font.Font(None, 36)
try:
    result_font = pygame.font.Font(r"C:\assets\font.otf", 200)
except FileNotFoundError:
    print("Font file not found. Using default font.")
    result_font = pygame.font.SysFont("arial", 200)
BLACK = (0, 0, 0)
WHITE=(255,255,255)
def show_start_screen():
    while True:
        # Hiển thị hình nền
        SCREEN.blit(start_screen_bg, (0, 0))
        # Kiểm tra sự kiện để bắt đầu game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return  # Thoát vòng lặp và bắt đầu trò chơi


        # Cập nhật màn hình
        pygame.display.flip()
        clock.tick(60)


# Hiển thị màn hình bắt đầu
show_start_screen()
# Lớp chướng ngại vật
class Obstacle:
    def __init__(self, x, y, width, height, image, type):
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))  # Sử dụng 'topleft'
        self.type = type
    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)


# Lớp vật phẩm hỗ trợ
class Item:
    def __init__(self, x, y, width, height, image, item_type):
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.item_type = item_type  # Gán loại vật phẩm
    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)


# Hàm tạo chướng ngại vật
def create_obstacle():
    obstacle_type = random.choice(["jump", "duck", "stop"])
    x = SCREEN_WIDTH + random.randint(100, 300)
    if obstacle_type == "jump":
        return Obstacle(x, 530, 70, 70, jump_obstacle_img, "jump")
    elif obstacle_type == "duck":
        return Obstacle(x, player_y - 40, 60, 60, duck_obstacle_img, "duck")
    elif obstacle_type == "stop":
        return Obstacle(x, 400, 150, 150, stop_obstacle_img, "stop")


# Hàm tạo vật phẩm
def create_item():
    item_type = random.choice(["fuel", "water", "tip"])  
    width, height = 50, 50
    x = SCREEN_WIDTH + random.randint(100, 300)
    if item_type == "fuel":
        return Item(x, 450, width, height, fuel_img, "fuel")
    elif item_type == "water":
        return Item(x, 450, width, height, water_img, "water")
    elif item_type == "tip":
        return Item(x, 350, width, height, tip_img, "tip")


# Tập hợp các đối tượng nhà và cây
objects = [
    {"image": h0, "x": 1100, "y": player_y - 190},
    {"image": t0, "x": 900, "y": player_y - 190},
    {"image": h1, "x": 550, "y": player_y - 250},
    {"image": t1, "x": 350, "y": player_y - 120},
    {"image": h2, "x": 20, "y": player_y - 320},
]


# Danh sách vật phẩm và chướng ngại vật
items = []
obstacles = []


# Vòng lặp chính


running = True
item_timer = 0
obstacle_timer = 0
while running:
    x_def += 0.0001
    x_def_hold += 0.001


    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    # Xử lý phím bấm
    player_rect.y = player_y
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and not is_jumping:
        is_jumping = True
        player_velocity_y = -20
    if keys[pygame.K_DOWN]:
        is_ducking = True
        player_img = pygame.transform.scale(player_img, (100, 50))
        player_rect = player_img.get_rect(topleft=(200, player_y + 50))
    else:
        is_ducking = False
        player_img = pygame.transform.scale(player_img, (100, 100))
        player_rect = player_img.get_rect(topleft=(200, player_y))
    if keys[pygame.K_LEFT]:
        is_stopped = True
        x_def = 2
    else:
        is_stopped = False
        x_def = x_def_hold
    # Xử lý nhảy
    if is_jumping:
        player_velocity_y += 1
        player_y += player_velocity_y
        if player_y >= 450:
            player_y = 450
            is_jumping = False


    # Tạo vật phẩm và chướng ngại vật
    item_timer += 1
    obstacle_timer += 1
    if item_timer > 60 * 5:
        items.append(create_item())
        item_timer = 0
    if obstacle_timer > 60 * 3:
        obstacles.append(create_obstacle())
        obstacle_timer = 0


    # Vẽ nền di chuyển
    SCREEN.blit(bg, (bg_x, bg_y))
    SCREEN.blit(bg, (bg_x + SCREEN_WIDTH, bg_y))
    bg_x -= x_def
    if bg_x <= -SCREEN_WIDTH:
        bg_x = 0


    # Vẽ nhà và cây
    for obj in objects:
        obj["x"] -= x_def
        SCREEN.blit(obj["image"], (obj["x"], obj["y"]))
        if obj["x"] <= -obj["image"].get_width():
            obj["x"] = SCREEN_WIDTH


    # Vẽ vật phẩm và xử lý va chạm
    for item in items[:]:
        item.rect.x -= x_def
        item.draw(SCREEN)
        if item.rect.right < 0:  # Xóa vật phẩm nếu ra khỏi màn hình
            items.remove(item)
        elif player_rect.colliderect(item.rect):  # Kiểm tra va chạm với nhân vật
           
            if item.item_type == "fuel":  # Nếu là bình xăng
                score += 10
                audio["point"].play()
            elif item.item_type == "water":  # Nếu là bình nước
                score += 5
                audio["point"].play()
            elif item.item_type == "tips":  # Nếu là tips
                if is_jumping:  # Chỉ thu thập được khi đang nhảy
                    score += 20
                    audio["point"].play()
            items_collected += 1  # Tăng số lượng vật phẩm thu thập
            items.remove(item)  # Xóa vật phẩm khỏi danh sách


    # Vẽ và kiểm tra chướng ngại vật
    for obstacle in obstacles[:]:
        obstacle.rect.x -= x_def
        obstacle.draw(SCREEN)
        if obstacle.rect.x < -obstacle.rect.width:
            obstacles.remove(obstacle)
        elif player_rect.colliderect(obstacle.rect):
            if (obstacle.type == "jump" and not is_jumping) or (obstacle.type == "duck" and not is_ducking) or (obstacle.type == "stop" and not is_stopped):
                running = False
                x_def = 0
                audio["hit"].play()
                result_text = result_font.render(f"Oh no...", True, WHITE)
                SCREEN.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2  - result_text.get_height() // 2))


    # Kiểm tra level
    if score >= 100 and level < 2:
        level = 2
        audio["lv_up"].play()
    if score >= 300 and level < 3:
        level = 3
        audio["lv_up"].play()
    if score >= 600:
        running = False
        result_text = result_font.render(f"Giao hàng thành công", True, WHITE)
        SCREEN.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2  - result_text.get_height() // 2))


    # Hiển thị thông tin
    score_text = font.render(f"Score: {score}", True, BLACK)
    SCREEN.blit(score_text, (10, 10))
    level_text = font.render(f"Level: {level}", True, BLACK)
    SCREEN.blit(level_text, (10, 50))


    # Vẽ người chơi
    SCREEN.blit(player_img, (player_rect.x, player_rect.y))
    pygame.display.flip()
    if not running:
        sleep(1)
        
pygame.quit()



