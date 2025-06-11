import random
import sys
import time
import os

# --- CONSTANTES ---
VIDA_MAXIMA = 100
ENERGIA_MAXIMA = 100
PONTUACAO_MAXIMA = 500
MOCHILA_MAX = 5
ENERGIA_CUSTO_ABRIGO_BASE = 20
PORCENTAGEM_COMIDA_BASE = 0.6
TEMPO_LIMITE_DIA = 10
ENERGIA_REGEN_SONO_BASE = 40
VIDA_REGEN_SONO_BASE = 15

# --- DADOS DO JOGO ---
# Dicionários centralizados pra evitar repetição
# Adicionado "tipo" para facilitar o filtro e manuseio
ITENS_GERAL = {
#Armas 
    "Faca": {"tipo": "arma", "dano_min": 10, "dano_max": 20},
    "Arco": {"tipo": "arma", "dano_min": 15, "dano_max": 25},
    "Escopeta": {"tipo": "arma", "dano_min": 30, "dano_max": 50},
    "Machado": {"tipo": "arma", "dano_min": 20, "dano_max": 35},
    "Lança": {"tipo": "arma", "dano_min": 18, "dano_max": 28},
    "Pistola": {"tipo": "arma", "dano_min": 25, "dano_max": 40},
    "Espingarda de Cano Curto": {"tipo": "arma", "dano_min": 35, "dano_max": 55},
    "Taco com Pregos": {"tipo": "arma", "dano_min": 12, "dano_max": 24},
    "Foice Enferrujada": {"tipo": "arma", "dano_min": 16, "dano_max": 26},
#Itens de defesa 
    "Armadura de Couro": {"tipo": "protecao", "protecao": 10},
    "Capacete": {"tipo": "protecao", "protecao": 5},
    "Escudo Improvisado": {"tipo": "protecao", "protecao": 8},
#itens de regeneração
    "Kit de Primeiros Socorros": {"tipo": "medico", "vida_recuperada": 25, "cura_ferimento_grave": True}, 
    "Atadura": {"tipo": "medico", "vida_recuperada": 10},
    "Antídoto": {"tipo": "medico", "cura_envenenamento": True, "energia_recuperada": 0}, # Adicionei energia_recuperada para ser consistente
    "Chá de Ervas": {"tipo": "medico", "cura_doenca": True, "energia_recuperada": 5}, 
#itens comestiveis
    "Fruta": {"tipo": "comida", "vida_recuperada": (3, 8), "energia_recuperada": 10},
    "Nozes": {"tipo": "comida", "vida_recuperada": (3, 8), "energia_recuperada": 10},
    "Raiz comestível": {"tipo": "comida", "vida_recuperada": (3, 8), "energia_recuperada": 10},
    "Cogumelo Desconhecido": {"tipo": "comida", "vida_recuperada": (-5, 0), "energia_recuperada": 5, "chance_doenca": 0.5},
}

ANIMAIS = {
    "🐆Onça": {"dano_min": 15, "dano_max": 25, "vida": 60, "chance_fuga_base": 0.3, "chance_ferimento_grave": 0.2},
    "🐍Cobra": {"dano_min": 8, "dano_max": 18, "vida": 30, "chance_fuga_base": 0.6, "chance_envenenamento": 0.7},
    "🐺Lobo Guará": {"dano_min": 12, "dano_max": 22, "vida": 50, "chance_fuga_base": 0.4, "chance_ferimento_grave": 0.1},
    "🐗Javali": {"dano_min": 10, "dano_max": 20, "vida": 30, "chance_fuga_base": 0.4, "chance_ferimento_grave": 0.15},
    "🐊jacaré": {"dano_min": 8, "dano_max": 25, "vida": 60, "chance_fuga_base": 0.7, "chance_ferimento_grave": 0.3},
    "🐒Chimpanzé": {"dano_min": 6, "dano_max": 15, "vida": 80, "chance_fuga_base": 0.7},
    "🦍Gorila": {"dano_min": 12, "dano_max": 25, "vida": 100, "chance_fuga_base": 0.3, "chance_ferimento_grave": 0.25},
}

# --- ESTADOS DO JOGO ---
INTRO = 0
JOGANDO = 1
ESPERA_COMIDA = 2 
ESPERA_USAR_ITEM = 3 
FIM = 4
COMBATE = 5

# --- VARIÁVEIS GLOBAIS (estado do jogo) ---
nome_jogador = "Aventureiro(a)"
vida = VIDA_MAXIMA
energia = ENERGIA_MAXIMA
mochila = []
pontuacao = 0
encontrou_saida = False
abrigo_construido = False
dias_passados = 1
acoes_no_dia = 0
historico_acoes = {1: []}
estado_jogo = INTRO
mensagem_final = ""
mensagem_acao = ""
item_a_processar = None # Usado para comida encontrada ou item da mochila a usar
inimigo_atual = None
vida_inimigo_atual = 0

#VARIÁVEIS DE SAÚDE
status_envenenado = False
status_ferimento_grave = False
status_doente = False

# --- FUNÇÕES DE UTILIDADE ---
def clear_screen():
    """Limpa a tela do terminal."""
    os.system('cls' if sys.platform.startswith('win') else 'clear')

def show_animation(frames, delay=0.2, message="Processando..."):
    """Exibe uma sequência de quadros como uma animação no terminal."""
    for frame in frames:
        clear_screen()
        print(message)
        print(frame)
        time.sleep(delay)
    clear_screen()

