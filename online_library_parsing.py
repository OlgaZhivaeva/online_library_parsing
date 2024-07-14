import argparse
import os
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
    parser.add_argument('-e', '--end_id', type=int, default=11, help='id последней книги для скачивания')
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
    response = requests.get(url, params=params)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except HTTPError:
        return
    with open(path_to_file, 'w', encoding="UTF-8") as book:
        book.write(response.text)
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
    response = requests.get(url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except HTTPError:
        return
    with open(path_to_image, 'wb') as image:
        image.write(response.content)
    return path_to_image


def parse_book_page(page_url, book_id):
    response = requests.get(page_url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except HTTPError:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('table', class_='tabs').find('h1')
    title_text = title_tag.text
    split_text = title_text.split('::')
    book_title = split_text[0].strip()
    filename = f'{book_id}. {book_title}'
    book_author = split_text[1].strip()
    image_src = soup.find('div', class_='bookimage').find('img')['src']
    image_url = urljoin('https://tululu.org/', image_src)
    imagename = unquote(image_src, encoding='utf-8', errors='replace').split('/')[-1]
    book_genres_tag = soup.find('span', class_='d_book').find_all('a')
    book_genres = []
    for genre in book_genres_tag:
        book_genres.append(genre.text)
    book_comments_tag = soup.find_all('div', class_='texts')
    book_comments = []
    for comment in book_comments_tag:
        book_comments.append(comment.find('span', class_='black').text)
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
        book_url = f'https://tululu.org/txt.php'
        page_url = f'https://tululu.org/b{book_id}/'
        book_page_parse = parse_book_page(page_url, book_id)
        if book_page_parse:
            book_name = book_page_parse['filename']
            book_image = book_page_parse['imagename']
            image_url = book_page_parse['image_url']
            download_txt(book_url, params, book_name)
            download_image(image_url, book_image)
            print(f"Заголовок: {book_page_parse['book_title']}")
            print(book_page_parse['book_genres'])


if __name__ == "__main__":
    main()
