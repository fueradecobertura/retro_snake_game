import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

url = "https://habr.com/ru/search/?q=ddos&target_type=posts&order=relevance"
resp = requests.get(url, headers=HEADERS)
soup = BeautifulSoup(resp.text, 'lxml')

articles = soup.select('article.tm-articles-list__item')

print(f"Найдено статей: {len(articles)}")

for art in articles[:10]:
    title_tag = art.select_one('a.tm-title__link')
    if title_tag:
        print("Заголовок:", title_tag.get_text(strip=True))
        print("Ссылка:", "https://habr.com" + title_tag['href'])
        print("---")
