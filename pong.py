import pygame
import sys
import random
from groq import Groq
 
# --- CONFIGURAÇÃO IA (GROQ) ---
try:
    client = Groq(api_key="SUA_CHAVE_GROQ_AQUI")
except:
    client = None
 
# --- CONFIGURAÇÕES ---
WIDTH, HEIGHT = 800, 600
WHITE, BLACK, GREEN_NEON = (255, 255, 255), (0, 0, 0), (57, 255, 20)
FPS = 60
 
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PONG AI - 1980s ULTIMATE")
clock = pygame.time.Clock()
font_pixel = pygame.font.SysFont("Courier", 24, bold=True)
font_big = pygame.font.SysFont("Courier", 50, bold=True)
 
# --- VARIÁVEIS DE ESTADO ---
game_state = 0 # 0: Nome, 1: Dificuldade, 2: Jogando, 3: Game Over
current_difficulty = ""
winner_name = ""
player_name = ""
ia_comment = "SISTEMA OPERACIONAL ATIVO"
 
# --- ENTIDADES ---
ball = pygame.Rect(WIDTH//2 - 10, HEIGHT//2 - 10, 20, 20)
player = pygame.Rect(10, HEIGHT//2 - 50, 15, 100)
opponent = pygame.Rect(WIDTH - 25, HEIGHT//2 - 50, 15, 100)
 
ball_speed_x, ball_speed_y = 0, 0
player_speed = 0
opponent_ai_speed = 0
player_score, opponent_score = 0, 0
 
def reset_ball(direction):
    global ball_speed_x, ball_speed_y
    ball.center = (WIDTH//2, HEIGHT//2)
   
    # Velocidades baseadas na dificuldade
    if current_difficulty == "FACIL": b_speed = 5
    elif current_difficulty == "NORMAL": b_speed = 8
    else: b_speed = 11 # Dificil
   
    ball_speed_x = b_speed * direction
    ball_speed_y = b_speed * random.choice((1, -1))
 
def set_difficulty(level):
    global opponent_ai_speed, current_difficulty
    current_difficulty = level
    if level == "FACIL": opponent_ai_speed = 4
    elif level == "NORMAL": opponent_ai_speed = 7
    elif level == "DIFICIL": opponent_ai_speed = 10.5 # Mais rápida que o normal
 
def get_ia_comment(msg_type):
    if not client: return "SISTEMA OPERACIONAL EM LOOP"
    prompts = {
        "ponto": "O jogador marcou ponto. Diga algo curto e sarcástico dos anos 80.",
        "vitoria": "O jogador venceu a máquina. Reaja com fúria de computador antigo.",
        "derrota": "A máquina venceu. Zombe da lentidão humana."
    }
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompts[msg_type]}]
        )
        return response.choices[0].message.content.upper()
    except: return "ERRO NA MATRIX"
 
# --- LOOP PRINCIPAL ---
while True:
    screen.fill(BLACK) # Limpa a tela no início de cada frame
   
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
       
        # LÓGICA DE ENTRADA POR ESTADO
        if game_state == 0: # Nome
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name.strip() != "": game_state = 1
                elif event.key == pygame.K_BACKSPACE: player_name = player_name[:-1]
                else:
                    if len(player_name) < 10: player_name += event.unicode
 
        elif game_state == 1: # Dificuldade
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: set_difficulty("FACIL"); reset_ball(1); game_state = 2
                elif event.key == pygame.K_2: set_difficulty("NORMAL"); reset_ball(1); game_state = 2
                elif event.key == pygame.K_3: set_difficulty("DIFICIL"); reset_ball(1); game_state = 2
 
        elif game_state == 2: # Jogando
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: player_speed = -9
                if event.key == pygame.K_DOWN: player_speed = 9
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_UP, pygame.K_DOWN): player_speed = 0
       
        elif game_state == 3: # Game Over
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: # REVANCHE (Continua na mesma dificuldade)
                    player_score = 0
                    opponent_score = 0
                    set_difficulty(current_difficulty)
                    reset_ball(1)
                    game_state = 2
                if event.key == pygame.K_m: # MENU (Reseta tudo)
                    player_score = 0
                    opponent_score = 0
                    player_name = ""
                    game_state = 0
 
    # --- ATUALIZAÇÃO E DESENHO ---
    if game_state == 0: # Tela de Nome
        txt = font_pixel.render("PILOTO, IDENTIFIQUE-SE:", True, GREEN_NEON)
        name_txt = font_pixel.render(f"> {player_name}_", True, WHITE)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 250))
        screen.blit(name_txt, (WIDTH//2 - name_txt.get_width()//2, 300))
 
    elif game_state == 1: # Tela de Dificuldade
        txt = font_pixel.render("SELECIONE O NÍVEL DE COMBATE:", True, GREEN_NEON)
        opt = font_pixel.render("[1] FACIL | [2] NORMAL | [3] DIFICIL", True, WHITE)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 200))
        screen.blit(opt, (WIDTH//2 - opt.get_width()//2, 300))
 
    elif game_state == 2: # Jogo Ativo
        # Movimentação Jogador
        player.y += player_speed
        if player.top < 0: player.top = 0
        if player.bottom > HEIGHT: player.bottom = HEIGHT
 
        # Movimentação CPU (Melhorada)
        if current_difficulty == "DIFICIL":
            # No difícil, a CPU é mais precisa e reage mais rápido
            if opponent.centery < ball.y - 10: opponent.y += opponent_ai_speed
            elif opponent.centery > ball.y + 10: opponent.y -= opponent_ai_speed
        else:
            if opponent.centery < ball.y: opponent.y += opponent_ai_speed
            else: opponent.y -= opponent_ai_speed
 
        # Movimentação Bola
        ball.x += ball_speed_x
        ball.y += ball_speed_y
 
        # Colisões Paredes
        if ball.top <= 0 or ball.bottom >= HEIGHT: ball_speed_y *= -1
 
        # Colisões Raquetes
        if ball.colliderect(player) or ball.colliderect(opponent):
            ball_speed_x *= -1.05 # Aumenta velocidade gradualmente
            ball_speed_y *= 1.05
 
        # Pontuação
        if ball.left <= 0:
            opponent_score += 1
            if opponent_score >= 5:
                winner_name = "CPU"; game_state = 3; ia_comment = get_ia_comment("derrota")
            else:
                ia_comment = get_ia_comment("ponto"); reset_ball(1)
       
        if ball.right >= WIDTH:
            player_score += 1
            if player_score >= 5:
                winner_name = player_name; game_state = 3; ia_comment = get_ia_comment("vitoria")
            else:
                ia_comment = get_ia_comment("ponto"); reset_ball(-1)
 
        # Desenhar elementos do jogo
        pygame.draw.rect(screen, WHITE, player)
        pygame.draw.rect(screen, WHITE, opponent)
        pygame.draw.ellipse(screen, GREEN_NEON, ball)
        pygame.draw.aaline(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))
       
        screen.blit(font_pixel.render(f"{player_name}: {player_score}", True, WHITE), (50, 20))
        screen.blit(font_pixel.render(f"CPU: {opponent_score}", True, WHITE), (WIDTH - 200, 20))
        screen.blit(font_pixel.render(ia_comment[:60], True, GREEN_NEON), (20, HEIGHT - 40))
 
    elif game_state == 3: # Tela de Game Over
        res_txt = font_big.render(f"{winner_name} VENCEU!", True, GREEN_NEON)
        retry_txt = font_pixel.render("PRESSIONE [R] PARA REVANCHE", True, WHITE)
        menu_txt = font_pixel.render("PRESSIONE [M] PARA MENU PRINCIPAL", True, WHITE)
       
        screen.blit(res_txt, (WIDTH//2 - res_txt.get_width()//2, HEIGHT//2 - 100))
        screen.blit(retry_txt, (WIDTH//2 - retry_txt.get_width()//2, HEIGHT//2))
        screen.blit(menu_txt, (WIDTH//2 - menu_txt.get_width()//2, HEIGHT//2 + 50))
       
        # Comentário final da IA
        comment_surf = font_pixel.render(ia_comment[:60], True, GREEN_NEON)
        screen.blit(comment_surf, (WIDTH//2 - comment_surf.get_width()//2, HEIGHT - 60))
 
    pygame.display.flip()
    clock.tick(FPS)
 
 
