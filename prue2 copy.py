"""
PROJECT: HUMANUM EST - MASTER BUILD
Arquitectura: Orientada a Objetos, Patrón de Estados, Renderizado Multicapa.
Estética: Alto contraste, polígonos irregulares, tipografía agresiva (Inspiración P5).
"""

import pygame
import random
import math
import sys
import os

# ==============================================================================
# CONFIGURACIÓN GLOBAL Y CONSTANTES
# ==============================================================================
WIDTH, HEIGHT = 900, 650
FPS = 60

# --- PALETA DE COLORES (Alto Contraste) ---
P5_RED = (211, 47, 47)
P5_BLACK = (12, 12, 12)
P5_WHITE = (245, 245, 245)
P5_GRAY_D = (35, 35, 35)
P5_GRAY_L = (170, 170, 170)
P5_CYAN = (0, 220, 255)
P5_YELLOW = (255, 215, 0)
P5_GREEN = (0, 200, 100)

# --- ESTADOS DEL JUEGO ---
ST_BOOT = 0
ST_MENU = 1
ST_PLAY = 2
ST_DIALOGUE = 3
ST_TRANSITION = 4
ST_CLIMAX = 5
ST_ENDING = 6

# ==============================================================================
# MOTOR MATEMÁTICO Y DE COLOR
# ==============================================================================
class MathUtils:
    @staticmethod
    def lerp(a, b, t):
        """Interpolación lineal para movimientos suaves."""
        return a + (b - a) * t

    @staticmethod
    def apply_saturation(color, sat):
        """Convierte un color RGB hacia escala de grises basado en el factor sat."""
        sat = max(0.0, min(1.0, sat))
        r, g, b = color
        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
        return (
            int(r * sat + gray * (1 - sat)),
            int(g * sat + gray * (1 - sat)),
            int(b * sat + gray * (1 - sat))
        )

    @staticmethod
    def irregular_rect(rect_tuple, variance=3):
        """Genera puntos para un polígono estilo 'papel rasgado'."""
        x, y, w, h = rect_tuple
        return [
            (x + random.randint(-variance, variance), y + random.randint(-variance, variance)),
            (x + w + random.randint(-variance, variance), y + random.randint(-variance, variance)),
            (x + w + random.randint(-variance, variance), y + h + random.randint(-variance, variance)),
            (x + random.randint(-variance, variance), y + h + random.randint(-variance, variance))
        ]

# ==============================================================================
# GESTOR DE RECURSOS (FUENTES Y SUPERFICIES)
# ==============================================================================
class ResourceManager:
    def __init__(self):
        pygame.font.init()
        self.fonts = {
            'tiny': pygame.font.SysFont("Impact", 16),
            'sm': pygame.font.SysFont("Impact", 24),
            'md': pygame.font.SysFont("Impact", 40),
            'lg': pygame.font.SysFont("Impact", 85),
            'glitch': pygame.font.SysFont("Courier New", 20, bold=True)
        }
        self.surfaces = {}
        self.generate_vignette()

    def generate_vignette(self):
        """Genera una viñeta radial para oscurecer los bordes."""
        vig = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(HEIGHT):
            for x in range(WIDTH):
                dist = math.hypot(x - WIDTH//2, y - HEIGHT//2)
                alpha = min(255, max(0, int((dist - 200) * 0.6)))
                vig.set_at((x, y), (0, 0, 0, alpha))
        self.surfaces['vignette'] = vig

# ==============================================================================
# SISTEMA DE EFECTOS VISUALES (VFX)
# ==============================================================================
class VFXManager:
    def __init__(self):
        self.particles = []
        self.glitches = []
        self.scanlines = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.generate_scanlines()

    def generate_scanlines(self):
        """Simula el efecto de monitor CRT."""
        for i in range(0, HEIGHT, 3):
            pygame.draw.line(self.scanlines, (0, 0, 0, 40), (0, i), (WIDTH, i))

    def spawn_particles(self, x, y, color, type_str, count):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, type_str))

    def spawn_glitch(self, font, severity):
        """Los mensajes de glitch integran las ambiciones como fallos del sistema."""
        texts = [
            "ERROR: EMPATÍA DETECTADA", 
            "PROMEDIO EN DESCENSO", 
            "FALLA EN PROTOCOLO ", 
            "ALERTA: PROYECTOS RETRASADOS",
            "DISTRACCIÓN CRÍTICA",
            "RUIDO", 
            "FRACASO INMINENTE"
        ]
        text = random.choice(texts)
        self.glitches.append(GlitchText(text, font, severity))

    def update(self):
        for p in self.particles[:]:
            p.update()
            if p.life <= 0: self.particles.remove(p)
        for g in self.glitches[:]:
            g.update()
            if g.life <= 0: self.glitches.remove(g)

    def draw(self, surf, sat):
        for p in self.particles:
            p.draw(surf, sat)
        for g in self.glitches:
            g.draw(surf)

    def draw_post_processing(self, surf, stress_level, sat, vignette):
        """Aplica scanlines y aberración cromática si el estrés es alto."""
        surf.blit(self.scanlines, (0, 0))
        if sat < 1.0:
            surf.blit(vignette, (0, 0))

        # Aberración Cromática Simulada
        if stress_level > 60:
            offset = int((stress_level - 60) * 0.1)
            temp = surf.copy()
            temp.set_alpha(100)
            surf.blit(temp, (offset, 0))
            surf.blit(temp, (-offset, 0))