def adicionar_historico(mensagem):
    """Adiciona uma mensagem ao histórico de ações do dia atual."""
    historico_acoes.setdefault(dias_passados, []).append(mensagem)

def adicionar_item_mochila(item_nome):
    """Tenta adicionar um item à mochila."""
    if len(mochila) >= MOCHILA_MAX:
        return False
    mochila.append(item_nome)
    return True

def calcular_protecao_total():
    """Calcula o valor total de proteção física que o jogador possui na mochila."""
    return sum(ITENS_GERAL[item]["protecao"] for item in mochila if ITENS_GERAL.get(item, {}).get("tipo") == "protecao")

def escolher_melhor_arma():
    """Retorna a melhor arma na mochila, se houver."""
    armas_possuidas = [item for item in mochila if ITENS_GERAL.get(item, {}).get("tipo") == "arma"]
    if armas_possuidas:
        return max(armas_possuidas, key=lambda x: ITENS_GERAL[x]["dano_max"])
    return None

def usar_arma_em_combate():
    """Calcula o dano de ataque usando a melhor arma disponível."""
    arma = escolher_melhor_arma()
    if arma:
        dano = random.randint(ITENS_GERAL[arma]["dano_min"], ITENS_GERAL[arma]["dano_max"])
        return dano, arma
    return random.randint(5, 10), "mãos nuas" # Dano base se não tiver arma

# --- FUNÇÃO PARA PROCESSAR STATUS NEGATIVOS ---
def processar_status_negativos():
    """Aplica os efeitos dos status negativos (envenenamento, ferimento, doença) a cada turno/ação."""
    global vida, energia, mensagem_acao, status_envenenado, status_ferimento_grave, status_doente

    if status_envenenado:
        dano_veneno = random.randint(2, 5)
        vida -= dano_veneno
        mensagem_acao += f"\nVocê está envenenado(a) e perdeu {dano_veneno} de vida! 😵"
        adicionar_historico(f"Perdeu {dano_veneno} de vida devido ao envenenamento.")
        if vida <= 0: return # Sai cedo se a vida zerar

    if status_ferimento_grave:
        dano_ferimento = random.randint(1, 3)
        vida -= dano_ferimento
        mensagem_acao += f"\nSeu ferimento grave está sangrando e você perdeu {dano_ferimento} de vida! 🩸"
        adicionar_historico(f"Perdeu {dano_ferimento} de vida devido ao ferimento grave.")
        if vida <= 0: return # Sai cedo se a vida zerar

    if status_doente:
        energia_drenada = random.randint(1, 4)
        energia -= energia_drenada
        mensagem_acao += f"\nVocê se sente fraco(a) pela doença e perdeu {energia_drenada} de energia! 😩"
        adicionar_historico(f"Perdeu {energia_drenada} de energia devido à doença.")
        if energia <= 0: return # Sai cedo se a energia zerar

# --- FUNÇÕES DE AÇÃO DO JOGADOR ---

def processar_consumo_item(item_nome, vida_recuperada, energia_recuperada):
    """Aplica os efeitos de consumo de um item e remove-o da mochila."""
    global vida, energia, pontuacao, mensagem_acao, mochila, acoes_no_dia, status_envenenado, status_ferimento_grave, status_doente
    
    # Efeitos gerais de vida e energia
    vida = min(vida + vida_recuperada, VIDA_MAXIMA)
    energia = min(energia + energia_recuperada, ENERGIA_MAXIMA)
    pontuacao += 30 # Pontos fixos por consumir
    
    # Efeitos específicos para o novo sistema de saúde
    item_data = ITENS_GERAL[item_nome]
    
    efeitos_especificos_msg = ""

    if item_data.get("cura_envenenamento"):
        if status_envenenado:
            status_envenenado = False
            efeitos_especificos_msg += " Você se curou do envenenamento! ✨"
        else:
            efeitos_especificos_msg += " Não estava envenenado, mas o antídoto foi consumido. 🤔"
    
    if item_data.get("cura_ferimento_grave"):
        if status_ferimento_grave:
            status_ferimento_grave = False
            efeitos_especificos_msg += " Seu ferimento grave foi tratado! 💪"
        else:
            efeitos_especificos_msg += " Não tinha ferimento grave, mas o kit foi usado. 🤔"

    if item_data.get("cura_doenca"):
        if status_doente:
            status_doente = False
            efeitos_especificos_msg += " Você se sentiu melhor da doença! 🌟"
        else:
            efeitos_especificos_msg += " Não estava doente, mas o chá foi consumido. 🤔"
    
    # Efeito colateral da comida (Cogumelo Desconhecido)
    if item_data.get("chance_doenca") and random.random() < item_data["chance_doenca"]:
        status_doente = True
        efeitos_especificos_msg += " Mas parece que você pegou uma doença estranha... 🤢"
        adicionar_historico(f"Você consumiu {item_nome} e ficou doente.")

    mensagem_acao = f"Você usou o(a) {item_nome}. ❤️ +{vida_recuperada} vida, ⚡ +{energia_recuperada} energia, ⭐ +30 pontos!" + efeitos_especificos_msg
    adicionar_historico(f"Você consumiu um {item_nome}.")
    mochila.remove(item_nome) # Remove pelo nome porque pode haver duplicatas.

