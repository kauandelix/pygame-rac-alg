import pygame
import random
import time
import sys

# Inicialização do pygame
pygame.init()
pygame.font.init()

# Constantes
LARGURA, ALTURA = 1000, 800
VIDA_MAXIMA = 100
ENERGIA_MAXIMA = 100
PONTUACAO_MAXIMA = 900
MOCHILA_MAX = 6  # Limite de itens na mochila

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (34, 139, 34)
VERMELHO = (200, 30, 30)
AMARELO = (255, 255, 100)
AZUL = (100, 149, 237)
CINZA = (50, 50, 50)

# Configuração da tela
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Sobrevivência na Floresta")

# Fontes
font_titulo = pygame.font.SysFont("arial", 40, bold=True)
font_texto = pygame.font.SysFont("arial", 24)
font_pequena = pygame.font.SysFont("arial", 18)

# Variáveis globais do jogador
vida = VIDA_MAXIMA
energia = ENERGIA_MAXIMA
mochila = []
pontuacao = 0
encontrou_saida = False

# Estados do jogo
INTRO = 0
JOGANDO = 1
ESPERA_ESCOLHA_COMIDA = 2
ESPERA_ESCOLHA_USAR_ITEM = 3
FIM = 4

estado_jogo = INTRO
mensagem_final = ""

# Dicionário de animais selvagens e seus danos
animais = {
    "Onça": {"dano_min": 15, "dano_max": 30},
    "Cobra": {"dano_min": 5, "dano_max": 20},
    "Lobo": {"dano_min": 10, "dano_max": 25},
    "Arraia": {"dano_min": 7, "dano_max": 18},
}

# Dicionário de armas e seus danos para defesa
armas = {
    "Faca": {"dano_min": 15, "dano_max": 25},
    "Arco": {"dano_min": 10, "dano_max": 20},
    "Clava": {"dano_min": 12, "dano_max": 21},
}

# Para gerenciar item de comida encontrado aguardando escolha do jogador
comida_espera = None  # armazenará o texto mensagem da comida pendente
comida_espera_item_dados = None  # armazenará (item, ganho_vida, ganho_energia)

# Mensagem para usar item escolhidos
mensagem_acao = ""
# Item pendente para usar
item_usar_espera = None

# Funções auxiliares
def desenhar_texto_multilinha(superficie, texto, fonte, cor, rect, espacamento=5):
    linhas = texto.splitlines()
    y_offset = 0
    for linha in linhas:
        texto_render = fonte.render(linha, True, cor)
        superficie.blit(texto_render, (rect.x, rect.y + y_offset))
        y_offset += texto_render.get_height() + espacamento

def mostrar_status():
    # Fundo para informações
    status_rect = pygame.Rect(10, 10, LARGURA - 20, 130)
    pygame.draw.rect(tela, CINZA, status_rect, border_radius=10)
    # Informações texto
    texto_vida = font_texto.render(f"Vida: {vida} / {VIDA_MAXIMA}", True, VERMELHO)
    texto_energia = font_texto.render(f"Energia: {energia} / {ENERGIA_MAXIMA}", True, AMARELO)
    texto_pontos = font_texto.render(f"Pontos: {pontuacao}", True, AZUL)
    mochila_texto = font_texto.render("Mochila: " + (", ".join(mochila) if mochila else "Vazia"), True, BRANCO)

    tela.blit(texto_vida, (20, 20))
    tela.blit(texto_energia, (20, 50))
    tela.blit(texto_pontos, (20, 80))
    tela.blit(mochila_texto, (20, 110))

def adicionar_item_mochila(item):
    if len(mochila) >= MOCHILA_MAX:
        return False
    mochila.append(item)
    return True

def escolher_arma():
    # Escolhe a melhor arma na mochila para defesa, se tiver
    armas_possuida = [item for item in mochila if item in armas]
    if armas_possuida:
        # escolhe a arma com maior dano máximo
        melhor_arma = max(armas_possuida, key=lambda a: armas[a]["dano_max"])
        return melhor_arma
    return None

