import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.secret_key = 'n9$2@!Df6wE^zXoB7rL0#QsA3!vUz1gT'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'blog.db')

db = SQLAlchemy(app)

# Model
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(20), default=datetime.now().strftime('%Y-%m-%d %H:%M'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)



@app.route('/')
def index():
    posts = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = Blog.query.get_or_404(post_id)
    return render_template('post.html', post=post)


@app.route('/create', methods=['GET', 'POST'])
def create():
    if 'username' not in session:
        flash('Iltimos, post yozishdan oldin tizimga kiring.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_post = Blog(
            title=request.form['title'],
            author=session['username'],  
            content=request.form['content']
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Post muvaffaqiyatli yaratildi!')
        return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Blog.query.get_or_404(post_id)
    if 'username' not in session or post.author != session['username']:
        flash('Siz faqat o‘z postlaringizni o‘chira olasiz.')
        return redirect(url_for('index'))

    db.session.delete(post)
    db.session.commit()
    flash('Post o‘chirildi.')
    return redirect(url_for('index'))



@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Blog.query.get_or_404(post_id)
    if 'username' not in session or post.author != session['username']:
        flash('Faqat o‘z postlaringizni tahrirlashingiz mumkin.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']  # author не трогаем
        db.session.commit()
        flash('Post yangilandi!')
        return redirect(url_for('view_post', post_id=post.id))

    return render_template('edit.html', post=post)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))

        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!')
            return redirect(url_for('index'))  # Change to your homepage
        flash('Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Siz tizimdan chiqdingiz.')
    return redirect(url_for('index')) 


@app.route('/my-posts')
def my_posts():
    if 'username' not in session:
        flash('Avval tizimga kiring.')
        return redirect(url_for('login'))

    posts = Blog.query.filter_by(author=session['username']).order_by(Blog.id.desc()).all()
    return render_template('index.html', posts=posts)




if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Baza faylini va jadvallarni yaratadi
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000, debug=True)



