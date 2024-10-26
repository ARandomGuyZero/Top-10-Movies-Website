"""
My Top 10 Movie List

Author: Alan
Date: October 25th 2024

This code generates webpage where you can post your own favorite movies
"""
from os import environ

from dotenv import load_dotenv
from flask import Flask, render_template, request, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from requests import get
from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from werkzeug.utils import redirect
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired, Length

load_dotenv()

url = "https://api.themoviedb.org/3/search/movie"

API_KEY = environ["API_KEY"]

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
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String(500), nullable=True)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)


# Creates all the tables
with app.app_context():
    db.create_all()


# Creates a new form Edit
class EditForm(FlaskForm):
    rating = StringField(f'Your Rating out of 10 e.g. 7.5', validators=[DataRequired(), Length(max=250)])
    review = StringField(f'Your Review', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField(label="Done")


# Creates a new form Add
class AddForm(FlaskForm):
    movie = StringField(f'Movie Title', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField(label="Done")


@app.route("/")
def home():
    """
    Renders the index.html page
    :return:
    """

    # Gets all the movies
    movies = db.session.execute(db.select(Movies).order_by(Movies.rating)).scalars().all()

    # For each movie in the movies
    for i in range(len(movies)):
        # Updates the ranking by getting the iterator value
        movies[i].ranking = len(movies) - i

    # Saves changes
    db.session.commit()

    return render_template("index.html", movies=movies)


@app.route("/add", methods=["GET", "POST"])
def add():
    """
    Renders the add.html page
    :return:
    """

    add_form = AddForm()

    if request.method == "POST":
        parameters = {
            "query": request.form["movie"]
        }

        headers = {
            "accept": "application/json",
            "Authorization": API_KEY
        }

        response = get(url, headers=headers, params=parameters).json()

        return render_template("select.html", results=response)

    return render_template("add.html", form=add_form)


@app.route("/add_database", methods=["GET", "POST"])
def add_database():
    """
    Adds the data from The Movie Database to our database
    :return:
    """
    with app.app_context():
        title = request.args.get("title")
        # Formats the year [YYYY-MM-DD] to just get YYYY
        year = request.args.get("date").split("-")[0]
        # Adds a new movie
        new_movie = Movies(
            title=title,
            year=year,
            description=request.args.get("description"),
            rating=None,
            ranking=None,
            review=None,
            img_url="https://image.tmdb.org/t/p/w500" + request.args.get("img_url")
        )
        db.session.add(new_movie)
        db.session.commit()

        # Fetch the newly added movie by title
        movie = db.session.execute(db.select(Movies).filter_by(title=title)).scalar_one()

    return redirect(url_for("edit", movie_id=movie.id))


@app.route("/edit", methods=["GET", "POST"])
def edit():
    """
    Renders the edit.html page
    :return:
    """
    movie_id = request.args.get("movie_id")
    edit_form = EditForm()

    # If the user presses the button
    if request.method == "POST":
        # Select the movie from the database
        movie_to_update = db.get_or_404(Movies, movie_id)

        # Update the data
        movie_to_update.rating = request.form["rating"]
        movie_to_update.review = request.form["review"]

        # Saves changes
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("edit.html", form=edit_form)


@app.route("/delete")
def delete():
    """
    Deletes a row from the table Movies
    :return:
    """
    # Gets the movie_id from the GET method
    movie_id = request.args.get("movie_id")

    # Gets the row of the movie to delete
    movie_to_delete = (db.get_or_404(Movies, movie_id))

    # Deletes the row of the movie
    db.session.delete(movie_to_delete)

    # Saves changes
    db.session.commit()

    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
