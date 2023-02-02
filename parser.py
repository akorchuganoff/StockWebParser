import requests
from bs4 import BeautifulSoup
from lxml.html import soupparser, tostring, parse, fromstring
from lxml import etree
import json
import re

import config

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 YaBrowser/23.1.1.1138 Yowser/2.5 Safari/537.36",
    "date": "Thu, 02 Feb 2023 00:26:13 GMT"
}
BASE_URL = "https://finance.yahoo.com/quote/"

def get_prices(tickers_array):

    result = dict()
    for ticker in tickers_array:
        response = requests.get(url=BASE_URL + ticker, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            price = soup.find("fin-streamer", attrs={"data-symbol": ticker, "data-test": "qsp-price",
                                                     "data-field": "regularMarketPrice"}).get_text()
            result[ticker] = price
        else:
            result[ticker] = "Не смог найти"
    return result


def get_stats(ticker):
    response = requests.get(url=f'{BASE_URL}{ticker}/key-statistics?p={config.token}', headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        stats = dict()
        price = soup.find('fin-streamer', attrs={"data-test": "qsp-price", "data-field": "regularMarketPrice", "data-symbol": ticker}).get_text()
        stats['price'] = price

        stats_section = soup.find("section", attrs={"data-test":"qsp-statistics"})

        section_headers_soup = stats_section.find_all('h2')
        table_headers_soup = stats_section.find_all('h3')
        section_headers_arr = []
        table_headers_arr = []

        for header in section_headers_soup:
            section_headers_arr.append(header.get_text())

        for header in table_headers_soup:
            table_headers_arr.append(header.get_text())

        stats["section_headers"] = section_headers_arr
        stats["table_headers"] = table_headers_arr

        tables_soup = stats_section.find_all("table")
        tables_arr = []

        for table in tables_soup:
            table_dictionary = dict()
            rows = table.find_all("tr")

            for row in rows:
                columns = row.find_all("td")
                table_dictionary[columns[0].get_text()] = columns[1].get_text()

            tables_arr.append(table_dictionary)

        stats['tables'] = tables_arr


    else:
        stats = "Не смог найти информацию о компании"
    return stats


def main():
    tickers_array = ["META", "CVNA", "AMZN", "GOOG", "PTON"]
    # for k, v in get_single_company_news("META").items():
    #     print(f'{k}: {v}')



    data = get_stats("META")
    with open("stats.json", "w") as jsonfile:
        json.dump(data, jsonfile)


if __name__ == '__main__':
    main()
