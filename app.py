from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

#template language jinja로 설정

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('mongodb+srv://test:sparta@cluster0.fciykbx.mongodb.net/?retryWrites=true&w=majority')
db = client.dbMUMU

# 홈화면
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        #payload에서 아이디를 꺼내와서
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        #실제 유저의 정보를 가져와
        user_info = db.users.find_one({"username": payload["id"]})
        #그리고 클라이언트에게 보내줘
        return render_template('index.html', user_info=user_info)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# 로그인 화면
@app.route('/login')
def login():
    #jason형식으로 값을 가져온다
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

#로그인 API
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인(username과 password를 받아서)
    # post는 request.form형식으로 클라이언트에게 데이터를 가져온다.
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    #비밀번호의 해시값을 만들어 줌
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    #username과 password가 일치한느 사람이 있는지 판단
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})
    #만약 일치하는 사람이 있다면 로그인이 성공
    #그리고 서버는 JWT토큰을 발행해 줌
    #JWT(Jason Web Token)토큰은 자유입장권 같은 것(Jason객체를 이용해서 사용자 정보를 안정성 있게 전달하는 웹표준)
    if result is not None:
        payload = {
        #입장권의 아이디를 입력
         'id': username_receive,
        #입장권의 유효기간
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }


        #토큰을 만들어서 SECRET_KEY로 암호화해줌
        #decode가 필요없어서 주석처리함
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')#.decode('utf-8')
        #그리고 이 토큰을 클라이언트에게 넘겨줌
        #post와 get모두 return으로 클라이언트에게 데이터를 넘겨준다
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면 실패
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


#회원가입 API
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    #username과 password를 받아서
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    #password는 해시함수를 통해서 암호화해준다
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "profile_name": username_receive,                           # 프로필 이름 기본값은 아이디
        "profile_pic": "",                                          # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png", # 프로필 사진 기본 이미지
        "profile_info": ""                                          # 프로필 한 마디
    }
    #위 정보를 DB로 전송함
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

#이미 클라이언트에서 규칙 맞지 않거나 빈값 필터링해준 후
#DB에서 중복값이 있는지 여부를 체크하는 기능
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    #request로 username을 받아서
    username_receive = request.form['username_give']
    #DB에 존재유무를 확인함
    exists = bool(db.users.find_one({"username": username_receive}))
    #존재유무 여부를 클라이언테에게 보내줌
    return jsonify({'result': 'success', 'exists': exists})