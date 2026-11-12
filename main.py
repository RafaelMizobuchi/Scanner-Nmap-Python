import subprocess, sys, json, socket, argparse, ipaddress
import xml.etree.ElementTree as ET
from datetime import datetime

def procurar_host(raiz):
    host = raiz.find("host")

    if host is None:
        raise ValueError("Nenhum host encontrado no XML")

    endereco = host.find("address")

    if endereco is None:
        raise ValueError("Nenhum endereço encontrado para o host")

    ip = endereco.get("addr")

    return host, ip

def inventario_anterior(nome_arquivo):

    try:
        with open(nome_arquivo, "r", encoding="utf-8") as arquivo_json:
            dados_anteriores = json.load(arquivo_json)

        print("Arquivo lido com sucesso")
        return dados_anteriores
    except FileNotFoundError:
        print("Houve um erro e nao encontramos o arquivo desejado")
        return []

def comparar_portas(anterior, atual):
    inventario_anterior = {}
    inventario_atual = {}

    for item in anterior:
        chave = (
            item["porta"],
            item["ip"],
            item["protocolo"]
        )

        valor = (
            item["nome"],
            item["situacao"]
        )

        inventario_anterior[chave] = valor

    for item in atual:
        chave = (
            item["porta"],
            item["ip"],
            item["protocolo"]
        )

        valor = (
            item["nome"],
            item["situacao"]
        )

        inventario_atual[chave] = valor

    portas_removidas = inventario_anterior.keys() - inventario_atual.keys()
    portas_adicionadas = inventario_atual.keys() - inventario_anterior.keys()
    
    portas_comum = inventario_anterior.keys() & inventario_atual.keys()
    
    portas_alteradas = []
    
    for item in portas_comum:
        if inventario_anterior[item] != inventario_atual[item]:
            portas_alteradas.append({
                "porta": item,
                "anterior":inventario_anterior[item],
                "atual":inventario_atual[item]
            }) 
    
    return portas_adicionadas, portas_removidas, portas_alteradas     

def descobrir_ip():

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as conexao:
        conexao.connect(("8.8.8.8", 80))
        ip_local = conexao.getsockname()[0]
    
    return ip_local

def carregar_historico(nome_arquivo):
    try:
        with open(nome_arquivo, "r", encoding="utf-8") as arquivo:
            historico = json.load(arquivo)
            
        return historico
    except FileNotFoundError:
        return[]

inventario = []

def obter_argumentos():
    parser = argparse.ArgumentParser(
        description="Network Scanner & Service Inventory"
    )
    
    parser.add_argument(
        "--target",
        type=str,
        default=None,
        help="IP do dispositivo que será analisado"
    )

    return parser.parse_args()

def validar_ip(endereco):
    
    try:
        ip = ipaddress.IPv4Address(endereco)
        return str(ip)
    
    except ValueError:
        print(f"IP {endereco} inválido")
        sys.exit(1)
        
argumentos = obter_argumentos()
meu_ip = argumentos.target if argumentos.target is not None else descobrir_ip()
meu_ip = validar_ip(meu_ip)

nome_inventario = f"inventario_{meu_ip}.json"

resultado = subprocess.run([
"nmap",
"-sT",
"-sV",
"-Pn",
"-oX",
"scan_result.xml",
meu_ip
])

if resultado.returncode == 0:
    print("Scan realizado com sucesso")

    with open("scan_result.xml", "rb") as arquivoScan:
        arvore = ET.parse(arquivoScan)

    raiz = arvore.getroot()
    print("Raiz:", raiz.tag)
    print("Hosts encontrados:", len(raiz.findall("host")))
    print("Elementos da raiz:", [elemento.tag for elemento in raiz])
    portas = raiz.findall(".//port")
    print(f"O numero de portas encontradas é: {len(portas)}")

else:
    print("Erro ao realizar scan")
    sys.exit(1)

_, ip = procurar_host(raiz)

for numero in portas:
    protocolo = numero.get("protocol")
    id_porta = numero.get("portid")
    estado = numero.find("state")
    situacao = estado.get("state")
    service = numero.find("service")
    nome = service.get("name")


    dados_porta = {
        "ip" : ip,
        "porta" : id_porta,
        "protocolo" : protocolo,
        "situacao" : situacao,
        "nome" : nome
    }

    inventario.append(dados_porta)

dados_anteriores = inventario_anterior(nome_inventario)

novas_portas, portas_removidas, portas_alteradas = comparar_portas(dados_anteriores, inventario)

print("Portas novas:", novas_portas)
print("Portas removidas:", portas_removidas)
print("Portas alteradas", portas_alteradas )

with open(nome_inventario, "w", encoding="utf-8") as arquivo_json:
    json.dump(inventario, arquivo_json, indent=4)  
    
    
data_varredura = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

registro = {
    "data": data_varredura,
    "ip": meu_ip,
    "portas": inventario
    }

historico = carregar_historico("historico.json")

historico.append(registro)

with open("historico.json", "w", encoding="utf-8") as arquivo:
    json.dump(historico, arquivo, indent=4)
    
    