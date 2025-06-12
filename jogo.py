import random
import sys
import time
import os

# --- CONSTANTES GLOBAIS ---
VIDA_MAXIMA_JOGADOR = 100
ENERGIA_MAXIMA_JOGADOR = 100
PONTUACAO_MAXIMA_VITORIA = 500
MOCHILA_MAX_CAPACIDADE = 5
CUSTO_ENERGIA_ABRIGO = 20
CHANCE_BASE_COMIDA = 0.6
ACOES_POR_DIA = 10
REGEN_ENERGIA_SONO_ABRIGO = 40
REGEN_VIDA_SONO_ABRIGO = 15

# --- DADOS DO JOGO ---
# Dicionários configuráveis para fácil expansão
DADOS_ITENS = {
    # Armas
    "Faca": {"tipo": "arma", "dano_min": 10, "dano_max": 20},
    "Arco": {"tipo": "arma", "dano_min": 15, "dano_max": 25},
    "Escopeta": {"tipo": "arma", "dano_min": 30, "dano_max": 50},
    "Machado": {"tipo": "arma", "dano_min": 20, "dano_max": 35},
    "Lança": {"tipo": "arma", "dano_min": 18, "dano_max": 28},
    "Pistola": {"tipo": "arma", "dano_min": 25, "dano_max": 40},
    "Espingarda de Cano Curto": {"tipo": "arma", "dano_min": 35, "dano_max": 55},
    "Taco com Pregos": {"tipo": "arma", "dano_min": 12, "dano_max": 24},
    "Foice Enferrujada": {"tipo": "arma", "dano_min": 16, "dano_max": 26},
    # Itens de defesa
    "Armadura de Couro": {"tipo": "protecao", "protecao": 10},
    "Capacete": {"tipo": "protecao", "protecao": 5},
    "Escudo Improvisado": {"tipo": "protecao", "protecao": 8},
    # Itens de regeneração/cura
    "Kit de Primeiros Socorros": {"tipo": "medico", "vida_recuperada": 25, "cura_ferimento_grave": True},
    "Atadura": {"tipo": "medico", "vida_recuperada": 10},
    "Antídoto": {"tipo": "medico", "cura_envenenamento": True, "energia_recuperada": 0},
    "Chá de Ervas": {"tipo": "medico", "cura_doenca": True, "energia_recuperada": 5},
    # Itens comestíveis
    "Fruta": {"tipo": "comida", "vida_recuperada": (3, 8), "energia_recuperada": 10},
    "Nozes": {"tipo": "comida", "vida_recuperada": (3, 8), "energia_recuperada": 10},
    "Raiz comestível": {"tipo": "comida", "vida_recuperada": (3, 8), "energia_recuperada": 10},
    "Cogumelo Desconhecido": {"tipo": "comida", "vida_recuperada": (-5, 0), "energia_recuperada": 5, "chance_doenca": 0.5},
    "Erva do BOB MARLEY": {"tipo": "comida", "vida_recuperada": (-1, 0), "energia_recuperada": (-3,-1), "chance_doenca": 1},
     "Coxinha de Farofa": {"tipo": "comida", "vida_recuperada": (5, 0), "energia_recuperada": 6, "chance_doenca": 0},
     
}

DADOS_ANIMAIS = {
    "🐆Onça": {"dano_min": 15, "dano_max": 25, "vida": 60, "chance_fuga_base": 0.3, "chance_ferimento_grave": 0.2},
    "🐍Cobra": {"dano_min": 8, "dano_max": 18, "vida": 30, "chance_fuga_base": 0.6, "chance_envenenamento": 0.7},
    "🐺Lobo Guará": {"dano_min": 12, "dano_max": 22, "vida": 50, "chance_fuga_base": 0.4, "chance_ferimento_grave": 0.1},
    "🐗Javali": {"dano_min": 10, "dano_max": 20, "vida": 30, "chance_fuga_base": 0.4, "chance_ferimento_grave": 0.15},
    "🐊Jacaré": {"dano_min": 8, "dano_max": 25, "vida": 60, "chance_fuga_base": 0.7, "chance_ferimento_grave": 0.3},
    "🐒Chimpanzé": {"dano_min": 6, "dano_max": 15, "vida": 80, "chance_fuga_base": 0.7},
    "🦍Gorila": {"dano_min": 12, "dano_max": 25, "vida": 100, "chance_fuga_base": 0.3, "chance_ferimento_grave": 0.25},
}

# --- CLASSES DO JOGO ---
class Entidade:
    """Classe base para Jogador e Inimigos."""
    def __init__(self, nome, vida_max, energia_max=0):
        self.nome = nome
        self.vida_max = vida_max
        self.vida = vida_max
        self.energia_max = energia_max
        self.energia = energia_max

    def esta_vivo(self):
        return self.vida > 0

    def sofrer_dano(self, dano):
        self.vida = max(0, self.vida - dano)
        return dano

    def curar(self, quantidade):
        self.vida = min(self.vida + quantidade, self.vida_max)
        return quantidade

    def recuperar_energia(self, quantidade):
        self.energia = min(self.energia + quantidade, self.energia_max)
        return quantidade

