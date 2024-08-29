import os
from pathlib import Path
from PIL import Image
import secrets
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Post, User, Comment
from. import db

views = Blueprint("views", __name__)

@views.route("/")
@views.route("/home")
def home():
    return render_template("home.html", user=current_user)

@views.route("/blog")
@login_required
def blog():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_created.desc()).paginate(page=page, per_page=4)
    return render_template("blog.html", user=current_user, posts=posts)


@views.route("/create-post", methods=['GET','POST'])
@login_required
def create_post():
        if request.method == "POST":
            text = request.form.get('text')
            if not text:
                flash('Post cannot be empty', category='error')
            else:
                post = Post(text=text, author=current_user.id)
                db.session.add(post)
                db.session.commit()
                flash('Post created!', category='success')
                return redirect(url_for('views.blog'))
        return render_template("create_post.html", user=current_user)


@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('No user with that username exists.', category="error")
        return redirect(url_for('views.home'))
    
    posts = Post.query.filter_by(author=user.id).all()
    return render_template("posts.html", user=current_user, posts=posts, username=username)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    if not post:
        flash("Post does not exist.", category='error')
    elif post.author != current_user.id:
        flash("You do not have permission to delete this post.", category="error")
    else:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted.", category="success")
    return redirect(url_for('views.blog'))


@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')
    if not text:
        flash("Comment cannot be empty.", category="error")
    else:
        post = Post.query.filter_by(id=post_id)
        if post: 
            comment = Comment(text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash("Post does not exist.", category="error")
    return redirect(url_for('views.blog'))


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    if not comment:
        flash("Comment does not exist.", category="error")
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash("You do not have permission to delete this comment.", category="error")
    else:
        db.session.delete(comment)
        db.session.commit()
    return redirect(url_for('views.blog'))

def save_picture(form_picture):
    path = Path("blog_app/static/profile_pics")
    random_hex=secrets.token.hex(8)
    _,f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(path, picture_fn)
    output_size = (125, 125,)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)