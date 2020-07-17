import json
import requests
import datetime


class Catalog:
    headers = {
        "User-Agent":
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/84.0.4147.89 Safari/537.36 ",
    }

    params = {
        "records_per_page": 20,
    }

    def __init__(self, resource_url, categories_url):
        self.__resource_url = resource_url
        self.__categories_url = categories_url
        self.__catalog = [{}]

    def parse(self):
        url = self.__resource_url
        categories_response = requests.get(self.__categories_url, headers=self.headers)
        categories = categories_response.json()

        for elem in categories:
            params = self.params

            category = elem['parent_group_code']
            params['categories'] = category

            self.__catalog[0][category] = []

            while url:
                response = requests.get(url, headers=self.headers, params=params)
                data = response.json()
                self.__catalog[0][category].extend(data['results'])

                url = data['next']
                params = {'categories': category}

            url = self.__resource_url

    def export(self):
        timestamp = datetime.datetime.now().strftime('%d-%m-%Y')

        for category in self.__catalog[0]:
            with open(f'tmp/{timestamp}_{category}_catalog.json', 'w', encoding='UTF-8') as file:
                json.dump(self.__catalog[0][category], file, ensure_ascii=False)


if __name__ == '__main__':
    catalog = Catalog('https://5ka.ru/api/v2/special_offers/', 'https://5ka.ru/api/v2/categories/')
    catalog.parse()
    catalog.export()

    print('Done')