class Jogador(Entidade):
    """Representa o jogador principal."""
    def __init__(self, nome="Aventureiro(a)"):
        super().__init__(nome, VIDA_MAXIMA_JOGADOR, ENERGIA_MAXIMA_JOGADOR)
        self.mochila = []
        self.pontuacao = 0
        self.abrigo_construido = False
        self.dias_passados = 1
        self.acoes_no_dia = 0
        self.encontrou_saida = False
        self.historico_acoes = {1: []}

        # Status de saúde
        self.status_envenenado = False
        self.status_ferimento_grave = False
        self.status_doente = False
    
    def adicionar_historico(self, mensagem):
        """Adiciona uma mensagem ao histórico de ações do dia atual."""
        self.historico_acoes.setdefault(self.dias_passados, []).append(mensagem)

    def adicionar_item_mochila(self, item_nome):
        """Tenta adicionar um item à mochila."""
        if len(self.mochila) >= MOCHILA_MAX_CAPACIDADE:
            return False
        self.mochila.append(item_nome)
        return True

    def calcular_protecao_total(self):
        """Calcula o valor total de proteção física que o jogador possui na mochila."""
        return sum(DADOS_ITENS[item]["protecao"] for item in self.mochila if DADOS_ITENS.get(item, {}).get("tipo") == "protecao")

    def escolher_melhor_arma(self):
        """Retorna a melhor arma na mochila, se houver."""
        armas_possuidas = [item for item in self.mochila if DADOS_ITENS.get(item, {}).get("tipo") == "arma"]
        if armas_possuidas:
            return max(armas_possuidas, key=lambda x: DADOS_ITENS[x]["dano_max"])
        return None # Retorna None se não houver armas

    def usar_arma_em_combate(self):
        """Calcula o dano de ataque usando a melhor arma disponível."""
        arma = self.escolher_melhor_arma()
        if arma:
            dano = random.randint(DADOS_ITENS[arma]["dano_min"], DADOS_ITENS[arma]["dano_max"])
            return dano, arma
        return random.randint(5, 10), "mãos nuas" # Dano base se não tiver arma

    def processar_status_negativos(self):
        """Aplica os efeitos dos status negativos (envenenamento, ferimento, doença) a cada turno/ação."""
        mensagem_status = ""
        if self.status_envenenado:
            dano_veneno = random.randint(2, 5)
            self.vida = max(0, self.vida - dano_veneno)
            mensagem_status += f"\nVocê está envenenado(a) e perdeu {dano_veneno} de vida! 😵"
            self.adicionar_historico(f"Perdeu {dano_veneno} de vida devido ao envenenamento.")

        if self.status_ferimento_grave:
            dano_ferimento = random.randint(1, 3)
            self.vida = max(0, self.vida - dano_ferimento)
            mensagem_status += f"\nSeu ferimento grave está sangrando e você perdeu {dano_ferimento} de vida! 🩸"
            self.adicionar_historico(f"Perdeu {dano_ferimento} de vida devido ao ferimento grave.")

        if self.status_doente:
            energia_drenada = random.randint(1, 4)
            self.energia = max(0, self.energia - energia_drenada)
            mensagem_status += f"\nVocê se sente fraco(a) pela doença e perdeu {energia_drenada} de energia! 😩"
            self.adicionar_historico(f"Perdeu {energia_drenada} de energia devido à doença.")
        return mensagem_status

    def processar_consumo_item(self, item_nome):
        """Aplica os efeitos de consumo de um item e remove-o da mochila."""
        item_data = DADOS_ITENS[item_nome]
        
        vida_recuperada = 0
        if "vida_recuperada" in item_data:
            if isinstance(item_data["vida_recuperada"], tuple):
                vida_recuperada = random.randint(*item_data["vida_recuperada"])
            else:
                vida_recuperada = item_data["vida_recuperada"]
        
        energia_recuperada = item_data.get("energia_recuperada", 0)

        self.curar(vida_recuperada)
        self.recuperar_energia(energia_recuperada)
        self.pontuacao += 30 # Pontos fixos por consumir
        
        efeitos_especificos_msg = ""

        if item_data.get("cura_envenenamento") and self.status_envenenado:
            self.status_envenenado = False
            efeitos_especificos_msg += " Você se curou do envenenamento! ✨"
        
        if item_data.get("cura_ferimento_grave") and self.status_ferimento_grave:
            self.status_ferimento_grave = False
            efeitos_especificos_msg += " Seu ferimento grave foi tratado! 💪"

        if item_data.get("cura_doenca") and self.status_doente:
            self.status_doente = False
            efeitos_especificos_msg += " Você se sentiu melhor da doença! 🌟"
        
        # Efeito colateral (Cogumelo Desconhecido)
        if item_data.get("chance_doenca") and random.random() < item_data["chance_doenca"]:
            self.status_doente = True
            efeitos_especificos_msg += " Mas parece que você pegou uma doença estranha... 🤢"
            self.adicionar_historico(f"Você consumiu {item_nome} e ficou doente.")

        self.mochila.remove(item_nome)
        return (f"Você usou o(a) {item_nome}. ❤️ +{vida_recuperada} vida, ⚡ +{energia_recuperada} energia, "
                f"⭐ +30 pontos!" + efeitos_especificos_msg)

