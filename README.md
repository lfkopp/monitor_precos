# Monitor de Precos - Supermercados RJ

Monitoramento automatico de precos de supermercados do Rio de Janeiro via APIs publicas.

## Supermercados Monitorados

| Supermercado | Tipo | API | Status |
|-------------|------|-----|--------|
| **Zona Sul** | Varejo | GraphQL VTEX | ✅ Ativo |
| **Guanabara** | Varejo | HTML Scraping | ✅ Ativo |
| **Atacadao** | Atacarejo | Catalog VTEX | ✅ Ativo |
| **Prezunic** | Varejo | Catalog VTEX | ✅ Ativo |
| **Pao de Acucar** | Varejo | GPA/Linx API | ✅ Ativo |

## Estrutura

```
monitor_precos/
├── zsul.py              # Scraper Zona Sul (GraphQL VTEX)
├── guanabara.py         # Scraper Guanabara (HTML)
├── atacadao.py          # Scraper Atacadao (Catalog VTEX)
├── prezunic.py          # Scraper Prezunic (Catalog VTEX)
├── paodeacucar.py       # Scraper Pao de Acucar (GPA/Linx API)
├── requirements.txt     # Dependencias Python
└── .github/workflows/
    └── python-app.yml   # CI/CD diario
```

## Formato de Saida

Dados salvos em arquivos `.txt` com separador `;`:

```csv
data;cod;produto;preco;unidade;fator_unid;cod_id;cod_sku;marca
2026-08-17;arroz-tio-joao-1kg;Arroz Tio Joao 1kg;8.99;kg;1.0;12345;67890;Tio Joao
```

Arquivos mensais: `zsul_202608.txt`, `atacadao_202608.txt`, `prezunic_202608.txt`, `paodeacucar_202608.txt`

## Execucao Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Rodar scripts individualmente
python zsul.py
python guanabara.py
python atacadao.py
python prezunic.py
python paodeacucar.py
```

## CI/CD

O GitHub Actions executa diariamente as 06:30 (horario de Brasilia):
1. Roda `guanabara.py`
2. Roda `zsul.py`
3. Roda `atacadao.py`
4. Roda `prezunic.py`
5. Roda `paodeacucar.py`
6. Commita alteracoes automaticamente

## Analises Possiveis

- Comparacao de precos entre redes
- Historico de precos (tendencias)
- Alertas de promocao (queda > 20%)
- Analise por categoria
- Previsao de precos (series temporais)

## Notas Tecnicas

- **Zona Sul**: Usa API GraphQL com clusters de produtos
- **Guanabara**: Scraping HTML direto (BeautifulSoup)
- **Atacadao**: API VTEX publica (catalog_system)
- **Prezunic**: API VTEX publica (catalog_system)
- **Pao de Acucar**: API GPA/Linx (POST category-page)
