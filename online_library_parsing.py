import os
import requests
from requests import HTTPError
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib.parse import unquote


def check_for_redirect(response):
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
    path_to_file = f'{os.path.join(folder, san_filename)}.txt'
    response = requests.get(url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except HTTPError:
        return
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
    response = requests.get(url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except HTTPError:
        return
    # with open(path_to_image, 'wb') as image:
    #     image.write(response.content)
    return path_to_image


def parse_book_page(book_id):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
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
    book_comments_tag = soup.find_all('div', class_='texts')
    print(f'название: {filename}')
    for comment in book_comments_tag:
        print(comment.find('span', class_='black').text)

    return {
        'book_author': book_author,
        'filename': filename,
        'imagename': imagename,
        'image_url': image_url
    }


def main():
    for book_id in range(1, 11):
        book_url = f'https://tululu.org/txt.php?id={book_id}'
        book_page_dict = parse_book_page(book_id)
        if book_page_dict:
            book_name = book_page_dict['filename']
            book_imag = book_page_dict['imagename']
            image_url = book_page_dict['image_url']
            download_txt(book_url, book_name)
            download_image(image_url, book_imag)


if __name__ == "__main__":
    main()
