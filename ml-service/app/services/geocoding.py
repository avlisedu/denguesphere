"""Geocoding service: CEP/street/neighborhood -> lat/lon.

Ported from the original Streamlit page (pages/coordenadas.py), kept in
Python because it depends on geopy (Nominatim) and rapidfuzz.
"""
import re
import unicodedata
from time import sleep

import pandas as pd
from geopy.exc import GeocoderRateLimited, GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim
from rapidfuzz import fuzz, process


class GeocodingUnavailable(Exception):
    """Raised when Nominatim itself is failing (rate-limited or unreachable)
    after retries, as opposed to a query that Nominatim answered with zero
    results. Keeping these separate matters: silently treating a 429 as
    "not found" makes correctly-typed real addresses look unmatched."""

_STOPWORDS_RE = re.compile(r"\b(de|da|do|das|dos|rua|avenida|av|travessa|tv)\b")
_NON_DIGIT_RE = re.compile(r"\D")
_WHITESPACE_RE = re.compile(r"\s+")


def normalizar_texto(texto) -> str:
    if pd.isna(texto):
        return ""
    texto = str(texto).lower().strip()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    )
    texto = _STOPWORDS_RE.sub(" ", texto)
    texto = _WHITESPACE_RE.sub(" ", texto).strip()
    return texto


def limpar_cep(valor) -> str:
    if pd.isna(valor):
        return ""
    return _NON_DIGIT_RE.sub("", str(valor))


class GeocodingService:
    """Stateful helper: build once per request, holds a fuzzy-match
    dictionary of street names plus a geocode cache, then process rows.
    """

    def __init__(self, df: pd.DataFrame, rua_col: str, user_agent: str = "denguesphere_geocoder"):
        self.geolocator = Nominatim(user_agent=user_agent)
        self.cache: dict[str, dict] = {}
        self.ruas_unicas = sorted(set(df[rua_col].dropna().apply(normalizar_texto)))

    def corrigir_nome_rua(self, rua_digitada: str) -> str:
        if not rua_digitada:
            return ""
        rua_norm = normalizar_texto(rua_digitada)
        if not self.ruas_unicas:
            return rua_norm
        melhor, score, _ = process.extractOne(
            rua_norm, self.ruas_unicas, scorer=fuzz.token_sort_ratio
        )
        if score >= 70 and melhor != rua_norm:
            return melhor
        return rua_norm

    def _build_payload(self, cep, bairro, latitude=None, longitude=None, tipo_match="nao_encontrado"):
        return {
            "CEP_processado": cep,
            "latitude": latitude,
            "longitude": longitude,
            "bairro_utilizado": bairro,
            "tipo_match": tipo_match,
        }

    def _geocode_with_retry(self, consulta, max_retries=2):
        """Queries Nominatim, retrying transient failures (rate limit,
        timeout, 5xx) with backoff. Raises GeocodingUnavailable if the
        service is still failing after retries - callers must not treat
        that the same as "no result"."""
        last_exc = None
        for _ in range(max_retries):
            try:
                location = self.geolocator.geocode(consulta, timeout=10)
                sleep(1)
                return location
            except GeocoderRateLimited as exc:
                last_exc = exc
                sleep(getattr(exc, "retry_after", None) or 5)
            except (GeocoderTimedOut, GeocoderServiceError) as exc:
                last_exc = exc
                sleep(2)
        raise GeocodingUnavailable(str(last_exc))

    def _tentar_geocodificar(self, consultas, tipo_match, cep, bairro):
        for consulta in consultas:
            location = self._geocode_with_retry(consulta)
            if location:
                return self._build_payload(
                    cep, bairro,
                    latitude=location.latitude,
                    longitude=location.longitude,
                    tipo_match=tipo_match,
                )
        return None

    def get_coordinates(self, row, cep_col: str, rua_col: str, bairro_col: str) -> dict:
        bairro = normalizar_texto(row[bairro_col])
        rua = normalizar_texto(row[rua_col])
        cep = limpar_cep(row[cep_col])
        rua_corrigida = self.corrigir_nome_rua(rua)
        cache_key = f"cep:{cep}|rua:{rua_corrigida}|bairro:{bairro}"

        if cache_key in self.cache:
            return self.cache[cache_key].copy()

        try:
            return self._get_coordinates_uncached(cep, bairro, rua_corrigida, cache_key)
        except GeocodingUnavailable:
            resultado = self._build_payload(cep, bairro, tipo_match="erro_geocodificacao")
            self.cache[cache_key] = resultado.copy()
            return resultado

    def _get_coordinates_uncached(self, cep, bairro, rua_corrigida, cache_key) -> dict:
        if cep:
            resultado = self._tentar_geocodificar(
                [f"{cep}, Brasil", f"CEP {cep}, Brasil"], "cep", cep, bairro
            )
            if resultado:
                self.cache[cache_key] = resultado.copy()
                return resultado

        if rua_corrigida and bairro:
            resultado = self._tentar_geocodificar(
                [
                    f"{rua_corrigida}, {bairro}, Recife, Pernambuco, Brasil",
                    f"rua {rua_corrigida}, {bairro}, Recife, Pernambuco, Brasil",
                    f"avenida {rua_corrigida}, {bairro}, Recife, Pernambuco, Brasil",
                    f"travessa {rua_corrigida}, {bairro}, Recife, Pernambuco, Brasil",
                ],
                "rua_bairro", cep, bairro,
            )
            if resultado:
                self.cache[cache_key] = resultado.copy()
                return resultado

        if bairro:
            resultado = self._tentar_geocodificar(
                [f"{bairro}, Recife, Pernambuco, Brasil"], "bairro", cep, bairro
            )
            if resultado:
                self.cache[cache_key] = resultado.copy()
                return resultado

        resultado = self._build_payload(cep, bairro, tipo_match="nao_encontrado")
        self.cache[cache_key] = resultado.copy()
        return resultado


def geocode_dataframe(
    df: pd.DataFrame,
    cep_col: str,
    rua_col: str,
    bairro_col: str,
    on_progress=None,
) -> pd.DataFrame:
    """Geocode every row of df, returning the original columns plus the
    geocoding result columns appended. Calls on_progress(done, total)
    after each row, since Nominatim's ~1 req/s rate limit makes this
    slow enough that callers need progress feedback.
    """
    service = GeocodingService(df, rua_col)
    required_columns = ["CEP_processado", "latitude", "longitude", "bairro_utilizado", "tipo_match"]

    total = len(df)
    results = []
    for i, (_, row) in enumerate(df.iterrows()):
        results.append(service.get_coordinates(row, cep_col, rua_col, bairro_col))
        if on_progress:
            on_progress(i + 1, total)

    results_df = pd.DataFrame(results)
    for column in required_columns:
        if column not in results_df.columns:
            results_df[column] = None
    results_df = results_df[required_columns]

    return pd.concat([df.reset_index(drop=True), results_df.reset_index(drop=True)], axis=1)
