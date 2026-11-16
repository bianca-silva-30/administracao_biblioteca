def analisar_capa(sessao):
    """
    MOCK: devolve um resultado fixo para testarmos o fluxo completo.
    Depois, o corpo desta função chama a IA e devolve o mesmo formato.
    Dados que a IA não conseguir ler devem ficar vazios.
    """
    return {
        "titulo": "Livro de Teste (resultado simulado)",
        "autores": ["Autor de Teste"],
        "edicao": "",
        "ano": None,
        "isbn": "",
        "editora": "",
    }