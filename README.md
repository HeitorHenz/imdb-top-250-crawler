
# IMDb crawler
O seguinte projeto extrai os dados dos 250 filmes mais bem avaliados do IMDb, disponível em:
https://www.imdb.com/chart/top/?ref_=nv_mv_250

---

## Para executar o crawler:

O crawler pode ser executado de duas maneiras:

### Utilizando Docker. Para isso, basta ter o daemon rodando e executar os comandos:

    docker build -t crawler-image .

    docker run -v ${PWD}/dados/:/usr/src/app/dados crawler-image

### Com Python localmente. Basta ter qualquer instalação recente e executar:

    pip install --no-cache-dir -r requirements.txt

    py .\crawler.py

## NOTA:

É importante ter em mente que, em comparação, rodar o projeto diretamente no Python é substancialmente mais veloz.

---

## Bibliotecas utilizadas:
### Beautiful Soup(bs4) -> Para processamento dos dados brutos
### Requests -> Para executar as requisições
### Pandas -> Para a posterior organização dos dados após o processo de crawling