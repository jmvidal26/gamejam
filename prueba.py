import pygame
import random
import math

# --- Configuración Inicial ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)
font_large = pygame.font.SysFont("Arial", 24, bold=True)

# Constantes globales
PLAYER_SPEED = 3
STEP_SIZE = 32
MAX_DISTANCE = 320

# --- Funciones de Utilidad ---
def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def scr_circle_rect(cx, cy, cr, rx, ry, rw, rh):
    close_x = clamp(cx, rx, rx + rw)
    close_y = clamp(cy, ry, ry + rh)
    dist_sq = (cx - close_x)**2 + (cy - close_y)**2
    return dist_sq < cr**2

# --- Clases de Objetos ---
class Wall:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.col = (60, 60, 70)

    def draw(self, surface, offset_x, offset_y):
        draw_rect = self.rect.move(-offset_x, -offset_y)
        pygame.draw.rect(surface, self.col, draw_rect)
        pygame.draw.rect(surface, (20, 20, 30), draw_rect, 1)

class Desk:
    def __init__(self, x, y):
        self.size = 36
        self.x, self.y = x, y
        self.is_assigned = False
        self.col_normal = (180, 140, 90)
        self.col_gold = (255, 215, 0)

    def draw(self, surface, offset_x, offset_y):
        h = self.size / 2
        c = self.col_gold if self.is_assigned else self.col_normal
        rect = pygame.Rect(self.x - h - offset_x, self.y - h - offset_y, self.size, self.size)
        pygame.draw.rect(surface, (0, 0, 0), rect.move(4, 4))
        pygame.draw.rect(surface, c, rect)
        if self.is_assigned:
            txt = font.render("★", True, (255, 255, 255))
            surface.blit(txt, (rect.centerx - 5, rect.centery - 10))

# --- Sistema de NPCs ---
class NPC:
    def __init__(self, x, y, color, name):
        self.x, self.y = x, y
        self.radius = 14
        self.color = color
        self.name = name
        self.is_talking = False

    def draw(self, surface, offset_x, offset_y):
        px, py = self.x - offset_x, self.y - offset_y
        pygame.draw.circle(surface, (0, 0, 0), (px + 3, py + 4), self.radius) # Sombra
        pygame.draw.circle(surface, self.color, (px, py), self.radius) # Cuerpo
        
        if self.is_talking:
            txt = font.render(f"Hola, soy {self.name}", True, (255, 255, 255))
            surface.blit(txt, (px - 40, py - 40))

class MovingNPC(NPC):
    def __init__(self, x, y):
        super().__init__(x, y, (255, 140, 0), "Naranja") # Color Naranja
        self.dir = random.uniform(0, 2 * math.pi)
        self.speed = 1.5
        self.change_timer = 0

    def update(self, walls):
        self.change_timer += 1
        if self.change_timer > 60:
            self.dir += random.uniform(-0.5, 0.5)
            self.change_timer = 0
        
        new_x = self.x + math.cos(self.dir) * self.speed
        new_y = self.y + math.sin(self.dir) * self.speed
        
        # Colisión simple con paredes para no salirse
        hit = False
        for w in walls:
            if scr_circle_rect(new_x, new_y, self.radius, w.rect.x, w.rect.y, w.rect.width, w.rect.height):
                hit = True
        
        if not hit:
            self.x, self.y = new_x, new_y
        else:
            self.dir += math.pi # Rebotar

class StaticNPC(NPC):
    def __init__(self, x, y):
        super().__init__(x, y, (240, 240, 240), "Blanco") # Color Blanco

