import json

import requests
from bs4 import BeautifulSoup

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
        if response.status_code != 200 or "No results for" in response.text:
            result[ticker] = "Не смог найти"
        else:
            soup = BeautifulSoup(response.text, "lxml")
            price = soup.find("fin-streamer", attrs={"data-symbol": ticker, "data-test": "qsp-price",
                                                     "data-field": "regularMarketPrice"}).get_text()
            result[ticker] = price

    return result


def get_stats(ticker):
    response = requests.get(url=f'{BASE_URL}{ticker}/key-statistics?p={config.token}', headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        stats = dict()
        price = soup.find('fin-streamer', attrs={"data-test": "qsp-price", "data-field": "regularMarketPrice",
                                                 "data-symbol": ticker}).get_text()
        stats['price'] = price

        # Get all sections
        stats_section = soup.find("section", attrs={"data-test": "qsp-statistics"})
        stats_div = stats_section.find("div", attrs={"class": "Mstart(a) Mend(a)"})
        all_sections = []
        for section in stats_div.find_all("div", attrs={"class": "Fl(end)"}):
            all_sections.append(section)
        for section in stats_div.find_all("div", attrs={"class": "Fl(start)"}):
            all_sections.append(section)

        stats["sections"] = []

        for section in all_sections:
            section_dict = dict()
            section_header = section.find("h2")
            if section_header is not None:
                section_dict['section_header'] = section_header.get_text()
            else:
                section_dict['section_header'] = ''
            table_sections = section.find_all("div", attrs={"class": "Pos(r) Mt(10px)"})

            section_dict['tables'] = []

            for table_section in table_sections:
                table_dict = dict()
                table_header = table_section.find("h3")
                if table_header is not None:
                    table_dict['table_header'] = table_header.get_text()
                else:
                    table_dict['table_header'] = ''
                table = table_section.find("table")
                table_dict['table'] = dict()
                rows = table.find_all("tr")
                for row in rows:
                    columns = row.find_all("td")
                    if len(columns) == 2:
                        table_dict['table'][columns[0].get_text()] = columns[-1].get_text()
                section_dict['tables'].append(table_dict)
            stats['sections'].append(section_dict)
    else:
        stats = "Не смог найти информацию о компании"
    with open("stats.json", "w") as jsonfile:
        json.dump(stats, jsonfile)
    return stats


def main():
    tickers_array = ["META", "CVNA", "AMZN", "GOOG", "PTON"]
    data = get_stats("META")

    with open("stats.json", "w") as jsonfile:
        json.dump(data, jsonfile)


if __name__ == '__main__':
    main()