class Animal(Entidade):
    """Representa um animal selvagem (inimigo)."""
    def __init__(self, nome):
        data = DADOS_ANIMAIS[nome]
        super().__init__(nome, data["vida"])
        self.dano_min = data["dano_min"]
        self.dano_max = data["dano_max"]
        self.chance_fuga_base = data["chance_fuga_base"]
        self.chance_envenenamento = data.get("chance_envenenamento", 0)
        self.chance_ferimento_grave = data.get("chance_ferimento_grave", 0)

    def atacar(self):
        return random.randint(self.dano_min, self.dano_max)

# --- FUNÇÕES DE UTILIDADE E INTERFACE ---
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

def desenhar_intro(jogador):
    """Exibe a tela de introdução do jogo e coleta o nome do jogador."""
    clear_screen()
    print("===================================")
    print("    🌲 SOBREVIVÊNCIA NA FLORESTA 🌳     ")
    print("===================================\n")
    print("Você está perdido em uma floresta e precisa sobreviver. 🧭")
    print("Coletar recursos, montar um abrigo, explorar e fugir de animais selvagens. 🦊🐻🐍")
    print("Você também pode encontrar armas para se defender. 🗡️🛡️")
    print("A comida encontrada pode ser comida na hora ou guardada para depois. 🍎🌰")
    print("O tempo passa a cada ação. Gerencie seus dias para não se exaurir. ☀️🌙")
    print("Construa um abrigo para poder descansar e recuperar suas forças! 🏕️")
    print("Cuidado com os perigos ocultos: você pode ser envenenado(a), se ferir gravemente ou ficar doente!")
    print(f"Sua meta é acumular {PONTUACAO_MAXIMA_VITORIA} pontos ou encontrar o caminho de volta para casa. 🏠\n")
    print("--- Controles ---")
    print("1️⃣ - Buscar comida | 2️⃣ - Montar abrigo | 3️⃣ - Explorar")
    print("4️⃣ - Dormir (se tiver abrigo) | 🇺 - Usar item da mochila | 🇸 - Sair do jogo")
    print("Durante decisão: (C) Comer / (G) Guardar | Durante combate: (A) Atacar / (D) Defender / (F) Fugir")
    print("-----------------\n")
    
    nome_digitado = input("Antes de começar, digite seu nome (ou ENTER para 'Aventureiro(a)'): ").strip()
    if nome_digitado:
        jogador.nome = nome_digitado
    
    input(f"\nBem-vindo(a), {jogador.nome}! Pressione ENTER para começar sua jornada... ▶️")

def desenhar_fim(jogador, mensagem_final_tipo):
    """Exibe a tela final do jogo com base no resultado."""
    clear_screen()
    print("===================================")
    print("         FIM DE JOGO             ")
    print("===================================\n")
    
    if mensagem_final_tipo == "vitoria":
        print(f"🎉 Parabéns, {jogador.nome}! Você sobreviveu e encontrou o caminho de volta para casa! 🏡✨")
        print(f"Sua vasta experiência na floresta te guiou até a civilização em {jogador.dias_passados} dias!")
    elif mensagem_final_tipo == "saida":
        print(f"Você decidiu sair do jogo, {jogador.nome}. Até a próxima aventura! 👋")
    elif mensagem_final_tipo == "derrota_energia":
        print(f"⚡ {jogador.nome}, você ficou completamente exausto(a) e não conseguiu mais se mover. A floresta te consumiu. 😵")
    else: # derrota por vida
        print(f"💀 {jogador.nome}, você sucumbiu aos perigos da floresta. Fim de jogo. 🥀")
    
    print(f"\nSua pontuação final: ⭐ {jogador.pontuacao}")
    print("-----------------------------------\n")
    print("\n--- Diário de Bordo da Sua Jornada ---")
    if jogador.historico_acoes:
        for dia, eventos_do_dia in sorted(jogador.historico_acoes.items()):
            print(f"\n--- Dia {dia} ---")
            print("   " + "\n   ".join(eventos_do_dia) if eventos_do_dia else "   Nenhum evento registrado neste dia.")
    else:
        print("Não há registros de sua jornada.")
    print("-------------------------------------\n")
    input("Pressione ENTER para sair. 🚪")
    sys.exit()

def mostrar_status(jogador, inimigo_atual=None):
    """Exibe o status atual do jogador e do inimigo (se houver)."""
    print("--- Status do Jogador ---")
    print(f"👤 Nome: {jogador.nome}")
    print(f"🗓️ Dia: {jogador.dias_passados} | ⏰ Ações: {jogador.acoes_no_dia}/{ACOES_POR_DIA}")
    print(f"❤️ Vida: {jogador.vida}/{VIDA_MAXIMA_JOGADOR} | ⚡ Energia: {jogador.energia}/{ENERGIA_MAXIMA_JOGADOR}")
    print(f"⭐ Pontos: {jogador.pontuacao}")
    
    protecao_total = jogador.calcular_protecao_total()
    if protecao_total > 0:
        print(f"🛡️ Proteção Física: {protecao_total}")

    condicoes_atuais = []
    if jogador.status_envenenado:
        condicoes_atuais.append("☠️ Envenenado!")
    if jogador.status_ferimento_grave:
        condicoes_atuais.append("🩹 Ferimento Grave!")
    if jogador.status_doente:
        condicoes_atuais.append("🤢 Doente!")
    
    if condicoes_atuais:
        print("🚨 Condições: " + " | ".join(condicoes_atuais))

    print("🎒 Mochila: " + (", ".join(jogador.mochila) if jogador.mochila else "Vazia"))
    print("-------------------------")

    if inimigo_atual:
        print(f"👾 Vida do {inimigo_atual.nome}: {inimigo_atual.vida}/{DADOS_ANIMAIS[inimigo_atual.nome]['vida']}")

