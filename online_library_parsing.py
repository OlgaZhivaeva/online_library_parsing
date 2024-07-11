import os
import requests, lxml
from requests import HTTPError
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename




def check_for_redirect(response):
    print(f'response.history {response.history}')
    if response.history:
        raise HTTPError


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    san_filename = sanitize_filename(filename)
    Path(folder).mkdir(parents=True, exist_ok=True)
    save_to = f'{os.path.join(folder, san_filename)}.txt'
    response = requests.get(url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except HTTPError:
        return
    with open(save_to, 'w', encoding="UTF-8") as book:
        book.write(response.text)
    return save_to


def parse_filename(book_id):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('body').find('table', class_='tabs').find('h1')
    title_text = title_tag.text
    split_text = title_text.split('::')
    book_title = split_text[0].strip()
    filename = f'{book_id}. {book_title}'
    return filename


def main():
    for book_id in range(1, 11):
        book_url = f'https://tululu.org/txt.php?id={book_id}'
        filename = parse_filename(book_id)
        download_txt(book_url, filename)


if __name__ == "__main__":
    main()