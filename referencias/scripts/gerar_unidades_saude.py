"""
Gera referencias/recife/unidades_saude.csv a partir da "Rede de atenção à saúde no Recife"
(Portal de Dados Abertos da Prefeitura do Recife, licença ODbL):
https://dados.recife.pe.gov.br/dataset/rede-de-atencao-a-saude-no-recife

Uso: python referencias/scripts/gerar_unidades_saude.py rede-de-atencao-a-saude-no-recife.csv
"""
import sys
import pandas as pd

# Categoria da rede -> tipo no DengueSphere; a ordem define o tipo quando a unidade aparece em várias categorias
TIPOS = [
    ("12", "Vigilância de Zoonoses"),
    ("10", "Hospital"), ("10.1", "Hospital"), ("8", "Maternidade"),
    ("9.1", "Pronto Atendimento"), ("9.11", "Pronto Atendimento"), ("9.12", "Pronto Atendimento"),
    ("9.13", "Pronto Atendimento"), ("9.14", "Pronto Atendimento"),
    ("7", "Policlínica"),
    ("2.1", "Unidade Básica de Saúde"), ("2.2", "Unidade de Saúde da Família"), ("4.1", "Unidade de Saúde da Família"),
]
DISTRITOS = {str(i): f"DS {r}" for i, r in enumerate(["I", "II", "III", "IV", "V", "VI", "VII", "VIII"], start=1)}

rede = pd.read_csv(sys.argv[1], sep=";", dtype=str)
rede["categoria"] = rede["tipo_unidade"].str.split("|").str[0]
rede["servico"] = rede["tipo_unidade"].str.split("|").str[1].str.strip()
# A mesma unidade aparece uma vez por serviço (USF, vacinação, testagem...), às vezes com coordenadas um pouco diferentes
rede["unidade"] = rede["cnes"].fillna(rede["nome_oficial"].str.strip())
servicos = rede.groupby("unidade")["servico"].agg(lambda s: ", ".join(dict.fromkeys(s)))

prioridade = {c: i for i, (c, _) in enumerate(TIPOS)}
unidades = (
    rede[rede["categoria"].isin(prioridade)]
    .assign(prioridade=lambda d: d["categoria"].map(prioridade))
    .sort_values("prioridade")
    .drop_duplicates("unidade")
)
saida = pd.DataFrame({
    "tipo": unidades["categoria"].map(dict(TIPOS)),
    "nome": unidades["nome_oficial"].str.strip(),
    "cnes": unidades["cnes"],
    "endereco": unidades["endereço"].str.strip(),
    "bairro": unidades["bairro"],
    "distrito": unidades["distrito_sanitario"].map(DISTRITOS),
    "telefone": unidades["fone"],
    "horario": unidades["horario"],
    "servicos": unidades["unidade"].map(servicos),
    "latitude": unidades["latitude"],
    "longitude": unidades["longitude"],
}).sort_values(["tipo", "nome"])
saida.to_csv("referencias/recife/unidades_saude.csv", index=False)
print(saida["tipo"].value_counts().to_string(), f"\ntotal: {len(saida)}")
