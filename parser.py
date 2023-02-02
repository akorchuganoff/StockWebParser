import requests
from bs4 import BeautifulSoup

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


def get_single_company_news(ticker):
    result = dict()
    response = requests.get(url=f'{BASE_URL}{ticker}/news?p={ticker}', headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        news = soup.find_all('li', attrs={"class": "js-stream-content Pos(r)"})
        for elem in news:
            link = elem.find("a").get("href")
            text = elem.find("a").get_text()
            result[link] = text

    else:
        result[ticker] = "Не смог найти или нет новостей"
    return result


def main():
    tickers_array = ["META", "CVNA", "AMZN", "GOOG", "PTON"]
    for k, v in get_single_company_news("META").items():
        print(f'{k}: {v}')


if __name__ == '__main__':
    main()