class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius = 14
        self.col = (70, 130, 200)

    def update(self, walls, desks, mi_pupitre):
        keys = pygame.key.get_pressed()
        ix = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        iy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
        
        mag = math.sqrt(ix**2 + iy**2)
        vx = (ix / mag * PLAYER_SPEED) if mag != 0 else 0
        vy = (iy / mag * PLAYER_SPEED) if mag != 0 else 0

        self.x += vx
        for w in walls:
            if scr_circle_rect(self.x, self.y, self.radius, w.rect.x, w.rect.y, w.rect.width, w.rect.height):
                self.x -= vx
        for d in desks:
            if scr_circle_rect(self.x, self.y, self.radius, d.x-18, d.y-18, 36, 36):
                self.x -= vx

        self.y += vy
        for w in walls:
            if scr_circle_rect(self.x, self.y, self.radius, w.rect.x, w.rect.y, w.rect.width, w.rect.height):
                self.y -= vy
        for d in desks:
            if scr_circle_rect(self.x, self.y, self.radius, d.x-18, d.y-18, 36, 36):
                self.y -= vy

        dist = math.hypot(self.x - mi_pupitre.x, self.y - mi_pupitre.y)
        if dist / STEP_SIZE > 10:
            self.x, self.y = mi_pupitre.x + 50, mi_pupitre.y

    def draw(self, surface, offset_x, offset_y):
        px, py = self.x - offset_x, self.y - offset_y
        pygame.draw.circle(surface, (0, 0, 0), (px + 3, py + 4), self.radius)
        pygame.draw.circle(surface, self.col, (px, py), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (px - 3, py - 3), 4)
        pygame.draw.circle(surface, (0, 0, 0), (px - 3, py - 3), 2)

# --- Inicialización del Mundo ---
walls = [
    Wall(0, 0, WIDTH, 32), Wall(0, HEIGHT-32, WIDTH, 32),
    Wall(0, 32, 32, HEIGHT-64), Wall(WIDTH-32, 32, 32, HEIGHT-64)
]
desks = [Desk(150 + c*100, 150 + r*100) for r in range(3) for c in range(5)]
mi_pupitre = random.choice(desks)
mi_pupitre.is_assigned = True
player = Player(mi_pupitre.x + 50, mi_pupitre.y)

# Crear NPCs
npcs = []
for _ in range(4): npcs.append(MovingNPC(random.randint(100, 700), random.randint(100, 500)))
for _ in range(3): npcs.append(StaticNPC(random.randint(100, 700), random.randint(100, 500)))

# --- Loop Principal ---
running = True
interaction_text = ""

while running:
    screen.fill((30, 30, 35))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Interacción con ENTER
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                for n in npcs:
                    dist = math.hypot(player.x - n.x, player.y - n.y)
                    if dist < 50: # Distancia para hablar
                        n.is_talking = not n.is_talking

    # Lógica
    player.update(walls, desks, mi_pupitre)
    for n in npcs:
        if isinstance(n, MovingNPC):
            n.update(walls)
    
    dist_p = math.hypot(player.x - mi_pupitre.x, player.y - mi_pupitre.y)
    offset_x = player.x - WIDTH / 2
    offset_y = player.y - HEIGHT / 2

    # Dibujo
    for w in walls: w.draw(screen, offset_x, offset_y)
    for d in desks: d.draw(screen, offset_x, offset_y)
    for n in npcs: n.draw(screen, offset_x, offset_y)
    player.draw(screen, offset_x, offset_y)

    # --- HUD ---
    steps = int(dist_p // STEP_SIZE)
    left = max(0, 10 - steps)
    pygame.draw.rect(screen, (0, 0, 0), (10, 10, 260, 90))
    screen.blit(font.render(f"Pasos del pupitre: {steps}", True, (255, 255, 255)), (20, 20))
    screen.blit(font.render(f"Pasos restantes: {left}", True, (255, 255, 255)), (20, 45))
    
    pct = clamp(steps / 10, 0, 1)
    pygame.draw.rect(screen, (50, 50, 50), (20, 70, 240, 15))
    bar_col = (int(255 * pct), int(255 * (1 - pct)), 0)
    pygame.draw.rect(screen, bar_col, (20, 70, 240 * pct, 15))

    if steps >= 8:
        warn = font.render("¡REGRESA A TU PUPITRE!", True, (255, 0, 0))
        screen.blit(warn, (WIDTH//2 - 100, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()