def usar_item_da_mochila(indice_escolhido):
    """Gerencia o uso de um item da mochila."""
    global mensagem_acao, estado_jogo, item_a_processar, acoes_no_dia

    itens_usaveis = [item for item in mochila if ITENS_GERAL.get(item, {}).get("tipo") in ["comida", "medico", "utilitario"]]

    try:
        item_nome = itens_usaveis[indice_escolhido - 1] # Pega o nome do item da lista filtrada
        
        # Animação de uso para qualquer item
        frames_item = [
            "   [ ]", "   [U]", "   [U-]", "   [U-S]", "   [U-S-E]",
            "   [U-S-E] \n   _|_", "   [U-S-E] \n   _|_ \n    |", "   [U-S-E] \n   _|_ \n    | \n   / \\"
        ]
        show_animation(frames_item, delay=0.1, message="🩹 Usando item...")

        item_data = ITENS_GERAL[item_nome]
        item_tipo = item_data["tipo"]

        vida_recuperada = 0
        if "vida_recuperada" in item_data:
            if isinstance(item_data["vida_recuperada"], tuple):
                vida_recuperada = random.randint(*item_data["vida_recuperada"])
            else:
                vida_recuperada = item_data["vida_recuperada"]
        
        energia_recuperada = item_data.get("energia_recuperada", 0) # Certifica que sempre tenha um valor

        if item_tipo == "medico" or item_tipo == "comida":
            processar_consumo_item(item_nome, vida_recuperada, energia_recuperada)
        elif item_tipo == "utilitario":
            # Para itens utilitários que não se "consomem" ou têm efeito específico
            mensagem_acao = f"Você tentou usar o(a) {item_nome}, mas não teve efeito imediato. 🤔"
            adicionar_historico(f"Você tentou usar um {item_nome}.")
            # Se o item é de uso único, remova:
            if item_nome == "Corda": # Exemplo: corda pode ser usada uma vez
                mochila.remove(item_nome)
        else: # Tipo "arma" ou "protecao" ou outros sem uso direto
            mensagem_acao = f"O(a) {item_nome} não pode ser 'usado' assim. Ele(a) é {item_tipo} e é ativo(a) automaticamente."
            adicionar_historico(f"Você tentou usar {item_nome}, mas não é um item de uso direto.")
            
        acoes_no_dia += 1 # Usar item conta como uma ação
        estado_jogo = JOGANDO

    except (ValueError, IndexError):
        mensagem_acao = "Entrada inválida ou número fora do alcance dos itens usáveis. 🔢"
        estado_jogo = ESPERA_USAR_ITEM # Permanece no estado para nova tentativa

def buscar_comida():
    """Ação de buscar comida."""
    global mensagem_acao, item_a_processar, acoes_no_dia, vida, energia, pontuacao, status_doente
    
    frames_buscar = ["Buscando  .", "Buscando ..", "Buscando ..."]
    show_animation(frames_buscar, delay=0.3, message="🌳 Procurando por comida...")

    acoes_no_dia += 1

    chance_encontrar = PORCENTAGEM_COMIDA_BASE * (0.6 if abrigo_construido else 1.0)
    
    if random.random() < chance_encontrar:
        comidas_encontradas = [item for item, data in ITENS_GERAL.items() if data["tipo"] == "comida"]
        
        # Aumentar a chance de encontrar Cogumelo Desconhecido
        if random.random() < 0.15: # 15% de chance de ser um cogumelo desconhecido
            item_nome = "Cogumelo Desconhecido"
        else:
            # Garante que não escolha o cogumelo desconhecido se houver outras opções
            outras_comidas = [c for c in comidas_encontradas if c != "Cogumelo Desconhecido"]
            if outras_comidas:
                item_nome = random.choice(outras_comidas)
            else: # Caso só exista o cogumelo, ele será escolhido
                item_nome = "Cogumelo Desconhecido"
        
        item_a_processar = item_nome # Armazena o nome do item encontrado
        item_data = ITENS_GERAL[item_nome]
        
        # Ajuste para vida_recuperada que pode ser negativa
        vida_ganho_str = ""
        if isinstance(item_data["vida_recuperada"], tuple):
            vida_ganho = random.randint(*item_data["vida_recuperada"])
            vida_ganho_str = f"({vida_ganho})" # Mostra o valor exato que pode ser negativo
        else:
            vida_ganho = item_data["vida_recuperada"]
            vida_ganho_str = f"+{vida_ganho}"

        energia_ganho = item_data["energia_recuperada"]
        adicionar_historico(f"Você encontrou comida ({item_nome}).")
        mensagem_acao = (f"Você encontrou comida: {item_nome} (❤️ {vida_ganho_str} vida, ⚡ +{energia_ganho} energia).\n"
                         "Deseja (C) Comer agora ou (G) Guardar na mochila? (C/G) ❓")
        return True # Indica que encontrou algo e precisa de escolha
    else:
        energia_ganho = 10
        vida_ganho = random.randint(3, 8)
        energia = min(energia + energia_ganho, ENERGIA_MAXIMA)
        vida = min(vida + vida_ganho, VIDA_MAXIMA)
        pontuacao += 40
        adicionar_historico(f"Você buscou por comida, mas não encontrou nada de valor.")
        mensagem_acao = f"Você buscou, mas não encontrou comida. Ganhou ⚡ +{energia_ganho} energia e ❤️ +{vida_ganho} vida pelo esforço. ⭐ +40 pontos!"
        item_a_processar = None
        return False # Não encontrou nada que precise de escolha

