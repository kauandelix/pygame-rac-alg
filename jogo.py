import random
import sys

# Inicialização do pygame
pygame.init()
pygame.font.init()

# Constantes
LARGURA, ALTURA = 800, 600
VIDA_MAXIMA = 100
ENERGIA_MAXIMA = 100
PONTUACAO_MAXIMA = 500
MOCHILA_MAX = 5  # Limite de itens na mochila
ENERGIA_CUSTO_ABRIGO_BASE = 20
PORCENTAGEM_COMIDA_BASE = 0.6  # chance base de encontrar comida ao buscar/explorar

# Cores para UI limpa e elegante
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (34, 139, 34)
VERMELHO = (200, 30, 30)
AMARELO = (255, 255, 100)
AZUL = (100, 149, 237)
CINZA = (230, 230, 230)

# Configuração da tela
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Sobrevivência na Floresta")

# Fontes (usando tons neutros e bem legíveis)
font_titulo = pygame.font.SysFont("arial", 48, bold=True)
font_subtitulo = pygame.font.SysFont("arial", 28)
font_texto = pygame.font.SysFont("arial", 22)
font_pequena = pygame.font.SysFont("arial", 16)

# Variáveis globais do jogador
vida = VIDA_MAXIMA
energia = ENERGIA_MAXIMA
mochila = []
pontuacao = 0
encontrou_saida = False
abrigo_construido = False  # controla se abrigo já foi construído

# Estados do jogo
INTRO = 0
JOGANDO = 1
ESPERA_ESCOLHA_COMIDA = 2
ESPERA_ESCOLHA_USAR_ITEM = 3
FIM = 4

estado_jogo = INTRO
mensagem_final = ""

# Dicionário de animais e danos
animais = {
    "Onça": {"dano_min": 15, "dano_max": 60},
    "Cobra": {"dano_min": 10, "dano_max": 30},
    "Lobo": {"dano_min": 20, "dano_max": 65},
    "Arraia": {"dano_min": 9, "dano_max": 28},
}

# Dicionário armas e danos
armas = {
    "Faca": {"dano_min": 15, "dano_max": 65},
    "Arco": {"dano_min": 12, "dano_max": 50},
    "Escopeta": {"dano_min": 40, "dano_max": 90},
}

# Para gerenciar comida encontrada aguardando decisão
comida_espera = None
comida_espera_item_dados = None

# Mensagem atual ação e uso item
mensagem_acao = ""
item_usar_espera = None

def desenhar_texto_multilinha(superficie, texto, fonte, cor, rect, espacamento=6):
    linhas = texto.splitlines()
    y_offset = 0
    for linha in linhas:
        render_texto = fonte.render(linha, True, cor)
        superficie.blit(render_texto, (rect.x, rect.y + y_offset))
        y_offset += render_texto.get_height() + espacamento

def mostrar_status():
    # Fundo branco e sombra leve para área status (clean)
    status_rect = pygame.Rect(10, 10, LARGURA - 20, 140)
    pygame.draw.rect(tela, VERDE, status_rect, border_radius=12)
    pygame.draw.rect(tela, CINZA, status_rect, 2, border_radius=12)

    # Texto cinza escuro para corpo
    texto_vida = font_texto.render(f"Vida: {vida} / {VIDA_MAXIMA}", True, VERMELHO)
    texto_energia = font_texto.render(f"Energia: {energia} / {ENERGIA_MAXIMA}", True, AMARELO)
    texto_pontos = font_texto.render(f"Pontos: {pontuacao}", True, AZUL)
    mochila_texto = font_texto.render("Mochila: " + (", ".join(mochila) if mochila else "Vazia"), True, PRETO)

    tela.blit(texto_vida, (25, 20))
    tela.blit(texto_energia, (25, 50))
    tela.blit(texto_pontos, (25, 80))
    tela.blit(mochila_texto, (25, 110))

def adicionar_item_mochila(item):
    if len(mochila) >= MOCHILA_MAX:
        return False
    mochila.append(item_nome)
    return True

def escolher_arma():
    armas_possuida = [item for item in mochila if item in armas]
    if armas_possuida:
        melhor_arma = max(armas_possuida, key=lambda x: armas[x]["dano_max"])
        return melhor_arma
    return None

def usar_arma_defesa():
    arma = escolher_arma()
    if arma:
        dano_arma = random.randint(armas[arma]["dano_min"], armas[arma]["dano_max"])
        return dano_arma, arma
    return 0, None

def consumir_comida(item, ganho_vida, ganho_energia):
    global vida, energia, pontuacao
    vida += ganho_vida
    energia += ganho_energia
    vida = min(vida, VIDA_MAXIMA)
    energia = min(energia, ENERGIA_MAXIMA)
    pontuacao += 30
    return f"Você comeu o(a) {item}. +{ganho_vida} vida, +{ganho_energia} energia, +30 pontos!"