# --- LÓGICA DE AÇÕES DO JOGADOR ---
def acao_buscar_comida(jogador, game_state):
    """Lógica para a ação de buscar comida."""
    mensagem_acao_local = ""
    frames_buscar = ["Buscando  .", "Buscando ..", "Buscando ..."]
    show_animation(frames_buscar, delay=0.3, message="🌳 Procurando por comida...")

    jogador.acoes_no_dia += 1

    chance_encontrar = CHANCE_BASE_COMIDA * (0.6 if jogador.abrigo_construido else 1.0)
    
    if random.random() < chance_encontrar:
        comidas_disponiveis = [item for item, data in DADOS_ITENS.items() if data["tipo"] == "comida"]
        
        item_nome = random.choice(comidas_disponiveis) # Escolhe uma comida base
        if random.random() < 0.15: # 15% de chance de ser um cogumelo desconhecido
            item_nome = "Cogumelo Desconhecido"
        
        item_data = DADOS_ITENS[item_nome]
        
        vida_ganho_str = ""
        if isinstance(item_data["vida_recuperada"], tuple):
            vida_ganho = random.randint(*item_data["vida_recuperada"])
            vida_ganho_str = f"({vida_ganho})"
        else:
            vida_ganho = item_data["vida_recuperada"]
            vida_ganho_str = f"+{vida_ganho}"

        energia_ganho = item_data["energia_recuperada"]
        jogador.adicionar_historico(f"Você encontrou comida ({item_nome}).")
        mensagem_acao_local = (f"Você encontrou comida: {item_nome} (❤️ {vida_ganho_str} vida, ⚡ +{energia_ganho} energia).\n"
                               "Deseja (C) Comer agora ou (G) Guardar na mochila? (C/G) ❓")
        
        game_state["item_a_processar"] = item_nome
        game_state["estado"] = "ESPERA_COMIDA" # Transita para o estado de espera por decisão
        return mensagem_acao_local
    else:
        energia_ganho = 10
        vida_ganho = random.randint(3, 8)
        jogador.energia = min(jogador.energia + energia_ganho, ENERGIA_MAXIMA_JOGADOR)
        jogador.vida = min(jogador.vida + vida_ganho, VIDA_MAXIMA_JOGADOR)
        jogador.pontuacao += 40
        jogador.adicionar_historico(f"Você buscou por comida, mas não encontrou nada de valor.")
        mensagem_acao_local = f"Você buscou, mas não encontrou comida. Ganhou ⚡ +{energia_ganho} energia e ❤️ +{vida_ganho} vida pelo esforço. ⭐ +40 pontos!"
        game_state["item_a_processar"] = None
        game_state["estado"] = "JOGANDO"
        return mensagem_acao_local

def acao_montar_abrigo(jogador, game_state):
    """Lógica para a ação de montar um abrigo."""
    mensagem_acao_local = ""
    if jogador.abrigo_construido:
        jogador.adicionar_historico(f"Você tentou construir um abrigo novamente, mas já tinha um.")
        mensagem_acao_local = "Você já montou o abrigo, não pode construir novamente. 🏕️"
        # Não gasta ação extra se já tem abrigo, mas informa
        return mensagem_acao_local

    if jogador.energia < CUSTO_ENERGIA_ABRIGO:
        jogador.adicionar_historico(f"Você tentou montar um abrigo, mas não tinha energia suficiente.")
        mensagem_acao_local = f"⚡ Energia insuficiente para montar o abrigo! Você precisa de {CUSTO_ENERGIA_ABRIGO} de energia."
        # Não gasta ação se não tem energia suficiente
        return mensagem_acao_local
    
    frames_abrigo = ["Construindo [.]", "Construindo [..]", "Construindo [...]",
                     "Construindo [....]", "Construindo [.....]", "Construindo [✓]"]
    show_animation(frames_abrigo, delay=0.2, message="🛠️ Montando o abrigo...")

    jogador.energia -= CUSTO_ENERGIA_ABRIGO
    jogador.pontuacao += 30
    jogador.abrigo_construido = True
    jogador.acoes_no_dia += 1
    jogador.adicionar_historico(f"Você montou um abrigo seguro e descansou.")
    mensagem_acao_local = f"Você montou um abrigo e descansou um pouco. 😴 (-{CUSTO_ENERGIA_ABRIGO} energia, ⭐ +30 pontos)"
    return mensagem_acao_local

