import requests
import time

def get_crypto_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    data = response.json()
    return float(data['price'])

def send_notification(symbol, price):
    # Implement your notification sending logic here
    print(f"{symbol} price is now {price}")

def main():
    # List of cryptocurrencies to track
    cryptos = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'XRPUSDT']
    
    # Price thresholds
    thresholds = {
        'BTCUSDT': 50000,
        'ETHUSDT': 2000,
        'LTCUSDT': 100,
        'XRPUSDT': 0.5
    }
    
    while True:
        for symbol in cryptos:
            price = get_crypto_price(symbol)
            if price >= thresholds[symbol]:
                send_notification(symbol, price)
        
        # Check every 5 minutes
        time.sleep(300)

import requests
from bs4 import BeautifulSoup
import time

def scrape_news(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')
    return articles

def send_notification(article):
    # Implement your notification sending logic here
    print(f"New article: {article.title}")

def main():
    # List of cryptocurrency news websites
    websites = [
        'https://www.coindesk.com/',
        'https://www.cryptonews.com/',
        'https://www.newsbtc.com/'
    ]
    
    # Dictionary to store previously seen articles
    seen_articles = {}
    
    while True:
        for url in websites:
            articles = scrape_news(url)
            for article in articles:
                if article.title not in seen_articles:
                    send_notification(article)
                    seen_articles[article.title] = True
        
        # Check every 1 hour
        time.sleep(3600)

import requests
import time

def check_vulnerabilities(wallet):
    url = f"https://api.blockchair.com/vulnerabilities/{wallet}"
    response = requests.get(url)
    
    try:
        data = response.json()
        return data['data']
    except requests.exceptions.JSONDecodeError:
        print(f"Error decoding JSON for wallet: {wallet}")
        return []


def send_notification(vulnerability):
    # Implement your notification sending logic here
    print(f"New vulnerability: {vulnerability['title']}")

def main():
    # List of cryptocurrency wallets to check
    wallets = ['bitcoin', 'ethereum', 'litecoin', 'ripple']
    
    while True:
        for wallet in wallets:
            vulnerabilities = check_vulnerabilities(wallet)
            for vulnerability in vulnerabilities:
                send_notification(vulnerability)
        
        # Check every 24 hours
        time.sleep(86400)


if __name__ == "__main__":
    main()
