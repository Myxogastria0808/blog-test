from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
#パスワードのハッシュ化
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
#標準時の取得
import pytz
#秘密鍵の生成
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
#秘密鍵の生成(ログイン機能の実装)
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)

login_manager = LoginManager()
#LoginManagerとappの紐づけ
login_manager.init_app(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)

#ユーザー情報の読み込み
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
#デコレーター(ログインしているユーザーのみアクセス可能)
@login_required
def index():
    title = "Hello"
    if request.method == 'GET':
        #POSTの値を取得
        posts = Post.query.all()
        return render_template("index.html", title=title, posts=posts)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        #フォームの取得
        username = request.form.get('username')
        password = request.form.get('password')

        #DBに代入(passwordは、sha256でハッシュ化)
        user = User(username=username, password=generate_password_hash(password, method='sha256'))
        #接続
        db.session.add(user)
        #反映
        db.session.commit()
        db.session.close()
        return redirect('/login')
    else:
        return render_template("signup.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #フォームの取得
        username = request.form.get('username')
        password = request.form.get('password')

        #目的のidを取得(try-except文)
        user = User.query.filter_by(username=username).first()
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect('/')
    else:
        return render_template("login.html")

@app.route('/logout')
#デコレーター(ログインしているユーザーのみアクセス可能)
@login_required
def logout():
    logout_user()
    return render_template('logout.html')

@app.route('/create', methods=['GET', 'POST'])
#デコレーター(ログインしているユーザーのみアクセス可能)
@login_required
def create():
    if request.method == 'POST':
        #フォームの取得
        title = request.form.get('title')
        body = request.form.get('body')

        #DBに代入
        post = Post(title=title, body=body)
        #接続
        db.session.add(post)
        #反映
        db.session.commit()
        db.session.close()
        return redirect('/')
    else:
        return render_template("create.html")

@app.route('/<int:id>/update', methods=['GET', 'POST'])
#デコレーター(ログインしているユーザーのみアクセス可能)
@login_required
def update(id):
    #特定のid番号の情報を取得
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        #上書き
        post.title = request.form.get('title')
        post.body = request.form.get('body')
        db.session.commit()
        return redirect('/')

@app.route('/<int:id>/delete', methods=['GET'])
#デコレーター(ログインしているユーザーのみアクセス可能)
@login_required
def delete(id):
    #特定のid番号の情報を取得
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/')











# # テンプレートの使い方
# @app.route("/route")
# def route():
#     bullets = [
#         'Hello1',
#         'Hello2',
#         'Hello3',
#         'Hello4',
#         'Hello5',
#         'Hello6'
#     ]
#     return render_template("index.html", bullets=bullets)

# # 可変URL
# @app.route("/japan/<string:city>")
# def japan(city):
#     return f'Hello, {city} in Japan!'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)