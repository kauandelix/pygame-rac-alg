# logica_jogo.py

import random
from config import (
    CHANCE_BASE_COMIDA, CUSTO_ENERGIA_ABRIGO,
    PONTUACAO_MAXIMA_VITORIA, DADOS_ITENS, DADOS_ANIMAIS,
    VIDA_MAXIMA_JOGADOR, ENERGIA_MAXIMA_JOGADOR, REGEN_ENERGIA_SONO_ABRIGO, REGEN_VIDA_SONO_ABRIGO
)
from funcoes_utilidade import show_animation # Importa apenas o necessário
from classes import Animal # Importa Animal, pois acao_explorar cria um


def acao_buscar_comida(jogador, game_state):
    mensagem_acao_local = ""
    frames_buscar = ["Buscando  .", "Buscando ..", "Buscando ..."]
    show_animation(frames_buscar, delay=0.3, message="🌳 Procurando por comida...")

    jogador.acoes_no_dia += 1

    chance_encontrar = CHANCE_BASE_COMIDA * (0.6 if jogador.abrigo_construido else 1.0)
    
    if random.random() < chance_encontrar:
        comidas_disponiveis = [item for item, data in DADOS_ITENS.items() if data["tipo"] == "comida"]
        
        item_nome = random.choice(comidas_disponiveis)
        if random.random() < 0.15:
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
        game_state["estado"] = "ESPERA_COMIDA"
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
    mensagem_acao_local = ""
    if jogador.abrigo_construido:
        jogador.adicionar_historico(f"Você tentou construir um abrigo novamente, mas já tinha um.")
        mensagem_acao_local = "Você já montou o abrigo, não pode construir novamente. 🏕️"
        return mensagem_acao_local

    if jogador.energia < CUSTO_ENERGIA_ABRIGO:
        jogador.adicionar_historico(f"Você tentou montar um abrigo, mas não tinha energia suficiente.")
        mensagem_acao_local = f"⚡ Energia insuficiente para montar o abrigo! Você precisa de {CUSTO_ENERGIA_ABRIGO} de energia."
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
    mensagem_acao_local = ""
    custo_energia = 15
    if jogador.energia < custo_energia:
        jogador.adicionar_historico(f"Você tentou explorar, mas estava muito exausto.")
        mensagem_acao_local = "⚡ Energia insuficiente para explorar!"
        return mensagem_acao_local

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
        game_state["inimigo_atual"] = Animal(animal_nome)
        game_state["estado"] = "COMBATE"
        mensagem_acao_local = f"Você encontrou um {animal_nome}! 😱 Prepare-se para lutar!"
        jogador.adicionar_historico(f"Você foi surpreendido por um(a) {animal_nome} e entrou em combate!")
    elif evento == "comida":
        mensagem_acao_local = acao_buscar_comida(jogador, game_state) # Esta função já define o estado
    else:
        item_tipo_map = {
            "item_medico": "medico",
            "item_protecao": "protecao",
            "armamento": "arma"
        }
        tipo_item_encontrado = item_tipo_map.get(evento)

        if tipo_item_encontrado:
            possiveis_itens = [item for item, data in DADOS_ITENS.items() if data["tipo"] == tipo_item_encontrado]
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
        else:
            mensagem_acao_local = "Você explorou mas não encontrou nada relevante. 🤷"
            jogador.adicionar_historico(f"Você explorou a área, mas não encontrou nada de especial.")
    
    if game_state["estado"] not in ["COMBATE", "ESPERA_COMIDA"]:
        game_state["estado"] = "JOGANDO"
    return mensagem_acao_local

