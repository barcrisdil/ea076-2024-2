from machine import Pin, SoftI2C, ADC, PWM
import neopixel
import time
from ssd1306 import SSD1306_I2C
#Dificuldades
# Rodar preso no loop, ponto de exclamação e acento

# Configuração do OLED
i2c = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c)

# Configuração do buzzer (Buzzer A no GPIO21)
buzzer = PWM(Pin(21))

# Função para tocar o som
def play_sound(duration=0.5, frequency=1000):
    buzzer.freq(frequency)
    buzzer.duty_u16(32768)  # 50% duty cycle
    time.sleep(duration)
    buzzer.deinit()
    

# Mostrar mensagem de boas-vindas
def show_welcome_message():
    oled.fill(0)
    line1 = "BEM VINDO"
    line2 = "A NOVA ARTE"
    line3 = "MODERNA"
    
    oled.text(line1, (128 - len(line1) * 8) // 2, 20)  # Centraliza a primeira linha
    oled.text(line2, (128 - len(line2) * 8) // 2, 35)  # Centraliza a segunda linha
    oled.text(line3, (128 - len(line3) * 8) // 2, 50)  # Centraliza a segunda linha
    oled.show()
    time.sleep(2)
    
play_sound()
show_welcome_message()

# Configuração da Matriz de LEDs 5x5
NUM_LEDS = 25
np = neopixel.NeoPixel(Pin(7), NUM_LEDS)

# Definindo a matriz de LEDs (mapeamento dos LEDs na matriz 5x5)
LED_MATRIX = [
    [24, 23, 22, 21, 20],
    [15, 16, 17, 18, 19],
    [14, 13, 12, 11, 10],
    [5, 6, 7, 8, 9],
    [4, 3, 2, 1, 0]
]

# Configuração dos botões e joystick
button_a = Pin(5, Pin.IN, Pin.PULL_UP)
button_b = Pin(6, Pin.IN, Pin.PULL_UP)
joystick_x = ADC(Pin(27))
joystick_y = ADC(Pin(26))
joystick_button = Pin(22, Pin.IN, Pin.PULL_UP)

# Configuração inicial
canvas_width = 100
canvas_height = 50
brush_x = 0
brush_y = 0

# Inicializa o canvas (100x50 pixels) e a memória das cores
canvas = [[0] * canvas_width for _ in range(canvas_height)]
color_memory = [[(0, 0, 0)] * canvas_width for _ in range(canvas_height)]

# Função para limitar a luminosidade a 10%
def limit_brightness(color):
    return tuple(int(c * 0.1) for c in color)

# Cores limitadas em 10% de brilho
COLORS = [
    limit_brightness((255, 0, 0)),     # Vermelho
    limit_brightness((255, 165, 0)),   # Laranja
    limit_brightness((255, 255, 0)),   # Amarelo
    limit_brightness((0, 255, 0)),     # Verde
    limit_brightness((0, 0, 255)),     # Azul
    limit_brightness((75, 0, 130)),    # Índigo
    limit_brightness((238, 130, 238)), # Violeta
    limit_brightness((255, 255, 255))  # Branco
]

current_color_index = 0
current_color = COLORS[current_color_index]  # Cor inicial

# Função para desenhar o canvas no OLED com moldura
def draw_canvas():
    oled.fill(0)
    offset_x = 14  # Margem para centralizar horizontalmente (128-100)/2 = 14
    offset_y = 7   # Margem para centralizar verticalmente (64-50)/2 = 7

    # Desenhar a moldura
    oled.rect(offset_x - 1, offset_y - 1, canvas_width + 2, canvas_height + 2, 1)

    # Desenhar o canvas
    for y in range(canvas_height):
        for x in range(canvas_width):
            if canvas[y][x] == 1:
                oled.pixel(x + offset_x, y + offset_y, 1)
    oled.show()

# Função para atualizar a matriz de LEDs 5x5 com base no canvas e o LED do pincel piscando
def update_led_matrix():
    np.fill((0, 0, 0))  # Apaga os LEDs

    # Atualiza LEDs de acordo com o canvas
    for y in range(5):
        for x in range(5):
            global_x = brush_x // 5 * 5 + x
            global_y = brush_y // 5 * 5 + y
            if global_y < canvas_height and global_x < canvas_width:
                if canvas[global_y][global_x] == 1:
                    np[LED_MATRIX[4 - y][x]] = color_memory[global_y][global_x]

    # LED atual deve piscar
    current_led_x = brush_x % 5
    current_led_y = brush_y % 5
    np[LED_MATRIX[4 - current_led_y][current_led_x]] = limit_brightness(current_color)  # LED pisca com cor atual

    np.write()

# Função para atualizar a posição do pincel
def update_brush():
    global brush_x, brush_y
    
    x_val = joystick_x.read_u16() // 2048
    y_val = joystick_y.read_u16() // 2048
    
    # Atualiza as coordenadas do pincel
    if x_val > 20 and brush_x > 0:
        brush_x -= 1
    elif x_val < 10 and brush_x < canvas_width - 1:
        brush_x += 1

    if y_val > 20 and brush_y < canvas_height - 1:
        brush_y += 1
    elif y_val < 10 and brush_y > 0:
        brush_y -= 1

    # Atualiza a matriz de LEDs 5x5
    update_led_matrix()

# Função para desenhar ou apagar no canvas
def modify_canvas(action):
    if action == 'draw':
        canvas[brush_y][brush_x] = 1  # Desenha no canvas
        color_memory[brush_y][brush_x] = current_color  # Salva a cor do pixel no canvas
    elif action == 'erase':
        canvas[brush_y][brush_x] = 0  # Apaga do canvas

# Função para alternar a cor com o joystick
def select_color():
    global current_color_index, current_color
    if joystick_button.value() == 0:  # Verifica se o botão do joystick foi pressionado
        current_color_index = (current_color_index + 1) % len(COLORS)
        current_color = COLORS[current_color_index]
        time.sleep(0.2)  # Pequena pausa para evitar múltiplos registros da pressão do botão

# Loop principal
while True:
    update_brush()
    select_color()
    
    # Verifica os botões para desenhar ou apagar
    if button_a.value() == 0:
        modify_canvas('draw')
    elif button_b.value() == 0:
        modify_canvas('erase')

    draw_canvas()  # Atualiza o display OLED com o canvas atual e a moldura
    time.sleep(0.1)
