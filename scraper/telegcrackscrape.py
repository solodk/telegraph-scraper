import argparse
import requests
import os

from tqdm import tqdm

import extra

class Scraper(object):
    def __init__(self, query):
        self.input_query = query
        self.session = requests.Session()
        try:
            self.session.get(
                f"https://api.telegra.ph/",
                headers=extra.visitinfo,
            )
        except Exception as ex:
            print("API is down")
        self.dir_query = os.path.join(os.getcwd(), self.input_query)
        # If the path doesn't exist, then create it
        if not os.path.exists(self.dir_query):
            os.makedirs(self.dir_query)
        os.chdir(self.dir_query)
        self.indexQuery()
        
    def indexQuery(self):
        """
        Makes a list of pages by using getJSON() func for a single query
        :params: none
        :return: none
        """
        self.pagelist = []
        
        try:
            for MM in range(1, 13):
                for DD in range(1, 32):
                    index = 1
                    
                    while True:
                        if index == 1:
                            search_query = [self.input_query, f'{MM:02}', f'{DD:02}']
                            search_query = '-'.join(search_query)
                            data = self.getJSON(search_query)

                        else:
                            search_query = [self.input_query, f'{MM:02}', f'{DD:02}', f'{index}']
                            search_query = '-'.join(search_query)
                            data = self.getJSON(search_query)

                        if data['ok'] is False:
                            break
                        else:
                            self.pagelist.append(data)
                            index += 1
        except Exception as ex:
            print(f'indexQuery() error: {ex}')

    def getJSON(self, search_query):
        """
        Searching for a page by a single query
        :params: none
        :return: json answer from api
        """
        try:
            result = self.session.get(
                f'https://api.telegra.ph/getPage/{search_query}?return_content=true'
            ).json()
        except Exception as ex:
            print(f'getJSON(): Failed to get {search_query}')
        return result


    def getImages(self, page):
        """
        downloads a images of one page
        """
        self.getImageList(page)

        for index, file in enumerate(self.img_list, start=1):
            with open(f'{index}.jpg', 'wb') as f:
                f.write(requests.get(f'https://telegra.ph/file/{file}', stream=True).content)
    
    def getImageList(self, page):
        """
        Takes a names of images on a page
        """
        self.img_list = []

        content = page["result"]["content"]
        for item in content:
            if isinstance(item, dict) and item['tag'] == 'figure':
                for sub_tag in item['children']:
                    if sub_tag['tag'] == 'img':
                        self.img_list.append(sub_tag['attrs']['src'][6:])

    def getText(self, page):
        """
        Gather all text from page and saves it into file
        """
        self.getTextList(page)

        self.text_list = list(filter(None, self.text_list))
        if self.text_list:
            with open('text.txt', 'w', encoding="utf-8") as f:
                for line in self.text_list:
                    f.write(f'{line}\n')

    def getTextList(self, page):
        """
        Collect all text form page
        """
        self.text_list = []

        content = page["result"]["content"]
        for item in content:
            if 'tag' in item and item['tag'] == 'p':
                if 'children' in item:
                    paragraph_text = " ".join(child for child in item['children'] if isinstance(child, str))
                    self.text_list.append(paragraph_text)
    


def parser():
    """
    Returns the parser arguments
    :params: none
    :return: parser.parse_args() object
    """
    parser = argparse.ArgumentParser(
        description="Scrapes a telegraph pages from a specified search query"
    )
    main_grp = parser.add_argument_group('Main parameters')
    main_grp.add_argument('QUERY', help = 'Single query given as a positional argument', type=str, nargs = '?')
    main_grp.add_argument('-i', '--input-file', help = '<INPUT_FILE> text file containing the target list. Ex: list.txt')
    main_grp.add_argument('-o', '--output-directory', help = '<OUTPUT_DIRECTORY> (optional): query output directory (default \'./<QUERY>/\')')
    main_grp.add_argument('-w', '--workers', help = '<WORKERS> (optional): number of parallel execution workers (default 4)', default = 4)

    output_grp = parser.add_argument_group('Output parameters')
    output_grp.add_argument("-S", "--screenshot", action="store_true", help="Takes screenshot of each page")
    output_grp.add_argument('-I', '--images', action="store_true", help = 'collect all images on indexed pages')
    output_grp.add_argument("-T", "--text", action="store_true", help="collect all text on indexed pages")
    output_grp.add_argument('-L', '--links', action="store_true", help = 'collect all links on indexed pages')
    output_grp.add_argument('-H', '--html', action="store_true", help = 'download html of indexed pages')
    output_grp.add_argument('-l', '--limit', help="Filter pages with text lenth more than <limit>, default value = 2000", default = 2000, type=int, nargs="?")

    return parser.parse_args()


def filterSpam(page):
    """
    Checks if page ok for current filters
    :params: page in json, limit int
    :return: page if it ok
    """
    author_name = page.get("result", {}).get("author_name")
    if author_name is not None and author_name in extra.spam:
        return False
    return True

def filterText(page):
    """
    Checks if page ok for current filters
    :params: page in json, limit int
    :return: page if it ok
    """
    global limit

    if sum(len(string) for string in text) <= limit:
        return page        


def main():
    global limit

    args = parser()
    root = os.getcwd()
    

    if args.input_file != None:
        with open(args.input_file,'rb') as file:
            try:
                input_list = [l.decode('utf-8').strip() for l in file.readlines()]
            
            except UnicodeDecodeError as e:
                print('Your input file is not UTF-8 encoded, please encode it before using this script')
    else:
        input_list = [args.QUERY]
    
    for line in input_list:
        telegraph = Scraper(line)
        
        telegraph.pagelist = list(filter(filterSpam, telegraph.pagelist))
        # if args.limit:
        #     limit = args.limit
        #     telegraph.pagelist = list(filter(filterText, telegraph.pagelist))
        # need to rework scraper obj

        if args.screenshot or args.images or args.text or args.links or args.html:

            for page in telegraph.pagelist:
                page_name = page["result"]["path"]
                dir_page = os.path.join(telegraph.dir_query, page_name)
                if not os.path.exists(dir_page):
                    os.makedirs(dir_page)
                os.chdir(dir_page)
                
                if args.images:
                    telegraph.getImages(page)
                
                if args.text:
                    try:
                        telegraph.getText(page)
                    except Exception as ex:
                        print(f"Page {page_name} crashed: {ex}")

                
        else:
            links = [page["result"]["url"] for page in telegraph.pagelist]
            with open(f"{line}.txt", 'w') as f:
                for link in links:
                    f.write(f'{link}\n')
                
                

    


if __name__ == "__main__":
    main()