import os
from pathlib import Path
from PIL import Image
import secrets
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, abort
from flask_login import login_required, current_user
from .models import Post, User, Comment
from .forms import RegistrationForm, UpdateAccountForm, PostForm
from . import db

views = Blueprint("views", __name__)

# Route for home page (via blank url or/home)


@views.route("/")
@views.route("/home")
def home():
    # Renders the home page for route
    return render_template("home.html", user=current_user)

# Route for blog page, requires login to access


@views.route("/blog")
@login_required
def blog():
    # Page number, defaults to 1
    page = request.args.get('page', 1, type=int)
    # Paginates blog posts, limits 4 posts per page, descending by newest first.
    posts = Post.query.order_by(
        Post.date_created.desc()).paginate(page=page, per_page=4)
    # Renders the blog page for route
    return render_template("blog.html", user=current_user, posts=posts)

# Route for creating post, requires login to access


@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    # Takes Post form from forms.py
    form = PostForm()
    if form.validate_on_submit():
        # If input fields are valid, create post
        title = form.title.data
        text = form.text.data
        post = Post(title=title, text=text, author=current_user.id)
        # Adds post to database
        db.session.add(post)
        # Saves post to database
        db.session.commit()
        flash('Post created!', category='success')
        # Redirect user to blog page.
        return redirect(url_for('views.blog'))

    # Renders the create post page for route, if GET method
    return render_template("create_post.html", form=form, user=current_user)

# Route for checking blog posts of a user, requires login to access


@views.route("/posts/<username>")
@login_required
def posts(username):
    # Finds user by username saved on database
    user = User.query.filter_by(username=username).first()
    if not user:
        # If user not found, flash message and redirect to home page
        flash('No user with that username exists.', category="error")
        return redirect(url_for('views.home'))
    # Page number, defaults to 1
    page = request.args.get('page', 1, type=int)
    # Paginates blog posts, limits 4 posts per page, descending by newest first.
    posts = Post.query.filter_by(
        author=user.id).paginate(page=page, per_page=4)
    # Render posts page for route
    return render_template("posts.html", user=current_user, posts=posts, username=username)

# Route to delete post with specific id, requires login to access


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    # Find post by ID in database
    post = Post.query.filter_by(id=id).first()
    if not post:
        # If post does not exist, flash error
        flash("Post does not exist.", category='error')
    elif post.author != current_user.id:
        # If user doesn't own post, flash error
        flash("You do not have permission to delete this post.", category="error")
    else:
        # Delete the post from database and save (commit)
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted.", category="success")
    # Redirect to blog page
    return redirect(url_for('views.blog'))

# Route to create comment on post, requires login to access


@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    # Get comment content from form
    text = request.form.get('text')
    if not text:
        # If input is empty, flash error
        flash("Comment cannot be empty.", category="error")
    else:
        # Find post via post id
        post = Post.query.filter_by(id=post_id)
        if post:
            # Create comment
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            # If post does not exist, flash error
            flash("Post does not exist.", category="error")
    # Redirect to blog page
    return redirect(url_for('views.blog'))

# Route to delete specific comment on a post, requires login to access


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    # Find comment by ID in database
    comment = Comment.query.filter_by(id=comment_id).first()
    if not comment:
        # If comment doesn't exist, flash error
        flash("Comment does not exist.", category="error")
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        # If user doesn't own comment and post, flash error
        flash("You do not have permission to delete this comment.", category="error")
    else:
        # Delete comment from database and save (commit)
        db.session.delete(comment)
        db.session.commit()
    # Redirect to blog page
    return redirect(url_for('views.blog'))

# Function used to save picture in account page.


def save_picture(form_picture):
    # Takes root path of current app
    root_path = current_app.root_path
    # Generates random hex string for picture file
    random_hex = secrets.token_hex(8)
    # Splits file extension from picture file
    _, f_ext = os.path.splitext(form_picture.filename)
    # New filename is equal to random hex string plus split file extension
    picture_fn = random_hex + f_ext
    # Path to save picture
    picture_path = os.path.join(
        root_path, 'static', 'profile_pics', picture_fn)
    # Sets width and height of picture file to 125x125
    output_size = (125, 125)
    # Open picture file
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    # Saves image using path to save picture
    img.save(picture_path)
    # Returns to the file via saved filename
    return picture_fn

# Route to view and update user information, requires login to access


@views.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    # Takes update account form from forms.py
    form = UpdateAccountForm()
    if form.validate_on_submit():
        # If form input is valid, update user info
        if form.picture.data:
            # Takes new picture and replaces old profile picture
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        # Replaces old username and email with new details and saves
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated.')
        # Redirect to account page
        return redirect(url_for('views.account'))
    elif request.method == 'GET':
        # Defines initial values for form
        form.username.data = current_user.username
        form.email.data = current_user.email
    # Finds image via path
    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)
    # Renders account page for route
    return render_template('account.html', user=current_user, image_file=image_file, form=form)

# Route to update specific post, requires login to access


@views.route("/update-post/<id>", methods=['GET', 'POST'])
@login_required
def update_post(id):
    # Finds post via ID
    post = Post.query.filter_by(id=id).first()
    if post.author != current_user.id:
        # If user doesn't own post, abort with 403 Fordbidden error
        abort(403)
    # Takes Post form from forms.py
    form = PostForm()
    if form.validate_on_submit():
        # If form input is valid, update post data and save
        post.title = form.title.data
        post.text = form.text.data
        db.session.commit()
        flash('Your post has been updated!', category='success')
        page = request.args.get('page', 1, type=int)
        posts = Post.query.order_by(
            Post.date_created.desc()).paginate(page=page, per_page=4)
        # Renders blog page for route
        return render_template("blog.html", user=current_user, posts=posts)

    # If method is GET
    elif request.method == 'GET':
        # Defines initial values for form
        form.title.data = post.title
        form.text.data = post.text
        # Finds image via path
        image_file = url_for(
            'static', filename='profile_pics/' + current_user.image_file)
    # Render update post page for route
    return render_template("update_post.html", form=form, user=current_user, post=post, image_file=image_file)

# Route for about us page.


@views.route("/about")
def about():
    # Renders about page
    return render_template("about.html", user=current_user)
