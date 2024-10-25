"""
My Top 10 Movie List

Author: Alan
Date: October 25th 2024

This code generates webpage where you can post your own favorite movies
"""

from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Creates a new app for the website
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


# Class for Database
class Base(DeclarativeBase):
    pass


# New Database with the model we added
db = SQLAlchemy(model_class=Base)
# Add a URI to said database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movie_database.db"
# Initialize the database
db.init_app(app)


# New table Movies with the following data
class Movies(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)


# Creates all the tables
with app.app_context():
    db.create_all()
"""
with app.app_context():
    new_movie = Movies(
        title="Phone Booth",
        year=2002,
        description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
        rating=7.3,
        ranking=10,
        review="My favourite character was the caller.",
        img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    )
    db.session.add(new_movie)
    db.session.commit()
"""


@app.route("/")
def home():
    """
    Renders the index.html page
    :return:
    """
    movies = db.session.execute(db.select(Movies).order_by(Movies.rating)).scalars()
    return render_template("index.html", movies=movies)


@app.route("/add")
def add():
    """
    Renders the add.html page
    :return:
    """
    return render_template("add.html")


if __name__ == '__main__':
    app.run(debug=True)