def acao_explorar(jogador, game_state):
    """Lógica para a ação de explorar a floresta."""
    mensagem_acao_local = ""
    custo_energia = 15
    if jogador.energia < custo_energia:
        jogador.adicionar_historico(f"Você tentou explorar, mas estava muito exausto.")
        mensagem_acao_local = "⚡ Energia insuficiente para explorar!"
        return mensagem_acao_local # Não permite a ação de exploração

    jogador.energia -= custo_energia
    jogador.acoes_no_dia += 1

    frames_explorar = [" Explorando...", "|--|   .--|", "|  | /   |", "\\--/----|", "   ?     !"]
    show_animation(frames_explorar, delay=0.25, message="🗺️ Explorando a área...")
    
    chance_comida_explorar = CHANCE_BASE_COMIDA * (0.6 if jogador.abrigo_construido else 1.0)
    chance_caminho = min(0.10, jogador.pontuacao / PONTUACAO_MAXIMA_VITORIA * 0.10)

    evento = random.choices(
        population=["animal", "nada", "comida", "item_medico", "item_protecao", "armamento", "caminho_de_casa"],
        weights=[0.3, 0.15, chance_comida_explorar, 0.08, 0.07, 0.1, chance_caminho],
        k=1,
    )[0]
    
    if evento == "caminho_de_casa":
        jogador.encontrou_saida = True
        mensagem_acao_local = "Após muita exploração, você avista uma trilha conhecida! 🏞️ Parece que você encontrou o caminho de volta para casa! 🎉"
        jogador.adicionar_historico(f"Após vasta exploração, você encontrou o caminho de casa!")
    elif evento == "animal":
        animal_nome = random.choice(list(DADOS_ANIMAIS.keys()))
        game_state["inimigo_atual"] = Animal(animal_nome) # Cria uma instância do animal
        game_state["estado"] = "COMBATE"
        mensagem_acao_local = f"Você encontrou um {animal_nome}! 😱 Prepare-se para lutar!"
        jogador.adicionar_historico(f"Você foi surpreendido por um(a) {animal_nome} e entrou em combate!")
    elif evento == "comida":
        # Reutiliza a lógica de buscar_comida. A mensagem e estado serão definidos lá.
        mensagem_acao_local = acao_buscar_comida(jogador, game_state)
    else: # Itens ou nada
        item_tipo_map = {
            "item_medico": "medico",
            "item_protecao": "protecao",
            "armamento": "arma"
        }
        tipo_item_encontrado = item_tipo_map.get(evento)

        if tipo_item_encontrado:
            possiveis_itens = [item for item, data in DADOS_ITENS.items() if data["tipo"] == tipo_item_encontrado]
            # Excluir Cogumelo Desconhecido de item_medico para evitar que apareça aqui
            if tipo_item_encontrado == "medico":
                possiveis_itens = [item for item in possiveis_itens if item != "Cogumelo Desconhecido"]

            if possiveis_itens:
                item_encontrado = random.choice(possiveis_itens)
                if jogador.adicionar_item_mochila(item_encontrado):
                    pontuacao_extra = {"medico": 25, "protecao": 35, "arma": 40}.get(tipo_item_encontrado, 0)
                    jogador.pontuacao += pontuacao_extra
                    mensagem_acao_local = f"Você encontrou um item: {item_encontrado}! ({tipo_item_encontrado.capitalize()}) ⭐ +{pontuacao_extra} pontos!"
                    jogador.adicionar_historico(f"Você encontrou um item de {tipo_item_encontrado}: {item_encontrado}.")
                else:
                    mensagem_acao_local = f"Você encontrou um item: {item_encontrado}, mas sua mochila está cheia. 🎒🚫"
                    jogador.adicionar_historico(f"Você encontrou um item de {tipo_item_encontrado} ({item_encontrado}), mas sua mochila estava cheia.")
            else:
                mensagem_acao_local = "Você explorou mas não encontrou nada relevante. 🤷"
                jogador.adicionar_historico(f"Você explorou a área, mas não encontrou nada de especial.")
        else: # evento == "nada"
            mensagem_acao_local = "Você explorou mas não encontrou nada relevante. 🤷"
            jogador.adicionar_historico(f"Você explorou a área, mas não encontrou nada de especial.")
    
    # Se o estado não mudou para COMBATE ou ESPERA_COMIDA, volta para JOGANDO
    if game_state["estado"] not in ["COMBATE", "ESPERA_COMIDA"]:
        game_state["estado"] = "JOGANDO"
    return mensagem_acao_local

def acao_dormir(jogador, game_state):
    """Lógica para a ação de dormir e passar o dia."""
    mensagem_acao_local = ""
    if not jogador.abrigo_construido:
        jogador.adicionar_historico(f"Você tentou dormir, mas não tinha um abrigo seguro.")
        mensagem_acao_local = "Você não tem um abrigo seguro para dormir. Encontre um local ou construa um! 🏕️"
        # Não gasta ação para tentativa falha
        return mensagem_acao_local

    frames_dormir = ["Zzz .", "Zzz ..", "Zzz ...", "Zzz .", "Zzz ..", "Zzz ...", "🌄 Acordando..."]
    show_animation(frames_dormir, delay=0.3, message="😴 Você está dormindo...")

    jogador.acoes_no_dia = 0 # Reseta ações para o novo dia
    jogador.dias_passados += 1 # Avança o dia

    energia_recuperada = REGEN_ENERGIA_SONO_ABRIGO
    vida_recuperada = REGEN_VIDA_SONO_ABRIGO
    
    jogador.recuperar_energia(energia_recuperada)
    jogador.curar(vida_recuperada)
    
    sono_cura_mensagem = ""
    if jogador.status_doente and random.random() < 0.3: # 30% de chance de melhorar da doença ao dormir
        jogador.status_doente = False
        sono_cura_mensagem += " Você se sentiu um pouco melhor da doença. "
    
    jogador.adicionar_historico(f"Você dormiu em seu abrigo seguro e se recuperou bem.")
    mensagem_acao_local = (f"Você dormiu e um novo dia começou! ☀️"
                     f" ❤️ +{vida_recuperada} vida, ⚡ +{energia_recuperada} energia." + sono_cura_mensagem)
    game_state["estado"] = "JOGANDO"
    return mensagem_acao_local

