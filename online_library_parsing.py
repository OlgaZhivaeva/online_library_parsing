import argparse
import os
import time
import requests
from requests import HTTPError
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib.parse import unquote


def get_start_and_end_book():
    """Получить id первой и последней книги для скачивания."""
    parser = argparse.ArgumentParser(description='Скачивание книг с сайта tululu.org')
    parser.add_argument('-s', '--start_id', type=int, default=1, help='id первой книги для скачивания')
    parser.add_argument('-e', '--end_id', type=int, default=10, help='id последней книги для скачивания')
    args = parser.parse_args()
    return args


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def download_txt(url, params, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        params (dict): Параметры GET запроса для передачи id файла.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    san_filename = sanitize_filename(filename)
    Path(folder).mkdir(parents=True, exist_ok=True)
    path_to_file = f'{os.path.join(folder, san_filename)}.txt'
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    check_for_redirect(response)
    # with open(path_to_file, 'w', encoding="UTF-8") as book:
    #     book.write(response.text)
    return path_to_file


def download_image(url, imagename, folder='images/'):
    """Функция для скачивания картинок.
    Args:
        url (str): Cсылка на картинку, которую хочется скачать.
        imagename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    san_imagename = sanitize_filename(imagename)
    Path(folder).mkdir(parents=True, exist_ok=True)
    path_to_image = f'{os.path.join(folder, san_imagename)}'
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    check_for_redirect(response)
    # with open(path_to_image, 'wb') as image:
    #     image.write(response.content)
    return path_to_image


def parse_book_page(page_url, book_id):
    response = requests.get(page_url, timeout=60)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('table', class_='tabs').find('h1')
    title_text = title_tag.text
    split_text = title_text.split('::')
    book_title = split_text[0].strip()
    filename = f'{book_id}. {book_title}'
    book_author = split_text[1].strip()
    image_src = soup.find('div', class_='bookimage').find('img')['src']
    image_url = urljoin(page_url, image_src)
    imagename = unquote(image_src, encoding='utf-8', errors='replace').split('/')[-1]
    book_genres_tag = soup.find('span', class_='d_book').find_all('a')
    book_genres = [genre.text for genre in book_genres_tag]
    book_comments_tag = soup.find_all('div', class_='texts')
    book_comments = [comment.find('span', class_='black').text for comment in book_comments_tag]
    return {
        'book_title': book_title,
        'book_author': book_author,
        'filename': filename,
        'imagename': imagename,
        'image_url': image_url,
        'book_genres': book_genres,
        'book_comments': book_comments
    }


def main():
    args = get_start_and_end_book()
    for book_id in range(args.start_id, args.end_id+1):
        params = {'id': book_id}
        book_url = 'https://tululu.org/txt.php'
        page_url = f'https://tululu.org/b{book_id}/'
        try:
            book_page_parse = parse_book_page(page_url, book_id)
            book_name = book_page_parse['filename']
            book_image = book_page_parse['imagename']
            image_url = book_page_parse['image_url']
            try:
                download_txt(book_url, params, book_name)
            except requests.exceptions.HTTPError:
                print(f'Книги id {book_id} нет')
            except requests.exceptions.ConnectionError:
                print('Ошибка соединения download_txt')
                time.sleep(20)
            except requests.exceptions.ReadTimeout:
                print(f'Ошибка соединения download_txt timeout')
                time.sleep(20)
            try:
                download_image(image_url, book_image)
            except requests.exceptions.HTTPError:
                print(f'Обложки книги id {book_id} нет')
            except requests.exceptions.ConnectionError:
                print('Ошибка соединения download_image')
                time.sleep(20)
            except requests.exceptions.ReadTimeout:
                print(f'Ошибка соединения download_image timeout')
                time.sleep(20)
            print(f"Заголовок: {book_page_parse['book_title']}")
            print(book_page_parse['book_genres'])
        except requests.exceptions.HTTPError:
            print(f'Страницы книги id {book_id} нет')
        except requests.exceptions.ConnectionError:
            print('Ошибка соединения parse_book_page')
            time.sleep(20)
        except requests.exceptions.ReadTimeout:
            print(f'Ошибка соединения parse_book_page timeout')
            time.sleep(20)


if __name__ == "__main__":
    main()