def usar_item_da_mochila(indice):
    global vida, energia, pontuacao, mensagem_acao, mochila, item_usar_espera, estado_jogo
    if indice < 0 or indice >= len(mochila):
        mensagem_acao = "Índice inválido para usar item."
        estado_jogo = JOGANDO
        item_usar_espera = None
        return
    item = mochila[indice]
    if item in armas:
        mensagem_acao = f"O(a) {item} é uma arma e será usada automaticamente para defesa."
    elif item == "Kit de primeiros socorros":
        vida_recuperada = 20
        vida += vida_recuperada
        if vida > VIDA_MAXIMA:
            vida = VIDA_MAXIMA
        mensagem_acao = f"Você usou o(a) {item} e recuperou {vida_recuperada} de vida."
        mochila.pop(indice)
    elif item in ["Fruta", "Nozes", "Raiz comestível"]:
        ganho_vida = random.randint(3, 8)
        ganho_energia = 10
        vida += ganho_vida
        energia += ganho_energia
        if vida > VIDA_MAXIMA:
            vida = VIDA_MAXIMA
        if energia > ENERGIA_MAXIMA:
            energia = ENERGIA_MAXIMA
        mensagem_acao = f"Você comeu o(a) {item} da mochila. +{ganho_vida} vida, +{ganho_energia} energia."
        mochila.pop(indice)
    elif item == "Cordas":
        mensagem_acao = f"Você usou o(a) {item}, mas não há efeito imediato."
        mochila.pop(indice)
    else:
        mensagem_acao = f"Você usou o(a) {item}, mas não teve efeito especial."
        mochila.pop(indice)
    item_usar_espera = None
    estado_jogo = JOGANDO

# Bucando Comida
def buscar_comida():
    global comida_espera, comida_espera_item_dados
    ganho_energia = 10
    ganho_vida = random.randint(3, 8)
    # Reduz chance de encontrar comida se abrigo construído
    if abrigo_construido:
        chance_comida = PORCENTAGEM_COMIDA_BASE * 0.6
    else:
        chance_comida = PORCENTAGEM_COMIDA_BASE

    encontrou_item = random.random() < chance_comida
    if encontrou_item:
        item = random.choice(["Fruta", "Nozes", "Raiz comestível"])
        comida_espera_item_dados = (item, ganho_vida, ganho_energia)
        comida_espera = ("Você encontrou comida: " + item +
                         ".\nDeseja (E) Comer agora ou (G) Guardar na mochila? Pressione E ou G.")
        return comida_espera
    else:
        global vida, energia, pontuacao
        energia += ganho_energia
        vida += ganho_vida
        energia = min(energia, ENERGIA_MAXIMA)
        vida = min(vida, VIDA_MAXIMA)
        pontuacao += 40
        comida_espera = None
        comida_espera_item_dados = None
        return f"Você encontrou comida! +{ganho_energia} energia, +{ganho_vida} vida."

def montar_abrigos():
    global energia, pontuacao, abrigo_construido
    if abrigo_construido:
        return "Você já montou o abrigo, não pode construir novamente."
    custo_energia = int(ENERGIA_CUSTO_ABRIGO_BASE * 1.5)  # custo maior
    if energia < custo_energia:
        adicionar_historico(f"Você tentou montar um abrigo, mas não tinha energia suficiente.")
        mensagem_acao = f"⚡ Energia insuficiente para montar o abrigo! Você precisa de {custo_energia} de energia."
        return
    
    frames_abrigo = ["Construindo [.]", "Construindo [..]", "Construindo [...]",
                     "Construindo [....]", "Construindo [.....]", "Construindo [✓]"]
    show_animation(frames_abrigo, delay=0.2, message="🛠️ Montando o abrigo...")

    energia -= custo_energia
    pontuacao += 20
    abrigo_construido = True
    acoes_no_dia += 1
    adicionar_historico(f"Você montou um abrigo seguro e descansou.")
    mensagem_acao = f"Você montou um abrigo e descansou um pouco. 😴 (-{custo_energia} energia, ⭐ +30 pontos)"

