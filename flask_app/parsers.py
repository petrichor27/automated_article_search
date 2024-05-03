import random

import requests
import re
from bs4 import BeautifulSoup

from flask_app.article import Article, BlackList
from flask_app.db import db


def get_url_for_article(urls):
    url = None
    while url is None:
        site = random.choices(urls, weights=[0, 7, 7, 7, 7, 7, 7, 7, 7, 5])[0]
        response = requests.get(site)
        html = response.content
        soup = BeautifulSoup(html, 'html.parser')
        if site == urls[0]:
            url = get_url_from_moluch(soup)
        if site in urls[1:8]:
            url = get_url_from_sibac(soup)
        if site == urls[9]:
            url = get_url_from_nauchforum(soup)
    return url


def check_article(title, url):
    if Article.query.filter(Article.title == title).first():
        return True
    elif BlackList.query.filter(BlackList.url == url).first():
        print(f'url {url} in black list')
        return True
    else:
        print(title)
        return False


def get_url_from_moluch(soup):
    articles = soup.find_all('div', class_='org-article')
    for _ in range(len(articles)):
        article_ = random.choice(articles)
        a = article_.find('a')
        url = 'https://moluch.ru' + a['href']
        if not check_article(clean_html_text(a.get_text()), url):
            return url
        print(url)


def get_url_from_cyberleninka(soup):
    articles = soup.find_all('h2', class_='title')
    for _ in range(len(articles)):
        article_ = random.choice(articles)
        a = article_.find('a')
        url = 'https://cyberleninka.ru/' + a['href']
        if not check_article(clean_html_text(a.get_text()), url):
            return url
        print(url)


def get_url_from_sibac(soup):
    articles = soup.find_all('h3', class_='title')
    for _ in range(len(articles)):
        article_ = random.choice(articles)
        a = article_.find('a')
        url = a['href']
        if not check_article(clean_html_text(a.get_text()), url):
            return url
        print(url)


def get_url_from_nauchforum(soup):
    articles = soup.find_all('dt', class_='title')
    for _ in range(len(articles)):
        article_ = random.choice(articles)
        a = article_.find('a')
        url = a['href']
        if not check_article(clean_html_text(a.get_text()), url):
            return url
        print(url)


