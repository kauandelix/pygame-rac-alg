import pygame
import random
import sys

# Inicialização do pygame
pygame.init()
pygame.font.init()

# Constantes
LARGURA, ALTURA = 800, 600 # tela do jogo
VIDA_MAXIMA = 100 # Quantidade de vida
ENERGIA_MAXIMA = 100 # Quantidade de energiq
PONTUACAO_MAXIMA = 500 # pontuação necessária
MOCHILA_MAX = 5  # Limite de itens na mochila
ENERGIA_CUSTO_ABRIGO_BASE = 20 # Energia para contruir abrigo
PORCENTAGEM_COMIDA_BASE = 0.3  # chance base de encontrar comida ao buscar/explorar

# Cores
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

# Fontes
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
    "Onça": {"dano_min": 20, "dano_max": 60},
    "Cobra": {"dano_min": 10, "dano_max": 30},
    "Lobo": {"dano_min": 20, "dano_max": 65},
    "Arraia": {"dano_min": 9, "dano_max": 28},
    "Urso": {"dano_min": 20, "dano_max": 60},
    "Sapo": {"dano_min": 5, "dano_max": 50},
    "Jacaré": {"dano_min": 15, "dano_max": 55},
}

# Dicionário armas e danos
armas = {
    "Faca": {"dano_min": 15, "dano_max": 65},
    "Arco": {"dano_min": 12, "dano_max": 50},
    "Escopeta": {"dano_min": 40, "dano_max": 90},
    "Revolver": {"dano_min": 30, "dano_max": 80},
    "Chinelo de Mãe": {"dano_min": 2, "dano_max": 7},
    "Machado": {"dano_min": 20, "dano_max": 70},
    "Toco de Madeira": {"dano_min": 5, "dano_max": 15},
}

# Para gerenciar comida encontrada aguardando decisão
comida_espera = None
comida_espera_item_dados = None

# Mensagem atual ação e uso item
mensagem_acao = ""
item_usar_espera = None

# Linhas na superficie
def desenhar_texto_multilinha(superficie, texto, fonte, cor, rect, espacamento=6):
    linhas = texto.splitlines()
    y_offset = 0
    for linha in linhas:
        render_texto = fonte.render(linha, True, cor)
        superficie.blit(render_texto, (rect.x, rect.y + y_offset))
        y_offset += render_texto.get_height() + espacamento

# Staus de Vida, Pontuação, Energia e itens da mochila
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

# Add item na mochila
def adicionar_item_mochila(item):
    if len(mochila) >= MOCHILA_MAX:
        return False
    mochila.append(item)
    return True

# Escolher arma
def escolher_arma():
    armas_possuida = [item for item in mochila if item in armas]
    if armas_possuida:
        melhor_arma = max(armas_possuida, key=lambda x: armas[x]["dano_max"])
        return melhor_arma
    return None

# Usar Arma
def usar_arma_defesa():
    arma = escolher_arma()
    if arma:
        dano_arma = random.randint(armas[arma]["dano_min"], armas[arma]["dano_max"])
        return dano_arma, arma
    return 0, None

# Comer
def consumir_comida(item, ganho_vida, ganho_energia):
    global vida, energia, pontuacao
    vida += ganho_vida
    energia += ganho_energia
    vida = min(vida, VIDA_MAXIMA)
    energia = min(energia, ENERGIA_MAXIMA)
    pontuacao += 30
    return f"Você comeu o(a) {item}. +{ganho_vida} vida, +{ganho_energia} energia, +30 pontos!"

# Itens Mochila
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
        vida_recuperada = 30
        vida += vida_recuperada
        if vida > VIDA_MAXIMA:
            vida = VIDA_MAXIMA
        mensagem_acao = f"Você usou o(a) {item} e recuperou {vida_recuperada} de vida."
        mochila.pop(indice)
    elif item in ["Maçã", "Banana", "Laranja", "Uva", "Bergamota", "Jabuticaba", "Raiz comestível", "Nozes", "Morango", "Tomate"]:
        ganho_vida = random.randint(3, 5)
        ganho_energia = 5
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
    ganho_energia = 5
    ganho_vida = random.randint(3, 5)
    # Reduz chance de encontrar comida se abrigo construído
    if abrigo_construido:
        chance_comida = PORCENTAGEM_COMIDA_BASE * 0.3
    else:
        chance_comida = PORCENTAGEM_COMIDA_BASE

    encontrou_item = random.random() < chance_comida
    if encontrou_item:
        item = random.choice(["Maçã", "Banana", "Laranja", "Uva", "Bergamota", "Jabuticaba", "Raiz comestível", "Nozes", "Morango", "Tomate"])
        comida_espera = ("Você encontrou comida: " + item +
                         ".\nDeseja (E) Comer agora ou (G) Guardar na mochila? Pressione E ou G.")
        return comida_espera
    else:
        global vida, energia, pontuacao
        energia += ganho_energia
        vida += ganho_vida
        energia = min(energia, ENERGIA_MAXIMA)
        vida = min(vida, VIDA_MAXIMA)
        pontuacao += 25
        comida_espera = None
        comida_espera_item_dados = None
        return"Você encontrou comida:  + {item} + .\nDeseja (E) Comer agora ou (G) Guardar na mochila? Pressione E ou G."

