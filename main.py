import os
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


def get_pages() -> list[BeautifulSoup]:
    pages = []

    for page in range(1, MAX_PAGES):
        html = requests.get(URL, headers=HEADERS, params={"page": page})

        if html.status_code == 200:
            pages.append(BeautifulSoup(html.text, "html.parser"))
        else:
            break

    return pages


def digitalize(str: str) -> str:
    return "".join(filter(lambda char: char.isdigit(), str.split()))


def parse_pages(pages: list[BeautifulSoup]) -> list[dict]:
    data = []

    for page in pages:
        data.extend(parse_page(page))

    return data


def get_cars(page: BeautifulSoup) -> list[BeautifulSoup]:
    return page.find_all("div", "proposition")


def parse_page(page: BeautifulSoup) -> list[dict]:
    cars = []

    for data in get_cars(page):
        car = {
            "title": data.find("h3", "proposition_name").get_text(strip=True),
            "city": data.find("div", "proposition_region").strong.get_text(strip=True),
            "price_usd": digitalize(data.find("span", "green").get_text(strip=True)),
            "price_uah": digitalize(
                data.find("span", "grey size13").get_text(strip=True)
            ),
            "link": HOST + data.find("div", "proposition_title").a.get("href"),
        }

        cars.append(car)

    return cars


def save_file(cars: list[dict], path: str) -> None:
    with open(path, "w", newline="") as file:
        writer = csv.writer(file, delimiter=";")

        writer.writerow(["Марка", "Город", "Цена в $", "Цена в UAH", "Ссылка"])

        for car in cars:
            writer.writerow(list(car.values()))


def parse() -> None:
    print(f"Загрузка данных по Альфа-Ромео...")

    pages = get_pages()

    if len(pages):
        cars = parse_pages(pages)
        print(f"Обработанно машин: {len(cars)}")

        save_file(cars, FILE)
        print(f"Сохранено в файл: {FILE}")

        os.startfile(FILE)
    else:
        print("Информация не найдена.")


parse()