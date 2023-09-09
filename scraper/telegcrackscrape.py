import argparse
import os
import requests
import json
import logging

from datetime import datetime, timedelta
from tqdm import tqdm

import extra

logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    filename="scraper.log",  # Specify the log file
    format="%(asctime)s [%(levelname)s] - %(message)s",  # Define log message format
    datefmt="%Y-%m-%d %H:%M:%S",  # Define date and time format
)

class Scraper(object):
    def __init__(self, query):
        self.input_query = query
        self.session = requests.Session()
        self.cache_file = query + '_cache_store'
        self.cache_path = os.path.join(os.path.dirname(__file__), 'cache', self.cache_file)
        self.currentdate = datetime.now()
        self.headers = extra.visitinfo
        root = os.getcwd()
        self.query_path = os.path.join(root, query)
        if not os.path.exists(self.query_path):
            os.makedirs(self.query_path)
        os.chdir(self.query_path)
        self.getCache()
        self.indexQuery()
        self.updateCache()
        logging.info(f'Initialized scraper for query: {query}')
    
    def getCache(self):
        """
        Loads cached data from the cache file or initializes an empty cache if none is found
        :params: none
        :return: none
        """
        try:
            with open(self.cache_path, 'r', encoding='utf-8') as f:
                f.seek(0)
                self.cache = json.load(f)
            logging.info(f'Loaded cached data from: {self.cache_path}')
        except Exception:
            self.cache = {}
            logging.info(f'Loaded cached data from: {self.cache_path}')
        self.newQuery()

    def updateCache(self):
        '''
        Updates the cache with the current page list and date and writes it to the cache file
        :params: none
        :return: none
        '''
        self.cache = {
            'pagelist':self.pagelist[:],
            'date':self.currentdate
        }

        cache_dir = os.path.dirname(self.cache_path)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        with open(self.cache_path, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=4, default=str)
        logging.info(f'Updated cache at: {self.cache_path}')
    
    def newQuery(self):
        '''
        Sets up the start and end dates for the query and initializes an empty or cached page list
        :params: none
        :return: none
        '''
        if self.cache:
            self.start_date = datetime.fromisoformat(self.cache['date'])
            self.end_date = self.currentdate
            self.pagelist = self.cache['pagelist'][:]
        else:
            self.start_date = datetime(2000, 1, 1) #leap year
            self.end_date = self.start_date + timedelta(366)
            self.pagelist = []

    def indexQuery(self):
        '''
        Iterates through a range of dates to fetch pages using the search query, appending valid pages to the pagelist
        :params: none
        :return: none
        '''
        logging.info(f'Indexing "{self.input_query}" pages...')
        index = 1
        delta = self.end_date - self.start_date
        self.outer_pbar = tqdm(
                total=delta.days,
                desc=f'Indexing "{self.input_query}" pages',
                unit=' page',
                position=0,
                leave=True
            )
        while self.start_date < self.end_date:
            formatted_date = self.start_date.strftime('%m-%d')
            search_query = [self.input_query, formatted_date]

            if index > 1:
                search_query.append(str(index))

            search_query = '-'.join(search_query)

            try:
                data = self.getJSON(search_query)
                if data['ok']:
                    self.pagelist.append(data)
                    index += 1
                    logging.info(f'Successfully fetched page data for {search_query}')
                else:
                    self.start_date += timedelta(days=1)
                    index = 1 #Reset the index
                    self.outer_pbar.update()
            except Exception as ex:
                logging.error(f'Error at {search_query}: {ex}')
        self.outer_pbar.close()    
                
    def getJSON(self, search_query):
        '''
        Sends an HTTP request to the Telegraph API to fetch page data for a given search query
        :params: search_query (str) - The search query for a single page
        :return: JSON response from the API
        '''
        try:
            result = self.session.get(
                f'https://api.telegra.ph/getPage/{search_query}?return_content=true',
                headers=self.headers
            ).json()
            logging.info(f'Successfully fetched JSON data for {search_query}')
        except Exception as ex:
            logging.error(f'Error while processing {search_query}: {ex}')
            result = None
        return result

    def getImages(self):
        '''
        Downloads images from indexed pages and stores them in corresponding directories
        :params: none
        :return: none
        '''
        self.outer_pbar = tqdm(
                total=len(self.pagelist),
                desc=f'Scrapping images from "{self.input_query}" pages',
                unit=' page',
                position=0,
                leave=True
            )
        for page in self.pagelist:
            page_name = page['result']['path']
            page_path = os.path.join(self.query_path, page_name)
            if not os.path.exists(page_path):
                os.makedirs(page_path)
            os.chdir(page_path)

            logging.info(f'Extracting image URLs from page "{page_name}"...')
            try:
                self.getImageList(page)
            except Exception as ex:
                logging.error(f'Error while processing page "{page_name}": {ex}')

            self.inner_pbar = tqdm(
                total=len(self.imagelist),
                desc=f'Downloading images from "{page_name}" page',
                unit=' image',
                position=1,
                leave=False
            )
            for index, file in enumerate(self.imagelist, start=1):
                try:
                    with open(f'{index}.jpg', 'wb') as f:
                        image_url = f'https://telegra.ph/file/{file}'
                        image_response = requests.get(
                            image_url,
                            stream=True,
                            headers=self.headers
                        )
                        f.write(image_response.content)
                    logging.info(f'Downloaded {index} of {len(self.imagelist)} images from page "{page_name}"')
                except requests.RequestException as ex:
                    logging.error(f'Error downloading image {file}: {ex}')
                except Exception as ex:
                    logging.error(f'Error while processing image {file}: {ex}')
                self.inner_pbar.update()
            self.inner_pbar.close()

            self.outer_pbar.update()
        self.outer_pbar.close()
            
    
    def getImageList(self, page):
        '''
        Extracts image URLs from the content of a given page and populates the imagelist
        :params: page (dict) - JSON data for a telegraph page
        :return: None
        '''
        content = page['result']['content']
        self.imagelist = [sub_tag['attrs']['src'][6:]
                        for item in content
                        if isinstance(item, dict) and item['tag'] == 'figure'
                        for sub_tag in item['children']
                        if sub_tag['tag'] == 'img']

    def getText(self):
        '''
        Gathers all text content from indexed pages and saves it into text files
        :params: none
        :return: none
        '''
        self.outer_pbar = tqdm(
                total=len(self.pagelist),
                desc=f'Scrapping text from "{self.input_query}" pages',
                unit=' page',
                position=0,
                leave=True
            )
        for page in self.pagelist:
            page_name = page['result']['path']
            page_path = os.path.join(self.query_path, page_name)
            if not os.path.exists(page_path):
                os.makedirs(page_path)
            os.chdir(page_path)
            
            logging.info(f'Collecting text from page "{page_name}"...')
            try:
                self.getTextList(page)
            except Exception as ex:
                logging.error(f'Error while processing page "{page_name}": {ex}')

            self.textlist = list(filter(None, self.textlist)) #filter empty values from textlist
            if self.textlist:
                with open('text.txt', 'w', encoding='utf-8') as f:
                    for line in self.textlist:
                        f.write(f'{line}\n')

            self.outer_pbar.update()
        self.outer_pbar.close()

    def getTextList(self, page):
        '''
        Collects all text from a given page and stores it in the textlist
        :params: page (dict) - JSON data for a telegraph page.
        :return: None
        '''
        content = page['result']['content']
        self.textlist = [child.replace('\n', ' ').strip()
                        for item in content
                        if 'tag' in item and item['tag'] == 'p'
                        for child in item.get('children', [])
                        if isinstance(child, str)]
    
    def getLinks(self):
        '''
        Gathers all links from indexed pages and saves them into a text file
        :params: page (dict) - JSON data for a telegraph page.
        :return: none
        '''
        self.outer_pbar = tqdm(
                total=len(self.pagelist),
                desc=f'Scrapping links from "{self.input_query}" pages',
                unit=' page',
                position=0,
                leave=True
            )
        for page in self.pagelist:
            page_name = page['result']['path']
            page_path = os.path.join(self.query_path, page_name)
            if not os.path.exists(page_path):
                os.makedirs(page_path)
            os.chdir(page_path)
            
            logging.info(f'Collecting links from page "{page_name}"...')
            try:
                self.getLinksList(page)
            except Exception as ex:
                logging.error(f'Error while processing page "{page_name}": {ex}')

            if self.linklist:
                with open('links.txt', 'w', encoding='utf-8') as f:
                    for line in self.linklist:
                        f.write(f'{line}\n')

            self.outer_pbar.update()
        self.outer_pbar.close()

    def getLinksList(self, page):
        '''
        Collects all links from a given page and stores them in the linklist
        :params: page (dict) - JSON data for a telegraph page.
        :return: none
        '''
        content = page['result']['content']
        self.linklist = [link['attrs']['href']
                        for item in content
                        if 'children' in item
                        for child in item['children']
                        if isinstance(child, dict) and child['tag'] == 'a'
                        for link in [child]]


    def getPagesUrl(self):
        '''
        Collects and stores the URLs of all indexed pages in a text file
        :params: none
        :return: none
        '''
        links = [page['result']['url'] for page in self.pagelist]
        os.chdir(self.query_path)
        with open(f'{self.input_query}.txt', 'w') as f:
            for link in links:
                f.write(f'{link}\n')

    def filterSpam(self):
        '''
        Filters out pages with authors in a predefined spam list from the pagelist
        :params: none
        :return: none
        '''
        logging.info(f'Filtering out spam pages...')
        for page in self.pagelist[:]:
            author_name = page.get('result', {}).get('author_name')
            if author_name is not None and author_name in extra.spam:
                self.pagelist.remove(page)     

    def filterText(self, min_length, max_length):
        '''
        Filters pages based on text length criteria, removing pages falling outside the specified range
        :params: min_length (int, optional) - Minimum text length; max_length (int, optional) - Maximum text length.
        :return: none
        '''
        logging.info(f'Filtering pages based on text length criteria...')
        for page in self.pagelist[:]:
            self.getTextList(page)
            length = sum(len(string) for string in self.textlist)
            if min_length is not None and length < min_length:
                self.pagelist.remove(page)
            elif max_length is not None and length > max_length:
                self.pagelist.remove(page)
                    
