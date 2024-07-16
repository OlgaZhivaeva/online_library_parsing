# Parser of books from the site [https://tululu.org/](https://tululu.org/)

The project is designed to download books from the website [https://tululu.org/](https://tululu.org/).

### How to install

Python3 should be already installed. 
Then use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```commandline
pip install -r requirements.txt
```

### Arguments

Run the script using the optional arguments `--start_id` to set the id of the initial book
to download and `--end_id` to set the last book to download
```python
python online_library_parsing.py --start_id 20 --end_id 30
```
or
```python
python online_library_parsing.py -s 20 -e 30
```
By default, the arguments `--start_id=1` and `--end_id=10` will be set.

The downloaded books will be located in the `books` folder.
Their covers will be located in the `images` folder.
### Project Goals

The code is written for educational purposes on online-course for
web-developers [dvmn.org](https://dvmn.org/).