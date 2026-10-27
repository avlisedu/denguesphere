# Camadas de referência do Recife

Arquivos usados pelas caixas de "Camadas de referência" na página Clusterizar Casos.

| Arquivo | Conteúdo | Fonte |
| --- | --- | --- |
| `recife/unidades_saude.csv` | 182 unidades de saúde com coordenadas (USF, UBS, policlínicas, pronto atendimento, hospitais, maternidades e Vigilância de Zoonoses) | [Rede de atenção à saúde no Recife](https://dados.recife.pe.gov.br/dataset/rede-de-atencao-a-saude-no-recife), Portal de Dados Abertos da Prefeitura do Recife, versão de 04/03/2026, licença ODbL. Gerado com `scripts/gerar_unidades_saude.py`. |
| `recife/bairros_distritos.csv` | Distrito Sanitário de cada um dos 94 bairros, com os nomes da malha de bairros do IBGE (Censo 2022) | [Anexo 4.3, Seleção de Terrenos e Condicionantes](https://parcerias.recife.pe.gov.br/wp-content/uploads/2023/10/ANEXO-04.3-SELECAO-DE-TERRENOS-E-CONDICIONANTES.pdf), seção 3.2, Prefeitura do Recife, 2023 |
| `recife/sedes_distritos.csv` | Endereço, telefone e coordenadas das sedes dos 8 Distritos Sanitários | Endereços informados pela equipe; coordenadas pelo Nominatim (OpenStreetMap). A coluna `precisao` indica se o ponto foi achado pelo número do imóvel ou só pela rua. |

Na Rede de atenção à saúde, as unidades dos bairros Barro e Prado aparecem nos DS VIII e DS V, enquanto o Anexo 4.3 coloca esses bairros nos DS V e DS IV. Foi mantido o Anexo 4.3.
