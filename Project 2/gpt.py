from machine import Pin, SoftI2C, ADC, PWM, UART
import neopixel
import time
import _thread  # Para lidar com interrupções
from ssd1306 import SSD1306_I2C

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
    oled.text(line3, (128 - len(line3) * 8) // 2, 50)  # Centraliza a terceira linha
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

# Botão para iniciar a transmissão
transmit_button = Pin(16, Pin.IN, Pin.PULL_UP)  # Usando GPIO16 como botão de transmissão

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

# Configuração da UART para comunicação
uart = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(17))  # Ajuste os pinos conforme necessário

# Variável para indicar se a placa é master ou slave
IS_MASTER = False  # Defina True para uma placa e False para outra

# Flags de controle
transmission_in_progress = False

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
    if x_val > 20 and brush_x < canvas_width - 1:
        brush_x += 1
    elif x_val < 10 and brush_x > 0:
        brush_x -= 1

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

# Função para serializar o canvas
def serialize_canvas():
    serialized = bytearray()
    for y in range(canvas_height):
        row = 0
        for x in range(canvas_width):
            row <<= 1
            if canvas[y][x]:
                row |= 1
            if x % 8 == 7:
                serialized.append(row)
                row = 0
        if canvas_width % 8 != 0:
            serialized.append(row)
    return serialized

# Função para desserializar o canvas
def deserialize_canvas(data):
    index = 0
    for y in range(canvas_height):
        for x in range(0, canvas_width, 8):
            byte = data[index]
            index += 1
            for i in range(8):
                if x + (7 - i) < canvas_width:
                    bit = (byte >> i) & 1
                    if bit:
                        canvas[y][x + (7 - i)] = 1
                    else:
                        canvas[y][x + (7 - i)] = 0

# Função para enviar o canvas
def send_canvas():
    global transmission_in_progress
    transmission_in_progress = True
    play_sound(0.1, 1500)  # Som para indicar início da transmissão

    # Serializar o canvas
    data = serialize_canvas()

    # Enviar tamanho do canvas
    uart.write('START\n')
    uart.write('{}\n'.format(len(data)))

    # Enviar dados
    uart.write(data)

    # Indicar fim da transmissão
    uart.write('END\n')

    play_sound(0.1, 1500)  # Som para indicar fim da transmissão
    transmission_in_progress = False

# Função para receber o canvas
def receive_canvas():
    global transmission_in_progress
    transmission_in_progress = True
    play_sound(0.1, 1000)  # Som para indicar início da recepção

    # Ler tamanho do canvas
    line = ''
    while not line.endswith('\n'):
        line += uart.read(1).decode()
    if line.strip() == 'START':
        line = ''
        while not line.endswith('\n'):
            line += uart.read(1).decode()
        data_length = int(line.strip())

        # Ler dados
        data = uart.read(data_length)

        # Ler 'END'
        line = ''
        while not line.endswith('\n'):
            line += uart.read(1).decode()
        if line.strip() == 'END':
            # Desserializar e mesclar canvas
            deserialize_canvas(data)
            draw_canvas()
            play_sound(0.1, 1000)  # Som para indicar fim da recepção
        else:
            print("Erro: 'END' não recebido.")
    else:
        print("Erro: 'START' não recebido.")

    transmission_in_progress = False

# Função para lidar com a interrupção do botão de transmissão
def transmit_button_pressed(pin):
    if not transmission_in_progress:
        if IS_MASTER:
            send_canvas()
        else:
            receive_canvas()

# Configurar interrupção no botão de transmissão
transmit_button.irq(trigger=Pin.IRQ_FALLING, handler=transmit_button_pressed)

# Loop principal
while True:
    if not transmission_in_progress:
        update_brush()
        select_color()
        
        # Verifica os botões para desenhar ou apagar
        if button_a.value() == 0:
            modify_canvas('draw')
        elif button_b.value() == 0:
            modify_canvas('erase')

        draw_canvas()  # Atualiza o display OLED com o canvas atual e a moldura
        time.sleep(0.1)
