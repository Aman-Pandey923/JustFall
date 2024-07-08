import pygame
import random
import cv2
import mediapipe as mp
import time
import HandTrackingModule as htm 

# Initialize pygame and mixer
pygame.init()
pygame.mixer.init()

# Game settings
WIDTH = 500
HEIGHT = 800
FPS = 60
PLAYER_SPEED = 40
ENEMY_SPEED_INCREMENT = 15

# Colors and fonts
bg = (135, 206, 235)
huge_font = pygame.font.Font('assets/Terserah.ttf', 42)
font = pygame.font.Font('assets/Terserah.ttf', 24)

# Screen setup
pygame.display.set_caption('Penguins Can\'t Fly!')
screen = pygame.display.set_mode([WIDTH, HEIGHT])

# Load images
cloud_images = [pygame.image.load(f'assets/clouds/cloud{i}.png') for i in range(1, 4)]
penguin = pygame.transform.scale(pygame.image.load('assets/penguin.png'), (50, 50))
shark = pygame.transform.scale(pygame.image.load('assets/jetpack_shark.png'), (300, 200))

# Load sounds
pygame.mixer.music.load('assets/theme.mp3')
bounce = pygame.mixer.Sound('assets/bounce.mp3')
end_sound = pygame.mixer.Sound('assets/game_over.mp3')
pygame.mixer.music.play()
pygame.mixer.music.set_volume(0.2)

# Initialize hand detector
cap = cv2.VideoCapture(0)
detector = htm.handDetector(detectionCon=0.5)

# Player and game variables
player_x = 240
player_y = 40
direction = -1
y_speed = 0
gravity = 0.2
score = 0
total_distance = 0
game_over = False

# Read high score from file
with open('high_scores.txt', 'r') as file:
    first_high = int(file.readlines()[0])
    high_score = first_high

# Cloud and enemy settings
clouds = [[200, 100, 1], [50, 330, 2], [350, 330, 3], [200, 670, 1]]
enemies = [[-234, random.randint(400, HEIGHT - 100), 1]]

def draw_clouds(cloud_list, images):
    platforms = []
    for cloud in cloud_list:
        image = images[cloud[2] - 1]
        platform = pygame.rect.Rect((cloud[0] + 5, cloud[1] + 40), (120, 10))
        screen.blit(image, (cloud[0], cloud[1]))
        pygame.draw.rect(screen, 'gray', [cloud[0] + 5, cloud[1] + 40, 120, 3])
        platforms.append(platform)
    return platforms

def draw_player(x_pos, y_pos, player_img, direc):
    if direc == -1:
        player_img = pygame.transform.flip(player_img, False, True)
    screen.blit(player_img, (x_pos, y_pos))
    player_rect = pygame.rect.Rect((x_pos + 7, y_pos + 40), (36, 10))
    return player_rect

def draw_enemies(enemy_list, shark_img):
    enemy_rects = []
    for enemy in enemy_list:
        enemy_rect = pygame.rect.Rect((enemy[0] + 40, enemy[1] + 50), (215, 70))
        enemy_rects.append(enemy_rect)
        if enemy[2] == 1:
            screen.blit(shark_img, (enemy[0], enemy[1]))
        else:
            screen.blit(pygame.transform.flip(shark_img, 1, 0), (enemy[0], enemy[1]))
    return enemy_rects

def move_enemies(enemy_list, current_score):
    enemy_speed = ENEMY_SPEED_INCREMENT + current_score // 15
    for enemy in enemy_list:
        if enemy[2] == 1:
            if enemy[0] < WIDTH:
                enemy[0] += enemy_speed
            else:
                enemy[2] = -1
        else:
            if enemy[0] > -235:
                enemy[0] -= enemy_speed
            else:
                enemy[2] = 1
        if enemy[1] < -100:
            enemy[1] = random.randint(HEIGHT, HEIGHT + 500)
    return enemy_list