class Particle:
    def __init__(self, x, y, color, p_type):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.life = random.randint(150, 255)
        self.color = color
        self.type = p_type
        self.size = random.uniform(2, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.type == "CONFETTI":
            self.vy += 0.2
            self.vx *= 0.95
        elif self.type == "SPARK":
            self.vy -= 0.1
            self.size *= 0.98
        elif self.type == "FOG":
            self.vx *= 0.9
            self.vy *= 0.9
            self.size += 0.2
        self.life -= 3

    def draw(self, surf, sat):
        if self.life <= 0: return
        c = MathUtils.apply_saturation(self.color, sat)
        alpha = max(0, int(self.life))
        
        if self.type == "FOG":
            s = pygame.Surface((int(self.size*4), int(self.size*4)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*c, alpha//3), (int(self.size*2), int(self.size*2)), int(self.size*2))
            surf.blit(s, (self.x - self.size*2, self.y - self.size*2))
        else:
            s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*c, alpha), (int(self.size), int(self.size)), int(self.size))
            surf.blit(s, (self.x - self.size, self.y - self.size))

class GlitchText:
    def __init__(self, text, font, severity):
        self.text = text
        self.font = font
        self.x = random.randint(20, WIDTH - 300)
        self.y = random.randint(20, HEIGHT - 50)
        self.life = 60 + severity * 2
        self.max_life = self.life
        self.color = P5_RED if random.random() > 0.3 else P5_WHITE

    def update(self):
        self.life -= 1
        if random.random() < 0.1:
            self.x += random.randint(-10, 10)
            self.y += random.randint(-5, 5)

    def draw(self, surf):
        alpha = int((self.life / self.max_life) * 255)
        txt_surf = self.font.render(self.text, True, self.color)
        txt_surf.set_alpha(alpha)
        # Efecto de duplicado glitch
        surf.blit(txt_surf, (self.x, self.y))
        if random.random() < 0.3:
            surf.blit(txt_surf, (self.x + random.randint(-5, 5), self.y))

# ==============================================================================
# ENTIDADES DEL MUNDO
# ==============================================================================
class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.shake = 0.0

    def apply_shake(self, amount):
        self.shake = min(self.shake + amount, 30.0)

    def update(self):
        if self.shake > 0:
            self.shake *= 0.9
            if self.shake < 0.5: self.shake = 0

    def get_offset(self):
        ox = random.uniform(-self.shake, self.shake)
        oy = random.uniform(-self.shake, self.shake)
        return ox, oy

class Player:
    def __init__(self):
        self.x = float(WIDTH // 2)
        self.y = float(HEIGHT // 2)
        self.speed_base = 6.0
        self.radius = 18

    def update(self, human_pts, limits=None):
        keys = pygame.key.get_pressed()
        # La humanidad física pesa. A más puntos humanos, más lento es el movimiento.
        current_speed = max(1.5, self.speed_base - (human_pts * 1.2))
        
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * current_speed
        dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * current_speed
        
        self.x += dx
        self.y += dy

        if limits:
            cx, cy, r = limits
            dist = math.hypot(self.x - cx, self.y - cy)
            if dist > r:
                # Si sale del límite, lo devolvemos (Castillo infinito)
                self.x = cx
                self.y = cy
                return True # Retorna True si cruzó el límite
        return False

    def draw(self, surf, sat, cx, cy):
        color = MathUtils.apply_saturation(P5_RED, sat)
        # Dibujamos al jugador como un diamante
        pts = [
            (self.x + cx, self.y - self.radius + cy),
            (self.x + self.radius + cx, self.y + cy),
            (self.x + cx, self.y + self.radius + cy),
            (self.x - self.radius + cx, self.y + cy)
        ]
        pygame.draw.polygon(surf, color, pts)
        pygame.draw.polygon(surf, P5_WHITE, pts, 2)

class EnvironmentObject:
    def __init__(self, x, y, obj_type):
        self.x, self.y = x, y
        self.type = obj_type
        self.scale = random.uniform(0.8, 1.2)

    def draw(self, surf, px, py, zoom, gx, gy, sat):
        # Lógica de renderizado espejado
        bx = WIDTH - self.x if gx % 2 != 0 else self.x
        by = HEIGHT - self.y if gy % 2 != 0 else self.y
        fx, fy = bx + gx * WIDTH, by + gy * HEIGHT
        rx, ry = (fx - px) * zoom + WIDTH // 2, (fy - py) * zoom + HEIGHT // 2
        
        sz = self.scale * zoom
        color = MathUtils.apply_saturation(P5_GRAY_D, sat)
        
        if self.type == 'LOCKER':
            pygame.draw.rect(surf, color, (rx, ry, 45*sz, 110*sz))
            pygame.draw.rect(surf, MathUtils.apply_saturation(P5_GRAY_L, sat), (rx, ry, 45*sz, 110*sz), 2)
        elif self.type == 'TREE':
            pygame.draw.circle(surf, color, (int(rx), int(ry)), int(40*sz))
            pygame.draw.line(surf, color, (rx, ry), (rx, ry + 80*sz), 4)
        elif self.type == 'TABLE':
            pygame.draw.rect(surf, color, (rx-30*sz, ry, 60*sz, 40*sz))
        elif self.type == 'CHAIR':
            pygame.draw.rect(surf, color, (rx, ry, 25*sz, 25*sz), 2)

class InteractionNode:
    def __init__(self, act_id):
        self.act = act_id
        self.interacted = False
        self.pulse = 0.0
        
        # Base de datos narrativa de los actos
        # 1: Pasillo, 2: Áreas Verdes, 3: Comedor (Nuevo), 4: Auditorio
        db = {
            1: ("Estudiante (Ataque Pánico)", "Carrito Limpieza", P5_CYAN, (250, 250)),
            2: ("Pareja (Discusión)", "Valla Excelencia", P5_YELLOW, (650, 150)),
            3: ("Grupo (Humillado)", "Panel de Anuncios", P5_GREEN, (700, 450)),
            4: ("Amigo (Colapsado)", "Podio Pesado", (100, 255, 100), (450, 500))
        }
        
        if act_id in db:
            self.npc_name, self.obj_name, self.npc_color, (self.x, self.y) = db[act_id]
        else:
            self.npc_name, self.obj_name, self.npc_color, (self.x, self.y) = ("", "", P5_WHITE, (0,0))

    def update(self):
        self.pulse += 0.05

    def draw(self, surf, px, py, zoom, gx, gy, sat, fonts):
        if self.act > 4: return # No hay nodos interactivos estándar en el clímax
        
        bx = WIDTH - self.x if gx % 2 != 0 else self.x
        by = HEIGHT - self.y if gy % 2 != 0 else self.y
        fx, fy = bx + gx * WIDTH, by + gy * HEIGHT
        rx, ry = (fx - px) * zoom + WIDTH // 2, (fy - py) * zoom + HEIGHT // 2
        
        # Dibujar NPC
        n_col = MathUtils.apply_saturation(self.npc_color, sat)
        float_y = math.sin(self.pulse) * 12
        pygame.draw.circle(surf, n_col, (int(rx), int(ry + float_y)), int(25 * zoom))
        
        # Dibujar Objeto Gris
        if not self.interacted:
            glow = (math.sin(self.pulse * 0.5) + 1) / 2
            o_col = MathUtils.apply_saturation(P5_WHITE, sat)
            
            s = pygame.Surface((120*zoom, 160*zoom), pygame.SRCALPHA)
            pygame.draw.rect(s, (*o_col, int(150 * glow)), (0, 0, 90*zoom, 140*zoom), border_radius=10)
            surf.blit(s, (rx + 60*zoom, ry - 80*zoom))
            
            # Etiquetas UI Dinámicas
            surf.blit(fonts['sm'].render(f"[Q] OCULTAR", True, o_col), (rx + 60*zoom, ry - 110*zoom))
            surf.blit(fonts['sm'].render(f"[E] AYUDAR", True, n_col), (rx - 140*zoom, ry - 110*zoom))

# ==============================================================================
# SISTEMAS DE INTERFAZ (GUI)
# ==============================================================================
class HUD:
    def __init__(self, fonts):
        self.fonts = fonts

    def draw(self, surf, game_state):
        sat = game_state.saturation
        stress = game_state.stress
        satisfaction = game_state.satisfaction
        is_bad = game_state.grey_pts > game_state.human_pts

        # Contenedor de Estrés
        c_red = MathUtils.apply_saturation(P5_RED, sat)
        stress_rect = (20, 20, 280, 40)
        pts = MathUtils.irregular_rect(stress_rect, 0)
        pygame.draw.polygon(surf, P5_BLACK, pts)
        pygame.draw.polygon(surf, c_red, pts, 3)
        
        # Barra interna de estrés
        bar_w = min(270, max(0, stress * 2.7))
        pygame.draw.rect(surf, c_red, (25, 25, bar_w, 30))
        surf.blit(self.fonts['sm'].render("RUIDO MENTAL", True, P5_WHITE), (30, 70))

        # Contenedor de Satisfacción
        sat_col = MathUtils.apply_saturation(P5_GRAY_L if is_bad else P5_CYAN, sat)
        sat_rect = (WIDTH - 320, 20, 300, 25)
        pts2 = MathUtils.irregular_rect(sat_rect, 0)
        pygame.draw.polygon(surf, P5_BLACK, pts2)
        pygame.draw.polygon(surf, sat_col, pts2, 2)
        
        bar_sat_w = min(290, max(0, satisfaction * 2.9))
        pygame.draw.rect(surf, sat_col, (WIDTH - 315, 22, bar_sat_w, 20))
        label = "SATISFACCIÓN ARTIFICIAL" if is_bad else "SATISFACCIÓN"
        surf.blit(self.fonts['tiny'].render(label, True, P5_WHITE), (WIDTH - 315, 55))

        # Indicador de Acto
        if game_state.act <= 4:
            txt = self.fonts['md'].render(f"ACTO 0{game_state.act}", True, c_red)
            surf.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 20))

class DialogueBox:
    def __init__(self, fonts):
        self.fonts = fonts
        self.active = False
        self.lines = []
        self.warning = ""
        self.timer = 0
        self.char_index = 0
        self.current_line = 0

    def start(self, lines, warning=""):
        self.lines = lines
        self.warning = warning
        self.active = True
        self.current_line = 0
        self.char_index = 0
        self.timer = 240 # Tiempo en frames que dura el diálogo

    def update(self):
        if not self.active: return
        self.timer -= 1
        if self.timer <= 0:
            self.active = False
        if self.char_index < len(self.lines[self.current_line]):
            self.char_index += 1
        elif self.current_line < len(self.lines) - 1 and self.timer % 60 == 0:
            # Avanza de línea automáticamente
            self.current_line += 1
            self.char_index = 0

    def draw(self, surf, sat):
        if not self.active: return
        
        # Fondo oscuro
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))
        
        # Caja Principal (Estilo Persona)
        box_rect = (40, HEIGHT - 200, WIDTH - 80, 160)
        pts = MathUtils.irregular_rect(box_rect, 5)
        border_c = MathUtils.apply_saturation(P5_RED, sat)
        
        pygame.draw.polygon(surf, P5_BLACK, pts)
        pygame.draw.polygon(surf, border_c, pts, 4)
        
        # Render de Texto Typewriter
        display_text = self.lines[self.current_line][:int(self.char_index)]
        txt_surf = self.fonts['md'].render(display_text, True, P5_WHITE)
        surf.blit(txt_surf, (70, HEIGHT - 170))
        
        # Líneas anteriores estáticas
        for i in range(self.current_line):
            old_surf = self.fonts['sm'].render(self.lines[i], True, MathUtils.apply_saturation(P5_GRAY_L, sat))
            surf.blit(old_surf, (70, HEIGHT - 170 - (self.current_line - i)*35))

        # Advertencia del Sistema
        if self.warning:
            w_col = P5_RED if "ADVERTENCIA" in self.warning else P5_GRAY_L
            w_surf = self.fonts['sm'].render(self.warning, True, w_col)
            surf.blit(w_surf, (70, HEIGHT - 60))

