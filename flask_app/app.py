from flask import Flask, redirect, render_template, request, session

from flask_app.article import Article
from flask_app.db import app, db
from flask_app.parsers import get_article


@app.route("/")
def index():
    if 'action' not in session or session['action'] == 0:
        return render_template("index.html", h1="Меню", action=0)
    if session['action'] == 1:
        session['action'] = 0
        return render_template("index.html", h1="Меню", action=1)
    else:
        session['action'] = 0
        return render_template("index.html", h1="Меню", action=2)


@app.route("/articles")
def view_articles():
    return render_template(
        "articles.html",
        h1="Статьи",
        articles=db.session.execute(db.select(Article).order_by(Article.id)).scalars(),
    )


@app.route("/add_article")
def add_article():
    try:
        get_article()
        session['action'] = 1
    except Exception as e:
        print(e)
        session['action'] = 2
    return redirect('/')


@app.route('/update_checkbox', methods=['POST'])
def update_checkbox():
    data = request.get_json()
    checkbox_value = data.get('checkboxValue', False)
    article_id = data.get('articleId', None)

    article = Article.query.filter_by(id=int(article_id)).first()
    article.compliance_label = checkbox_value
    db.session.commit()
    return 'Checkbox updated', 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