def usar_arma_defesa():
    arma = escolher_arma()
    if arma:
        dano_arma = random.randint(armas[arma]["dano_min"], armas[arma]["dano_max"])
        return dano_arma, arma
    else:
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
    # Tratamento dependendo do item
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

def buscar_comida():
    global comida_espera, comida_espera_item_dados
    ganho_energia = 10
    ganho_vida = random.randint(3, 8)
    # Chance de encontrar comida (item)
    encontrou_item = random.random() < 0.6
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
    global energia, pontuacao
    custo_energia = 20
    if energia < custo_energia:
        return "Energia insuficiente para montar o abrigo!"
    energia -= custo_energia
    pontuacao += 30
    msg = "Você montou um abrigo e descansou um pouco. (-20 energia, +30 pontos)"
    if random.random() < 0.3:
        item = "Cordas"
        if adicionar_item_mochila(item):
            msg = "Você montou um abrigo, gastou energia, e encontrou Cordas! (+30 pontos)"
        else:
            msg = "Você montou um abrigo, gastou energia, mas sua mochila está cheia para as Cordas. (+30 pontos)"
    return msg

def explorar():
    global vida, energia, pontuacao, comida_espera, comida_espera_item_dados
    custo_energia = 15
    if energia < custo_energia:
        return "Energia insuficiente para explorar!"
    energia -= custo_energia
    evento = random.choices(
        population=["animal", "nada", "comida", "item", "armamento"],
        weights=[0.35, 0.2, 0.2, 0.15, 0.1],  # adicionada chance para armamento
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
            pontuacao -= 20
        else:
            pontuacao -= 10
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
            pontuacao += 25
            msg = f"Você encontrou um item: {item}! (+25 pontos)"
        else:
            msg = f"Você encontrou um item: {item}, mas sua mochila está cheia."
    elif evento == "armamento":
        item = random.choice(list(armas.keys()))
        if adicionar_item_mochila(item):
            pontuacao += 40
            msg = f"Você encontrou um armamento: {item}! (+40 pontos)"
        else:
            msg = f"Você encontrou um armamento: {item}, mas sua mochila está cheia."
    else:
        msg = "Você explorou mas não encontrou nada relevante."
    return msg

def verificar_vitoria_ou_derrota():
    global encontrou_saida, pontuacao, vida
    if vida <= 0:
        return "derrota"
    if pontuacao >= PONTUACAO_MAXIMA:
        encontrou_saida = True
        return "vitoria"
    return "continuar"

def desenhar_intro():
    tela.fill(PRETO)
    titulo = font_titulo.render("Sobrevivência na Floresta", True, VERDE)
    tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 50))

    texto_introducao = (
        "Você está perdido em uma floresta e precisa sobreviver.\n"
        "Coleta recursos, monta abrigo, explora e foge de animais selvagens.\n"
        "Você também pode encontrar armas para se defender.\n"
        "Comida encontrada pode ser comida na hora ou guardada para depois.\n"
        "Faça escolhas para acumular pontos até encontrar o caminho de casa.\n"
        "\n"
        "Controles:\n"
        "1 - Buscar comida\n"
        "2 - Montar abrigo\n"
        "3 - Explorar\n"
        "U - Usar um item da mochila\n\n"
        "Durante decisão: (E) - Comer item, (G) - Guardar na mochila\n\n"
        "Pressione ESPAÇO para começar o jogo."
    )
    rect_texto = pygame.Rect(50, 150, LARGURA - 100, ALTURA - 200)
    desenhar_texto_multilinha(tela, texto_introducao, font_texto, BRANCO, rect_texto)

