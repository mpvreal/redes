import sys
import locale

from select import select
from socket import *
from time import time_ns

# Formatação em pt_BR
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
# Tamanho da mensagem
SIZE = 500
# Mensagem
MESSAGE = b'teste de rede *2022*' * 25
# Tempo em segundos
TIME_SECONDS = 20

def error():
    print(f'Formato de utilização:\n\t{sys.argv[0]} <ip> <porta> \
<protocolo>\n\tPara iniciar listening, insira \"listen\" em <ip>')
    exit(1)

def download(speedtest):
    counter = 0

    ready = select([speedtest], [], [], 3)[0]
    while ready:
        if not speedtest.recv(SIZE):
            break
        counter += 1
        
        ready = select([speedtest], [], [], 3)[0]

    print(f'Pacotes recebidos: {counter}')

    return counter / TIME_SECONDS

def upload_tcp(speedtest):
    counter = 0

    start = time_ns()
    while time_ns() - start < TIME_SECONDS * 1000000000:
        speedtest.sendall(MESSAGE)
        counter += 1
    
    print(f'Pacotes enviados: {counter}')

    return counter / TIME_SECONDS

def upload_udp(speedtest, peer):
    counter = 0

    start = time_ns()
    while time_ns() - start < TIME_SECONDS * 1000000000:
        speedtest.sendto(MESSAGE, peer)
        counter += 1

    print(f'Pacotes enviados: {counter}')

    return counter / TIME_SECONDS

# Parâmetros corretos
if(len(sys.argv) < 3):
    error()

elif(sys.argv[3] == 'tcp'):
    speedtest = socket(AF_INET, SOCK_STREAM)
    speedtest.settimeout(5)

    if(sys.argv[1] == 'listen'):
        speedtest.bind((gethostbyname(gethostname()), 
            int(sys.argv[2])))
        
        try:
            speedtest.listen(1)
            print('Aguardando conexão...')
            speedtest, address = speedtest.accept()
        except:
            print(f'Erro: Tempo limite de conexão excedido.\nAbortando.')
            exit(1)

        print(f'Conexão aceita de {address[0]}:{address[1]}')

        print('Iniciando teste de download...')
        speed = download(speedtest)
        print('Download médio:')
        print(f'\t\t' + \
            locale.format_string('%.2f', speed, True) + ' pacotes/s')
        print(f'\t\t' + \
            locale.format_string('%.2f', speed * 500, True) + ' bits/s')

        speedtest.sendall(b'OK')
        
        print('Iniciando teste de upload...')
        speed = upload_tcp(speedtest)
        print('Upload médio:')
        print(f'\t\t' + \
            locale.format_string('%.2f', speed, True) + ' pacotes/s')
        print(f'\t\t' + \
            locale.format_string('%.2f', speed * 500, True) + ' bits/s')

    else:
        speedtest.connect((sys.argv[1], int(sys.argv[2])))
        print(f'Conectado a {sys.argv[1]}:{sys.argv[2]}')

        print('Iniciando teste de upload...')
        speed = upload_tcp(speedtest)
        print('Upload médio:')
        print(f'\t\t' + \
            locale.format_string('%.2f', speed, True) + ' pacotes/s')
        print(f'\t\t' + \
            locale.format_string('%.2f', speed * 500, True) + ' bits/s')

        try:
            speedtest.recv(2)
        except TimeoutError:
            print(f'Erro: Nenhum pacote recebido.\nAbortando...')
            exit(1)

        print('Iniciando teste de download...')
        speed = download(speedtest)
        print('Download médio:')
        print(f'\t\t' + \
            locale.format_string('%.2f', speed, True) + ' pacotes/s')
        print(f'\t\t' + \
            locale.format_string('%.2f', speed * 500, True) + ' bits/s')

elif(sys.argv[3] == 'udp'):
    speedtest = socket(AF_INET, SOCK_DGRAM)
    speedtest.settimeout(5)

    if(sys.argv[1] == 'listen'):
        speedtest.bind((gethostbyname(gethostname()), 
            int(sys.argv[2])))
        print(f'Aguardando em {gethostbyname(gethostname())}:{sys.argv[2]}...')   
        try:
            peer = speedtest.recvfrom(3)[1]
        except TimeoutError:
            print(f'Erro: Limite de tempo excedido.\nAbortando.')
            exit(1)
    
        print('Iniciando teste de download...')
        speed = download(speedtest)
        print('Download médio:')
        print(f'\t\t' + \
            locale.format_string('%.2f', speed, True) + ' pacotes/s')
        print(f'\t\t' + \
            locale.format_string('%.2f', speed * 500, True) + ' bits/s')

        speedtest.sendto(b'OK', peer)
        
        print('Iniciando teste de upload...')
        speed = upload_udp(speedtest, peer)
        print('Upload médio:')
        print(f'\t\t' + \
            locale.format_string('%.2f', speed, True) + ' pacotes/s')
        print(f'\t\t' + \
            locale.format_string('%.2f', speed * 500, True) + ' bits/s')
        
    else:
        speedtest.connect((sys.argv[1], int(sys.argv[2])))
        print(f'Conectado a {sys.argv[1]}:{sys.argv[2]}')
        speedtest.sendall(b'OK')

        print('Iniciando teste de upload...')
        speed = upload_udp(speedtest, (sys.argv[1], int(sys.argv[2])))
        print('Upload médio:')
        print(f'\t\t' + \
            locale.format_string('%.2f', speed, True) + ' pacotes/s')
        print(f'\t\t' + \
            locale.format_string('%.2f', speed * 500, True) + ' bits/s')

        try:
            speedtest.recv(2)
        except TimeoutError:
            print(f'Erro: Nenhum pacote recebido.\nAbortando...')
            exit(1)

        print('Iniciando teste de download...')
        speed = download(speedtest)
        print('Download médio:')
        print(f'\t\t' + \
            locale.format_string('%.2f', speed, True) + ' pacotes/s')
        print(f'\t\t' + \
            locale.format_string('%.2f', speed * 500, True) + ' bits/s')
else:
    error()