def montar_abrigo():
    """Ação de montar um abrigo."""
    global energia, pontuacao, abrigo_construido, mensagem_acao, acoes_no_dia
    if abrigo_construido:
        adicionar_historico(f"Você tentou construir um abrigo novamente, mas já tinha um.")
        mensagem_acao = "Você já montou o abrigo, não pode construir novamente. 🏕️"
        return

    custo_energia = int(ENERGIA_CUSTO_ABRIGO_BASE * 1.5)
    if energia < custo_energia:
        adicionar_historico(f"Você tentou montar um abrigo, mas não tinha energia suficiente.")
        mensagem_acao = f"⚡ Energia insuficiente para montar o abrigo! Você precisa de {custo_energia} de energia."
        return
    
    frames_abrigo = ["Construindo [.]", "Construindo [..]", "Construindo [...]",
                     "Construindo [....]", "Construindo [.....]", "Construindo [✓]"]
    show_animation(frames_abrigo, delay=0.2, message="🛠️ Montando o abrigo...")

    energia -= custo_energia
    pontuacao += 30
    abrigo_construido = True
    acoes_no_dia += 1
    adicionar_historico(f"Você montou um abrigo seguro e descansou.")
    mensagem_acao = f"Você montou um abrigo e descansou um pouco. 😴 (-{custo_energia} energia, ⭐ +30 pontos)"

def explorar():
    """Ação de explorar a floresta."""
    global vida, energia, pontuacao, estado_jogo, inimigo_atual, vida_inimigo_atual, encontrou_saida, mensagem_acao, acoes_no_dia, item_a_processar
    
    custo_energia = 15
    if energia < custo_energia:
        adicionar_historico(f"Você tentou explorar, mas estava muito exausto.")
        mensagem_acao = "⚡ Energia insuficiente para explorar!"
        return False # Não permite a ação de exploração
    
    energia -= custo_energia
    acoes_no_dia += 1

    frames_explorar = [" Explorando...", "|--|  .--|", "|  | /   |", "\\--/----|", "   ?     !"]
    show_animation(frames_explorar, delay=0.25, message="🗺️ Explorando a área...")
    
    chance_comida_explorar = PORCENTAGEM_COMIDA_BASE * (0.6 if abrigo_construido else 1.0)
    chance_caminho = min(0.10, pontuacao / PONTUACAO_MAXIMA * 0.10)

    evento = random.choices(
        population=["animal", "nada", "comida", "item_medico", "item_protecao", "armamento", "caminho_de_casa"],
        weights=[0.3, 0.15, chance_comida_explorar, 0.08, 0.07, 0.1, chance_caminho],
        k=1,
    )[0]
    
    if evento == "caminho_de_casa":
        encontrou_saida = True
        mensagem_acao = "Após muita exploração, você avista uma trilha conhecida! 🏞️ Parece que você encontrou o caminho de volta para casa! 🎉"
        adicionar_historico(f"Após vasta exploração, você encontrou o caminho de casa!")
    elif evento == "animal":
        animal_encontrado = random.choice(list(ANIMAIS.keys()))
        inimigo_atual = animal_encontrado
        vida_inimigo_atual = ANIMAIS[animal_encontrado]["vida"]
        estado_jogo = COMBATE
        mensagem_acao = f"Você encontrou um {inimigo_atual}! 😱 Prepare-se para lutar!"
        adicionar_historico(f"Você foi surpreendido por um(a) {inimigo_atual} e entrou em combate!")
    elif evento == "comida":
        return buscar_comida() # Reutiliza a lógica de buscar comida para o evento de comida
    else: # Itens ou nada
        item_tipo_map = {
            "item_medico": "medico",
            "item_protecao": "protecao",
            "armamento": "arma"
        }
        tipo_item_encontrado = item_tipo_map.get(evento)

        if tipo_item_encontrado:
            possiveis_itens = [item for item, data in ITENS_GERAL.items() if data["tipo"] == tipo_item_encontrado]
            # Excluir Cogumelo Desconhecido de item_medico para evitar que apareça aqui
            if tipo_item_encontrado == "medico":
                possiveis_itens = [item for item in possiveis_itens if item != "Cogumelo Desconhecido"]

            if possiveis_itens:
                item_encontrado = random.choice(possiveis_itens)
                if adicionar_item_mochila(item_encontrado):
                    pontuacao_extra = {"medico": 25, "protecao": 35, "arma": 40}.get(tipo_item_encontrado, 0)
                    pontuacao += pontuacao_extra
                    mensagem_acao = f"Você encontrou um item: {item_encontrado}! ({tipo_item_encontrado.capitalize()}) ⭐ +{pontuacao_extra} pontos!"
                    adicionar_historico(f"Você encontrou um item de {tipo_item_encontrado}: {item_encontrado}.")
                else:
                    mensagem_acao = f"Você encontrou um item: {item_encontrado}, mas sua mochila está cheia. 🎒🚫"
                    adicionar_historico(f"Você encontrou um item de {tipo_item_encontrado} ({item_encontrado}), mas sua mochila estava cheia.")
            else: # Não encontrou itens específicos do tipo, mesmo que o evento tenha sido sorteado
                mensagem_acao = "Você explorou mas não encontrou nada relevante. 🤷"
                adicionar_historico(f"Você explorou a área, mas não encontrou nada de especial.")
        else: # evento == "nada"
            mensagem_acao = "Você explorou mas não encontrou nada relevante. 🤷"
            adicionar_historico(f"Você explorou a área, mas não encontrou nada de especial.")
    return False # Não requer escolha adicional como a comida

