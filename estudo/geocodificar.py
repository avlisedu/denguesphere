"""Geocodificação local dos casos usando a malha viária do OpenStreetMap.

Para cada par único (logradouro, bairro) do SINAN:
  1. rua_bairro  - logradouro encontrado (fuzzy >= LIMIAR_RUA) entre as ruas do bairro informado;
                   coordenada = ponto da rua mais próximo do centroide do trecho dentro do bairro
  2. rua_vizinha - logradouro encontrado na cidade (fuzzy >= LIMIAR_RUA_CIDADE) a até 1 km do bairro
  3. rua_cidade  - bairro desconhecido, mas o logradouro existe em um único bairro
  4. bairro      - fallback: ponto representativo do polígono do bairro
  5. nao_encontrado
Mesma lógica de cascata do GeocodingService do DengueSphere, trocando o Nominatim
por uma base local (reprodutível e sem limite de requisições).
"""
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from rapidfuzz import fuzz, process
from shapely.geometry import LineString, MultiLineString, Point
from shapely.ops import linemerge, nearest_points, polygonize, unary_union
from shapely.strtree import STRtree

from carregar import casos_nao_descartados

DADOS = Path(__file__).resolve().parent / "dados"
LIMIAR_RUA = 85
LIMIAR_RUA_CIDADE = 90
DIST_VIZINHA_KM = 1.0

# projeção equiretangular local (erro desprezível na escala de um município)
LAT0 = -8.05
KX = 111.320 * np.cos(np.radians(LAT0))
KY = 110.574

# caracteres corrompidos (mistura de CP437/CP850/Latin-1) -> letra provável
MOJIBAKE = str.maketrans({
    "├": "A", "┴": "A", "┬": "A", "Μ": "A", "¬": "A", "ª": "A", "º": "O", "°": "O",
    "╔": "E", "\x90": "E", "╩": "E", "═": "I", "Ë": "O", "Ö": "O", "Ò": "O",
    "║": "U", "┌": "U", "\x80": "C", "░": "", "¶": "", "┐": "", "╦": "", "?": "",
})
ORDINAIS = {
    "PRIMEIRA": "1", "PRIMEIRO": "1", "SEGUNDA": "2", "SEGUNDO": "2", "TERCEIRA": "3", "TERCEIRO": "3",
    "QUARTA": "4", "QUINTA": "5", "SEXTA": "6", "SETIMA": "7", "OITAVA": "8", "NONA": "9", "DECIMA": "10",
}
ABREV = {
    "DR": "DOUTOR", "PROF": "PROFESSOR", "PROFA": "PROFESSORA", "ENG": "ENGENHEIRO", "PE": "PADRE",
    "CEL": "CORONEL", "GAL": "GENERAL", "GEN": "GENERAL", "CAP": "CAPITAO", "STA": "SANTA", "STO": "SANTO",
    "MAL": "MARECHAL", "DES": "DESEMBARGADOR", "CONS": "CONSELHEIRO", "PRES": "PRESIDENTE",
    "VER": "VEREADOR", "DEP": "DEPUTADO", "SEN": "SENADOR", "GOV": "GOVERNADOR", "CMTE": "COMANDANTE",
    "SGT": "SARGENTO", "TEN": "TENENTE", "MONS": "MONSENHOR", "N": "NOSSA", "SRA": "SENHORA", "SR": "SENHOR",
    "TRAVESSA": "TV", "TRAV": "TV", "TRV": "TV", "TR": "TV",
}
TIPOS = {
    "RUA", "R", "RU", "AV", "AVENIDA", "ESTRADA", "EST", "ESTR", "PRACA", "PCA", "PC", "ALAMEDA", "AL",
    "LARGO", "LG", "RODOVIA", "ROD", "LADEIRA", "LD", "VIA",
}
UNIDADES = {
    "UM": 1, "HUM": 1, "DOIS": 2, "TRES": 3, "QUATRO": 4, "CINCO": 5, "SEIS": 6, "SETE": 7, "OITO": 8,
    "NOVE": 9, "DEZ": 10, "ONZE": 11, "DOZE": 12, "TREZE": 13, "QUATORZE": 14, "CATORZE": 14,
    "QUINZE": 15, "DEZESSEIS": 16, "DEZESSETE": 17, "DEZOITO": 18, "DEZENOVE": 19,
}
DEZENAS = {"VINTE": 20, "TRINTA": 30, "QUARENTA": 40, "CINQUENTA": 50}
STOP = {"DE", "DA", "DO", "DAS", "DOS", "E"}
NULOS = {"", "NAO INFORMADO", "IGNORADO", "SEM DENOMINACAO", "SN", "S N"}

