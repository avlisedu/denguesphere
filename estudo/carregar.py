"""Leitura e padronização dos CSVs anuais de dengue do Recife (2013–2025).

Os arquivos do portal de dados abertos vêm em formatos diferentes:
- 2013–2020: nomes longos (dt_notificacao, no_bairro_residencia, ...)
- 2021–2025: nomes do SINAN (DT_NOTIFIC, NM_BAIRRO, ...), maiúsculos ou não
- 2015, 2019, 2023: cada linha inteira entre aspas, separada por vírgula
- codificação UTF-8, UTF-8 com BOM ou Latin-1
"""
import csv
import io
from pathlib import Path

import pandas as pd

RECIFE_IBGE = 261160
PASTA = Path(__file__).resolve().parent.parent / "Casos Dengue"

# nome SINAN -> nome padronizado (o dos arquivos antigos)
SINAN = {
    "nu_notific": "nu_notificacao",
    "dt_notific": "dt_notificacao",
    "dt_sin_pri": "dt_diagnostico_sintoma",
    "sem_pri": "ds_semana_sintoma",
    "nu_ano": "notificacao_ano",
    "id_mn_resi": "co_municipio_residencia",
    "id_bairro": "co_bairro_residencia",
    "nm_bairro": "no_bairro_residencia",
    "nm_logrado": "nome_logradouro_residencia",
    "nu_cep": "nu_cep_residencia",
    "cs_sexo": "tp_sexo",
    "nu_idade_n": "nu_idade",
    "classi_fin": "tp_classificacao_final",
    "criterio": "tp_criterio_confirmacao",
    "evolucao": "tp_evolucao_caso",
    "id_distrit": "co_distrito_residencia",
}


def _texto(caminho: Path) -> str:
    bruto = caminho.read_bytes()
    try:
        return bruto.decode("utf-8-sig")
    except UnicodeDecodeError:
        return bruto.decode("latin-1")


def ler_ano(caminho: Path) -> pd.DataFrame:
    texto = _texto(caminho)
    primeira = texto.split("\n", 1)[0]
    if primeira.startswith('"') and primeira.count(";") == 0:
        # linha inteira entre aspas: remove as aspas externas e lê como CSV com vírgula
        # a linha é um único campo CSV ("" = aspas internas); desembrulha e lê de novo
        linhas = [r[0] for r in csv.reader(io.StringIO(texto)) if r]
        df = pd.read_csv(io.StringIO("\n".join(linhas)), sep=",", dtype=str)
    else:
        df = pd.read_csv(io.StringIO(texto), sep=";", dtype=str, quoting=csv.QUOTE_MINIMAL)
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.loc[:, [c for c in df.columns if c and not c.startswith("unnamed")]]
    df = df.rename(columns={k: v for k, v in SINAN.items() if k in df.columns})
    df["arquivo_ano"] = int(caminho.stem)
    for c in ("dt_notificacao", "dt_diagnostico_sintoma"):
        df[c] = _datas(df[c])
    return df


def _datas(col: pd.Series) -> pd.Series:
    """Cada ano usa um formato: 2013/01/04 00:00:00, 2015-12-10 ou 01/01/2021 (dia primeiro)."""
    amostra = col.dropna().astype(str).head(200)
    dia_primeiro = amostra.str.match(r"^\d{2}/\d{2}/\d{4}").mean() > 0.5
    return pd.to_datetime(col, errors="coerce", dayfirst=dia_primeiro, format="mixed")


def carregar_todos(pasta: Path = PASTA) -> pd.DataFrame:
    partes = [ler_ano(p) for p in sorted(pasta.glob("*.csv"))]
    df = pd.concat(partes, ignore_index=True, sort=False).copy()
    df["tp_classificacao_final"] = pd.to_numeric(df["tp_classificacao_final"], errors="coerce")
    # confirmados: códigos antigos (1–4: clássica, FHD, SCD, com complicações) e
    # atuais (10 dengue, 11 com sinais de alarme, 12 grave); 5 = descartado, 8 = inconclusivo
    df["confirmado"] = df["tp_classificacao_final"].isin([1, 2, 3, 4, 10, 11, 12])
    df["co_municipio_residencia"] = pd.to_numeric(df["co_municipio_residencia"], errors="coerce")
    cep = pd.to_numeric(df["nu_cep_residencia"], errors="coerce")
    cep = cep.where(cep.between(50_000_000, 56_999_999))  # faixa de CEPs de PE
    df["nu_cep_residencia"] = cep.map(lambda v: f"{int(v):08d}" if pd.notna(v) else None)
    df["no_bairro_residencia"] = df["no_bairro_residencia"].str.strip().str.upper()
    df["nome_logradouro_residencia"] = df["nome_logradouro_residencia"].str.strip().str.upper()
    df["recife"] = df["co_municipio_residencia"] == RECIFE_IBGE
    df["data"] = df["dt_diagnostico_sintoma"].fillna(df["dt_notificacao"])
    # descarta datas fora da janela do arquivo (erros de digitação como 1950 ou 1970)
    fora = (df["data"].dt.year - df["arquivo_ano"]).abs() > 1
    df.loc[fora, "data"] = pd.NaT
    iso = df["data"].dt.isocalendar()
    df["ano_epi"] = iso["year"]
    df["semana_epi"] = iso["week"]
    return df


def casos_confirmados(df: pd.DataFrame | None = None) -> pd.DataFrame:
    df = carregar_todos() if df is None else df
    return df[df["confirmado"] & df["recife"] & df["data"].notna()].copy()


def casos_nao_descartados(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Confirmados + inconclusivos + sem classificação: o que a vigilância vê em tempo real,
    antes do encerramento das investigações (análise de sensibilidade)."""
    df = carregar_todos() if df is None else df
    return df[(df["tp_classificacao_final"] != 5) & df["recife"] & df["data"].notna()].copy()


if __name__ == "__main__":
    df = carregar_todos()
    print(df.shape)
    print(df.groupby("arquivo_ano").size())