def acao_usar_item_mochila(jogador, game_state):
    """Lógica para usar um item da mochila."""
    mensagem_acao_local = ""
    itens_usaveis = [item for item in jogador.mochila if DADOS_ITENS.get(item, {}).get("tipo") in ["comida", "medico", "utilitario"]]

    if not itens_usaveis:
        mensagem_acao_local = "Você não tem itens usáveis na mochila (apenas armas ou proteção). 🤔"
        game_state["estado"] = "JOGANDO" # Volta para o estado de jogo normal
        return mensagem_acao_local

    game_state["estado"] = "ESPERA_USAR_ITEM"
    return "Escolha um item para usar:"

def gerenciar_combate(jogador, inimigo_atual, game_state):
    """Gerencia o combate turno a turno."""
    mensagem_combate_turno = ""
    clear_screen()
    mostrar_status(jogador, inimigo_atual)
    
    print("\nEscolha sua ação:")
    print("   (A) Atacar")
    print("   (D) Defender")
    print("   (F) Fugir")

    escolha_combate = input("Sua ação: ").strip().upper()
    dano_defesa = 0

    if escolha_combate == 'A':
        dano_causado, arma_usada = jogador.usar_arma_em_combate()
        inimigo_atual.sofrer_dano(dano_causado)
        jogador.pontuacao += 5
        mensagem_combate_turno += f"Você ataca com seu(sua) {arma_usada}, causando {dano_causado} de dano! 💥"
        jogador.adicionar_historico(f"Você atacou o(a) {inimigo_atual.nome} com {arma_usada}, causando {dano_causado} de dano.")

    elif escolha_combate == 'D':
        energia_gasta = 5
        if jogador.energia >= energia_gasta:
            jogador.energia -= energia_gasta
            dano_defesa = random.randint(10, 20)
            mensagem_combate_turno += f"Você se defende, reduzindo o próximo dano recebido em {dano_defesa}. 🛡️ (-{energia_gasta} energia)"
            jogador.adicionar_historico(f"Você se defendeu do ataque do(a) {inimigo_atual.nome}.")
        else:
            mensagem_combate_turno = "⚡ Energia insuficiente para defender! Você fica vulnerável."
            jogador.adicionar_historico(f"Você tentou se defender do(a) {inimigo_atual.nome}, mas estava sem energia.")

    elif escolha_combate == 'F':
        custo_energia_fuga = 10
        if jogador.energia >= custo_energia_fuga:
            jogador.energia -= custo_energia_fuga
            chance_fuga = inimigo_atual.chance_fuga_base + (jogador.vida / VIDA_MAXIMA_JOGADOR * 0.2)
            
            frames_fuga = ["Correndo   . ", "Correndo ..", "Correndo ... 🏃", "Fugindo!"]
            show_animation(frames_fuga, delay=0.15, message="Tentando fugir...")

            if random.random() < chance_fuga:
                mensagem_combate_turno = f"Você conseguiu fugir do(a) {inimigo_atual.nome}! 💨 (-{custo_energia_fuga} energia)"
                jogador.adicionar_historico(f"Você conseguiu fugir do(a) {inimigo_atual.nome}!")
                game_state["estado"] = "JOGANDO"
                game_state["inimigo_atual"] = None
                jogador.acoes_no_dia += 1 # Fuga gasta uma ação
                return mensagem_combate_turno
            else:
                dano_retaliacao = inimigo_atual.atacar() // 2 # Sofre dano de retaliação
                jogador.sofrer_dano(dano_retaliacao)
                mensagem_combate_turno = f"Você tentou fugir, mas falhou! 😬 O(a) {inimigo_atual.nome} não te deixa escapar! (-{custo_energia_fuga} energia). Você sofreu {dano_retaliacao} de dano de retaliação! 💔"
                jogador.adicionar_historico(f"Você tentou fugir do(a) {inimigo_atual.nome}, mas falhou e sofreu dano.")
        else:
            mensagem_combate_turno = "⚡ Energia insuficiente para tentar a fuga! Você precisa de mais energia."
            jogador.adicionar_historico(f"Você tentou fugir do(a) {inimigo_atual.nome}, mas estava sem energia.")
    else:
        mensagem_combate_turno = "Comando inválido no combate. Tente (A)tacar, (D)efender ou (F)Fugir."
        # Não gasta ação para comando inválido em combate, apenas informa

    if not inimigo_atual.esta_vivo():
        jogador.pontuacao += 100
        mensagem_combate_turno = f"Você derrotou o(a) {inimigo_atual.nome}! 🎉 (+100 pontos)"
        jogador.adicionar_historico(f"Você derrotou o(a) {inimigo_atual.nome} em combate!")
        game_state["estado"] = "JOGANDO"
        game_state["inimigo_atual"] = None
        jogador.acoes_no_dia += 1 # Derrotar o inimigo gasta uma ação
        return mensagem_combate_turno

    # Ataque do animal (se o combate não terminou)
    dano_animal = inimigo_atual.atacar()
    protecao_total = jogador.calcular_protecao_total()
    dano_animal_final = max(0, dano_animal - dano_defesa - protecao_total) # Dano real após defesa e proteção
    
    jogador.sofrer_dano(dano_animal_final)
    mensagem_combate_turno += f"\nO(a) {inimigo_atual.nome} ataca, causando {dano_animal_final} de dano a você! 🩸"
    if protecao_total > 0:
        mensagem_combate_turno += f" (Sua proteção física reduziu {protecao_total} de dano!)"

    jogador.adicionar_historico(f"O(a) {inimigo_atual.nome} te atacou, causando {dano_animal_final} de dano.")
    jogador.pontuacao = max(0, jogador.pontuacao - 5) # Perde pontos por sofrer dano

    # APLICAÇÃO DE STATUS NEGATIVOS APÓS O ATAQUE DO ANIMAL
    if random.random() < inimigo_atual.chance_envenenamento:
        if not jogador.status_envenenado:
            jogador.status_envenenado = True
            mensagem_combate_turno += f" Você foi envenenado(a) pelo(a) {inimigo_atual.nome}! ☠️"
            jogador.adicionar_historico(f"Você foi envenenado(a) pelo(a) {inimigo_atual.nome}.")
    
    if random.random() < inimigo_atual.chance_ferimento_grave:
        if not jogador.status_ferimento_grave:
            jogador.status_ferimento_grave = True
            mensagem_combate_turno += f" Você sofreu um ferimento grave! 🩹"
            jogador.adicionar_historico(f"Você sofreu um ferimento grave em combate contra o(a) {inimigo_atual.nome}.")
    
    frames_combate = [f"Você vs {inimigo_atual.nome}", "   ⚔️", "   💥", "   ⚔️", f"({inimigo_atual.nome} ataca!)"]
    show_animation(frames_combate, delay=0.2, message="⚔️ Combate em andamento!")
    
    return mensagem_combate_turno