def parser():
    '''
    Returns the parser arguments
    :params: none
    :return: parser.parse_args() object
    '''
    parser = argparse.ArgumentParser(
        description='Scrapes a telegraph pages from a specified search query'
    )
    main_grp = parser.add_argument_group('Main parameters')
    main_grp.add_argument('QUERY', help = 'Single query given as a positional argument', type=str, nargs = '?')
    main_grp.add_argument('-i', '--input-file', help = '<INPUT_FILE> text file containing the target list. Ex: list.txt')
    main_grp.add_argument('-o', '--output-directory', help = '<OUTPUT_DIRECTORY> (optional): query output directory (default \'./<QUERY>/\')')
    main_grp.add_argument('-w', '--workers', help = '<WORKERS> (optional): number of parallel execution workers (default 4)', default = 4)

    output_grp = parser.add_argument_group('Output parameters')
    output_grp.add_argument('-I', '--images', action='store_true', help = 'collect all images on indexed pages')
    output_grp.add_argument('-T', '--text', action='store_true', help='collect all text on indexed pages')
    output_grp.add_argument('-L', '--links', action='store_true', help = 'collect all links on indexed pages')
    output_grp.add_argument('-max', help='<MAX> (optional): Filter pages with text length greater than defined value.', type=int, nargs='?')
    output_grp.add_argument('-min', help='<MIN> (optional): Filter pages with text length less than defined value.', type=int, nargs='?')

    return parser.parse_args()

def main():
    args = parser()
    
    if args.input_file != None:
        with open(args.input_file,'rb') as file:
            try:
                input_list = [l.decode('utf-8').strip() for l in file.readlines()]
            
            except UnicodeDecodeError as e:
                print('Your input file is not UTF-8 encoded, please encode it before using this script')
    else:
        input_list = [args.QUERY]
    
    if args.output_directory:
        os.chdir(os.path.abspath(args.output_directory))

    if args.workers:
        pass
    
    for query in input_list:
        scraper = Scraper(query)
        
        scraper.filterSpam()

        if args.min or args.max:
            scraper.filterText(args.min, args.max)

        if args.images:
            scraper.getImages()
        
        if args.text:
            scraper.getText()
        
        if args.links:
            scraper.getLinks()
                
        if not args.images or not args.text or not args.links:
            scraper.getPagesUrl()            

if __name__ == '__main__':
    main()