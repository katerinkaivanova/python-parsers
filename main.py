import os
import json
import requests
import datetime as dt

from bs4 import BeautifulSoup as bs


class GbBlogParser:
    __domain = 'https://geekbrains.ru'
    __url = 'https://geekbrains.ru/posts'
    __done_urls = set()

    def __init__(self, folder_name='tmp'):
        self.posts_urls = set()
        self.pagination_urls = set()
        self.posts_data = []

        self.folder_data = os.path.join(os.path.dirname(__file__), folder_name)

    # создание soup-объекта
    @staticmethod
    def get_page_soup(url):
        response = requests.get(url)
        soup = bs(response.text, 'lxml')
        return soup

    # парсинг ссылок
    def run(self, url=None):
        url = url or self.__url
        soup = self.get_page_soup(url)
        self.pagination_urls.update(self.get_pagination(soup))
        self.posts_urls.update(self.get_posts_urls(soup))

        for url in tuple(self.pagination_urls):
            if url not in self.__done_urls:
                self.__done_urls.add(url)
                self.run(url)

    # парсинг данных
    def extract(self):
        for url in tuple(self.posts_urls):
            soup = self.get_page_soup(url)
            title = soup.find('h1', attrs={'class': 'blogpost-title'}).text
            writer_name = soup.find('div', attrs={'itemprop': 'author'}).text

            writer_url = ''
            links = soup.find_all('a')
            for link in links:
                if link.get("href") and 'users' in link.get('href'):
                    writer_url = f'{self.__domain}{link.get("href")}'
                    break

            data = {
                'title': title,
                'post_url': url,
                'writer_name': writer_name,
                'writer_url': writer_url
            }

            self.posts_data.append(data)

    # экспорт в json-файл
    def save(self):
        now = dt.datetime.now().strftime('%d-%m-%Y')
        file_path = os.path.join(self.folder_data, f'{now}.json')

        with open(file_path, 'w', encoding='UTF-8') as file:
            json.dump(self.posts_data, file, ensure_ascii=False)

    # ссылки на страницы
    def get_pagination(self, soup):
        ul = soup.find('ul', attrs={'class': 'gb__pagination'})
        a_list = [f'{self.__domain}{a.get("href")}' for a in ul.find_all('a') if a.get("href")]
        return a_list

    # ссылки на посты
    def get_posts_urls(self, soup):
        posts_wrap = soup.find('div', attrs={'class': 'post-items-wrapper'})
        a_list = [f'{self.__domain}{a.get("href")}' for a in
                  posts_wrap.find_all('a', attrs={'class': 'post-item__title'})]
        return a_list


if __name__ == '__main__':
    parser = GbBlogParser()
    parser.run()
    parser.extract()
    parser.save()
