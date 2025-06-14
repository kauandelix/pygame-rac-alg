# config.py

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
    "Maçã": {"tipo": "comida", "vida_recuperada": (3, 8), "energia_recuperada": 10},
    "Banana": {"tipo": "comida", "vida_recuperada": (3, 8), "energia_recuperada": 10},
    "Morango": {"tipo": "comida", "vida_recuperada": (3, 8), "energia_recuperada": 10},
    "Coxinha de Farofa": {"tipo": "comida", "vida_recuperada": (3, 8), "energia_recuperada": 10},
    "Jabuticaba": {"tipo": "comida", "vida_recuperada": (3, 8), "energia_recuperada": 10},
    "Pinhão CRU": {"tipo": "comida", "vida_recuperada": (-1, 8), "energia_recuperada": 10, "chance_doecnca": 0.3},
    "Nozes": {"tipo": "comida", "vida_recuperada": (3, 8), "energia_recuperada": 10},
    "Mandioca": {"tipo": "comida", "vida_recuperada": (3, 8), "energia_recuperada": 10},
    "Cogumelo Desconhecido": {"tipo": "comida", "vida_recuperada": (-5, 0), "energia_recuperada": 5, "chance_doenca": 0.5},
     "Erva do BOB MARLEY": {"tipo": "comida", "vida_recuperada": (-5, -1), "energia_recuperada": -1, "chance_doenca": 0.2},
}

DADOS_ANIMAIS = {
    "🐆Onça": {"dano_min": 15, "dano_max": 25, "vida": 60, "chance_fuga_base": 0.3, "chance_ferimento_grave": 0.2},
    "🐍Cobra": {"dano_min": 8, "dano_max": 18, "vida": 30, "chance_fuga_base": 0.6, "chance_envenenamento": 0.7},
    "🐺Lobo Guará": {"dano_min": 12, "dano_max": 22, "vida": 50, "chance_fuga_base": 0.4, "chance_ferimento_grave": 0.1},
    "🐗Javali": {"dano_min": 10, "dano_max": 20, "vida": 30, "chance_fuga_base": 0.4, "chance_ferimento_grave": 0.15},
    "🐊Jacaré": {"dano_min": 8, "dano_max": 25, "vida": 60, "chance_fuga_base": 0.7, "chance_ferimento_grave": 0.3},
    "🐒Chimpanzé": {"dano_min": 6, "dano_max": 15, "vida": 80, "chance_fuga_base": 0.7},
    "🦍Gorila": {"dano_min": 12, "dano_max": 25, "vida": 100, "chance_fuga_base": 0.3, "chance_ferimento_grave": 0.25},
    "Capivara": {"dano_min": 7, "dano_max": 19, "vida": 70, "chance_fuga_base": 0.5, "chance_ferimento_grave": 0.1},
}