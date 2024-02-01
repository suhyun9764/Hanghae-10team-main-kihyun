from flask import Flask, render_template, request,redirect,url_for,session,jsonify
import os
import requests,os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import asc
from flask_migrate import Migrate


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'session_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)

class Member(db.Model):
    member_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    pwd = db.Column(db.String, nullable=False)
    memos = relationship('Memo', backref='member', lazy=True)
    todo_lists = relationship('Todo', backref='member', lazy=True)
    address_books = relationship('AddressBook', backref='member', lazy=True)
    diaries = relationship('Diary', backref='member', lazy=True)

class Memo(db.Model):
    memo_id = db.Column(db.Integer, primary_key=True)
    main_text = db.Column(db.Text, nullable=False)
    edit_time = db.Column(db.String, default=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'), nullable=False)
    member_id = db.Column(db.String, db.ForeignKey('member.member_id'), nullable=False)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime)
    member_id = db.Column(db.String, db.ForeignKey('member.member_id'), nullable=False)

class AddressBook(db.Model):
    address_id = db.Column(db.Integer, primary_key=True)
    member_name = db.Column(db.String, nullable=False)
    role_mbti = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String, nullable=False)
    project = db.Column(db.String, nullable=False)
    member_id = db.Column(db.String, db.ForeignKey('member.member_id'), nullable=False)

