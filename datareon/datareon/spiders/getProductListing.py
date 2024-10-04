import base64
import json
import os
from dotenv import dotenv_values

import scrapy


class GetproductlistingSpider(scrapy.Spider):
    name = "getProductListing"
    # allowed_domains = ["dat-pub.muztorg.ru"]
    # start_urls = ["https://dat-pub.muztorg.ru"]
    # base_url = 'https://dat-pub.muztorg.ru:9009/pimcore/out/getAdditionalFeatures?pageNumber='  # URL с подставляемым номером страницы
    base_url = 'https://dat-pub.muztorg.ru:9009/pimcore/in/getProductListing?pageNumber='  # URL с подставляемым номером страницы
    page_number = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        config = dotenv_values(".env")

        username = config.get("DATAREON_LOGIN")
        password = config.get("DATAREON_PASSWORD")

        # Кодируем имя пользователя и пароль в Base64
        credentials = f'{username}:{password}'
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

        self.headers = {'Authorization': f'Basic {encoded_credentials}'}

    def start_requests(self):
        url = self.base_url + str(self.page_number)
        yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        # Предполагаем, что ответ в формате JSON
        data = json.loads(response.body)

        total_pages = int(data["resultSet"].get('PageCount', 1))  # Общее количество страниц

        # Сохранение данных в файл
        file_name = f'page_{self.page_number}.json'
        file_path = os.path.join('pages_prod', file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        # Если есть еще страницы, отправляем запросы на следующую
        if self.page_number < total_pages:
            self.page_number += 1
            next_page_url = self.base_url + str(self.page_number)
            yield scrapy.Request(url=next_page_url, headers=self.headers, callback=self.parse)
