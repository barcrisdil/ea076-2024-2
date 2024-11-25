# A Nova Arte Moderna 3.0 

O projeto 3 consiste em uma nova versão dos anteriores em que após integrar a cooperação entre dois usuários pela comunicação UART, iremos criar um módulo em placa impressa para agregar de forma otimizada os seguintes features:

- Comunicação Bluetooth usando uma das UART disponíveis;
- Controle da intensidade por um potenciômetro em uma entrada ADC do Raspberry pi;
- Um botão para acionar o envio de mensagens e sincronização do canvas;
- Oled colorido de 1,8'' para melhorar a experiência visual do macro;

Além disso para dar suporte ao Oled será utilizado um mini-cavalete confeccionado em uma impressora 3D.

# Cavalete 3D

O cavalete foi obtido através do link: [Cavalete](https://www.thingiverse.com/thing:355110)

<img src="Minicavalete.jpg" width="50%" height="50%">

# Esquemático de conexões
Com as conexões necessárias identificadas, elaborou-se o seguite esquemático.

<img src="Esquemático.png" width="60%" height="00%">

# Layout das Trilhas
Em seguida, pensou-se nas trilhas a serem confeccionadas. Alguns ajustes de localização dos componentes foram realizados para otimizar a placa.

<img src="Layout_placa.png" width="50%" height="50%">

# 3D
Dessa forma, o 3D obtido no KiCAD encontra-se abaixo:

<img src="Layout_3D.png" width="50%" height="50%">

# Setup Final
Com os conectores devidamente soldados e os periféricos conectados, o projeto final apresenta-se abaixo:

<img src="Setup - EA076.jpeg" width="60%" height="60%">

* O projeto completo da placa se encontra no arquivo [ArquivoKicad_placa](https://github.com/barcrisdil/ea076-2024-2/blob/main/Project3/ArquivoKicad_placa)
# Resultados e Conclusão 

Como parte do projeto tivemos um erro de design na placa em que o potenciômetro não foi conectado a uma entrada ADC, impossibilitando sua leitura. No geral a limitação de usar as apenas as entradas disponíveis no conector IDC da Bitdoglab, gerou complexidade e inflexibilidade nas possibilidades de design. Em relação a UART que estava disponivel nos GPIO 8 e 9, ela não funcionou como esperado sem conclusão sobre seu mal funcionamento. Para o correto funcionamento desse projeto é necessário reajustar esses pontos de design como um todo da placa impressa e suas conexões com a Bitdoglab. 



