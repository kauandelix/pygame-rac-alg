# main.py

from config import ACOES_POR_DIA, PONTUACAO_MAXIMA_VITORIA
from classes import Jogador, Animal
from funcoes_utilidade import clear_screen, show_animation, desenhar_intro, desenhar_fim, mostrar_status
from logica_jogo import (
    acao_buscar_comida,
    acao_montar_abrigo,
    acao_explorar,
    acao_dormir,
    acao_usar_item_mochila,
    gerenciar_combate,
    verificar_fim_de_jogo
)
import sys

def jogar():
    """Função principal que controla o fluxo do jogo."""
    jogador = Jogador()
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
        
        status_msg = jogador.processar_status_negativos()
        if status_msg:
            game_state["mensagem_acao"] += status_msg
        
        if verificar_fim_de_jogo(jogador, game_state):
            desenhar_fim(jogador, game_state["mensagem_final_tipo"])
            break

        if jogador.acoes_no_dia >= ACOES_POR_DIA and game_state["estado"] == "JOGANDO":
            game_state["mensagem_acao"] += "\nO dia terminou! Você está exausto e precisa dormir. 😴"
            jogador.adicionar_historico("O dia terminou. Você precisa descansar.")
            
            if not jogador.abrigo_construido:
                jogador.vida = max(0, jogador.vida - 10)
                jogador.energia = max(0, jogador.energia - 15)
                game_state["mensagem_acao"] += "\nVocê não tem um abrigo seguro para dormir. Perdeu mais vida e energia por não descansar adequadamente! 💀"
                jogador.adicionar_historico("Você não conseguiu dormir em segurança e sofreu as consequências.")
            
            jogador.dias_passados += 1
            jogador.acoes_no_dia = 0
            
            if verificar_fim_de_jogo(jogador, game_state):
                desenhar_fim(jogador, game_state["mensagem_final_tipo"])
                break

        print(f"\n{game_state['mensagem_acao']}\n")
        game_state["mensagem_acao"] = ""

        if game_state["estado"] == "JOGANDO":
            print("--- Escolha uma ação ---")
            print("1. Buscar comida 🍎")
            print("2. Montar abrigo 🏕️")
            print("3. Explorar 🗺️")
            if jogador.abrigo_construido:
                print("4. Dormir 😴")
            if jogador.mochila:
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
            else:
                game_state["mensagem_acao"] = "Comando inválido. Tente novamente."
                jogador.adicionar_historico("Erro: Comando inválido no menu principal.")
            
        elif game_state["estado"] == "ESPERA_COMIDA":
            print(game_state["mensagem_acao"])
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

        elif game_state["estado"] == "ESPERA_USAR_ITEM":
            print("--- Itens Usáveis na Mochila ---")
            itens_usaveis = [item for item in jogador.mochila if game_state["DADOS_ITENS"].get(item, {}).get("tipo") in ["comida", "medico", "utilitario"]]
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

        elif game_state["estado"] == "COMBATE":
            game_state["mensagem_acao"] = gerenciar_combate(jogador, game_state["inimigo_atual"], game_state)

if __name__ == "__main__":
    jogar()