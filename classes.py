# classes.py

import random
from config import VIDA_MAXIMA_JOGADOR, ENERGIA_MAXIMA_JOGADOR, MOCHILA_MAX_CAPACIDADE, DADOS_ITENS, DADOS_ANIMAIS

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

        self.status_envenenado = False
        self.status_ferimento_grave = False
        self.status_doente = False
    
    def adicionar_historico(self, mensagem):
        self.historico_acoes.setdefault(self.dias_passados, []).append(mensagem)

    def adicionar_item_mochila(self, item_nome):
        if len(self.mochila) >= MOCHILA_MAX_CAPACIDADE:
            return False
        self.mochila.append(item_nome)
        return True

    def calcular_protecao_total(self):
        return sum(DADOS_ITENS[item]["protecao"] for item in self.mochila if DADOS_ITENS.get(item, {}).get("tipo") == "protecao")

    def escolher_melhor_arma(self):
        armas_possuidas = [item for item in self.mochila if DADOS_ITENS.get(item, {}).get("tipo") == "arma"]
        if armas_possuidas:
            return max(armas_possuidas, key=lambda x: DADOS_ITENS[x]["dano_max"])
        return None

    def usar_arma_em_combate(self):
        arma = self.escolher_melhor_arma()
        if arma:
            dano = random.randint(DADOS_ITENS[arma]["dano_min"], DADOS_ITENS[arma]["dano_max"])
            return dano, arma
        return random.randint(5, 10), "mãos nuas"

    def processar_status_negativos(self):
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
        self.pontuacao += 30
        
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