def verificar_fim_de_jogo(jogador, game_state):
    """Verifica as condições de vitória ou derrota."""
    if not jogador.esta_vivo():
        game_state["mensagem_final_tipo"] = "derrota"
        jogador.adicionar_historico(f"Você sucumbiu aos ferimentos. Fim da jornada.")
        game_state["estado"] = "FIM"
        return True
    if jogador.energia <= 0:
        game_state["mensagem_final_tipo"] = "derrota_energia"
        jogador.adicionar_historico(f"Você ficou completamente exausto(a) e não conseguiu mais continuar. Fim da jornada.")
        game_state["estado"] = "FIM"
        return True
    if jogador.pontuacao >= PONTUACAO_MAXIMA_VITORIA or jogador.encontrou_saida:
        jogador.encontrou_saida = True # Garante que a flag esteja true para a mensagem final
        game_state["mensagem_final_tipo"] = "vitoria"
        game_state["estado"] = "FIM"
        return True
    return False

# --- LOOP PRINCIPAL DO JOGO ---
def jogar():
    """Função principal que controla o fluxo do jogo."""
    jogador = Jogador()
    # Dicionário para gerenciar o estado do jogo de forma centralizada
    game_state = {
        "estado": "INTRO",
        "mensagem_acao": "",
        "item_a_processar": None,
        "inimigo_atual": None,
        "mensagem_final_tipo": ""
    }

    desenhar_intro(jogador)
    game_state["estado"] = "JOGANDO"
    game_state["mensagem_acao"] = "Sua jornada na floresta começa agora! Boa sorte!"

    while True:
        clear_screen()
        mostrar_status(jogador, game_state["inimigo_atual"])
        
        # Processa status negativos ANTES de verificar o fim do jogo
        status_msg = jogador.processar_status_negativos()
        if status_msg:
            game_state["mensagem_acao"] += status_msg
        
        if verificar_fim_de_jogo(jogador, game_state):
            desenhar_fim(jogador, game_state["mensagem_final_tipo"])
            break # Sai do loop principal do jogo

        # --- Lógica de Fim de Dia ---
        if jogador.acoes_no_dia >= ACOES_POR_DIA and game_state["estado"] == "JOGANDO":
            game_state["mensagem_acao"] += "\nO dia terminou! Você está exausto e precisa dormir. 😴"
            jogador.adicionar_historico("O dia terminou. Você precisa descansar.")
            
            if not jogador.abrigo_construido:
                jogador.vida = max(0, jogador.vida - 10)
                jogador.energia = max(0, jogador.energia - 15)
                game_state["mensagem_acao"] += "\nVocê não tem um abrigo seguro para dormir. Perdeu mais vida e energia por não descansar adequadamente! 💀"
                jogador.adicionar_historico("Você não conseguiu dormir em segurança e sofreu as consequências.")
            
            # Avança o dia e reinicia as ações, independentemente de ter abrigo ou não
            # A função dormir() já faz isso quando chamada explicitamente.
            # Aqui, para o fim de dia automático, só avançamos o dia e resetamos ações.
            jogador.dias_passados += 1
            jogador.acoes_no_dia = 0 # Reinicia as ações para o novo dia
            
            # Verifica o fim do jogo novamente após a penalidade de exaustão
            if verificar_fim_de_jogo(jogador, game_state):
                desenhar_fim(jogador, game_state["mensagem_final_tipo"])
                break

        # Exibe mensagens de ação acumuladas
        print(f"\n{game_state['mensagem_acao']}\n")
        game_state["mensagem_acao"] = "" # Limpa a mensagem após exibir

        # --- Lógica de Estados do Jogo ---
        if game_state["estado"] == "JOGANDO":
            print("--- Escolha uma ação ---")
            print("1. Buscar comida 🍎")
            print("2. Montar abrigo 🏕️")
            print("3. Explorar 🗺️")
            if jogador.abrigo_construido:
                print("4. Dormir 😴")
            if jogador.mochila: # Só mostra a opção se houver algo na mochila
                print("U. Usar item da mochila 🎒")
            print("S. Sair do jogo 🚪")
            
            escolha = input("Sua escolha: ").strip().lower()

            if escolha == '1':
                game_state["mensagem_acao"] = acao_buscar_comida(jogador, game_state)
            elif escolha == '2':
                game_state["mensagem_acao"] = acao_montar_abrigo(jogador, game_state)
            elif escolha == '3':
                game_state["mensagem_acao"] = acao_explorar(jogador, game_state)
            elif escolha == '4':
                if jogador.abrigo_construido:
                    game_state["mensagem_acao"] = acao_dormir(jogador, game_state)
                else:
                    game_state["mensagem_acao"] = "Você precisa de um abrigo para dormir. 🏕️"
                    jogador.adicionar_historico("Tentou dormir sem abrigo.")
            elif escolha == 'u':
                game_state["mensagem_acao"] = acao_usar_item_mochila(jogador, game_state)
            elif escolha == 's':
                game_state["mensagem_final_tipo"] = "saida"
                game_state["estado"] = "FIM"
                # A verificação de fim de jogo no início do loop cuidará da saída.
            else:
                game_state["mensagem_acao"] = "Comando inválido. Tente novamente."
                jogador.adicionar_historico("Erro: Comando inválido no menu principal.")
            
        elif game_state["estado"] == "ESPERA_COMIDA":
            print(game_state["mensagem_acao"]) # Reexibe a pergunta de comida
            escolha_comida = input("Deseja (C) Comer agora ou (G) Guardar na mochila? (C/G): ").strip().lower()
            
            if escolha_comida == 'c':
                game_state["mensagem_acao"] = jogador.processar_consumo_item(game_state["item_a_processar"])
                jogador.acoes_no_dia += 1
                game_state["item_a_processar"] = None
                game_state["estado"] = "JOGANDO"
            elif escolha_comida == 'g':
                if jogador.adicionar_item_mochila(game_state["item_a_processar"]):
                    game_state["mensagem_acao"] = f"Você guardou o(a) {game_state['item_a_processar']} na mochila. 🎒"
                    jogador.adicionar_historico(f"Você guardou um(a) {game_state['item_a_processar']} na mochila.")
                else:
                    game_state["mensagem_acao"] = f"Sua mochila está cheia! Você teve que consumir o(a) {game_state['item_a_processar']}. "
                    game_state["mensagem_acao"] += jogador.processar_consumo_item(game_state["item_a_processar"])
                
                jogador.acoes_no_dia += 1
                game_state["item_a_processar"] = None
                game_state["estado"] = "JOGANDO"
            else:
                game_state["mensagem_acao"] = "Escolha inválida. Digite 'C' para Comer ou 'G' para Guardar."
                # Permanece em ESPERA_COMIDA para nova tentativa

        elif game_state["estado"] == "ESPERA_USAR_ITEM":
            print("--- Itens Usáveis na Mochila ---")
            itens_usaveis = [item for item in jogador.mochila if DADOS_ITENS.get(item, {}).get("tipo") in ["comida", "medico", "utilitario"]]
            for i, item in enumerate(itens_usaveis):
                print(f"{i+1}. {item}")
            print("0. Voltar")
            
            try:
                escolha_item = int(input("Escolha o número do item para usar (0 para voltar): "))
                if escolha_item == 0:
                    game_state["mensagem_acao"] = "Você decidiu não usar nenhum item."
                    jogador.adicionar_historico("Decidiu não usar item da mochila.")
                    game_state["estado"] = "JOGANDO"
                elif 1 <= escolha_item <= len(itens_usaveis):
                    item_nome = itens_usaveis[escolha_item - 1]
                    game_state["mensagem_acao"] = jogador.processar_consumo_item(item_nome)
                    jogador.acoes_no_dia += 1
                    game_state["estado"] = "JOGANDO"
                else:
                    game_state["mensagem_acao"] = "Número de item inválido. Tente novamente."
            except ValueError:
                game_state["mensagem_acao"] = "Entrada inválida. Digite um número."
            # Permanece em ESPERA_USAR_ITEM para nova tentativa se a entrada for inválida

        elif game_state["estado"] == "COMBATE":
            game_state["mensagem_acao"] = gerenciar_combate(jogador, game_state["inimigo_atual"], game_state)
            # A função gerenciar_combate já atualiza o estado do jogo quando o combate termina.

# Executa o jogo
if __name__ == "__main__":
    jogar()