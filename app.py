from flask import Flask, request, render_template,  redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = "123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
print('connect_db')


@app.route('/')
def list_users():
    users = User.query.all()
    tags = Tag.query.all()
    return render_template('list.html', users=users, tags=tags)


@app.route("/<int:user_id>")
def show_user(user_id):
    """Show details about a USER"""
    user = User.query.get_or_404(user_id)
    return render_template("details.html", user=user)

@app.route("/tag/<int:tag_id>")
def show_tag(tag_id):
    """Show tag"""
    tag = Tag.query.get_or_404(tag_id)
    posts = tag.posts
    return render_template("tag.html", tag=tag, posts=posts)

@app.route("/<int:user_id>/<int:post_id>")
def show_post(user_id, post_id):
    """Show post"""
    user = User.query.get_or_404(user_id)
    p = Post.query.get_or_404(post_id)
    return render_template("post.html", user=user, p=p)


@app.route("/<int:user_id>/delete_user", methods=["POST"])
def delete_user(user_id):
    """delete user"""
    user = User.query.get_or_404(user_id)
    posts = user.posts
    for post in posts:
        post.tags = []
        Post.query.filter_by(id=post.id).delete()
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    return redirect('/')

@app.route("/delete_tag/<int:tag_id>", methods=["POST"])
def delete_tag(tag_id):
    """delete tag"""
    Tag.query.filter_by(id=tag_id).delete()
    db.session.commit()
    return redirect('/')



@app.route('/form')
def show_add_user_form():
    return render_template('form.html')

@app.route('/tag_form')
def show_add_tag_form():
    return render_template('add_tag.html')

@app.route('/tag_form', methods=["POST"])
def create_tag():
    name = request.form["name"]
    new_tag  = Tag(name=name)
    db.session.add(new_tag)
    db.session.commit()
    return redirect('/')


@app.route('/form', methods=["POST"])
def create_user():
    first = request.form["first_name"]
    last = request.form["last_name"]
    url = request.form["image_url"]
   
    new_user  = User(first_name=first, last_name=last, image_url=url)
    db.session.add(new_user)
    db.session.commit()

    return redirect(f'/{new_user.id}')




@app.route("/<int:user_id>/edit_user")
def show_edit_user_form(user_id):
    """show edit user form"""
    user = User.query.get_or_404(user_id)
   
    return render_template("edit.html", user=user)



@app.route("/edit_tag/<int:tag_id>")
def show_edit_tag_form(tag_id):
    """show edit tag form"""
    tag = Tag.query.get_or_404(tag_id)
    return render_template("edit_tag.html", tag=tag)

@app.route('/edit_tag/<int:tag_id>', methods=["POST"])
def edit_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form["name"]
    db.session.add(tag)
    db.session.commit()
    return redirect('/')


@app.route('/<int:user_id>/edit_user', methods=["POST"])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    user.first_name = request.form["first_name"]
    user.last_name = request.form["last_name"]
    user.image_url = request.form["image_url"]

    db.session.add(user)
    db.session.commit()

    return redirect(f'/{user.id}')

@app.route("/<int:user_id>/new_post")
def show_new_post_form(user_id):
    """show post form"""
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()
    return render_template("new_post.html", user=user, tags=tags)

@app.route('/<int:user_id>/new_post', methods=["POST"])
def handle_new_post(user_id):

    title = request.form["title"]
    content = request.form["content"]

    tag_ids = [int(num) for num in request.form.getlist("tags")]
    for id in tag_ids:
        print(id)

    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    
    new_post  = Post(title=title, content=content, user_id=user_id,tags=tags)
    db.session.add(new_post)
    db.session.commit()
    post = Post.query.filter(Post.title==title)
    p = post.filter(Post.user_id==user_id).first()
    for tag in p.tags:
        print(tag.name)
    return redirect(f'/{user_id}/{p.id}')

@app.route("/<int:p_id>/delete_post", methods=["POST"])
def delete_post(p_id):
    """delete post"""
    print('delete post'*10)
    post = Post.query.filter_by(id=p_id).first()
    post.tags = []
    user_id = post.user_id
    print(user_id)
    Post.query.filter_by(id=p_id).delete()
    
    db.session.commit()

    return redirect(f'/{user_id}')
    

@app.route("/<int:p_id>/edit_post")
def show_edit_post_form(p_id):
    """show edit post form"""
    post = Post.query.get_or_404(p_id)
    user = post.author
    tags = Tag.query.all()
    return render_template("edit_post.html", post=post, user=user, tags=tags)

@app.route('/<int:p_id>/edit_post', methods=["POST"])
def edit_post(p_id):
    post = Post.query.get_or_404(p_id)
    post.title = request.form["title"]
    post.content = request.form["content"]
    tag_ids = [int(num) for num in request.form.getlist("tags")]
    for id in tag_ids:
        print(id)
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    post.tags = tags
    user_id = post.user_id
    db.session.add(post)
    db.session.commit()
    return redirect(f'/{user_id}/{p_id}')