def acao_dormir(jogador, game_state):
    mensagem_acao_local = ""
    if not jogador.abrigo_construido:
        jogador.adicionar_historico(f"Você tentou dormir, mas não tinha um abrigo seguro.")
        mensagem_acao_local = "Você não tem um abrigo seguro para dormir. Encontre um local ou construa um! 🏕️"
        return mensagem_acao_local

    frames_dormir = ["Zzz .", "Zzz ..", "Zzz ...", "Zzz .", "Zzz ..", "Zzz ...", "🌄 Acordando..."]
    show_animation(frames_dormir, delay=0.3, message="😴 Você está dormindo...")

    jogador.acoes_no_dia = 0
    jogador.dias_passados += 1

    energia_recuperada = REGEN_ENERGIA_SONO_ABRIGO
    vida_recuperada = REGEN_VIDA_SONO_ABRIGO
    
    jogador.recuperar_energia(energia_recuperada)
    jogador.curar(vida_recuperada)
    
    sono_cura_mensagem = ""
    if jogador.status_doente and random.random() < 0.3:
        jogador.status_doente = False
        sono_cura_mensagem += " Você se sentiu um pouco melhor da doença. "
    
    jogador.adicionar_historico(f"Você dormiu em seu abrigo seguro e se recuperou bem.")
    mensagem_acao_local = (f"Você dormiu e um novo dia começou! ☀️"
                     f" ❤️ +{vida_recuperada} vida, ⚡ +{energia_recuperada} energia." + sono_cura_mensagem)
    game_state["estado"] = "JOGANDO"
    return mensagem_acao_local

def acao_usar_item_mochila(jogador, game_state):
    mensagem_acao_local = ""
    itens_usaveis = [item for item in jogador.mochila if DADOS_ITENS.get(item, {}).get("tipo") in ["comida", "medico", "utilitario"]]

    if not itens_usaveis:
        mensagem_acao_local = "Você não tem itens usáveis na mochila (apenas armas ou proteção). 🤔"
        game_state["estado"] = "JOGANDO"
        return mensagem_acao_local

    game_state["estado"] = "ESPERA_USAR_ITEM"
    return "Escolha um item para usar:"

def gerenciar_combate(jogador, inimigo_atual, game_state):
    from funcoes_utilidade import mostrar_status # Importa aqui para evitar circular import com main
    mensagem_combate_turno = ""
    
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
                jogador.acoes_no_dia += 1
                return mensagem_combate_turno
            else:
                dano_retaliacao = inimigo_atual.atacar() // 2
                jogador.sofrer_dano(dano_retaliacao)
                mensagem_combate_turno = f"Você tentou fugir, mas falhou! 😬 O(a) {inimigo_atual.nome} não te deixa escapar! (-{custo_energia_fuga} energia). Você sofreu {dano_retaliacao} de dano de retaliação! 💔"
                jogador.adicionar_historico(f"Você tentou fugir do(a) {inimigo_atual.nome}, mas falhou e sofreu dano.")
        else:
            mensagem_combate_turno = "⚡ Energia insuficiente para tentar a fuga! Você precisa de mais energia."
            jogador.adicionar_historico(f"Você tentou fugir do(a) {inimigo_atual.nome}, mas estava sem energia.")
    else:
        mensagem_combate_turno = "Comando inválido no combate. Tente (A)tacar, (D)efender ou (F)Fugir."
        
    if not inimigo_atual.esta_vivo():
        jogador.pontuacao += 100
        mensagem_combate_turno = f"Você derrotou o(a) {inimigo_atual.nome}! 🎉 (+100 pontos)"
        jogador.adicionar_historico(f"Você derrotou o(a) {inimigo_atual.nome} em combate!")
        game_state["estado"] = "JOGANDO"
        game_state["inimigo_atual"] = None
        jogador.acoes_no_dia += 1
        return mensagem_combate_turno

    dano_animal = inimigo_atual.atacar()
    protecao_total = jogador.calcular_protecao_total()
    dano_animal_final = max(0, dano_animal - dano_defesa - protecao_total)
    
    jogador.sofrer_dano(dano_animal_final)
    mensagem_combate_turno += f"\nO(a) {inimigo_atual.nome} ataca, causando {dano_animal_final} de dano a você! 🩸"
    if protecao_total > 0:
        mensagem_combate_turno += f" (Sua proteção física reduziu {protecao_total} de dano!)"

    jogador.adicionar_historico(f"O(a) {inimigo_atual.nome} te atacou, causando {dano_animal_final} de dano.")
    jogador.pontuacao = max(0, jogador.pontuacao - 5)

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
        jogador.encontrou_saida = True
        game_state["mensagem_final_tipo"] = "vitoria"
        game_state["estado"] = "FIM"
        return True
    return False