# ==============================================================================
# GESTOR DEL MUNDO Y ESCENARIO
# ==============================================================================
class SceneManager:
    def __init__(self):
        self.decor = []
        
    def build_scene(self, act):
        self.decor.clear()
        types = {
            1: ['LOCKER', 'LOCKER', 'CHAIR'], 
            2: ['TREE', 'TREE', 'TREE'], 
            3: ['TABLE', 'TABLE', 'CHAIR'], 
            4: ['CHAIR', 'LOCKER', 'TABLE']
        }
        
        if act > 4: return # Acto 5 es especial
        
        choices = types.get(act, ['LOCKER'])
        for _ in range(35): # Población densa para el efecto infinito
            t = random.choice(choices)
            x, y = random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50)
            self.decor.append(EnvironmentObject(x, y, t))

    def draw(self, surf, px, py, sat):
        # Lógica de cálculo de Zoom según distancia al centro (Regla de 10 pasos)
        dist = math.hypot(px - WIDTH//2, py - HEIGHT//2)
        zoom = max(0.5, 1.0 - (dist / 400.0) * 0.4)
        
        # Efecto Castillo Infinito (Dibujar cuadrícula 3x3)
        for gx in range(-1, 2):
            for gy in range(-1, 2):
                for d in self.decor:
                    d.draw(surf, px, py, zoom, gx, gy, sat)
        return zoom

# ==============================================================================
# MOTOR PRINCIPAL Y MÁQUINA DE ESTADOS
# ==============================================================================
class GameEngine:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("PROJECT: HUMANUM EST - OMNISCIENT BUILD")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Sistemas Centrales
        self.res = ResourceManager()
        self.vfx = VFXManager()
        self.cam = Camera()
        self.scene = SceneManager()
        self.hud = HUD(self.res.fonts)
        self.dialogue = DialogueBox(self.res.fonts)
        self.player = Player()
        
        # Variables de Estado Global
        self.current_state = ST_BOOT
        self.act = 1
        self.saturation = 1.0
        self.stress = 20.0
        self.satisfaction = 0.0
        self.human_pts = 0
        self.grey_pts = 0
        
        self.node = InteractionNode(1)
        self.state_timer = 0
        
        # Inicio
        self.scene.build_scene(self.act)

    def change_state(self, new_state):
        self.current_state = new_state
        self.state_timer = 0

    def trigger_climax(self):
        self.change_state(ST_CLIMAX)
        self.vfx.particles.clear()
        self.vfx.glitches.clear()
        self.player.x, self.player.y = WIDTH//2, HEIGHT - 100
        
        if self.human_pts > self.grey_pts:
            self.dialogue.start(
                ["El examen final está frente a ti.", "Pero el Sistema rechaza tu presencia.", "Tus errores pasados han corrompido el entorno."],
                "FRACASO INMINENTE."
            )
        else:
            self.dialogue.start(
                ["El examen final está frente a ti.", "El camino es perfecto.", "El silencio es absoluto."],
                "ÉXITO ASEGURADO."
            )

    def handle_interaction(self, choice):
        self.node.interacted = True
        self.cam.apply_shake(20)
        
        if choice == "GREY":
            self.grey_pts += 1
            self.saturation -= 0.25 # En 4 actos, llega a 0
            self.stress -= 15
            self.satisfaction += 25
            self.vfx.spawn_particles(WIDTH//2, HEIGHT//2, P5_GRAY_L, "CONFETTI", 80)
            
            msgs = {
                1: "Has ocultado el pánico. El pasillo está limpio.",
                2: "La valla oculta la discusión. La excelencia brilla.",
                3: "Has ignorado la humillación. Tu comida no se enfría.",
                4: "Has tapado a tu amigo. El auditorio está impecable."
            }
            self.dialogue.start([msgs[self.act]], "SATISFACCIÓN ARTIFICIAL AUMENTADA.")
            
        elif choice == "HUMAN":
            self.human_pts += 1
            self.stress += 25
            self.vfx.spawn_particles(WIDTH//2, HEIGHT//2, P5_CYAN, "SPARK", 80)
            self.vfx.spawn_glitch(self.res.fonts['glitch'], self.human_pts)
            
            msgs = {
                1: "Ayudaste al chico. El Sistema ha registrado el retraso.",
                2: "Abrazaste a la pareja. El Sistema penaliza la distracción.",
                3: "Te sentaste con los humillados. El profesor te ha marcado.",
                4: "Te quedaste con tu amigo colapsado. Has perdido el examen."
            }
            self.dialogue.start([msgs[self.act], "¿De verdad valió la pena?"], "ADVERTENCIA: PROMEDIO EN RIESGO CRÍTICO.")

    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if self.current_state == ST_BOOT:
                if event.type == pygame.KEYDOWN: self.change_state(ST_MENU)
                
            elif self.current_state == ST_MENU:
                if event.type == pygame.KEYDOWN: 
                    self.change_state(ST_TRANSITION)
                    
            elif self.current_state == ST_PLAY:
                if not self.dialogue.active and not self.node.interacted:
                    dist = math.hypot(self.player.x - self.node.x, self.player.y - self.node.y)
                    if dist < 160:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_q: self.handle_interaction("GREY")
                            if event.key == pygame.K_e: self.handle_interaction("HUMAN")

    def update_logic(self):
        self.cam.update()
        self.vfx.update()
        self.dialogue.update()
        self.state_timer += 1
        
        if self.current_state == ST_TRANSITION:
            if self.state_timer > 60:
                self.change_state(ST_PLAY)
                
        elif self.current_state == ST_PLAY:
            self.node.update()
            if not self.dialogue.active:
                # Actualizar movimiento jugador
                loop_trigger = self.player.update(self.human_pts, limits=(WIDTH//2, HEIGHT//2, 400))
                
                if loop_trigger:
                    self.cam.apply_shake(10)
                    if self.human_pts > 0:
                        self.vfx.spawn_glitch(self.res.fonts['glitch'], self.human_pts)
                
                if self.node.interacted:
                    self.act += 1
                    if self.act > 4:
                        self.trigger_climax()
                    else:
                        self.scene.build_scene(self.act)
                        self.node = InteractionNode(self.act)
                        self.change_state(ST_TRANSITION)
                        self.player.x, self.player.y = WIDTH//2, HEIGHT//2

            # Generación aleatoria de ruido si eres humano
            if self.human_pts > 0 and random.random() < 0.02 * self.human_pts:
                self.vfx.spawn_glitch(self.res.fonts['glitch'], 1)

        elif self.current_state == ST_CLIMAX:
            # En el clímax, hay que caminar hacia arriba
            if not self.dialogue.active:
                self.player.update(self.human_pts)
                
                # Si eres humano, el juego intenta detenerte físicamente
                if self.human_pts > self.grey_pts:
                    if random.random() < 0.1:
                        self.player.y += random.randint(5, 20) # Te empuja hacia atrás
                        self.cam.apply_shake(5)
                        self.vfx.spawn_glitch(self.res.fonts['glitch'], 5)
                        
                # Condición de victoria/final
                if self.player.y < 100:
                    self.change_state(ST_ENDING)

    def draw_boot_menu(self):
        self.screen.fill(P5_BLACK)
        if self.state_timer % 60 < 30:
            txt = self.res.fonts['sm'].render("PRESIONA CUALQUIER TECLA", True, P5_RED)
            self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))

    def draw_main_menu(self):
        self.screen.fill(P5_RED)
        
        # Elementos dinámicos de fondo
        for i in range(5):
            off = math.sin(self.state_timer * 0.05 + i) * 50
            pts = [(0, i*130 + off), (WIDTH, i*130 - off), (WIDTH, i*130+50), (0, i*130+50)]
            pygame.draw.polygon(self.screen, P5_BLACK, pts)
            
        t1 = self.res.fonts['lg'].render("HUMANUM EST", True, P5_WHITE)
        self.screen.blit(t1, (50, HEIGHT//2 - 100))
        t2 = self.res.fonts['md'].render("INICIAR SEMESTRE", True, P5_BLACK)
        self.screen.blit(t2, (50, HEIGHT//2 + 20))

    def draw_climax(self):
        self.screen.fill(MathUtils.apply_saturation(P5_BLACK, self.saturation))
        cx, cy = self.cam.get_offset()
        
        # Puerta Final
        pygame.draw.rect(self.screen, MathUtils.apply_saturation(P5_WHITE, self.saturation), (WIDTH//2 - 50 + cx, 50 + cy, 100, 150), 4)
        txt = self.res.fonts['sm'].render("SALÓN FINAL", True, MathUtils.apply_saturation(P5_WHITE, self.saturation))
        self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2 + cx, 20 + cy))
        
        # Si eres humano, aparecen siluetas de amigos alrededor de la puerta
        if self.human_pts > self.grey_pts:
            friends = [(WIDTH//2 - 150, 150), (WIDTH//2 + 150, 150), (WIDTH//2 - 100, 200), (WIDTH//2 + 100, 200)]
            for fx, fy in friends:
                pygame.draw.circle(self.screen, P5_CYAN, (int(fx + cx), int(fy + cy)), 25)
                self.screen.blit(self.res.fonts['tiny'].render("Gracias.", True, P5_CYAN), (fx - 20 + cx, fy - 40 + cy))

        self.player.draw(self.screen, self.saturation, cx, cy)
        self.vfx.draw(self.screen, self.saturation)
        self.vfx.draw_post_processing(self.screen, self.stress, self.saturation, self.res.surfaces['vignette'])
        self.hud.draw(self.screen, self)
        self.dialogue.draw(self.screen, self.saturation)

    def draw_ending(self):
        is_bad = self.grey_pts > self.human_pts
        bg_col = P5_BLACK if is_bad else P5_WHITE
        self.screen.fill(bg_col)
        
        if is_bad:
            t1 = self.res.fonts['lg'].render("SUMMA CUM LAUDE", True, P5_GRAY_L)
            t2 = self.res.fonts['md'].render("Éxito absoluto. Soledad eterna.", True, P5_GRAY_D)
            # Confeti gris cayendo infinitamente
            if self.state_timer % 5 == 0:
                self.vfx.spawn_particles(random.randint(0, WIDTH), 0, P5_GRAY_L, "CONFETTI", 1)
        else:
            t1 = self.res.fonts['lg'].render("HUMANUM EST", True, P5_RED)
            t2 = self.res.fonts['md'].render("Fracaso total. Has recuperado tu humanidad.", True, P5_BLACK)
            # Chispas subiendo
            if self.state_timer % 5 == 0:
                self.vfx.spawn_particles(random.randint(0, WIDTH), HEIGHT, P5_CYAN, "SPARK", 1)

        self.screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 80))
        self.screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 + 40))
        self.vfx.draw(self.screen, 1.0) # Dibujar partículas de final puro

    def render(self):
        if self.current_state == ST_BOOT:
            self.draw_boot_menu()
        elif self.current_state == ST_MENU:
            self.draw_main_menu()
        elif self.current_state in [ST_PLAY, ST_TRANSITION]:
            self.screen.fill(MathUtils.apply_saturation(P5_BLACK, self.saturation))
            cx, cy = self.cam.get_offset()
            
            # Dibujar Mundo
            zoom = self.scene.draw(self.screen, self.player.x, self.player.y, self.saturation)
            
            # Efecto de transición oscuro
            if self.current_state == ST_TRANSITION:
                alpha = max(0, 255 - (self.state_timer * 4))
                s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                s.fill((0,0,0, alpha))
                self.screen.blit(s, (0,0))
                
            self.node.draw(self.screen, self.player.x, self.player.y, zoom, 0, 0, self.saturation, self.res.fonts)
            self.player.draw(self.screen, self.saturation, cx, cy)
            
            # Capas superiores
            self.vfx.draw(self.screen, self.saturation)
            self.vfx.draw_post_processing(self.screen, self.stress, self.saturation, self.res.surfaces['vignette'])
            self.hud.draw(self.screen, self)
            self.dialogue.draw(self.screen, self.saturation)
            
        elif self.current_state == ST_CLIMAX:
            self.draw_climax()
        elif self.current_state == ST_ENDING:
            self.draw_ending()

        pygame.display.flip()

    def run(self):
        while self.running:
            self.process_input()
            self.update_logic()
            self.render()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

# ==============================================================================
# ENTRY POINT DEL SISTEMA
# ==============================================================================
if __name__ == "__main__":
    # Inicialización del entorno gráfico y ejecución del motor
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    game_instance = GameEngine()
    game_instance.run()