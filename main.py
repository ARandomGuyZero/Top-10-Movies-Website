"""
My Top 10 Movie List

Author: Alan
Date: October 25th 2024

This code generates webpage where you can post your own favorite movies
"""

from flask import Flask, render_template, request, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from werkzeug.utils import redirect
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired, Length

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


# Creates a new form Edit
class EditForm(FlaskForm):
    rating = StringField(f'Your rating out of 10 e.g. 7.5', validators=[DataRequired(), Length(max=250)])
    review = StringField(f'Your review', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField(label="Done")


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


@app.route("/add")
def add():
    """
    Renders the add.html page
    :return:
    """
    return render_template("add.html")


if __name__ == '__main__':
    app.run(debug=True)
