from flask import Flask, render_template, request, jsonify
# 크롤링임포트
import requests



from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.dbsparta

app = Flask(__name__)


# rendering (html 파일 넘겨주기)
@app.route('/community')
def community():
    post_list = list(db.postList.find({}, {'_id': False}))
    return render_template('Community/CommunityMain.html', post_list=post_list)

@app.route('/communityWrite')
def communityWrite():
    return render_template('Community/CommunityWrite.html')


@app.route('/communitydetail')
def communitydetail():
    id_receive = request.args.get("id")
    id = int(id_receive)
    post = list(db.postList.find({'postId':id}, {'_id': False}))
    print(post)
    return render_template('Community/Communitydetail.html', post=post)

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
    return render_template('header.html')


@app.route('/footer')
def footer():
    return render_template('footer.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
