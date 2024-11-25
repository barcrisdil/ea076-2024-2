from machine import Pin, SoftI2C, ADC, PWM, UART
import neopixel
import time
from ssd1306 import SSD1306_I2C


# Configuração do UART (TX em GPIO16, RX em GPIO17)
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))


# Configuração dos LEDs RGB (cátodo comum) com PWM para controlar o brilho
led_vermelho = PWM(Pin(13))  # GPIO 13 - Vermelho
led_verde = PWM(Pin(11))     # GPIO 11 - Verde
led_azul = PWM(Pin(12))      # GPIO 12 - Azul


# Frequência PWM para controle de brilho
led_vermelho.freq(1000)
led_verde.freq(1000)
led_azul.freq(1000)


# Função para ajustar o brilho do LED (duty cycle)
def set_brilho(led, porcentagem):
    duty = int(65535 * (porcentagem / 100))  # PWM usa valores de 0 a 65535
    led.duty_u16(duty)


# Configuração do botão A no GPIO5
botao_a = Pin(5, Pin.IN, Pin.PULL_UP)


# Função para desligar todos os LEDs
def apagar_led():
    set_brilho(led_vermelho, 0)  # Desliga o LED vermelho
    set_brilho(led_verde, 0)     # Desliga o LED verde
    set_brilho(led_azul, 0)      # Desliga o LED azul


# Função para configurar o LED na cor azul (transmissor) com 10% de brilho
def led_azul_on():
    apagar_led()  # Garante que todos os LEDs sejam apagados antes
    set_brilho(led_azul, 10)  # Acende o LED azul com 10% de brilho


# Função para configurar o LED na cor verde (receptor) com 10% de brilho
def led_verde_on():
    apagar_led()  # Garante que todos os LEDs sejam apagados antes
    set_brilho(led_verde, 10)  # Acende o LED verde com 10% de brilho


# Função para lidar com a recepção de dados UART e atualizar a matriz color_memory
def receber_mensagem():
    if uart.any():  # Se há dados na UART
        led_verde_on()  # Acende o LED verde ao iniciar a recepção
        mensagem = uart.read().decode('utf-8').strip()  # Lê e decodifica a mensagem
        if mensagem.startswith("[") and mensagem.endswith("]"):
            lista_acoes = eval(mensagem)  # Converte a string para lista
            for acao in lista_acoes:
                x, y, r, g, b = acao
                if r == 0 and g == 0 and b == 0:  # Se for apagar o LED
                    canvas[y][x] = 0  # Apaga no canvas
                    color_memory[y][x] = (0, 0, 0)  # Atualiza a matriz de cor
                else:
                    canvas[y][x] = 1  # Desenha no canvas
                    color_memory[y][x] = (r, g, b)  # Atualiza a matriz de cor
            update_led_matrix()  # Atualiza a matriz de LEDs
        time.sleep(1)  # Pequena pausa para garantir que o LED fique ligado por um tempo
        apagar_led()  # Apaga o LED verde após terminar o recebimento


# Função para enviar mensagem via UART
def transmitir_mensagem(lista_acoes):
    uart.write(str(lista_acoes) + "\n")  # Envia a lista de ações como string
    led_azul_on()  # Acende o LED azul na placa transmissora
    print("Mensagem enviada:", lista_acoes)
    time.sleep(1)  # Pequena pausa para garantir que o LED fique ligado por um tempo
    apagar_led()  # Apaga o LED azul após a transmissão




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
botao_a = Pin(5, Pin.IN, Pin.PULL_UP)
botao_b = Pin(6, Pin.IN, Pin.PULL_UP)
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
                    # Corrigindo a inversão do eixo Y
                    np[LED_MATRIX[y][x]] = color_memory[global_y][global_x]


    # LED atual deve piscar
    current_led_x = brush_x % 5
    current_led_y = brush_y % 5
    # Corrigindo a inversão do eixo Y ao piscar o LED
    np[LED_MATRIX[current_led_y][current_led_x]] = limit_brightness(current_color)  # LED pisca com cor atual


    np.write()


# Função para atualizar a posição do pincel
def update_brush():
    global brush_x, brush_y


    x_val = joystick_x.read_u16() // 2048
    y_val = joystick_y.read_u16() // 2048


    # Atualiza as coordenadas do pincel com as direções corrigidas para o eixo Y
    if x_val > 20 and brush_x < canvas_width - 1:
        brush_x += 1
    elif x_val < 10 and brush_x > 0:
        brush_x -= 1


    # Inverter os comandos "para cima" e "para baixo"
    if y_val > 20 and brush_y > 0:
        brush_y -= 1
    elif y_val < 10 and brush_y < canvas_height - 1:
        brush_y += 1


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


# Lista de ações para ser enviada via UART
lista_acoes = []


# Contador de ações para transmissão após 10 pressionamentos
contador_acoes = 0


# Loop principal
while True:
    update_brush()
    select_color()


    # Verifica se o botão foi pressionado para transmitir
    if not botao_a.value():  # Se o botão A for pressionado
        modify_canvas('draw')
        lista_acoes.append((brush_x, brush_y, current_color[0], current_color[1], current_color[2]))
        contador_acoes += 1
        time.sleep(0.3)  # Debounce do botão


    elif not botao_b.value():  # Se o botão B for pressionado
        modify_canvas('erase')
        lista_acoes.append((brush_x, brush_y, 0, 0, 0))  # Ação de apagar com cor (0, 0, 0)
        contador_acoes += 1
        time.sleep(0.3)  # Debounce do botão


    if contador_acoes >= 10:  # Transmite após 10 ações
        transmitir_mensagem(lista_acoes)
        lista_acoes = []  # Reseta a lista de ações
        contador_acoes = 0


    draw_canvas()  # Atualiza o display OLED com o canvas atual e a moldura
    receber_mensagem()  # Verifica se há mensagem recebida para atualizar a matriz color_memory
    time.sleep(0.3)