ALIAS_BAIRRO = {
    "GRAAS": "GRACAS", "AREAIS": "AREIAS", "JIQU": "JIQUIA", "TEJIPI": "TEJIPIO", "PONRO PARADA": "PONTO PARADA",
    "ILHA JOANA BEZERRA": "JOANA BEZERRA", "VASCO": "VASCO GAMA", "IMB": "IMBIRIBEIRA", "GUAB": "GUABIRABA",
    "TAMA": "TAMARINEIRA", "POCO": "POCO PANELA", "BREJO GUABIRABA": "BREJO GUABIRABA",
}


def _base(texto) -> str:
    if texto is None or (isinstance(texto, float) and np.isnan(texto)):
        return ""
    t = str(texto).upper().translate(MOJIBAKE)
    t = "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^A-Z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _numeros_por_extenso(t: str) -> str:
    """VINTE E SETE DE JANEIRO -> 27 DE JANEIRO; TREZE DE JUNHO -> 13 DE JUNHO."""
    def dezena(m):
        return str(DEZENAS[m.group(1)] + (UNIDADES[m.group(2)] if m.group(2) else 0))
    t = re.sub(rf"\b({'|'.join(DEZENAS)})(?: E ({'|'.join(UNIDADES)}))?\b", dezena, t)
    return re.sub(rf"\b({'|'.join(UNIDADES)})\b", lambda m: str(UNIDADES[m.group(1)]), t)


def similaridade(a: str, b: str, **_) -> float:
    """token_sort_ratio, aceitando também nome contido no outro quando há 2+ palavras
    (DOMINGOS FERREIRA ~ ENGENHEIRO DOMINGOS FERREIRA)."""
    s = fuzz.token_sort_ratio(a, b)
    if min(a.count(" "), b.count(" ")) >= 1:
        s = max(s, fuzz.token_set_ratio(a, b) - 5)
    return s


def norm_rua(texto) -> str:
    t = _numeros_por_extenso(_base(texto))
    t = re.sub(r"\b(\d+)\s*[AO]\b", r"\1", t)  # 1A TRAV -> 1 TRAV
    tokens = []
    for tok in t.split():
        tok = ORDINAIS.get(tok, tok)
        tok = ABREV.get(tok, tok)
        if tok.isdigit():
            tok = str(int(tok))
        if tok in TIPOS or tok in STOP:
            continue
        tokens.append(tok)
    r = " ".join(tokens)
    return "" if r in NULOS else r


def norm_bairro(texto) -> str:
    t = " ".join(tok for tok in _base(texto).split() if tok not in STOP)
    return ALIAS_BAIRRO.get(t, t)


def para_km(lon, lat):
    return (np.asarray(lon) * KX, np.asarray(lat) * KY)


def para_graus(x, y):
    return (x / KX, y / KY)


def _linha(geom_osm) -> LineString:
    xs, ys = para_km([p["lon"] for p in geom_osm], [p["lat"] for p in geom_osm])
    return LineString(list(zip(xs, ys)))


def _poligono(el):
    linhas = [_linha(m["geometry"]) for m in el.get("members", []) if m.get("role") == "outer" and m.get("geometry")]
    uniao = unary_union(linhas)
    contorno = linemerge(list(getattr(uniao, "geoms", [uniao])))
    partes = getattr(contorno, "geoms", [contorno])
    # fecha anéis com fresta < 100 m (Coelhos e Ilha do Leite têm um trecho de divisa ausente no OSM)
    partes = [
        LineString(list(p.coords) + [p.coords[0]]) if not p.is_ring and Point(p.coords[0]).distance(Point(p.coords[-1])) < 0.1 else p
        for p in partes
    ]
    return unary_union(list(polygonize(unary_union(partes))))


def carregar_municipio():
    return _poligono(json.loads((DADOS / "osm_municipio.json").read_text())["elements"][0])


def carregar_bairros() -> dict:
    """Bairros do OSM dentro do Recife. A consulta por área também devolve bairros
    vizinhos que tocam a divisa (Aldeia/Camaragibe, Paratibe/Paulista): ficam de fora
    os que têm menos da metade da área dentro do município."""
    dados = json.loads((DADOS / "osm_bairros.json").read_text())
    municipio = carregar_municipio()
    bairros = {}
    for el in dados["elements"]:
        geom = _poligono(el)
        if not geom.is_empty and geom.intersection(municipio).area / geom.area >= 0.5:
            bairros[norm_bairro(el["tags"]["name"])] = {"nome": el["tags"]["name"], "geom": geom}
    return bairros


def carregar_ruas(bairros: dict) -> dict:
    """(rua_norm, bairro_norm) -> geometria do trecho da rua dentro do bairro."""
    dados = json.loads((DADOS / "osm_ruas.json").read_text())
    nomes_b = list(bairros)
    arvore = STRtree([bairros[b]["geom"] for b in nomes_b])
    trechos = defaultdict(list)
    for el in dados["elements"]:
        if len(el.get("geometry", [])) < 2:
            continue
        linha = _linha(el["geometry"])
        nome = norm_rua(el["tags"]["name"])
        if not nome:
            continue
        for i in arvore.query(linha, predicate="intersects"):
            parte = linha.intersection(bairros[nomes_b[i]]["geom"])
            if not parte.is_empty and parte.length > 0:
                trechos[(nome, nomes_b[i])].append(parte)
    return {k: unary_union(v) for k, v in trechos.items()}


