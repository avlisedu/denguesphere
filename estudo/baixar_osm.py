"""Baixa do OpenStreetMap (Overpass) a malha viária nomeada e os limites de
bairros do Recife, usados como base local de geocodificação."""
import json
import time
from pathlib import Path

import requests

DADOS = Path(__file__).resolve().parent / "dados"
URLS = ["https://overpass-api.de/api/interpreter", "https://maps.mail.ru/osm/tools/overpass/api/interpreter"]
AREA = 'area["boundary"="administrative"]["name"="Recife"]["admin_level"="8"]->.r;'

CONSULTAS = {
    "municipio": '[out:json][timeout:180];relation["boundary"="administrative"]["name"="Recife"]["admin_level"="8"];out geom;',
    "bairros": f'[out:json][timeout:180];{AREA}relation(area.r)["boundary"="administrative"]["admin_level"="10"];out geom;',
    "ruas": f'[out:json][timeout:300];{AREA}way(area.r)["highway"]["name"];out tags geom;',
    # mapa base: corpos d'água e áreas alagadas (mangues), só para as figuras
    "agua": f'[out:json][timeout:300];{AREA}(way(area.r)["natural"~"water|wetland"];relation(area.r)["natural"~"water|wetland"];'
            f'way(area.r)["waterway"~"riverbank|river|canal|stream"];relation(area.r)["waterway"="riverbank"];);out tags geom;',
}


def baixar(nome: str, consulta: str) -> None:
    destino = DADOS / f"osm_{nome}.json"
    if destino.exists():
        return
    for tentativa in range(6):
        url = URLS[tentativa % len(URLS)]
        try:
            r = requests.post(url, data={"data": consulta}, headers={"User-Agent": "denguesphere-estudo"}, timeout=400)
            if r.ok and r.text.lstrip().startswith("{"):
                dados = r.json()
                if dados.get("elements"):
                    destino.write_text(json.dumps(dados))
                    print(nome, len(dados["elements"]), "elementos")
                    return
            print(nome, "falhou", r.status_code, r.text[:120])
        except requests.RequestException as e:
            print(nome, "erro", e)
        time.sleep(15)
    raise SystemExit(f"não consegui baixar {nome}")


if __name__ == "__main__":
    DADOS.mkdir(exist_ok=True)
    for nome, consulta in CONSULTAS.items():
        baixar(nome, consulta)