def desenhar_fim(mensagem):
    tela.fill(PRETO)
    if mensagem == "vitoria":
        texto = "Parabéns! Você sobreviveu e encontrou o caminho de volta para casa!"
        cor = VERDE
    else:
        texto = "Você morreu na floresta. Fim de jogo."
        cor = VERMELHO
    titulo = font_titulo.render("Fim de Jogo", True, cor)
    tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 100))

    rect_texto = pygame.Rect(50, 200, LARGURA - 100, ALTURA - 300)
    desenhar_texto_multilinha(tela, texto, font_texto, cor, rect_texto)

    instrucao = font_pequena.render("Pressione ESC para sair.", True, BRANCO)
    tela.blit(instrucao, (LARGURA//2 - instrucao.get_width()//2, ALTURA - 60))

def main():
    global estado_jogo, vida, energia, pontuacao, mochila, mensagem_final
    global comida_espera, comida_espera_item_dados, mensagem_acao, item_usar_espera
    
    relogio = pygame.time.Clock()
    mensagem_acao = ""
    item_usar_espera = None
    
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
                        # Espera decisão sobre comida, bloqueia outras ações
                        pass
                    elif item_usar_espera:
                        # Espera decisão sobre item a usar, bloqueia outras ações
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
                                mensagem_acao = "Pressione a tecla de 1 a {} para usar o item correspondente na mochila.".format(len(mochila))
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
                            item, ganho_vida, ganho_energia = comida_espera_item_dados
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
                        mensagem_acao = "Pressione tecla de 1 a {} para usar item.".format(len(mochila))
                    # Após uso, sai do modo usar item
                    if estado_jogo != ESPERA_ESCOLHA_USAR_ITEM:
                        item_usar_espera = None

                elif estado_jogo == FIM:
                    if evento.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

        if estado_jogo == INTRO:
            desenhar_intro()

        elif estado_jogo == JOGANDO:
            tela.fill(PRETO)
            mostrar_status()

            ops_texto = "(1) Buscar comida  (2) Montar abrigo  (3) Explorar  (U) Usar item mochila"
            texto_ops = font_texto.render(ops_texto, True, BRANCO)
            tela.blit(texto_ops, (LARGURA//2 - texto_ops.get_width()//2, ALTURA - 80))

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

                y_base = ALTURA - 150
                for i, linha in enumerate(linhas):
                    linha_render = font_pequena.render(linha.strip(), True, AMARELO)
                    tela.blit(linha_render, (20, y_base + i * 22))

            resultado = verificar_vitoria_ou_derrota()
            if resultado in ("vitoria", "derrota"):
                estado_jogo = FIM
                mensagem_final = resultado

        elif estado_jogo == ESPERA_ESCOLHA_COMIDA:
            tela.fill(PRETO)
            mostrar_status()
            instrucao = font_texto.render("Você encontrou comida! Pressione (E) para comer ou (G) para guardar.", True, AMARELO)
            tela.blit(instrucao, (LARGURA//2 - instrucao.get_width()//2, ALTURA - 150))
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
                    linha_render = font_pequena.render(linha.strip(), True, AMARELO)
                    tela.blit(linha_render, (20, y_base + i * 22))

            ops_texto = "(Jogo pausado - escolha sobre comida)"
            texto_ops = font_texto.render(ops_texto, True, CINZA)
            tela.blit(texto_ops, (LARGURA//2 - texto_ops.get_width()//2, ALTURA - 80))

        elif estado_jogo == ESPERA_ESCOLHA_USAR_ITEM:
            tela.fill(PRETO)
            mostrar_status()
            instrucao = font_texto.render("Pressione 1 a {} para usar o item correspondente na mochila.".format(len(mochila)), True, AMARELO)
            tela.blit(instrucao, (LARGURA//2 - instrucao.get_width()//2, ALTURA - 150))

            # Mostrar itens da mochila enumerados
            y_base = ALTURA - 120
            for i, item in enumerate(mochila):
                linha_texto = f"{i+1} - {item}"
                linha_render = font_pequena.render(linha_texto, True, AMARELO)
                tela.blit(linha_render, (20, y_base + i * 22))

        elif estado_jogo == FIM:
            desenhar_fim(mensagem_final)

        pygame.display.flip()
        relogio.tick(30)

if __name__ == "__main__":
    main()