def _ponto_na_rua(geom) -> Point:
    if isinstance(geom, MultiLineString):
        geom = linemerge(geom)
    return nearest_points(geom, geom.centroid)[0]


class GeocodificadorLocal:
    def __init__(self):
        self.bairros = carregar_bairros()
        self.ruas = carregar_ruas(self.bairros)
        self.nomes_bairros = list(self.bairros)
        self.ruas_por_bairro = defaultdict(list)
        self.bairros_por_rua = defaultdict(list)
        for nome, b in self.ruas:
            self.ruas_por_bairro[b].append(nome)
            self.bairros_por_rua[nome].append(b)
        self.todas_ruas = list(self.bairros_por_rua)

    def casar_bairro(self, bairro_sinan) -> str | None:
        b = norm_bairro(bairro_sinan)
        if not b:
            return None
        if b in self.bairros:
            return b
        m = process.extractOne(b, self.nomes_bairros, scorer=fuzz.ratio, score_cutoff=85)
        return m[0] if m else None

    def _ret(self, ponto, tipo, bairro, rua=None, score=None):
        lon, lat = para_graus(ponto.x, ponto.y) if ponto is not None else (None, None)
        return {"latitude": lat, "longitude": lon, "tipo_match": tipo, "bairro_osm": bairro, "rua_osm": rua, "score": score}

    def geocodificar(self, rua_sinan, bairro_sinan) -> dict:
        rua = norm_rua(rua_sinan)
        bairro = self.casar_bairro(bairro_sinan)

        if rua and bairro and self.ruas_por_bairro.get(bairro):
            m = process.extractOne(rua, self.ruas_por_bairro[bairro], scorer=similaridade, score_cutoff=LIMIAR_RUA)
            if m:
                return self._ret(_ponto_na_rua(self.ruas[(m[0], bairro)]), "rua_bairro", bairro, m[0], m[1])

        if rua:
            m = process.extractOne(rua, self.todas_ruas, scorer=fuzz.token_sort_ratio, score_cutoff=LIMIAR_RUA_CIDADE)
            if m:
                candidatos = self.bairros_por_rua[m[0]]
                if bairro:
                    poli = self.bairros[bairro]["geom"]
                    dist, b_viz = min((self.ruas[(m[0], b)].distance(poli), b) for b in candidatos)
                    if dist <= DIST_VIZINHA_KM:
                        geom = self.ruas[(m[0], b_viz)]
                        return self._ret(nearest_points(geom, poli)[0], "rua_vizinha", bairro, m[0], m[1])
                elif len(candidatos) == 1:
                    return self._ret(_ponto_na_rua(self.ruas[(m[0], candidatos[0])]), "rua_cidade", candidatos[0], m[0], m[1])

        if bairro:
            return self._ret(self.bairros[bairro]["geom"].representative_point(), "bairro", bairro)
        return self._ret(None, "nao_encontrado", None)


def geocodificar_casos(casos: pd.DataFrame) -> pd.DataFrame:
    geo = GeocodificadorLocal()
    chaves = casos[["nome_logradouro_residencia", "no_bairro_residencia"]].drop_duplicates()
    resultados = [
        {"nome_logradouro_residencia": r, "no_bairro_residencia": b, **geo.geocodificar(r, b)}
        for r, b in chaves.itertuples(index=False)
    ]
    tabela = pd.DataFrame(resultados)
    return casos.merge(tabela, on=["nome_logradouro_residencia", "no_bairro_residencia"], how="left")


COLUNAS = [
    "nu_notificacao", "arquivo_ano", "data", "ano_epi", "semana_epi", "tp_classificacao_final", "confirmado",
    "tp_sexo", "nu_idade", "no_bairro_residencia", "nome_logradouro_residencia", "nu_cep_residencia",
    "latitude", "longitude", "tipo_match", "bairro_osm", "rua_osm", "score",
]

if __name__ == "__main__":
    casos = casos_nao_descartados()
    geo = geocodificar_casos(casos)[COLUNAS]
    geo.to_csv(DADOS / "casos_geocodificados.csv.gz", index=False)
    print(len(geo), "casos não descartados;", int(geo["confirmado"].sum()), "confirmados")
    geo = geo[geo["confirmado"]]
    print(geo["tipo_match"].value_counts(normalize=True).round(3))
    print(geo.groupby("ano_epi")["tipo_match"].value_counts(normalize=True).unstack().round(2))