# Abrigo
def montar_abrigos():
    global energia, pontuacao, abrigo_construido
    if abrigo_construido:
        return "Você já montou o abrigo, não pode construir novamente."
    custo_energia = int(ENERGIA_CUSTO_ABRIGO_BASE * 2.0)  # custo maior
    if energia < custo_energia:
        return "Energia insuficiente para montar o abrigo!"
    energia -= custo_energia
    pontuacao += 10
    abrigo_construido = True
    msg = f"Você montou um abrigo e descansou um pouco. (-{custo_energia} energia, +30 pontos)"
    return msg

# Exploração
def explorar():
    global vida, energia, pontuacao, comida_espera, comida_espera_item_dados
    custo_energia = 15
    if energia < custo_energia:
        return "Energia insuficiente para explorar!"
    energia -= custo_energia
    # Ajustar chance de comida se abrigo construído
    if abrigo_construido:
        chance_comida = PORCENTAGEM_COMIDA_BASE * 0.3
    else:
        chance_comida = PORCENTAGEM_COMIDA_BASE
    evento = random.choices(
        population=["animal", "nada", "comida", "item", "armamento"],
        weights=[0.3, 0.2, chance_comida, 0.1, 0.2],
        k=1,
    )[0]
    if evento == "animal":
        animal = random.choice(list(animais.keys()))
        dano_animal = random.randint(animais[animal]["dano_min"], animais[animal]["dano_max"])
        dano_defesa, arma = usar_arma_defesa()
        dano_final = dano_animal - dano_defesa
        if dano_final < 0:
            dano_final = 0
        vida -= dano_final
        msg = f"Você encontrou um {animal}! Sofreu {dano_final} de dano"
        if arma:
            msg += f", mas defendeu com a {arma} causando dano ao animal."
        msg += "."
        if dano_final > 20:
            pontuacao -= 10
        else:
            pontuacao -= 5
    elif evento == "comida":
        ganho_energia = 5
        ganho_vida = random.randint(3, 5)
        item = random.choice(["Maçã", "Banana", "Laranja", "Uva", "Bergamota", "Jabuticaba", "Raiz comestível", "Nozes", "Morango", "Tomate"])
        comida_espera_item_dados = (item, ganho_vida, ganho_energia)
        comida_espera = ("Você encontrou comida: " + item +
                         ".\nDeseja (E) Comer agora ou (G) Guardar na mochila? Pressione E ou G.")
        return comida_espera
    elif evento == "item":
        item = random.choice(["Kit de primeiros socorros", "Corda"])
        if adicionar_item_mochila(item):
            pontuacao += 5
            msg = f"Você encontrou um item: {item}! (+5 pontos)"
        else:
            msg = f"Você encontrou um item: {item}, mas sua mochila está cheia."
    elif evento == "armamento":
        item = random.choice(list(armas.keys()))
        if adicionar_item_mochila(item):
            pontuacao += 20
            msg = f"Você encontrou um armamento: {item}! (+20 pontos)"
        else:
            msg = f"Você encontrou um armamento: {item}, mas sua mochila está cheia."
    else:
        msg = "Você explorou mas não encontrou nada relevante."
    return msg

# Verificar a vitoria ou derrota
def verificar_vitoria_ou_derrota():
    global encontrou_saida, pontuacao, vida
    if vida <= 0:
        return "derrota"
    if pontuacao >= PONTUACAO_MAXIMA:
        encontrou_saida = True
        return "vitoria"
    return "continuar"

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

# Final
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