# Exploração
def explorar():
    """Ação de explorar a floresta."""
    global vida, energia, pontuacao, estado_jogo, inimigo_atual, vida_inimigo_atual, encontrou_saida, mensagem_acao, acoes_no_dia, item_a_processar
    
    custo_energia = 15
    if energia < custo_energia:
        adicionar_historico(f"Você tentou explorar, mas estava muito exausto.")
        mensagem_acao = "⚡ Energia insuficiente para explorar!"
        return False # Não permite a ação de exploração
    
    energia -= custo_energia
    # Ajustar chance de comida se abrigo construído
    if abrigo_construido:
        chance_comida = PORCENTAGEM_COMIDA_BASE * 0.6
    else:
        chance_comida = PORCENTAGEM_COMIDA_BASE
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
        ganho_energia = 10
        ganho_vida = random.randint(3, 8)
        item = random.choice(["Fruta", "Nozes", "Raiz comestível"])
        comida_espera_item_dados = (item, ganho_vida, ganho_energia)
        comida_espera = ("Você encontrou comida: " + item +
                         ".\nDeseja (E) Comer agora ou (G) Guardar na mochila? Pressione E ou G.")
        return comida_espera
    elif evento == "item":
        item = random.choice(["Kit de primeiros socorros", "Corda"])
        if adicionar_item_mochila(item):
            pontuacao += 18
            msg = f"Você encontrou um item: {item}! (+18 pontos)"
        else:
            msg = f"Você encontrou um item: {item}, mas sua mochila está cheia."
    elif evento == "armamento":
        item = random.choice(list(armas.keys()))
        if adicionar_item_mochila(item):
            pontuacao += 40
            msg = f"Você encontrou um armamento: {item}! (+40 pontos)"
        else:
            mensagem_acao_combate_turno = "⚡ Energia insuficiente para tentar a fuga! Você precisa de mais energia."
            adicionar_historico(f"Você tentou fugir do(a) {inimigo_atual}, mas estava sem energia.")
    else:
        msg = "Você explorou mas não encontrou nada relevante."
    return msg

def verificar_vitoria_ou_derrota():
    global encontrou_saida, pontuacao, vida
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

# Introdução
def desenhar_intro():
    tela.fill(BRANCO)
    titulo = font_titulo.render("Sobrevivência na Floresta", True, PRETO)
    tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 60))

    texto_introducao = (
        "Você está perdido em uma floresta e precisa sobreviver.\n"
        "Coletar recursos, montar um abrigo, explorar e fugir de animais selvagens.\n"
        "Você também pode encontrar armas para se defender.\n"
        "A comida encontrada pode ser comida na hora ou guardada para depois.\n"
        "Faça escolhas para acumular pontos até encontrar o caminho de casa.\n\n"
        "Controles:\n"
        "1 - Buscar comida\n"
        "2 - Montar abrigo (apenas uma vez)\n"
        "3 - Explorar\n"
        "U - Usar um item da mochila\n\n"
        "Durante decisão: (E) - Comer item, (G) - Guardar na mochila\n\n"
        "Pressione ESPAÇO para começar o jogo."
    )
    rect_texto = pygame.Rect(50, 150, LARGURA - 100, ALTURA - 220)
    desenhar_texto_multilinha(tela, texto_introducao, font_texto, PRETO, rect_texto)

def desenhar_fim(mensagem):
    tela.fill(BRANCO)
    if mensagem == "vitoria":
        texto = "Parabéns! Você sobreviveu e encontrou o caminho de volta para casa!"
        cor = VERDE
    else:
        texto = "Você morreu na floresta. Fim de jogo."
        cor = VERMELHO
    titulo = font_titulo.render("Fim de Jogo", True, cor)
    tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 120))

    rect_texto = pygame.Rect(50, 200, LARGURA - 100, ALTURA - 320)
    desenhar_texto_multilinha(tela, texto, font_texto, cor, rect_texto)

    instrucao = font_pequena.render("Pressione ESC para sair.", True, PRETO)
    tela.blit(instrucao, (LARGURA//2 - instrucao.get_width()//2, ALTURA - 60))

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
                        linhas.append(linha_atual)
                        linha_atual = palavra + " "
                linhas.append(linha_atual)
                y_base = ALTURA - 120
                for i, linha in enumerate(linhas):
                    linha_render = font_pequena.render(linha.strip(), True, BRANCO)
                    tela.blit(linha_render, (20, y_base + i * 22))

            ops_texto = "(Jogo pausado - escolha sobre comida)"
            texto_ops = font_texto.render(ops_texto, True, BRANCO)
            tela.blit(texto_ops, (LARGURA // 2 - texto_ops.get_width() // 2, ALTURA - 80))

        elif estado_jogo == ESPERA_ESCOLHA_USAR_ITEM:
            tela.fill(PRETO)
            mostrar_status()
            instrucao = font_texto.render(
                f"Pressione 1 a {len(mochila)} para usar o item correspondente na mochila.", True, BRANCO
            )
            tela.blit(instrucao, (LARGURA // 2 - instrucao.get_width() // 2, ALTURA - 150))

            y_base = ALTURA - 120
            for i, item in enumerate(mochila):
                linha_texto = f"{i+1} - {item}"
                linha_render = font_pequena.render(linha_texto, True, BRANCO)
                tela.blit(linha_render, (20, y_base + i * 22))

        elif estado_jogo == FIM:
            tela.fill(PRETO)
            desenhar_fim(mensagem_final)

        pygame.display.flip()
        pygame.time.Clock().tick(30)


if __name__ == "__main__":
    main()