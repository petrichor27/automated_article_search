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
        article = get_article()
        db.session.add(article)
        db.session.commit()
        session['action'] = 1
    except Exception:
        session['action'] = 2
    return redirect('/')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
