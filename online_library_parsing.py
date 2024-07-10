import requests
from pathlib import Path

from requests import HTTPError


# url = "https://dvmn.org/filer/canonical/1542890876/16/"
#
# response = requests.get(url)
# response.raise_for_status()
#
# filename = 'dvmn.svg'
# with open(filename, 'wb') as file:
#     file.write(response.content)


# url = 'https://tululu.org/txt.php?id=32168'
# response = requests.get(url)
# response.raise_for_status()
# print(response.text)



def check_for_redirect(response):
    if response.history:
        raise HTTPError


Path('books').mkdir(parents=True, exist_ok=True)
for book_id in range(1, 11):
    url = f'https://tululu.org/txt.php?id={book_id}'
    book_path = Path('books', f'id{book_id}.txt')
    response = requests.get(url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except HTTPError:
        continue

    with open(book_path, 'w', encoding="UTF-8") as book:
            book.write(response.text)
