import json
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

# from pymongo import MongoClient
# client = MongoClient('localhost', 27017)
# db = client.dbsparta

client = MongoClient('mongodb+srv://test:sparta@cluster0.fciykbx.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta


###################################################################창균님 소스####################
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
        return render_template('Home/home.html', user_info=user_info)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# 로그인 화면
@app.route('/login')
def login():
    #jason형식으로 값을 가져온다
    msg = request.args.get("msg")
    return render_template('Login/login.html', msg=msg)

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


############################ 선호 소스 ######################################
@app.route('/community')
def community():
    token = request.cookies.get('mytoken')
    if token != None:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        payload = payload.get("id")
    else:
        payload = ""

    print(payload)

    post_list = list(db.postList.find({}, {'_id': False}))
    return render_template('Community/CommunityMain.html', post_list=post_list , payload=payload)

@app.route('/communityWrite')
def communityWrite():
    token = request.cookies.get('mytoken')
    if token != None:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        payload = payload.get("id")
    else:
        payload = ""

    return render_template('Community/CommunityWrite.html', payload=payload)


@app.route('/communitydetail')
def communitydetail():
    id_receive = request.args.get("id")
    id = int(id_receive)
    post = list(db.postList.find({'postId':id}, {'_id': False}))

    token = request.cookies.get('mytoken')
    if token != None:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        payload = payload.get("id")
    else:
        payload = ""


    return render_template('Community/Communitydetail.html', post=post, payload=payload)

@app.route('/write', methods=["POST"])
def write():
    postTitle_receive = request.form['postTitle_give']
    movieTitle_receive = request.form['movieTitle_give']
    writer_receive = request.form['writer_give']
    content_receive = request.form['content_give']

    post_list = list(db.postList.find({}, {'_id': False}))
    count = len(post_list) + 1

    doc = {
        'postId': count,
        'postTitle': postTitle_receive,
        'movieTitle': movieTitle_receive,
        'writer': writer_receive,
        'content': content_receive,
        'status': 0
    }

    db.postList.insert_one(doc)
    return jsonify({'msg': '글쓰기 저장 완료'})

@app.route('/update', methods=["POST"])
def update():
    postTitle_receive = request.form['postTitle_give']
    content_receive = request.form['content_give']
    postId_receive = request.form['postId_give']

    id = int(postId_receive)

    db.postList.update_one({'postId': id},{'$set':{'postTitle':postTitle_receive}})
    db.postList.update_one({'postId': id}, {'$set': {'content': content_receive}})
    return jsonify({'msg': '글쓰기 수정 완료'})

@app.route('/delete', methods=["POST"])
def delete():
    postId_receive = request.form['postId_give']

    id = int(postId_receive)

    db.postList.update_one({'postId': id},{'$set':{'status':1}})

    return jsonify({'msg': '글쓰기 삭제완료 완료'})


@app.route('/header')
def header():
    token = request.cookies.get('mytoken')
    if token != None:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        payload = payload.get("id")
    else:
        payload = ""

    return render_template('header.html', payload=payload)


@app.route('/footer')
def footer():
    return render_template('footer.html')

@app.route('/movieInfo')
def movieInfo():
    movieDetail = request.args.get("movieDetail")
    print(movieDetail)

    movie_list = list(db.mumu_movie.find({"title":movieDetail}, {'_id': False}))
    comment_list = list(db.comment_list.find({"movieTitle": movieDetail}, {'_id': False}))

    token = request.cookies.get('mytoken')
    if token != None:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        payload = payload.get("id")
    else:
        payload = ""

    return render_template('movieInfo/movieInfo.html', movieDetail=movie_list, payload=payload,comment=comment_list)


@app.route('/commentSave', methods=["POST"])
def commentSave():
    userStar_receive = request.form['userStar_give']
    comment_receive = request.form['comment_give']
    movieTitle_receive = request.form['movieTitle_give']
    userId_receive = request.form['userId_give']


    comment_list = list(db.comment_list.find({"movieTitle": movieTitle_receive}, {'_id': False}))
    count = len(comment_list) + 1

    doc = {
        'commentId': count,
        'comment': comment_receive,
        'commentUserId': userId_receive,
        'userStar': userStar_receive,
        'movieTitle': movieTitle_receive

    }
    db.comment_list.insert_one(doc)
    return jsonify({'msg': '댓글 저장 완료'})


############################################동건님 소스##############################
@app.route("/main")
def movie_get():
    movie_list = list(db.mumu_movie.find({}, {'_id': False}))
    try:
        return render_template("Home/home.html", moviej=movie_list)
    except exceptions.TemplateAssertionError:
        pass
    except exceptions.UndefinedError:
        pass



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)