class Diary(db.Model):
    diary_id = db.Column(db.Integer, primary_key=True)
    main_text = db.Column(db.Text, nullable=False)
    edit_time = db.Column(db.String, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    member_id = db.Column(db.String, db.ForeignKey('member.member_id'), nullable=False)

# @app.route('/')
# def index():
#     return render_template('index.html')


# 다이어리 시작
@app.route('/diary')
def diary_list():
    all_diaries = Diary.query.all()
    return render_template('diary.html', all_diaries=all_diaries)

@app.route('/search')
def search():
    data = []
    # URL에서 'query' 파라미터를 가져옵니다.
    query = request.args.get('query', '').lower()
    # 검색어에 해당하는 자료를 찾습니다.
    search_results = [item for item in data if query in item['title'].lower()]

    return render_template('search_results.html', query=query, results=search_results)


@app.route('/diary/regist', methods=['GET', 'POST'])
def diary_regist():
    if request.method == 'POST':
        title = request.form.get('title')
        main_text = request.form.get('mainText')
        edit_time = datetime.now().strftime('%Y-%m-%d')
        memberid = "suhyun9764"

        diary = Diary(title=title, main_text=main_text, edit_time = edit_time,member_id = memberid)
        db.session.add(diary)
        db.session.commit()

        return redirect(url_for('diary_list'))

    return render_template('diary_regist.html')


@app.route('/diary/<num>', methods=['GET', 'POST'])
def diary_detail(num):
    diary = Diary.query.get_or_404(num)

    if request.method == 'POST':
        new_title = request.form['title']
        new_main_text = request.form['mainText']

        diary.title = new_title
        diary.mainText = new_main_text
        db.session.commit()

        return redirect(url_for('diary_list'))

    return render_template('diary_detail.html', diary=diary)


@app.route('/diary/delete/<diaryId>', methods=['post'])
def delete_diary(diaryId):
    diary = Diary.query.get_or_404(diaryId)
    db.session.delete(diary)
    db.session.commit()
    return jsonify({'success': True, 'redirect': url_for('diary_list')})


# class Diary(db.Model):
#     diaryId = db.Column(db.Integer, primary_key=True,
#                         autoincrement=True)  # 시퀀스로 증가
#     title = db.Column(db.String, nullable=False)
#     editTime = db.Column(db.String, nullable=False)
#     mainText = db.Column(db.Text)

#     def __repr__(self):
#         return f"Diary(diaryId={self.diary_id}, title='{self.title}', text='{self.main_text}', editTime='{self.edit_time}')"


# 회원가입 및 로그인
# class Member(db.Model):
#     member_id = db.Column(db.String, primary_key=True)
#     name = db.Column(db.String, nullable=False)
#     pwd = db.Column(db.String, nullable=False)


def __repr__(self):
    return f"Member(member_id={self.member_id}, name='{self.name}', pwd='{self.pwd}')"

# 로그인
@app.route('/signIn', methods=['GET', 'POST'])
def sign_in():
    checkId = None
    checkPw = None

    if request.method == 'POST':
        checkId = request.form.get('memberId')
        checkPw = request.form.get('pwd')
        
        member = Member.query.filter_by(
            member_id=checkId, pwd=checkPw).first()
        print(member.member_id)
        if member:
            # 로그인 성공 시 세션에 사용자 정보 저장
            session['member_id'] = checkId
            return redirect(url_for('dashboard'))
        else:
            return render_template('signin.html', msg='아이디 또는 비밀번호를 확인해 주세요')

    return render_template('signin.html')

##############################################################################################
# 대시보드 페이지 - 로그인이 필요한 페이지

@app.route('/dashboard')
def dashboard():
    if 'member_id' in session:
        # 세션에 사용자 정보가 있다면 index 화면을 렌더링
        return render_template('index.html', member_id=session['member_id'])
    else:
        # 세션에 사용자 정보가 없다면 로그인 화면으로 리다이렉트
        return redirect(url_for('sign_in'))

# 로그아웃
@app.route('/logout')
def logout():
    # 세션에서 사용자 정보 삭제
    session.pop('member_id', None)
    return redirect(url_for('sign_in'))
###############################################################################################

# 회원가입
@app.route('/signUp', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        newId = request.form.get('newId')
        newPwd = request.form.get('newPwd')
        newName = request.form.get('newName')

        new_member = Member(member_id=newId, name=newName, pwd=newPwd)
        db.session.add(new_member)
        db.session.commit()

        # 회원가입 성공 후 signin.html로 이동
        return redirect(url_for('sign_in'))

    return render_template('signup.html')


@app.route('/check', methods=['POST'])
def check_duplicate():
    if request.method == 'POST':
        data = request.get_json()
        newId = data.get('newId')

        oldMember = Member.query.filter_by(member_id=newId).first()

        if oldMember:
            print('duplicate')
            return jsonify({'result': 'duplicate'})
        else:
            print('success')
            return jsonify({'result': 'success'})
    return render_template('signup.html')
    

@app.route("/memo/",methods=["GET"])
def memo():
    print("memo")
    member_id_to_query = 'kihyun2079'
    memo_data = Memo.query.filter_by(member_id=member_id_to_query).order_by(Memo.edit_time.desc()).all()

    if memo_data:
        memo_per_page = 6
        page = request.args.get('page', 1, type=int)
        start_index = (page - 1) * memo_per_page
        end_index = start_index + memo_per_page

        current_page_memo = memo_data[start_index:end_index]

        total_memos = len(memo_data)
        total_pages = (total_memos + memo_per_page - 1) // memo_per_page

        return render_template('memo.html', data=current_page_memo, page_num=total_pages)
    else:
        return "No memo data found for the given member ID."
    
    

@app.route("/memo/", methods=["POST"])
def handle_memo():
    if request.form.get("_method") == "POST":
        return create_memo()
    elif request.form.get("_method") == "PUT":
        return update_memo()
    else:
        return "Invalid request"

def create_memo():
    print("create")
    text = request.form.get("content")
    edit_time = request.form.get("current_time")
    memo_data = Memo(main_text=text, edit_time=edit_time, member_id='kihyun2079')
    db.session.add(memo_data)
    db.session.commit()
    return redirect(url_for('memo'))

def update_memo():
    print("update")
    text_receive = request.form.get("content")
    edit_time_receive = request.form.get("current_time")
    memo_id_receive = request.form.get("memo_id")
    memo_data = Memo.query.filter_by(memo_id=memo_id_receive).first()
    memo_data.main_text = text_receive
    memo_data.edit_time = edit_time_receive
    db.session.add(memo_data)

    db.session.commit()  
    return redirect(url_for('memo'))

@app.route("/memo/delete/<id>")
def delete_memo(id):
    print("delete")
    print(id)
    memo = Memo.query.filter_by(memo_id=id).first()
    if memo:
        db.session.delete(memo)
        db.session.commit()
        return redirect(url_for('memo'))
    else:
        return 'Memo not found', 404

    # 예시 Adress

# 추가한 데이터를 화면에 표시
@app.route("/AddressBook/")
def member():
        member_list = AddressBook.query.all()
        return render_template('address.html', data=member_list)


@app.route("/AddressBook/Add/",methods=["GET"])
def add_member():
    # form 에서 보낸 데이터 받아오기
        member_name_receive = request.args.get("member_name")
        role_mbti_receive = request.args.get("role_mbti")
        image_url_receive = request.args.get("image_url")
        address_id_receive = request.args.get("address_id")
        project_receive = request.args.get("project")
        member_id_receive = request.args.get("member_id")


    # 데이터를 DB에 저장
        adress = AddressBook (member_name=member_name_receive, role_mbti=role_mbti_receive, image_url=image_url_receive, address_id=address_id_receive, project=project_receive, member_id=member_id_receive)
        db.session.add(adress)
        db.session.commit()
        print(project_receive)
        return render_template('address.html')

# Define the route to render the index.html template
@app.route('/')
def index():
    todos = Todo.query.order_by(asc(Todo.date)).all()
    return render_template('todo.html', todos=todos)

# Define the route to add a new todo
@app.route('/api/todolist/', methods=['POST'])
def add_todo():
    try:
        data = request.get_json()
        task = data['task']
        date_str = data['date']
        date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else None
        member_id = "suhyun9764"
        new_todo = Todo(task=task, completed=False, date=date, member_id=member_id)
        db.session.add(new_todo)
        db.session.commit()
        sorted_todos = Todo.query.order_by(asc(Todo.date)).all()

        todos_list = [
            {
                "id": todo.id,
                "task": todo.task,
                "completed": todo.completed,
                "date": todo.date.strftime('%Y-%m-%d') if todo.date else None,
            }
            for todo in sorted_todos
        ]
        response_data = {
            "task":task,
            "success": True,
            "message": "할 일이 성공적으로 추가되었습니다",
            "id": new_todo.id,
            "todos": todos_list
        }

        if new_todo.date:
            response_data["date"] = new_todo.date.strftime('%Y-%m-%d')

        return jsonify(response_data)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# Define the route to update a todo using PATCH
@app.route('/api/todolist/<int:todo_id>', methods=['PATCH'])
def update_todo(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        if todo:
            data = request.get_json()
            todo.completed = data.get('completed', False)
            db.session.commit()
            return jsonify({"success": True, "message": "할 일이 성공적으로 업데이트되었습니다"})
        else:
            return jsonify({"success": False, "message": "존재하지 않는 할 일입니다"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

# Define the route to delete a todo using DELETE
@app.route('/api/todolist/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        if todo:
            db.session.delete(todo)
            db.session.commit()
            return jsonify({"success": True, "message": "할 일이 성공적으로 삭제되었습니다"})
        else:
            return jsonify({"success": False, "message": "존재하지 않는 할 일입니다"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

if __name__ == '__main__':
    app.run()