
# IMDb crawler
O seguinte projeto extrai os dados dos 250 filmes mais bem avaliados do IMDb, disponível em:
https://www.imdb.com/chart/top/?ref_=nv_mv_250

## Para rodar o crawler, basta executar:

    docker build -t crawler-image .

    docker run -v ${PWD}/dados/:/usr/src/app/dados crawler-image