def clean_html_text(html_text):
    cleaned_text = re.sub(r'<[^>]+>', '', html_text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    cleaned_text = cleaned_text.strip()
    return cleaned_text


def for_moluch(soup):
    print(soup.find('h1', itemprop='headline'))
    title = soup.find('h1', itemprop='headline').get_text()

    authors = [author.get_text() for author in soup.find_all('span', itemprop='author')]

    article_body = soup.find('div', itemprop='articleBody')
    keywords_started = False
    annotation = []
    article_text = []
    for paragraph in article_body.find_all('p'):
        if keywords_started:
            article_text.append(paragraph.get_text())
        elif 'Ключевые слова' in paragraph.get_text():
            keywords_started = True
        elif not keywords_started:
            annotation.append(paragraph.get_text())

    return {
        'title': title,
        'authors': clean_html_text(', '.join(authors)),
        'annotation': clean_html_text(' '.join(annotation)),
        'article_text': clean_html_text('\n'.join(article_text))
    }


def for_cyberleninka(soup):
    print(soup.find('i', itemprop='headline'))
    title = soup.find('i', itemprop='headline').get_text()

    authors = [author.find('span').get_text() for author in soup.find_all('li', itemprop='author')]

    annotation = soup.find('p', itemprop='description').get_text()

    article_body = soup.find('div', class_='ocr', itemprop='articleBody')
    keywords_started = False
    author_started = False
    article_text = []
    for paragraph in article_body.find_all('p'):
        if keywords_started:
            article_text.append(paragraph.get_text())
        elif paragraph.get_text().startswith("Ключевые слова"):
            keywords_started = True
        if not authors:
            if author_started:
                authors.append(paragraph.get_text())
                author_started = False
            elif title.lower() in paragraph.get_text().lower():
                author_started = True

    return {
        'title': title,
        'authors': clean_html_text(', '.join(authors)),
        'annotation': clean_html_text(annotation),
        'article_text': clean_html_text('\n'.join(article_text))
    }


def for_sibac(soup):
    print(soup.find('h1', class_='page_title'))
    title = soup.find('h1', class_='page_title').get_text()

    authors = [author.get_text() for author in soup.find('div', class_='authors').find_all('a')]

    article_body = soup.find('div', class_='field-item even')
    article_text = []
    annotation = None
    for paragraph in article_body.find_all('p'):
        if not annotation:
            annotation = paragraph.get_text()
        else:
            article_text.append(paragraph.get_text())

    return {
        'title': title,
        'authors': clean_html_text(', '.join(authors)),
        'annotation': clean_html_text(annotation),
        'article_text': clean_html_text('\n'.join(article_text)),
    }


def for_nauchforum(soup):
    print(soup.find('p', class_='title'))
    title = soup.find('p', class_='title').get_text()

    authors = []
    for author in soup.find_all('div', class_='fio_article'):
        authors.append(author.get_text())

    annotation = None
    article_text = []
    texts = soup.find_all('p', class_='rtejustify')
    for text in texts:
        if not text.find('strong'):
            article_text.append(text.get_text())
        elif text.find('strong').get_text() == 'Аннотация.':
            annotation = text.get_text()[12:]

    return {
        'title': title,
        'authors': clean_html_text(', '.join(authors)),
        'annotation': clean_html_text(annotation),
        'article_text': clean_html_text('\n'.join(article_text))
    }


def get_article():
    # url = 'https://moluch.ru/archive/468/103329/'
    # url = 'https://cyberleninka.ru/article/n/kriptoanaliz-i-kriptografiya-istoriya-protivostoyaniya'
    # url = 'https://nauchforum.ru/conf/tech/xxxiv/73493'

    urls = [
        'https://moluch.ru/keywords/%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%BE%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7/',
        # 'https://cyberleninka.ru/search?q=%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%BE%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7&page=1',
        'https://sibac.info/search/node/%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%BE%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7',
        'https://sibac.info/search/node/%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%BE%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7?page=1',
        'https://sibac.info/search/node/%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%BE%D0%B3%D1%80%D0%B0%D1%84%D0%B8%D1%8F',
        'https://sibac.info/search/node/%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%BE%D0%B3%D1%80%D0%B0%D1%84%D0%B8%D1%8F?page=1',
        'https://sibac.info/search/node/%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%BE%D0%B3%D1%80%D0%B0%D1%84%D0%B8%D1%8F?page=2',
        'https://sibac.info/search/node/%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%BE%D0%B3%D1%80%D0%B0%D1%84%D0%B8%D1%8F?page=3',
        'https://sibac.info/search/node/%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%BE%D0%B3%D1%80%D0%B0%D1%84%D0%B8%D1%8F?page=4',
        'https://sibac.info/search/node/%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%BE%D0%B3%D1%80%D0%B0%D1%84%D0%B8%D1%8F?page=5',
        'https://nauchforum.ru/search/node/%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%BE%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7',
    ]
    url = get_url_for_article(urls)
    print(f'url: {url}')

    try:
        response = requests.get(url)
        html = response.content
        soup = BeautifulSoup(html, 'html.parser')
        article_data = None
        if 'moluch' in url:
            article_data = for_moluch(soup)
        elif 'cyberleninka' in url:
            article_data = for_cyberleninka(soup)
        elif 'nauchforum' in url:
            article_data = for_nauchforum(soup)
        elif 'sibac' in url:
            article_data = for_sibac(soup)

        article = Article(
            title=article_data['title'],
            author=article_data['authors'],
            annotation=article_data['annotation'],
            text=article_data['article_text'],
            url=url,
        )
        db.session.add(article)
        db.session.commit()
    except Exception:
        black_list = BlackList(url=url)
        db.session.add(black_list)
        db.session.commit()
        raise