def dormir():
    """Ação de dormir para passar o dia."""
    global vida, energia, dias_passados, acoes_no_dia, mensagem_acao, status_doente, status_envenenado, status_ferimento_grave

    if not abrigo_construido:
        adicionar_historico(f"Você tentou dormir, mas não tinha um abrigo seguro.")
        mensagem_acao = "Você não tem um abrigo seguro para dormir. Encontre um local ou construa um!"
        return

    frames_dormir = ["Zzz .", "Zzz ..", "Zzz ...", "Zzz .", "Zzz ..", "Zzz ...", "🌄 Acordando..."]
    show_animation(frames_dormir, delay=0.3, message="😴 Você está dormindo...")

    energia_recuperada = int(ENERGIA_REGEN_SONO_BASE * 1.5)
    vida_recuperada = int(VIDA_REGEN_SONO_BASE * 1.5)
    
    vida = min(vida + vida_recuperada, VIDA_MAXIMA)
    energia = min(energia + energia_recuperada, ENERGIA_MAXIMA)
    
    dias_passados += 1
    acoes_no_dia = 0

    # EFEITOS DO SONO NOS STATUS NEGATIVOS
    sono_cura_mensagem = ""
    if status_doente and random.random() < 0.3: # 30% de chance de melhorar da doença ao dormir
        status_doente = False
        sono_cura_mensagem += " Você se sentiu um pouco melhor da doença. "

    adicionar_historico(f"Você dormiu em seu abrigo seguro e se recuperou bem.")
    mensagem_acao = (f"Você dormiu e um novo dia começou! ☀️"
                     f" ❤️ +{vida_recuperada} vida, ⚡ +{energia_recuperada} energia." + sono_cura_mensagem)

# --- FUNÇÕES DE COMBATE ---
def gerenciar_combate():
    """Gerencia o combate turno a turno."""
    global vida, energia, pontuacao, estado_jogo, inimigo_atual, vida_inimigo_atual, mensagem_acao, acoes_no_dia, status_envenenado, status_ferimento_grave

    clear_screen()
    print(f"⚔️ VOCÊ ESTÁ EM COMBATE COM UM(A) {inimigo_atual}! ⚔️")
    print(f"❤️ Sua vida: {vida}/{VIDA_MAXIMA} | ⚡ Sua energia: {energia}/{ENERGIA_MAXIMA}")
    print(f"👾 Vida do {inimigo_atual}: {vida_inimigo_atual}/{ANIMAIS[inimigo_atual]['vida']}")
    print("\nEscolha sua ação:")
    print("   (A) Atacar")
    print("   (D) Defender")
    print("   (F) Fugir")

    escolha_combate = input("Sua ação: ").strip().upper()
    mensagem_acao_combate_turno = "" # Mensagem específica para este turno de combate
    dano_defesa = 0

    if escolha_combate == 'A':
        dano_causado, arma_usada = usar_arma_em_combate()
        vida_inimigo_atual -= dano_causado
        pontuacao += 5
        mensagem_acao_combate_turno += f"Você ataca com seu(sua) {arma_usada}, causando {dano_causado} de dano! 💥"
        adicionar_historico(f"Você atacou o(a) {inimigo_atual} com {arma_usada}, causando {dano_causado} de dano.")

    elif escolha_combate == 'D':
        energia_gasta = 5
        if energia >= energia_gasta:
            energia -= energia_gasta
            dano_defesa = random.randint(10, 20)
            mensagem_acao_combate_turno += f"Você se defende, reduzindo o próximo dano recebido em {dano_defesa}. 🛡️ (-{energia_gasta} energia)"
            adicionar_historico(f"Você se defendeu do ataque do(a) {inimigo_atual}.")
        else:
            mensagem_acao_combate_turno = "⚡ Energia insuficiente para defender! Você fica vulnerável."
            adicionar_historico(f"Você tentou se defender do(a) {inimigo_atual}, mas estava sem energia.")

    elif escolha_combate == 'F':
        custo_energia_fuga = 10
        if energia >= custo_energia_fuga:
            energia -= custo_energia_fuga
            chance_fuga = ANIMAIS[inimigo_atual]["chance_fuga_base"] + (vida / VIDA_MAXIMA * 0.2)
            
            frames_fuga = ["Correndo  . ", "Correndo ..", "Correndo ... 🏃", "Fugindo!"]
            show_animation(frames_fuga, delay=0.15, message="Tentando fugir...")

            if random.random() < chance_fuga:
                mensagem_acao = f"Você conseguiu fugir do(a) {inimigo_atual}! 💨 (-{custo_energia_fuga} energia)"
                adicionar_historico(f"Você conseguiu fugir do(a) {inimigo_atual}!")
                estado_jogo = JOGANDO
                inimigo_atual = None
                vida_inimigo_atual = 0
                acoes_no_dia += 1
                return # Sai da função pois o combate terminou
            else:
                dano_retaliacao = random.randint(ANIMAIS[inimigo_atual]["dano_min"], ANIMAIS[inimigo_atual]["dano_max"]) // 2
                vida -= dano_retaliacao
                mensagem_acao_combate_turno = f"Você tentou fugir, mas falhou! 😬 O(a) {inimigo_atual} não te deixa escapar! (-{custo_energia_fuga} energia). Você sofreu {dano_retaliacao} de dano de retaliação! 💔"
                adicionar_historico(f"Você tentou fugir do(a) {inimigo_atual}, mas falhou e sofreu dano.")
        else:
            mensagem_acao_combate_turno = "⚡ Energia insuficiente para tentar a fuga! Você precisa de mais energia."
            adicionar_historico(f"Você tentou fugir do(a) {inimigo_atual}, mas estava sem energia.")
    else:
        mensagem_acao_combate_turno = "Comando inválido no combate. Tente (A)tacar, (D)efender ou (F)ugir."
        
    if vida_inimigo_atual <= 0:
        pontuacao += 100
        mensagem_acao = f"Você derrotou o(a) {inimigo_atual}! 🎉 (+100 pontos)" # Esta mensagem será a principal agora
        adicionar_historico(f"Você derrotou o(a) {inimigo_atual} em combate!")
        estado_jogo = JOGANDO
        inimigo_atual = None
        vida_inimigo_atual = 0
        acoes_no_dia += 1
        return # Sai da função pois o combate terminou

    # Ataque do animal (se o combate não terminou)
    dano_animal = random.randint(ANIMAIS[inimigo_atual]["dano_min"], ANIMAIS[inimigo_atual]["dano_max"])
    protecao_total = calcular_protecao_total()
    dano_animal_final = max(0, dano_animal - dano_defesa - protecao_total)
    
    vida -= dano_animal_final
    mensagem_acao_combate_turno += f"\nO(a) {inimigo_atual} ataca, causando {dano_animal_final} de dano a você! 🩸"
    if protecao_total > 0:
        mensagem_acao_combate_turno += f" (Sua proteção física reduziu {protecao_total} de dano!)"

    adicionar_historico(f"O(a) {inimigo_atual} te atacou, causando {dano_animal_final} de dano.")
    pontuacao -= 5

    # APLICAÇÃO DE STATUS NEGATIVOS APÓS O ATAQUE DO ANIMAL
    if ANIMAIS[inimigo_atual].get("chance_envenenamento") and random.random() < ANIMAIS[inimigo_atual]["chance_envenenamento"]:
        if not status_envenenado: # Evita aplicar se já estiver envenenado
            status_envenenado = True
            mensagem_acao_combate_turno += f" Você foi envenenado(a) pelo(a) {inimigo_atual}! ☠️"
            adicionar_historico(f"Você foi envenenado(a) pelo(a) {inimigo_atual}.")
    
    if ANIMAIS[inimigo_atual].get("chance_ferimento_grave") and random.random() < ANIMAIS[inimigo_atual]["chance_ferimento_grave"]:
        if not status_ferimento_grave: # Evita aplicar se já tiver ferimento grave
            status_ferimento_grave = True
            mensagem_acao_combate_turno += f" Você sofreu um ferimento grave! 🩹"
            adicionar_historico(f"Você sofreu um ferimento grave em combate contra o(a) {inimigo_atual}.")
    
    mensagem_acao = mensagem_acao_combate_turno # Atualiza a mensagem principal do jogo
    
    frames_combate = [f"Você vs {inimigo_atual}", "   ⚔️", "   💥", "   ⚔️", f"({inimigo_atual} ataca!)"]
    show_animation(frames_combate, delay=0.2, message="⚔️ Combate em andamento!")
    
    if vida <= 0:
        estado_jogo = FIM
        mensagem_final = "derrota"
        adicionar_historico(f"Você sucumbiu aos ferimentos e foi derrotado(a) pelo(a) {inimigo_atual}.")
        return

