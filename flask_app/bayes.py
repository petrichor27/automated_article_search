from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import ComplementNB
from sklearn.metrics import accuracy_score

from flask_app.article import Article


def bayes():
    x_articles = []
    y_labels = []
    for article in Article.query.all():
        x_articles.append(article.text)
        y_labels.append(article.compliance_label)

    x_train, x_test, y_train, y_test = train_test_split(x_articles, y_labels, test_size=0.2, random_state=42)

    vectorizer = CountVectorizer()
    x_train_vectorized = vectorizer.fit_transform(x_train)
    x_test_vectorized = vectorizer.transform(x_test)

    clf = ComplementNB()
    clf.fit(x_train_vectorized, y_train)

    y_pred = clf.predict(x_test_vectorized)
    accuracy = accuracy_score(y_test, y_pred)
    print(f'accuracy = {accuracy}')
    return round(accuracy, 3)
