from bs4 import BeautifulSoup as bs
import requests
import re
import logging
import pandas as pd
import sqlite3
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

base_url = 'https://www.imdb.com'

base_headers = {
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0'
}

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(message)s')

top_250_list = base_url + '/chart/top/?ref_=nv_mv_250'

def main():
    get_movie_list(top_250_list)

def get_movie_list(list):
    try:
        response = requests.get(list)
    except requests.exceptions.RequestException as e:
        log.error('\nNão foi possível obter lista de filmes.\nDados do Erro: ')
        raise SystemExit(e)
    
    parsed_response = bs(response.text, "html.parser")
    movie_list = parsed_response.select('td.titleColumn')
    log.info("\nObtendo lista de filmes\n")
    get_links(movie_list)

def get_links(movie_list):
    link_list = []
    log.info("\nAdquirindo links individuais dos filmes listados\n")

    for movie in movie_list:
        link = base_url + movie.find('a').get('href')
        link_list.append(link)
    get_movie_details(link_list)

def get_movie(link):
    try:
        movie_request = requests.get(link, headers=base_headers)
    except requests.exceptions.RequestException as e:
        log.error(f'\nHouve um erro ao acessar os dados do filme: {link}.\nDados do Erro: ')
        raise SystemExit(e)
    return movie_request
    
def get_movie_details(link_list):
    detais_list = []
        
    log.info("\nIniciando Scraping\n")
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        for movie in executor.map(get_movie ,link_list):
            if(movie.status_code != 200):
                raise Exception("Houve algum erro de conexão. Não foi possível completar busca") 
            movie_details = bs(movie.text, "html.parser").find('section',class_='ipc-page-section')

            title = movie_details.find('h1', attrs={'data-testid': 'hero-title-block__title'}).text

            log.info(f'\nExtraindo informações do filme: {title}\n')
            
            metadata = movie_details.find('ul', attrs={'data-testid': 'hero-title-block__metadata'}).find_all('li', class_='ipc-inline-list__item')

            # Formatação básica caso tenha mais de uma estrela, diretor ou escritor
            stars = movie_details.find(text=re.compile('Star')).parent.nextSibling.text
            for stars_pattern in  re.findall(r'[^\s-][A-Z]', stars):
                stars = stars.replace(stars_pattern, ', '.join(stars_pattern))
            
            director = movie_details.find('button', text=re.compile('Director'))
            
            # Validação para o caso específico de múltiplos diretores/ diretores não creditados
            if director == None:
                director = movie_details.find('a', text=re.compile('Director')).parent.text
            else:
                director = director.parent.find(role="presentation").text
            for director_pattern in  re.findall(r'[^\s-][A-Z]', director):
                director = director.replace(director_pattern, ', '.join(director_pattern))

            writer = movie_details.find(text=re.compile('Writer')).parent.nextSibling.text
            for writer_pattern in  re.findall(r'\)[A-Z]', writer):
                writer = writer.replace(writer_pattern, ', '.join(writer_pattern))

            description = movie_details.find(attrs={'data-testid': 'plot'})

            # Tratativa caso a descrição seja loga demais, requerindo o clique no Read More...
            if description.find('a',attrs={'data-testid':'plot-read-all-link'}) == None:
                description = description.find('span').text
            else:
                description = description.find('a',attrs={'data-testid':'plot-read-all-link'}).parent.nextSibling.text
        
            
            movie_data = {
                'title' : title,
                'year' : metadata[0].find('span').string, 
                'movieLength' : metadata[2].text, 
                'description' : description, 
                'director' : director, 
                'writer' : writer, 
                'stars' : stars, 
                'imbdRating' : movie_details.find('div',attrs={'data-testid':'hero-rating-bar__aggregate-rating__score'}).text
            }
            detais_list.append(movie_data)

    movies_output(detais_list)

def movies_output(detais_list):
        # Formatação dos dados em data frame(Pandas)
    movies_df = pd.DataFrame(detais_list, columns=[
        'title',
        'year',
        'movieLength',
        'description',
        'director',
        'writer',
        'stars',
        'imbdRating'
    ])

    # Data para geração dos arquivos
    date = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
    # Formatação dos dados em csv
    movies_df.to_csv(f'./dados/imdb-top-250_{date}.csv', index=False, sep=';')
    log.info(f'\nDados salvos em csv\n')

    # Formatação dos dados em json
    movies_json = movies_df.to_json(orient='records')
    log.info(f'\nDados salvos em json\n')

    # Inserindo dados em um banco SQLite
    database = f'./dados/db_{date}.sqlite'
    connection = sqlite3.connect(database)
    movies_df.to_sql(name='imdb-top-250', con=connection)
    log.info(f'\nDados salvos em SQLite\n')

    log.info(f'\n\n\nConsulta finalizada.\n\n\n')

if __name__ == "__main__":
    main()