# --- FUNÇÕES DE EXIBIÇÃO E FIM DE JOGO ---
def mostrar_status():
    """Exibe o status atual do jogador no terminal."""
    print("--- Status do Jogador ---")
    print(f"👤 Nome: {nome_jogador}")
    print(f"🗓️ Dia: {dias_passados} | ⏰ Ações: {acoes_no_dia}/{TEMPO_LIMITE_DIA}")
    print(f"❤️ Vida: {vida}/{VIDA_MAXIMA} | ⚡ Energia: {energia}/{ENERGIA_MAXIMA}")
    print(f"⭐ Pontos: {pontuacao}")
    protecao_total = calcular_protecao_total()
    if protecao_total > 0:
        print(f"🛡️ Proteção Física: {protecao_total}")

    condicoes_atuais = []
    if status_envenenado:
        condicoes_atuais.append("☠️ Envenenado!")
    if status_ferimento_grave:
        condicoes_atuais.append("🩹 Ferimento Grave!")
    if status_doente:
        condicoes_atuais.append("🤢 Doente!")
    
    if condicoes_atuais:
        print("🚨 Condições: " + " | ".join(condicoes_atuais))

    print("🎒 Mochila: " + (", ".join(mochila) if mochila else "Vazia"))
    print("-------------------------")

def verificar_fim_de_jogo():
    """Verifica as condições de vitória ou derrota."""
    global encontrou_saida, pontuacao, vida, energia, mensagem_final, estado_jogo

    if vida <= 0:
        mensagem_final = "derrota"
        adicionar_historico(f"Você sucumbiu aos ferimentos. Fim da jornada.")
        estado_jogo = FIM
        return True
    if energia <= 0:
        mensagem_final = "derrota_energia"
        adicionar_historico(f"Você ficou completamente exausto(a) e não conseguiu mais continuar. Fim da jornada.")
        estado_jogo = FIM
        return True
    if pontuacao >= PONTUACAO_MAXIMA or encontrou_saida:
        encontrou_saida = True # Garante que a flag esteja true para a mensagem final
        mensagem_final = "vitoria"
        estado_jogo = FIM
        return True
    return False

