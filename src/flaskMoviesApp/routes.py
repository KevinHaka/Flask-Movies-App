from flask import render_template, redirect, url_for, request, flash, abort
from flaskMoviesApp.forms import SignupForm, LoginForm, NewMovieForm, AccountUpdateForm
from flaskMoviesApp.models import User, Movie
from flask_login import login_user, current_user, logout_user, login_required
from flaskMoviesApp import app, db, bcrypt

import secrets
from PIL import Image
import os
from datetime import datetime as dt


current_year = dt.now().year


def image_save(image, where, size):
    random_filename = secrets.token_hex(8)
    file_name, file_extension = os.path.splitext(image.filename)
    image_filename = random_filename + file_extension
    image_path = os.path.join(app.root_path, 'static/images/'+ where, image_filename)
    image_size = size

    img = Image.open(image)
    img.thumbnail(image_size)
    img.save(image_path)

    return image_filename

def image_delete(name, where):
    os.remove(os.path.join(app.root_path, 'static/images/'+ where, name))
    



@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(415)
def unsupported_media_type(e):
    return render_template('errors/415.html'), 415

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500



@app.route("/home/")
@app.route("/")
def root():
    page = request.args.get("page", 1, type=int)
    ordering_by = request.args.get('ordering_by', 'date_created', type=str)
    sort = request.args.get('sort', 'desc', type=str)
    movies = Movie.query.order_by(getattr(getattr(Movie, ordering_by), sort)()).paginate(per_page=5, page=page)    
    return render_template("index.html", movies=movies, ordering_by=ordering_by, sort=sort)



@app.route("/signup/", methods=['GET','POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("root"))

    form = SignupForm()

    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        password2 = form.password2.data

        encrypted_password = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(username=username, email=email, password=encrypted_password)
        db.session.add(user)
        db.session.commit()

        flash(f'Ο λογαριασμός για το χρήστη: <b>{username}</b> δημιουργήθηκε με επιτυχία', 'success')

        return redirect(url_for('login'))
    return render_template("signup.html", form=form)



@app.route("/account/", methods=['GET','POST'])
@login_required
def account():
    form = AccountUpdateForm(username=current_user.username, email=current_user.email)

    if request.method == 'POST' and form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data

        if form.image.data:
            try: 
                image_file = image_save(form.image.data, 'profiles_images', (150, 150))

                if current_user.profile_image not in ['default_profile_image.png', 'default_profile_image.jpg']: 
                    image_delete(current_user.profile_image, 'profiles_images')
            except: abort(415)

            current_user.profile_image = image_file

        db.session.commit()
        flash(f'Ο λογαριασμός του χρήστη: <b>{current_user.username}</b> ενημερώθηκε με επιτυχία', 'success')
        
        return redirect(url_for('root'))
    else: return render_template("account_update.html", form=form)



@app.route("/login/", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("root"))

    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            flash(f"Η είσοδος του χρήστη με email: {email} στη σελίδα μας έγινε με επιτυχία.", "success")
            login_user(user, remember=form.remember_me.data)

            next_link = request.args.get("next")

            return redirect(next_link) if next_link else redirect(url_for("root"))
        else:
            flash("Η είσοδος του χρήστη ήταν ανεπιτυχής, παρακαλούμε δοκιμάστε ξανά με τα σωστά email/password.", "warning")
    return render_template("login.html", form=form)



@app.route("/logout/")
def logout():
    logout_user()
    flash("Έγινε αποσύνδεση του χρήστη.", "success")
    return redirect(url_for("root"))



@app.route("/new_movie/", methods=['GET','POST'])
@login_required
def new_movie():
    form = NewMovieForm()

    if request.method == 'POST' and form.validate_on_submit():
        title = form.title.data
        plot = form.plot.data
        rating = form.rating.data
        release_year = form.release_year.data

        if form.image.data:
            try: image = image_save(form.image.data, 'movies_images', (640, 640))
            except: abort(415)
            
            movie = Movie(title=title,
                          plot=plot,
                          author=current_user,
                          image=image,
                          rating=rating,
                          release_year=release_year)

        else:
            movie = Movie(title=title,
                          plot=plot,
                          author=current_user,
                          rating=rating,
                          release_year=release_year)

        db.session.add(movie)
        db.session.commit()

        flash(f'Η ταινία με τίτλο: "{title}" δημοσιεύτηκε με επιτυχία', 'success')

        return redirect(url_for("root"))
    return render_template("new_movie.html", form=form, page_title="Εισαγωγή Νέας Ταινίας", current_year=current_year)



@app.route("/movie/<int:movie_id>")
def movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    return render_template("movie.html", movie=movie)



@app.route("/movies_by_author/<int:author_id>")
def movies_by_author(author_id):
    user = User.query.get_or_404(author_id)
    page = request.args.get("page", 1, type=int)
    ordering_by = request.args.get('ordering_by', 'date_created', type=str)
    sort = request.args.get('sort', 'desc', type=str)
    movies = Movie.query.filter_by(author=user).order_by(getattr(getattr(Movie, ordering_by), sort)()).paginate(per_page=3, page=page)    
    return render_template("movies_by_author.html", movies=movies, author=user, ordering_by=ordering_by, sort=sort)



@app.route("/edit_movie/<int:movie_id>", methods=['GET', 'POST'])
@login_required
def edit_movie(movie_id):
    movie = Movie.query.filter_by(id=movie_id, author=current_user).first_or_404()

    form = NewMovieForm(title=movie.title, plot=movie.plot, rating=movie.rating, release_year=movie.release_year)

    if request.method == 'POST' and form.validate_on_submit():
        movie.title = form.title.data
        movie.plot = form.plot.data
        movie.rating = form.rating.data
        movie.release_year = form.release_year.data
        
        if form.image.data:
            try: 
                if movie.image not in ['default_movie_image.png', 'default_movie_image_l.png']: 
                    image_delete(movie.image, 'movies_images')

                movie.image = image_save(form.image.data, 'movies_images', (640, 640))
            except: abort(415)

        db.session.commit()
        flash(f'Η επεξεργασία της ταινίας έγινε με επιτυχία', 'success')
        
        return redirect(url_for("root"))
    return render_template("new_movie.html", form=form, movie=movie, page_title="Αλλαγή Ταινίας")



@app.route("/delete_movie/<int:movie_id>", methods=["GET", "POST"])
@login_required
def delete_movie(movie_id):
    movie = Movie.query.filter_by(id=movie_id, author=current_user).first_or_404()

    if movie:
        db.session.delete(movie)
        db.session.commit()

        flash("Η ταίνια διεγράφη με επιτυχία.", "success")
    return redirect(url_for("root"))