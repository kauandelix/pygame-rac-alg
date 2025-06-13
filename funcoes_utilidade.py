# funcoes_utilidade.py

import os
import sys
import time
from config import VIDA_MAXIMA_JOGADOR, ENERGIA_MAXIMA_JOGADOR, ACOES_POR_DIA, PONTUACAO_MAXIMA_VITORIA

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
        # Import DADOS_ANIMAIS localmente para evitar circular import se classes.py já importa utilidades
        from config import DADOS_ANIMAIS 
        print(f"👾 Vida do {inimigo_atual.nome}: {inimigo_atual.vida}/{DADOS_ANIMAIS[inimigo_atual.nome]['vida']}")