from flask import Flask, request, render_template,  redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post

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
    return render_template('list.html', users=users)


@app.route("/<int:user_id>")
def show_user(user_id):
    """Show details about a USER"""
    user = User.query.get_or_404(user_id)
    return render_template("details.html", user=user)

@app.route("/<int:user_id>/<int:post_id>")
def show_post(user_id, post_id):
    """Show post"""
    user = User.query.get_or_404(user_id)
    p = Post.query.get_or_404(post_id)
    return render_template("post.html", user=user, p=p)


@app.route("/<int:user_id>/delete_user", methods=["POST"])
def delete_user(user_id):
    """delete user"""
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    return redirect('/')





@app.route('/form')
def show_form():
    return render_template('form.html')


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
def show_edit_form(user_id):
    """show edit form"""
    user = User.query.get_or_404(user_id)
   
    return render_template("edit.html", user=user)




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
    return render_template("new_post.html", user=user)

@app.route('/<int:user_id>/new_post', methods=["POST"])
def handle_new_post(user_id):

    title = request.form["title"]
    content = request.form["content"]
    
    new_post  = Post(title=title, content=content, user_id=user_id)
    db.session.add(new_post)
    db.session.commit()
    post = Post.query.filter(Post.title==title)
    p = post.filter(Post.user_id==user_id).first()
    return redirect(f'/{user_id}/{p.id}')

@app.route("/<int:p_id>/delete_post", methods=["POST"])
def delete_post(p_id):
    """delete post"""
    print('delete post'*10)
    post = Post.query.filter_by(id=p_id).first()
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
    return render_template("edit_post.html", post=post, user=user)

@app.route('/<int:p_id>/edit_post', methods=["POST"])
def edit_post(p_id):
    post = Post.query.get_or_404(p_id)
    post.title = request.form["title"]
    post.content = request.form["content"]
    user_id = post.user_id
    db.session.add(post)
    db.session.commit()
  
    return redirect(f'/{user_id}/{p_id}')