# Main
def main():
    global estado_jogo, vida, energia, pontuacao, mochila, mensagem_final
    global comida_espera, comida_espera_item_dados, mensagem_acao, item_usar_espera, abrigo_construido

    relogio = pygame.time.Clock()
    mensagem_acao = ""
    item_usar_espera = None
    abrigo_construido = False

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if estado_jogo == INTRO:
                    if evento.key == pygame.K_SPACE:
                        estado_jogo = JOGANDO
                        mensagem_acao = ""
                elif estado_jogo == JOGANDO:
                    if comida_espera:
                        # Aguarda decisão sobre comida
                        pass
                    elif item_usar_espera:
                        # Aguarda escolha do item a usar
                        pass
                    else:
                        if evento.key == pygame.K_1:
                            resultado = buscar_comida()
                            if comida_espera:
                                estado_jogo = ESPERA_ESCOLHA_COMIDA
                                mensagem_acao = comida_espera
                            else:
                                mensagem_acao = resultado
                        elif evento.key == pygame.K_2:
                            mensagem_acao = montar_abrigos()
                        elif evento.key == pygame.K_3:
                            resultado = explorar()
                            if comida_espera:
                                estado_jogo = ESPERA_ESCOLHA_COMIDA
                                mensagem_acao = comida_espera
                            else:
                                mensagem_acao = resultado
                        elif evento.key == pygame.K_u:
                            if mochila:
                                item_usar_espera = True
                                estado_jogo = ESPERA_ESCOLHA_USAR_ITEM
                                mensagem_acao = f"Pressione a tecla de 1 a {len(mochila)} para usar o item correspondente na mochila."
                            else:
                                mensagem_acao = "Sua mochila está vazia, nada para usar."
                elif estado_jogo == ESPERA_ESCOLHA_COMIDA:
                    if evento.key == pygame.K_e:
                        if comida_espera_item_dados:
                            item, ganho_vida, ganho_energia = comida_espera_item_dados
                            mensagem_acao = consumir_comida(item, ganho_vida, ganho_energia)
                        else:
                            mensagem_acao = "Erro: sem comida para comer."
                        comida_espera = None
                        comida_espera_item_dados = None
                        estado_jogo = JOGANDO
                    elif evento.key == pygame.K_g:
                        if comida_espera_item_dados:
                            item, _, _ = comida_espera_item_dados
                            if adicionar_item_mochila(item):
                                mensagem_acao = f"Você guardou o(a) {item} na mochila."
                            else:
                                mensagem_acao = f"Sua mochila está cheia, não foi possível guardar o(a) {item}."
                        else:
                            mensagem_acao = "Erro: sem comida para guardar."
                        comida_espera = None
                        comida_espera_item_dados = None
                        estado_jogo = JOGANDO
                elif estado_jogo == ESPERA_ESCOLHA_USAR_ITEM:
                    if pygame.K_1 <= evento.key <= pygame.K_5:
                        indice = evento.key - pygame.K_1
                        if indice < len(mochila):
                            usar_item_da_mochila(indice)
                        else:
                            mensagem_acao = "Índice inválido para usar o item."
                            estado_jogo = JOGANDO
                            item_usar_espera = None
                    else:
                        mensagem_acao = f"Pressione tecla de 1 a {len(mochila)} para usar item."
                    if estado_jogo != ESPERA_ESCOLHA_USAR_ITEM:
                        item_usar_espera = None
                elif estado_jogo == FIM:
                    if evento.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

        if estado_jogo == INTRO:
            tela.fill(PRETO)
            desenhar_intro()

        elif estado_jogo == JOGANDO:
            tela.fill(PRETO)
            mostrar_status()

            ops_texto = "(1) Buscar comida   (2) Montar abrigo   (3) Explorar   (U) Usar item mochila"
            texto_ops = font_texto.render(ops_texto, True, BRANCO)
            tela.blit(texto_ops, (LARGURA // 2 - texto_ops.get_width() // 2, ALTURA - 70))

            if mensagem_acao:
                linhas = []
                palavras = mensagem_acao.split()
                linha_atual = ""
                for palavra in palavras:
                    if len(linha_atual) + len(palavra) + 1 <= 70:
                        linha_atual += palavra + " "
                    else:
                        linhas.append(linha_atual)
                        linha_atual = palavra + " "
                linhas.append(linha_atual)

                y_base = ALTURA - 140
                for i, linha in enumerate(linhas):
                    linha_render = font_pequena.render(linha.strip(), True, BRANCO)
                    tela.blit(linha_render, (20, y_base + i * 22))

            resultado = verificar_vitoria_ou_derrota()
            if resultado in ("vitoria", "derrota"):
                estado_jogo = FIM
                mensagem_final = resultado

        elif estado_jogo == ESPERA_ESCOLHA_COMIDA:
            tela.fill(PRETO)
            mostrar_status()
            instrucao = font_texto.render(
                "Você encontrou comida! Pressione (E) para comer ou (G) para guardar.", True, BRANCO
            )
            tela.blit(instrucao, (LARGURA // 2 - instrucao.get_width() // 2, ALTURA - 150))
            if mensagem_acao:
                linhas = []
                palavras = mensagem_acao.split()
                linha_atual = ""
                for palavra in palavras:
                    if len(linha_atual) + len(palavra) + 1 <= 70:
                        linha_atual += palavra + " "
                    else:
                        linhas.append(linha_atual)
                        linha_atual = palavra + " "
                linhas.append(linha_atual)
                y_base = ALTURA - 120
                for i, linha in enumerate(linhas):
                    linha_render = font_pequena.render(linha.strip(), True, BRANCO)
                    tela.blit(linha_render, (20, y_base + i * 22))

            ops_texto = "(Jogo pausado - escolha sobre a comida)"
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
    