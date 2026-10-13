"""Gera as tabelas LaTeX (artigo/tabelas/*.tex) a partir de resultados/*.csv,
para que nenhum número do texto seja transcrito à mão."""
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent
RES = RAIZ / "resultados"
TAB = RAIZ / "artigo" / "tabelas"
CONFIG = (0.3, 3)  # escolhida no treino (ver log de analises.py)


def n(v, d=1):
    """Número no padrão brasileiro: 1.234,5."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "--"
    s = f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if s.startswith("-"):
        s = s[1:] if not s.strip("-0,.") else "$-$" + s[1:]
    return s


def iqr(s, d=2):
    return f"{n(s.median(), d)} [{n(s.quantile(.25), d)}--{n(s.quantile(.75), d)}]"


def tabela(nome, legenda, rotulo, cabecalho, linhas, alinhamento, nota=None, largo=False, pequeno=True):
    amb = "table*" if largo else "table"
    corpo = "\n".join(linhas)
    texto = (
        f"\\begin{{{amb}}}[htbp]\n\\centering\n" + ("\\small\n" if pequeno else "") +
        f"\\caption{{{legenda}}}\n\\label{{{rotulo}}}\n"
        f"\\begin{{adjustbox}}{{max width=\\linewidth}}\n\\begin{{tabular}}{{{alinhamento}}}\n\\toprule\n{cabecalho} \\\\\n\\midrule\n{corpo}\n\\bottomrule\n\\end{{tabular}}\n\\end{{adjustbox}}\n"
        + (f"\\par\\smallskip\\begin{{minipage}}{{0.95\\linewidth}}\\footnotesize {nota}\\end{{minipage}}\n" if nota else "")
        + f"\\end{{{amb}}}\n"
    )
    (TAB / f"{nome}.tex").write_text(texto)


def t_casos():
    t = pd.read_csv(RES / "tab1_casos_por_ano.csv")
    linhas = []
    for _, r in t.iterrows():
        total = r["ano_epi"] == "Total"
        if total:
            linhas.append("\\midrule")
        linhas.append(" & ".join([
            "\\textbf{Total}" if total else str(r["ano_epi"]), n(r["notificados"], 0), n(r["confirmados"], 0),
            n(r["incidencia_100mil"]), n(r["pct_nivel_rua"]), n(r["pct_centroide_bairro"]), n(r["pct_nao_encontrado"]),
            "--" if total else n(r["pico_semanal"], 0), "--" if total else n(r["se_pico"], 0)]) + " \\\\")
    tabela("tab_casos_ano",
           "Notificações, casos confirmados, incidência e precisão da geocodificação por ano epidemiológico, Recife, 2013--2025.",
           "tab:casos",
           "Ano & Notificados & Confirmados & Incid./100 mil & Rua (\\%) & Bairro (\\%) & Não enc. (\\%) & Pico/sem. & SE do pico",
           linhas, "lrrrrrrrr",
           nota="Notificados: residentes no Recife com data válida (qualquer classificação). Incidência: confirmados por "
                "100 mil habitantes (Censo 2022, 1.488.924 hab.); na linha Total, média anual. Rua: geocodificado no nível de "
                "logradouro (no bairro informado, em bairro vizinho ou único na cidade). Bairro: ponto representativo do "
                "polígono do bairro. SE: semana epidemiológica. O arquivo de 2014 contém notificações apenas até julho.")


def t_validacao():
    t = pd.read_csv(RES / "tab_validacao_geocodificacao.csv")
    t = t[(t["tipo_local"] != "nao_encontrado") & (t["n"] >= 9)]
    nome_nom = {"endereco_exato": "Endereço exato", "fallback_bairro": "Fallback bairro",
                "fallback_bairro_corrigido": "Fallback bairro corrigido", "rua_sem_bairro": "Rua sem bairro"}
    nome_loc = {"rua_bairro": "Rua no bairro", "rua_vizinha": "Rua em bairro vizinho", "rua_cidade": "Rua (cidade)",
                "bairro": "Centroide do bairro"}
    linhas, ant = [], None
    for _, r in t.iterrows():
        if ant is not None and r["fonte_nominatim"] != ant:
            linhas.append("\\addlinespace")
        linhas.append(" & ".join([nome_nom[r["fonte_nominatim"]] if r["fonte_nominatim"] != ant else "",
                                  nome_loc[r["tipo_local"]], n(r["n"], 0), n(r["mediana_m"], 0), n(r["p90_m"], 0),
                                  n(r["pct_ate_250m"]), n(r["pct_ate_500m"]), n(r["pct_ate_1km"])]) + " \\\\")
        ant = r["fonte_nominatim"]
    tabela("tab_validacao",
           "Distância entre a geocodificação local (OSM) e a do DengueSphere (Nominatim) na amostra de 2021 ($n = 1.219$).",
           "tab:validacao",
           "Nominatim & Local (OSM) & $n$ & Mediana (m) & P90 (m) & $\\leq$250 m & $\\leq$500 m & $\\leq$1 km",
           linhas, "llrrrrrr", nota="Colunas $\\leq$: percentual de casos a até a distância indicada. "
                                    "Categorias com $n < 9$ omitidas.")


def t_sensibilidade():
    d = pd.read_csv(RES / "sensibilidade_janelas.csv")
    d = d[d["eps_km"].isin([0.2, 0.3, 0.5, 0.75]) & d["min_samples"].isin([3, 5, 10])]
    linhas = []
    for niv in ["baixa (<100 casos/4 sem)", "média (100–400)", "alta (>400)"]:
        sub = d[d["nivel"] == niv]
        rot = {"baixa (<100 casos/4 sem)": "Baixa ($<$100)", "média (100–400)": "Média (100--400)", "alta (>400)": "Alta ($>$400)"}[niv]
        linhas.append(f"\\multicolumn{{6}}{{l}}{{\\textit{{Incidência {rot[0].lower() + rot[1:]}; {sub['semana_final'].nunique()} janelas}}}} \\\\")
        for (e, m), g in sub.groupby(["eps_km", "min_samples"]):
            linhas.append(" & ".join(["", n(e, 2), str(m), iqr(g["n_clusters"], 0), iqr(g["pct_ruido"], 0),
                                      n((g["n_clusters"] > 0).mean() * 100, 0)]) + " \\\\")
        linhas.append("\\addlinespace")
    tabela("tab_sensibilidade",
           "Sensibilidade do DBSCAN aos parâmetros, por nível de incidência da janela de 4 semanas (mediana [IIQ]).",
           "tab:sensibilidade", "& eps (km) & min\\_samples & Nº de clusters & Ruído (\\%) & Janelas c/ cluster (\\%)",
           linhas[:-1], "llrrrr", nota="Janelas de 4 semanas não sobrepostas com ao menos 30 casos geocodificados no "
                                       "nível de rua. IIQ: intervalo interquartil.")


def t_estabilidade():
    e = pd.read_csv(RES / "estabilidade_janelas.csv")

    def rel(r):
        p = r["perturbacao"]
        if p.startswith("min_samples"):
            v = int(p.split()[1])
            return "m-1" if v < r["min_samples"] else "m+1"
        return {"eps 0.90x": "e-", "eps 1.10x": "e+", "subamostra 90%": "sub"}[p]
    e["rel"] = e.apply(rel, axis=1)
    linhas = []
    for (eps, m), g in e.groupby(["eps_km", "min_samples"]):
        cel = [n(g.loc[g["rel"] == k, "ari"].median(), 2) if (g["rel"] == k).any() else "--"
               for k in ["e-", "e+", "m-1", "m+1", "sub"]]
        linhas.append(" & ".join([n(eps, 2), str(m), str(g["semana_final"].nunique())] + cel) + " \\\\")
    tabela("tab_estabilidade",
           "Estabilidade dos agrupamentos: ARI mediano entre a solução de referência e a solução perturbada.",
           "tab:estabilidade",
           "eps (km) & min\\_samples & Janelas & eps $\\times$0,9 & eps $\\times$1,1 & min\\_samples $-$1 & min\\_samples $+$1 & Subamostra 90\\%",
           linhas, "rrrrrrrr", nota="ARI: índice de Rand ajustado (1 = partições idênticas). Perturbações de parâmetros "
                                    "calculadas com \\texttt{stability\\_analysis} do DengueSphere; subamostra: 10 réplicas "
                                    "por janela, ARI sobre os casos retidos. Excluídas as janelas sem cluster na referência, "
                                    "em que o ARI seria 1 trivialmente.")


def t_grade_prospectiva():
    t = pd.read_csv(RES / "tab4a_prospectiva_grade_dbscan.csv")
    tr, te = t[t["conjunto"] == "treino"].set_index(["eps_km", "min_samples"]), t[t["conjunto"] == "teste"].set_index(["eps_km", "min_samples"])
    linhas = []
    for (e, m) in tr.index:
        a, b = tr.loc[(e, m)], te.loc[(e, m)]
        cel = [n(e, 2), str(m), n(a["pct_janelas_com_alerta"], 0), n(a["captura_med"]), n(a["area_med"], 2), n(a["pai_med"], 2),
               n(b["pct_janelas_com_alerta"], 0), n(b["captura_med"]), n(b["area_med"], 2), n(b["pai_med"], 2), n(b["pai_pop_med"], 2)]
        if (e, m) == CONFIG:
            cel = [f"\\textbf{{{c}}}" for c in cel]
        linhas.append(" & ".join(cel) + " \\\\")
    tabela("tab_grade_prospectiva",
           "Desempenho prospectivo do DBSCAN na grade de parâmetros (medianas por janela). Em negrito, a configuração "
           "escolhida no treino.",
           "tab:grade",
           "& & \\multicolumn{4}{c}{Treino (2013--2019)} & \\multicolumn{5}{c}{Teste (2020--2025)} \\\\\n"
           "\\cmidrule(lr){3-6}\\cmidrule(lr){7-11}\neps & min\\_s. & Alerta \\% & Capt. \\% & Área \\% & PAI & Alerta \\% & Capt. \\% & Área \\% & PAI & PAI$_\\text{pop}$",
           linhas, "rrrrrrrrrrr", largo=True,
           nota="Alerta: \\% de janelas em que o DBSCAN encontrou ao menos um cluster. Captura: \\% dos casos das 4 semanas "
                "seguintes dentro da área sinalizada (zero quando não há alerta). Área: \\% da área do município (219,3 km$^2$). "
                "PAI = Captura/Área e PAI$_\\text{pop}$ = Captura/\\% da população, calculados apenas nas janelas com alerta. "
                "Critério de escolha: maior PAI mediano no treino entre as configurações com alerta em $\\geq$80\\% das janelas.")


ORDEM = ["DBSCAN (DengueSphere)", "KDE (mesma área)", "Ranking de bairros", "População (mesma área)",
         "Todos os casos (sem clusterizar)"]
ROTULO = {"Ranking de bairros": "Ranking de bairros (incidência)"}


def t_comparacao():
    pj = pd.read_csv(RES / "prospectiva_janelas.csv")
    sel = pj[(pj["variante"] == "confirmados, nível de rua") & (pj["eps_km"] == CONFIG[0]) & (pj["min_samples"] == CONFIG[1])]
    linhas = []
    for mt in ORDEM:
        rot = ROTULO.get(mt, mt)
        cel = ["\\textbf{DBSCAN (DengueSphere)}" if mt.startswith("DBSCAN") else rot]
        tr = sel[(sel["conjunto"] == "treino") & (sel["metodo"] == mt) & sel["pai"].notna()]
        te = sel[(sel["conjunto"] == "teste") & (sel["metodo"] == mt) & sel["pai"].notna()]
        cel += [n(tr["pai"].median(), 2), n(tr["pai_pop"].median(), 2),
                n(te["captura_pct"].median()), n(te["area_pct"].median(), 2), n(te["pop_pct"].median(), 2),
                iqr(te["pai"]), iqr(te["pai_pop"])]
        linhas.append(" & ".join(cel) + " \\\\")
    tabela("tab_comparacao",
           f"Validação prospectiva: DBSCAN ($\\varepsilon$ = {n(CONFIG[0], 1)} km, min\\_samples = {CONFIG[1]}) e métodos de "
           "referência na previsão dos casos das 4 semanas seguintes (medianas por janela com alerta).",
           "tab:comparacao",
           "& \\multicolumn{2}{c}{Treino} & \\multicolumn{5}{c}{Teste (2020--2025)} \\\\\n"
           "\\cmidrule(lr){2-3}\\cmidrule(lr){4-8}\nMétodo & PAI & PAI$_\\text{pop}$ & Capt. \\% & Área \\% & Pop. \\% & PAI [IIQ] & PAI$_\\text{pop}$ [IIQ]",
           linhas, "lrrrrrrr", largo=True,
           nota="PAI = captura/\\% da área; PAI$_\\text{pop}$ = captura/\\% da população residente (Censo 2022) na área "
                "sinalizada. KDE: células com maior densidade kernel ($\\sigma$ = $\\varepsilon$) até a mesma área do DBSCAN. "
                "Ranking de bairros: bairros inteiros por incidência (casos/habitante) na janela até atingir a área do DBSCAN. "
                "População: células mais populosas, com a mesma área do DBSCAN, sem informação de casos. Todos os casos: buffer "
                "de raio $\\varepsilon$ em torno de todos os casos da janela, sem clusterização.")

    from scipy.stats import wilcoxon
    linhas = []
    for metrica, rot_m in [("pai", "PAI"), ("pai_pop", "PAI$_\\text{pop}$")]:
        for conj in ["treino", "teste"]:
            piv = sel[sel["conjunto"] == conj].pivot_table(index="semana_final", columns="metodo", values=metrica)
            for ref in ORDEM[1:]:
                a, b = piv[ORDEM[0]], piv[ref]
                ok = a.notna() & b.notna()
                p = wilcoxon(a[ok], b[ok]).pvalue
                linhas.append(" & ".join([rot_m if (conj == "treino" and ref == ORDEM[1]) else "",
                                          conj.capitalize() if ref == ORDEM[1] else "", ROTULO.get(ref, ref), str(int(ok.sum())),
                                          n((a[ok] > b[ok]).mean() * 100), n((a[ok] - b[ok]).median(), 2),
                                          "$<$0,001" if p < 0.001 else n(p, 3)]) + " \\\\")
            linhas.append("\\addlinespace")
        linhas.append("\\midrule")
    tabela("tab_pareada",
           "Comparação pareada, janela a janela, do DBSCAN com cada método de referência (teste de Wilcoxon).",
           "tab:pareada", "Métrica & Período & Referência & Janelas & DBSCAN melhor (\\%) & $\\Delta$ mediano & $p$",
           linhas[:-2], "lllrrrr",
           nota="$\\Delta$ = métrica do DBSCAN $-$ métrica da referência, por janela; valores positivos favorecem o DBSCAN. "
                "As janelas semanais se sobrepõem (3 das 4 semanas), de modo que os valores de $p$ são aproximados.")


def t_guia():
    t = pd.read_csv(RES / "tab4b_guia_parametros_por_nivel.csv")
    linhas = []
    rot = {"baixa (<100 casos/4 sem)": "Baixa ($<$100)", "média (100–400)": "Média (100--400)", "alta (>400)": "Alta ($>$400)"}
    for niv, g in t.groupby("nivel", sort=False):
        d = g[g["metodo"].str.startswith("DBSCAN")].set_index("conjunto")
        k = g[g["metodo"].str.startswith("KDE")].set_index("conjunto")
        linhas.append(" & ".join([rot[niv], n(d["eps_km"].iloc[0], 1), str(int(d["min_samples"].iloc[0])),
                                  n(d.loc["treino", "pct_janelas_com_alerta"], 0), n(d.loc["teste", "pct_janelas_com_alerta"], 0),
                                  n(d.loc["treino", "pai_med"], 2), n(d.loc["teste", "pai_med"], 2),
                                  n(k.loc["teste", "pai_med"], 2), n(d.loc["teste", "pai_pop_med"], 2),
                                  n(d.loc["teste", "area_med"], 2)]) + " \\\\")
    tabela("tab_guia",
           "Parâmetros escolhidos no treino para cada nível de incidência e seu desempenho no teste.",
           "tab:guia",
           "Incidência (casos/4 sem.) & $\\varepsilon$ & min\\_s. & Alerta treino \\% & Alerta teste \\% & PAI treino & PAI teste & PAI KDE teste & PAI$_\\text{pop}$ teste & Área teste \\%",
           linhas, "lrrrrrrrrr", largo=True, nota="Mesmo critério de escolha da Tabela~\\ref{tab:grade}, aplicado dentro de cada estrato.")


def t_variantes():
    pj = pd.read_csv(RES / "prospectiva_variantes_janelas.csv")
    nomes = {"confirmados, nível de rua": "Principal: confirmados, nível de rua",
             "não descartados, nível de rua": "Não descartados (tempo real), nível de rua",
             "confirmados, incl. centroide de bairro": "Confirmados, incluindo centroides de bairro"}
    linhas = []
    for var, rot in nomes.items():
        g = pj[pj["variante"] == var]
        db = g[g["metodo"].str.startswith("DBSCAN")]
        ok = g[g["pai"].notna()]
        med = lambda mt, col: ok.loc[ok["metodo"] == mt, col].median()
        linhas.append(" & ".join([rot, str(db["semana_final"].nunique()), n(db["sinalizou"].mean() * 100, 0),
                                  n(med("DBSCAN (DengueSphere)", "captura_pct")), n(med("DBSCAN (DengueSphere)", "pai"), 2),
                                  n(med("DBSCAN (DengueSphere)", "pai_pop"), 2), n(med("KDE (mesma área)", "pai_pop"), 2),
                                  n(med("Ranking de bairros", "pai_pop"), 2), n(med("População (mesma área)", "pai_pop"), 2)]) + " \\\\")
    tabela("tab_variantes",
           "Análise de sensibilidade da validação prospectiva (2013--2025, configuração principal; medianas nas janelas com alerta).",
           "tab:variantes",
           "& & & & \\multicolumn{2}{c}{DBSCAN} & \\multicolumn{3}{c}{PAI$_\\text{pop}$ das referências} \\\\\n"
           "\\cmidrule(lr){5-6}\\cmidrule(lr){7-9}\nVariante & Janelas & Alerta \\% & Capt. \\% & PAI & PAI$_\\text{pop}$ & KDE & Bairros & População",
           linhas, "lrrrrrrrr", largo=True,
           nota="Não descartados: confirmados, inconclusivos e sem classificação final --- o conjunto disponível à vigilância "
                "antes do encerramento das investigações. Com centroides de bairro, casos empilhados no mesmo ponto formam "
                "clusters artificiais, o que infla a captura.")


def t_persistencia():
    t = pd.read_csv(RES / "tab7_persistencia_interanual.csv")
    cols = ["spearman_celulas_500m", "spearman_incidencia_bairro", "jaccard_top10pct", "pct_area_top10",
            "pct_casos_seguinte_no_top10_anterior"]
    linhas = [" & ".join([f"{int(r['ano'])}--{int(r['ano_seguinte'])}"] + [n(r[c], 2 if i < 3 else 1) for i, c in enumerate(cols)]) + " \\\\"
              for _, r in t.iterrows()]
    linhas += ["\\midrule", " & ".join(["Média"] + [n(t[c].mean(), 2 if i < 3 else 1) for i, c in enumerate(cols)]) + " \\\\"]
    tabela("tab_persistencia", "Persistência espacial entre anos consecutivos.", "tab:persistencia",
           "& \\multicolumn{2}{c}{Spearman} & & & \\\\\n\\cmidrule(lr){2-3}\n"
           "Anos & Células 500 m & Incidência bairro & Jaccard top 10\\% & Células top 10\\% (\\%) & Casos seguintes no top 10\\% (\\%)",
           linhas, "lrrrrr", nota="Células: contagem de casos por célula de 500 m. Incidência bairro: casos por habitante nos "
                                  "bairros com pelo menos 1.000 moradores. Top 10\\%: células no decil superior de casos do ano "
                                  "anterior (empates incluídos).")


def t_incidencia():
    t = pd.read_csv(RES / "tab_incidencia_bairros.csv").head(15)
    linhas = [" & ".join([str(i + 1), r["bairro"], n(r["populacao_2022"], 0), n(r["casos_2013_2025"], 0),
                          n(r["incidencia_media_anual_100mil"])]) + " \\\\" for i, r in t.iterrows()]
    tabela("tab_incidencia", "Bairros com maior incidência média anual de dengue, 2013--2025.", "tab:incidencia",
           "& Bairro & População (2022) & Casos & Incidência média anual/100 mil", linhas, "rlrrr",
           nota="Casos confirmados com bairro identificado (inclui casos localizados pelo centroide). Apenas bairros com "
                "pelo menos 5.000 habitantes. População estimada por ponderação areal dos setores censitários.")


def t_desempenho():
    t = pd.read_csv(RES / "tab8_desempenho.csv").pivot_table(index="n_casos", columns="eps_km", values="tempo_s_mediana")
    linhas = [" & ".join([n(i, 0), n(r[0.3] * 1000, 0), n(r[0.5] * 1000, 0)]) + " \\\\" for i, r in t.iterrows()]
    tabela("tab_desempenho", "Tempo de execução da clusterização do DengueSphere (mediana de 3 execuções).", "tab:desempenho",
           "Casos & eps = 0,3 km (ms) & eps = 0,5 km (ms)", linhas, "rrr",
           nota="\\texttt{executar\\_clusterizacao} (DBSCAN, métrica haversine, \\textit{ball tree}), min\\_samples = 10; "
                "Apple M2, 16 GB, Python 3.11, scikit-learn.")


def t_classificacao():
    c = pd.read_csv(RES / "tab_classificacao_por_ano.csv", index_col=0)
    k = pd.read_csv(RES / "tab_criterio_confirmacao.csv", index_col=0)
    conf = [x for x in c.columns if x.split()[0] in {"1", "2", "3", "4", "10", "11", "12"}]
    linhas = []
    for ano, r in c.iterrows():
        linhas.append(" & ".join([str(ano), n(r[conf].sum(), 0), n(r.get("5 Descartado", 0), 0), n(r.get("8 Inconclusivo", 0), 0),
                                  n(r.get("Sem classificação", 0), 0), n(k.loc[ano, "laboratorial"]),
                                  n(k.loc[ano, "clinico_epidemiologico"])]) + " \\\\")
    tabela("tab_classificacao", "Classificação final das notificações e critério de confirmação dos casos confirmados, por ano.",
           "tab:classificacao", "Ano & Confirmados & Descartados & Inconclusivos & Sem classif. & Laboratorial (\\%) & Clínico-epid. (\\%)",
           linhas, "lrrrrrr", nota="Confirmados: códigos 1--4 (classificação até 2014: dengue clássico, com complicações, FHD, SCD) "
                                    "e 10--12 (classificação de 2014: dengue, com sinais de alarme, grave).")


if __name__ == "__main__":
    TAB.mkdir(parents=True, exist_ok=True)
    for f in [t_casos, t_validacao, t_sensibilidade, t_estabilidade, t_grade_prospectiva, t_comparacao, t_guia,
              t_variantes, t_persistencia, t_incidencia, t_desempenho, t_classificacao]:
        f()
    print(sorted(p.name for p in TAB.glob("*.tex")))