def desenhar_intro():
    """Exibe a tela de introdução do jogo e coleta o nome do jogador."""
    global nome_jogador
    clear_screen()
    print("===================================")
    print("     🌲 SOBREVIVÊNCIA NA FLORESTA 🌳     ")
    print("===================================\n")
    print("Você está perdido em uma floresta e precisa sobreviver. 🧭")
    print("Coletar recursos, montar um abrigo, explorar e fugir de animais selvagens. 🦊🐻🐍")
    print("Você também pode encontrar armas para se defender. 🗡️🛡️")
    print("A comida encontrada pode ser comida na hora ou guardada para depois. 🍎🌰")
    print("O tempo passa a cada ação. Gerencie seus dias para não se exaurir. ☀️🌙")
    print("Construa um abrigo para poder descansar e recuperar suas forças! 🏕️")
    print("☠️Cuidado com os perigos ocultos: você pode ser envenenado(a), se ferir gravemente ou ficar doente!☠️")
    print("Sua meta é acumular pontos e explorar o suficiente para encontrar o caminho de casa. 🏠\n")
    print("--- Controles ---")
    print("1️⃣ - Buscar comida | 2️⃣ - Montar abrigo | 3️⃣ - Explorar")
    print("4️⃣ - Dormir (se tiver abrigo) | 🇺 - Usar item da mochila | 🇸 - Sair do jogo")
    print("Durante decisão: (C) Comer / (G) Guardar | Durante combate: (A) Atacar / (D) Defender / (F) Fugir")
    print("-----------------\n")
    nome_digitado = input("Antes de começar, digite seu nome (ou ENTER para 'Aventureiro(a)'): ").strip()
    if nome_digitado:
        nome_jogador = nome_digitado
    input(f"\nBem-vindo(a), {nome_jogador}! Pressione ENTER para começar sua jornada... ▶️")

def desenhar_fim():
    """Exibe a tela final do jogo com base no resultado."""
    clear_screen()
    print("===================================")
    print("         FIM DE JOGO             ")
    print("===================================\n")
    if mensagem_final == "vitoria":
        print(f"🎉 Parabéns, {nome_jogador}! Você sobreviveu e encontrou o caminho de volta para casa! 🏡✨")
        print(f"Sua vasta experiência na floresta te guiou até a civilização em {dias_passados} dias!")
    elif mensagem_final == "saida":
        print(f"Você decidiu sair do jogo, {nome_jogador}. Até a próxima aventura! 👋")
    elif mensagem_final == "derrota_energia":
        print(f"⚡ {nome_jogador}, você ficou completamente exausto(a) e não conseguiu mais se mover. A floresta te consumiu. 😵")
    else: # derrota por vida
        print(f"💀 {nome_jogador}, você sucumbiu aos perigos da floresta. Fim de jogo. 🥀")
    print(f"\nSua pontuação final: ⭐ {pontuacao}")
    print("-----------------------------------\n")
    print("\n--- Diário de Bordo da Sua Jornada ---")
    if historico_acoes:
        for dia, eventos_do_dia in sorted(historico_acoes.items()):
            print(f"\n--- Dia {dia} ---")
            print("   " + "\n   ".join(eventos_do_dia) if eventos_do_dia else "   Nenhum evento registrado neste dia.")
    else:
        print("Não há registros de sua jornada.")
    print("-------------------------------------\n")
    input("Pressione ENTER para sair. 🚪")
    sys.exit()

