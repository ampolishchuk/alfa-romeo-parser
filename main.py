from os import write, startfile
import requests
from bs4 import BeautifulSoup
import csv

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "accept": "*/*",
}
HOST = "https://auto.ria.com"
URL = "https://auto.ria.com/newauto/marka-alfa-romeo/"
MAX_PAGES = 1000
FILE = "cars.csv"


def get_html(params=None):
    return requests.get(URL, headers=HEADERS, params=params)


def get_pages():
    pages = []

    for page in range(1, MAX_PAGES):
        html = get_html({"page": page})

        if html.status_code == 200:
            pages.append(BeautifulSoup(html.text, "html.parser"))
        else:
            break

    return pages


def digitalize(str):
    return "".join(filter(lambda char: char.isdigit(), str.split()))


def parse_pages(pages):
    data = []

    for page in pages:
        data.extend(parse_page(page))

    return data


def parse_page(page):
    return map(
        lambda data: {
            "title": data.find("h3", "proposition_name").get_text(strip=True),
            "city": data.find("div", "proposition_region").strong.get_text(strip=True),
            "price_usd": digitalize(data.find("span", "green").get_text(strip=True)),
            "price_uah": digitalize(
                data.find("span", "grey size13").get_text(strip=True)
            ),
            "link": HOST + data.find("div", "proposition_title").a.get("href"),
        },
        page.find_all("div", "proposition"),
    )


def save_file(cars, path):
    with open(path, "w", newline="") as file:
        writer = csv.writer(file, delimiter=";")

        writer.writerow(["Марка", "Город", "Цена в $", "Цена в UAH", "Ссылка"])

        for car in cars:
            writer.writerow(list(car.values()))


def parse():
    print(f"Загрузка данных по Альфа-Ромео...")

    pages = get_pages()

    if len(pages):
        cars = parse_pages(pages)
        print(f"Обработанно машин: {len(cars)}")

        save_file(cars, FILE)
        print(f"Сохранено в файл: {FILE}")

        startfile(FILE)
    else:
        print("Информация не найдена.")


parse()