def update_objects(cloud_list, play_y, enemy_list):
    lowest_cloud = 0
    update_speed = 20  # Increased speed
    if play_y > 200:
        play_y -= update_speed
        for enemy in enemy_list:
            enemy[1] -= update_speed
        for cloud in cloud_list:
            cloud[1] -= update_speed
            if cloud[1] > lowest_cloud:
                lowest_cloud = cloud[1]
        if lowest_cloud < 750:
            num_clouds = random.randint(1, 2)
            if num_clouds == 1:
                x_pos = random.randint(0, WIDTH - 70)
                y_pos = random.randint(HEIGHT + 100, HEIGHT + 300)
                cloud_type = random.randint(1, 3)
                cloud_list.append([x_pos, y_pos, cloud_type])
            else:
                x_pos = random.randint(0, WIDTH // 2 - 70)
                y_pos = random.randint(HEIGHT + 100, HEIGHT + 300)
                cloud_type = random.randint(1, 3)
                x_pos2 = random.randint(WIDTH // 2 + 70, WIDTH - 70)
                y_pos2 = random.randint(HEIGHT + 100, HEIGHT + 300)
                cloud_type2 = random.randint(1, 3)
                cloud_list.extend([[x_pos, y_pos, cloud_type], [x_pos2, y_pos2, cloud_type2]])
    return play_y, cloud_list, enemy_list

# Main game loop
run = True
while run:
    # Hand detection
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img)
    if len(lmList) != 0:
        hand_x = lmList[9][1]  # Using landmark 9 (index finger tip) for horizontal movement
        player_x = int(hand_x * WIDTH / cap.get(3))  # Scaling hand_x to game width

    # Display the webcam feed
    cv2.imshow("Hand Tracker", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    screen.fill(bg)
    timer = pygame.time.Clock()
    timer.tick(FPS)

    cloud_platforms = draw_clouds(clouds, cloud_images)
    player = draw_player(player_x, player_y, penguin, direction)
    enemy_boxes = draw_enemies(enemies, shark)
    enemies = move_enemies(enemies, score)
    player_y, clouds, enemies = update_objects(clouds, player_y, enemies)

    if game_over:
        end_text = huge_font.render('Penguins Can\'t Fly!', True, 'black')
        end_text2 = font.render('Game Over: Press Enter to Restart', True, 'black')
        screen.blit(end_text, (70, 20))
        screen.blit(end_text2, (60, 80))
        player_y = -300
        y_speed = 0

    for platform in cloud_platforms:
        if direction == -1 and player.colliderect(platform):
            y_speed *= -0.5
            if y_speed > -2:
                y_speed = -2
            bounce.play()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and game_over:
                game_over = False
                player_x = 240
                player_y = 40
                direction = -1
                y_speed = 0
                score = 0
                total_distance = 0
                enemies = [[-234, random.randint(400, HEIGHT - 100), 1]]
                clouds = [[200, 100, 1], [50, 330, 2], [350, 330, 3], [200, 670, 1]]
                pygame.mixer.music.play()

    if y_speed < 10 and not game_over:
        y_speed += gravity
    player_y += y_speed
    if y_speed < 0:
        direction = 1
    else:
        direction = -1
    if player_x > WIDTH:
        player_x = -30
    elif player_x < -50:
        player_x = WIDTH - 20

    for enemy_box in enemy_boxes:
        if player.colliderect(enemy_box) and not game_over:
            end_sound.play()
            game_over = True
            if score > first_high:
                with open('high_scores.txt', 'w') as file:
                    file.write(str(score))
                first_high = score

    total_distance += y_speed
    score = round(total_distance / 100)
    score_text = font.render(f'Score: {score}', True, 'black')
    screen.blit(score_text, (10, HEIGHT - 70))
    if score > high_score:
        high_score = score
    score_text2 = font.render(f'High Score: {high_score}', True, 'black')
    screen.blit(score_text2, (10, HEIGHT - 40))

    pygame.display.flip()

pygame.quit()
cap.release()
cv2.destroyAllWindows()
