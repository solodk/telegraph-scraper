import argparse
import requests
import json
import os

from datetime import datetime, timedelta
from tqdm import tqdm

import extra

class Scraper(object):
    def __init__(self, query):
        self.input_query = query
        self.session = requests.Session()
        self.cache_file = self.input_query + '_cache_store'
        self.cache_path = os.path.join(os.path.dirname(__file__), 'cache', self.cache_file)
        self.currentdate = datetime.now()
        self.filtered_pages = []
        self.getCache()
        self.indexQuery()
        self.updateCache()
    
    def getCache(self):
        try:
            with open(self.cache_path, 'r', encoding='utf-8') as f:
                f.seek(0)
                self.cache = json.load(f)
        except Exception:
            self.cache = {}
        self.newQuery()

    def updateCache(self):
        '''
        This function is meant to update the current used cache file with any new information
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
    
    def newQuery(self):

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
        Makes a list of pages by using getJSON() func for a single query
        :params: none
        :return: none
        '''
        index = 1

        while self.start_date < self.end_date:
            formatted_date = self.start_date.strftime('%m-%d')
            search_query = [self.input_query, formatted_date]

            if index > 1:
                search_query.append(str(index))

            search_query = '-'.join(search_query)

            try:
                data = self.getJSON(search_query)
                if data['ok'] is True:
                    self.pagelist.append(data)
                    index += 1
                else:
                    self.start_date += timedelta(days=1)
                    index = 1 #Reset the index
            except Exception as ex:
                print(f'indexQuery(): Error at {search_query}')
                
    def getJSON(self, search_query):
        '''
        Searching for a page by a single query
        :params: none
        :return: json answer from api
        '''
        try:
            result = self.session.get(
                f'https://api.telegra.ph/getPage/{search_query}?return_content=true'
            ).json()
        except Exception as ex:
            print(f'getJSON(): Failed to get {search_query}')
        return result

    def getImages(self, page):
        '''
        downloads a images of one page
        '''
        self.getImageList(page)

        for index, file in enumerate(self.imagelist, start=1):
            with open(f'{index}.jpg', 'wb') as f:
                f.write(requests.get(f'https://telegra.ph/file/{file}', stream=True).content)
    
    def getImageList(self, page):
        '''
        Takes a names of images on a page into list
        '''
        self.imagelist = []
        content = page['result']['content']
        for item in content:
            if isinstance(item, dict) and item['tag'] == 'figure':
                for sub_tag in item['children']:
                    if sub_tag['tag'] == 'img':
                        self.imagelist.append(sub_tag['attrs']['src'][6:])

    def getText(self, page):
        '''
        Gather all text from page and saves it into file
        '''
        self.getTextList(page)

        self.textlist = list(filter(None, self.textlist)) #filter empty values from textlist
        if self.textlist:
            with open('text.txt', 'w', encoding='utf-8') as f:
                for line in self.textlist:
                    f.write(f'{line}\n')

    def getTextList(self, page):
        '''
        Collect all text form page into list
        '''
        self.textlist = []
        content = page['result']['content']
        for item in content:
            if 'tag' in item and item['tag'] == 'p':
                if 'children' in item:
                    for child in item['children']:
                        if isinstance(child, str):
                            self.textlist.append(child.replace('\n', ' ').strip())
    
    def getLinks(self, page):
        '''
        Gather all links from page and saves it into file
        '''
        self.getLinksList(page)

        if self.linklist:
            with open('links.txt', 'w', encoding='utf-8') as f:
                for line in self.linklist:
                    f.write(f'{line}\n')

    def getLinksList(self, page):
        '''
        Collect all links form page into list
        '''
        self.linklist = []
        content = page['result']['content']
        for item in content:
            #if isinstance(item, dict) and 'children' in item:
            if 'children' in item:
                for dict in item['children']:
                    if 'tag' in dict and dict['tag'] == 'a':
                        #dict['attrs']['href']
                        self.linklist.append(dict['attrs']['href'])

    def filterSpam(self):
        '''
        Checks if page ok for current filters
        :params: page in json
        :return: true if author name is not in spamlist
        '''
        
        for page in self.pagelist[:]:
            author_name = page.get('result', {}).get('author_name')
            if author_name is not None and author_name in extra.spam:
                self.pagelist.remove(page)     

    def filterText(self, min_length, max_length):
        '''
        Checks if page ok for current filters
        :params: page in json
        :return: true if text length in range of min and max
        '''
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
    main_grp.add_argument('-c', '--cache', action='store_true', help = 'Use cached results')

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
        root = os.path.abspath(args.output_directory)
    else:
        root = os.getcwd()

    if args.workers:
        pass

    for query in input_list:
        telegraph = Scraper(query)
        
        telegraph.filterSpam()

        if args.min or args.max:
            telegraph.filterText(args.min, args.max)

        if args.images or args.text or args.links:
            query_path = os.path.join(root, query)
            if not os.path.exists(query_path):
                os.makedirs(query_path)

            for page in telegraph.pagelist:
                page_name = page['result']['path']
                page_path = os.path.join(query_path, page_name)
                if not os.path.exists(page_path):
                    os.makedirs(page_path)
                os.chdir(page_path)
                
                if args.images:
                    telegraph.getImages(page)
                
                if args.text:
                    telegraph.getText(page)
                
                if args.links:
                    telegraph.getLinks(page)
                
        else:
            links = [page['result']['url'] for page in telegraph.pagelist]
            with open(f'{query}.txt', 'w') as f:
                for link in links:
                    f.write(f'{link}\n')

        os.chdir(root)
      
if __name__ == '__main__':
    main()