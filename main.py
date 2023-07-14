import json
import re
import time

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import datetime
import csv


async def main():
    async with aiohttp.ClientSession() as request:
            cur_time = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')

            with open(f'chitai_gorod_{cur_time}.csv', 'w', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    (
                        "Название книги",
                        "Автор книги",
                        "Цена со скидкой",
                        "Цена без скидки",
                        "Процент скидки",
                        "Ссылка на книгу",
                    )
                )

            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 YaBrowser/23.5.4.674 Yowser/2.5 Safari/537.36",
                "accept": "*/*",
            }
            url = 'https://www.chitai-gorod.ru/catalog/books/nauka-tekhnika-it-110282/'

            response = await request.get(url=url, headers=headers)
            soup = BeautifulSoup(await response.text(), 'lxml')

            pages_count = int(soup.find('div', class_='pagination__wrapper').find_all('span', class_="pagination__text")[-1].text.strip())

            book_list = []

            #for page in range(1, pages_count + 1):
            for page in range(1, 3):
                url = f'https://www.chitai-gorod.ru/catalog/books/nauka-tekhnika-it-110282?page={page}'
                response = await request.get(url=url, headers=headers)
                soup = BeautifulSoup(await response.text(), 'lxml')

                try:
                    book_items = soup.find('div', class_="products-list").find_all('article')
                    nonBreakSpace = u'\xa0'

                    for bi in book_items:
                        book_data = bi.find_all('div', class_='product-card__text product-card__row')[0].find('a')
                        try:
                            book_title = book_data.get('title').strip()
                        except:
                            book_title = 'Нет названия.'

                        try:
                            book_author = book_data.find('div', class_='product-title__author').text.strip()
                        except:
                            book_author = 'Нет автора'

                        try:
                            book_new_price = int(book_data.parent.parent.find_all('div', class_='product-price__value')[0].text.strip().replace(' ₽', '').replace(nonBreakSpace, ''))
                        except:
                            book_new_price = 'Нет нового прайса'

                        try:
                            book_old_price = int(book_data.parent.parent.find_all('div', class_='product-price__old')[0].text.strip().replace(' ₽', '').replace(nonBreakSpace, ''))
                        except:
                            book_old_price = 'Нет старого прайса'

                        try:
                            book_sale = round(((book_old_price - book_new_price) / book_old_price) * 100)
                        except:
                            book_sale = 'Нет скидки'

                        try:
                           book_href = f'https://www.chitai-gorod.ru' + book_data.get('href')
                        except:
                            book_href = 'Нету ссылки'

                        book_list.append(
                            {
                                "book_title": book_title,
                                "book_author": book_author,
                                "book_new_price": book_new_price,
                                "book_old_price": book_old_price,
                                "book_sale": book_sale,
                                "book_href": book_href,
                            }
                        )

                        with open(f'chitai_gorod_{cur_time}.csv', 'a', encoding='utf-8') as file:
                            writer = csv.writer(file)
                            writer.writerow(
                                (
                                    book_title,
                                    book_author,
                                    book_new_price,
                                    book_old_price,
                                    book_sale,
                                    book_href,
                                )
                            )

                    print(f'Обработана {page}/{pages_count}')
                    time.sleep(1)

                except:
                    print('Ошибка')

            with open(f'chitai_gorod_{cur_time}.json', 'w', encoding='utf-8') as file:
                json.dump(book_list, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    asyncio.run(main())