# --- LOOP PRINCIPAL DO JOGO ---
def main():
    """Função principal que controla o fluxo do jogo."""
    global estado_jogo, mensagem_acao, item_a_processar

    while True:
        if estado_jogo != INTRO:
            mostrar_status()
            if estado_jogo == COMBATE and inimigo_atual:
                print(f"👾 Vida do {inimigo_atual}: {vida_inimigo_atual}/{ANIMAIS[inimigo_atual]['vida']}")

        # PROCESSAR STATUS NEGATIVOS ANTES DE VERIFICAR O FIM DE JOGO
        # Isso garante que os efeitos dos status negativos sejam aplicados
        # e potencialmente levem ao fim do jogo se vida/energia chegarem a zero.
        if estado_jogo == JOGANDO or estado_jogo == COMBATE:
            processar_status_negativos()

        if verificar_fim_de_jogo():
            desenhar_fim()
            break

        if estado_jogo == INTRO:
            desenhar_intro()
            estado_jogo = JOGANDO
            mensagem_acao = f"Bem-vindo(a) à floresta, {nome_jogador}! O que você fará? 🤔"
            adicionar_historico("Início da Jornada. Você acordou perdido(a) na floresta.")
        
        elif estado_jogo == JOGANDO:
            if acoes_no_dia >= TEMPO_LIMITE_DIA:
                mensagem_acao += "\n🌙 A noite está caindo. É perigoso continuar explorando. "
                mensagem_acao += "Considere dormir (4)." if abrigo_construido else "Você não tem um abrigo seguro para descansar. "
            elif energia < ENERGIA_MAXIMA / 3:
                mensagem_acao += "\n⚡ Sua energia está baixa. Considere dormir (4) para recuperar. "
                if not abrigo_construido:
                    mensagem_acao += "Você precisa construir um abrigo primeiro. "

            print(f"\n>> {mensagem_acao}\n")
            print("Suas opções: 1️⃣ Buscar comida | 2️⃣ Montar abrigo | 3️⃣ Explorar")
            if abrigo_construido:
                print("4️⃣ Dormir e passar o dia")
            print("🇺 Usar item da mochila | 🇸 Sair do jogo")
            
            escolha = input("Sua ação: ").strip().upper()
            mensagem_acao = "" # Resetar mensagem de ação para a próxima iteração

            if escolha == '1':
                if buscar_comida(): # Retorna True se encontrou comida e precisa de escolha
                    estado_jogo = ESPERA_COMIDA
            elif escolha == '2':
                montar_abrigo()
            elif escolha == '3':
                explorar() # Pode mudar o estado para COMBATE ou ESPERA_COMIDA internamente
            elif escolha == '4':
                dormir()
            elif escolha == 'U':
                itens_usaveis_mochila = [item for item in mochila if ITENS_GERAL.get(item, {}).get("tipo") in ["comida", "medico", "utilitario"]]
                if itens_usaveis_mochila:
                    estado_jogo = ESPERA_USAR_ITEM
                    mensagem_acao = "Selecione o número do item que deseja usar: 🎒"
                else:
                    mensagem_acao = "Sua mochila está vazia ou não tem itens usáveis. 😔"
                    adicionar_historico(f"Você tentou usar um item, mas a mochila estava vazia ou sem itens usáveis.")
            elif escolha == 'S':
                estado_jogo = FIM
                mensagem_final = "saida"
                adicionar_historico(f"Você decidiu desistir da jornada.")
            else:
                mensagem_acao = "Comando inválido. Tente novamente. 🤷‍♀️"

        elif estado_jogo == ESPERA_COMIDA:
            print(f"\n>> {mensagem_acao}\n")
            escolha_comida = input("Sua escolha (C/G): ").strip().upper()
            
            if escolha_comida == 'C':
                if item_a_processar and ITENS_GERAL.get(item_a_processar, {}).get("tipo") == "comida":
                    item_data = ITENS_GERAL[item_a_processar]
                    
                    # Cuidado com item_data["vida_recuperada"] que pode ser uma tupla (min, max)
                    if isinstance(item_data["vida_recuperada"], tuple):
                        vida_rec = random.randint(*item_data["vida_recuperada"])
                    else:
                        vida_rec = item_data["vida_recuperada"]
                    
                    energia_rec = item_data.get("energia_recuperada", 0) # Pode não ter energia recuperada
                    
                    # Consumir diretamente o item encontrado (não está na mochila ainda)
                    global vida, energia, pontuacao, status_doente
                    
                    vida = min(vida + vida_rec, VIDA_MAXIMA)
                    energia = min(energia + energia_rec, ENERGIA_MAXIMA)
                    pontuacao += 30
                    
                    mensagem_acao_temp = f"Você comeu o(a) {item_a_processar}. ❤️ {vida_rec if vida_rec < 0 else '+' + str(vida_rec)} vida, ⚡ +{energia_rec} energia, ⭐ +30 pontos!"
                    
                    if item_data.get("chance_doenca") and random.random() < item_data["chance_doenca"]:
                        status_doente = True
                        mensagem_acao_temp += " Mas parece que você pegou uma doença estranha... 🤢"
                        adicionar_historico(f"Você comeu {item_a_processar} e ficou doente.")
                    
                    mensagem_acao = mensagem_acao_temp
                    adicionar_historico(f"Você comeu o(a) {item_a_processar} que encontrou.")
                else:
                    mensagem_acao = "Erro: sem comida para comer. 😟"
                    adicionar_historico(f"Erro ao tentar consumir comida encontrada.")
            elif escolha_comida == 'G':
                if item_a_processar and adicionar_item_mochila(item_a_processar):
                    mensagem_acao = f"Você guardou o(a) {item_a_processar} na mochila. 👍"
                    adicionar_historico(f"Você guardou {item_a_processar} na mochila.")
                else:
                    mensagem_acao = f"Sua mochila está cheia, não foi possível guardar o(a) {item_a_processar}. 🎒🚫"
                    adicionar_historico(f"Você tentou guardar {item_a_processar}, mas a mochila estava cheia.")
            else:
                mensagem_acao = "Escolha inválida. Pressione C para comer ou G para guardar. 🤷‍♂️"
                continue # Permanece no estado para nova tentativa
            
            item_a_processar = None
            estado_jogo = JOGANDO

        elif estado_jogo == ESPERA_USAR_ITEM:
            print(f"\n>> {mensagem_acao}\n")
            itens_usaveis = [item for item in mochila if ITENS_GERAL.get(item, {}).get("tipo") in ["comida", "medico", "utilitario"]]
            
            for i, item_nome in enumerate(itens_usaveis):
                print(f"   ({i+1}) {item_nome}")
            
            try:
                escolha_idx = int(input("Número do item para usar: ").strip())
                usar_item_da_mochila(escolha_idx)
            except (ValueError, IndexError):
                mensagem_acao = "Entrada inválida. Digite um número válido. 🔢"
            
            # Se a mensagem de ação for a padrão de erro, permanece no estado ESPERA_USAR_ITEM
            if "inválida" not in mensagem_acao and "fora do alcance" not in mensagem_acao:
                estado_jogo = JOGANDO

        elif estado_jogo == COMBATE:
            gerenciar_combate()

        time.sleep(1) # Pequena pausa para o jogador ler

if __name__ == "__main__":
    main()