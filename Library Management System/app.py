import os
from flask import Flask,render_template,request,redirect,send_file
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
import PyPDF2
from datetime import datetime,date,timedelta
import matplotlib
matplotlib.use('agg')  
import matplotlib.pyplot as plt
from threading import Thread


# SET UP------------------------------------------------------------------------------------------------
app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project_database.sqlite3"
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


# MODELS------------------------------------------------------------------------------------------------
class User(db.Model):
    User_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    Username=db.Column(db.String,unique=True,nullable=False)
    Password=db.Column(db.String,nullable=False)
    children1 = db.relationship("Requests", back_populates="parent2", cascade="all, delete-orphan")
    children2 = db.relationship("Issued", back_populates="parent2", cascade="all, delete-orphan")
    children3 = db.relationship("Payments", back_populates="parent2", cascade="all, delete-orphan")
    children4 = db.relationship("Returned", back_populates="parent2", cascade="all, delete-orphan")
    children5 = db.relationship("Ratings", back_populates="parent2", cascade="all, delete-orphan")
    children6 = db.relationship("Reject", back_populates="parent2", cascade="all, delete-orphan")

class Admin(db.Model):
    Admin_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    Admin_name=db.Column(db.String,unique=True,nullable=False)
    Password=db.Column(db.String,nullable=False)

class Section(db.Model):
    Sec_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    Name=db.Column(db.String,nullable=False,unique=True)
    Description=db.Column(db.String,nullable=False,unique=True)
    Date_of_creation = db.Column(db.Date, nullable=False)
    children1 = db.relationship("Books", back_populates="parent", cascade="all, delete-orphan")

class Books(db.Model):
    Book_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    Title=db.Column(db.String,nullable=False,unique=True)
    Content=db.Column(db.LargeBinary,nullable=False)
    Authors=db.Column(db.String,nullable=False)
    Section=db.Column(db.String,db.ForeignKey(Section.Name),nullable=False) 
    Cover=db.Column(db.String,unique=True)
    Pages=db.Column(db.Integer,nullable=False)
    children1 = db.relationship("Requests", back_populates="parent1", cascade="all, delete-orphan")
    children2 = db.relationship("Issued", back_populates="parent1", cascade="all, delete-orphan")
    children3 = db.relationship("Payments", back_populates="parent1", cascade="all, delete-orphan")
    children4 = db.relationship("Returned", back_populates="parent1", cascade="all, delete-orphan")
    children5 = db.relationship("Ratings", back_populates="parent1", cascade="all, delete-orphan")
    children6 = db.relationship("Reject", back_populates="parent1", cascade="all, delete-orphan")
    parent = db.relationship("Section", back_populates="children1")

class Requests(db.Model):
    Request_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    Book_title=db.Column(db.String,db.ForeignKey(Books.Title),nullable=False)
    User_id=db.Column(db.String, db.ForeignKey(User.User_id), nullable=False)
    parent1 = db.relationship("Books", back_populates="children1")
    parent2 = db.relationship("User", back_populates="children1")

class Issued(db.Model):
    Issue_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    User_id=db.Column(db.Integer,db.ForeignKey(User.User_id),nullable=False) 
    Book_id=db.Column(db.Integer,db.ForeignKey(Books.Book_id),nullable=False) 
    Date_issued=db.Column(db.Date,nullable=False) 
    Return_date=db.Column(db.Date,nullable=False) 
    parent1 = db.relationship("Books", back_populates="children2")
    parent2 = db.relationship("User", back_populates="children2")

class Payments(db.Model):
    payment_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    User_id=db.Column(db.Integer,db.ForeignKey(User.User_id),nullable=False) 
    Book_id=db.Column(db.Integer,db.ForeignKey(Books.Book_id),nullable=False) 
    Price=db.Column(db.String,nullable=False)
    parent1 = db.relationship("Books", back_populates="children3")
    parent2 = db.relationship("User", back_populates="children3")

class Returned(db.Model):
    return_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    User_id=db.Column(db.Integer,db.ForeignKey(User.User_id),nullable=False) 
    Book_id=db.Column(db.Integer,db.ForeignKey(Books.Book_id),nullable=False) 
    Date_returned=db.Column(db.Date,nullable=False) 
    parent1 = db.relationship("Books", back_populates="children4")
    parent2 = db.relationship("User", back_populates="children4")

class Ratings(db.Model):
    rating_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    User_id=db.Column(db.Integer,db.ForeignKey(User.User_id),nullable=False) 
    Book_id=db.Column(db.Integer,db.ForeignKey(Books.Book_id),nullable=False) 
    Stars=db.Column(db.Integer,nullable=False)
    parent1 = db.relationship("Books", back_populates="children5")
    parent2 = db.relationship("User", back_populates="children5")

class Reject(db.Model):
    Reject_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    Book_title=db.Column(db.String,db.ForeignKey(Books.Title),nullable=False)
    User_id=db.Column(db.String, db.ForeignKey(User.User_id), nullable=False)
    parent1 = db.relationship("Books", back_populates="children6")
    parent2 = db.relationship("User", back_populates="children6")

db.create_all()


# LOGIN-------------------------------------------------------------------------------------------
@app.route('/',methods=['GET','POST'])
def login_as():
    return render_template('choose.html')

@app.route('/login_as',methods=['GET','POST'])
def login_pg():
    if request.method=='POST':
        if request.form['role'] == 'user':
            return render_template('user_login.html')
        if request.form['role'] == 'librarian':
            return render_template('admin_login.html')
        
@app.route('/user_logged_in',methods=['GET','POST'])
def user_logged_in():
    if request.method=='POST':
        if request.form['submit']=='Login':
            user_name=request.form['username']
            pwd=request.form['pass']
            users=User.query.filter_by(Username=user_name).first()
        
            if users is None:
                return render_template('no_user.html')
            else:
                if(pwd==users.Password):
                    return redirect('/user_dashboard/{0}'.format(users.Username)) 
                else:
                    return render_template("wng_pass.html",who="user")
        if request.form['submit']=='Register':  
            user_name=request.form['username']
            pwd=request.form['pass']
            users=User.query.filter_by(Username=user_name).first()
            if(users is None):
                return render_template("T_and_C.html",username=user_name,pwd=pwd)
            else:
                return render_template('user_exists.html')
            
@app.route("/user_relogin")
def userrelogin():
    return render_template('user_login.html')

@app.route("/admin_relogin")
def adminrelogin():
    return render_template('admin_login.html')

@app.route("/forgot",methods=["GET","POST"])
def forgot():
    if request.method=="POST":
        username=request.form["username"]
        pwd=request.form["pass"]

        user=User.query.filter_by(Username=username).first()

        if(user):
            user.Password=pwd
            db.session.add(user)
            db.session.commit()
            return render_template("user_login.html")
        else:
            return render_template("no_user.html")
    return render_template("forgot_pass.html")

@app.route ("/accept_tnc/<username>/<pwd>",methods=["GET","POST"])  
def register_tnc(username,pwd):
    if request.method=='POST':
        new_user=User(Username=username,Password=pwd)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/user_dashboard/{0}'.format(username))

@app.route("/admin_logged_in", methods=['GET','POST'])
def admin_logged_in():
    if request.method=='POST':
        admin_name=request.form['adminname']
        pwd=request.form['pass']

        admins=Admin.query.all()
        flag=False
        for i in admins:
            if i.Admin_name==admin_name :
                flag=True
                if(pwd==i.Password):
                    break
                else:
                    return render_template("wng_pass.html",who="admin")
        if(flag==False):
            new_admin=Admin(Admin_name=admin_name,Password=pwd)
            db.session.add(new_admin)
            db.session.commit()
            
        return redirect('/admin_dashboard')
    

# BOOK DETAILS--------------------------------------------------------------------------------------
@app.route("/see_detail/<book_title>")
def details(book_title):
    book=Books.query.filter_by(Title=book_title).first()
    issued=Issued.query.filter_by(Book_id=book.Book_id).all()
    rate=Ratings.query.filter_by(Book_id=book.Book_id).all()
    if(rate is not None):
        count=len(rate)
        x=0
        for i in rate:
            x+=i.Stars
        if(count>0):
            rating=x/count
        else:
            rating=None
    else:
        rating=None
    return render_template("details.html",book=book,issued=issued,rating=rating)
    

# DASHBOARD--------------------------------------------------------------------------------------
@app.route('/admin_dashboard',methods=['GET','POST'])
def lib_dashb():
    if request.method=='GET':
        reqs=Requests.query.all()
        issued_books=Issued.query.all()
        issues=[]
        for i in issued_books:
            b_title=Books.query.filter_by(Book_id=i.Book_id).first().Title
            issues.append({"Book Title":b_title,"User_id":i.User_id})
        revoke=[]
        for i in issued_books:
            if(i.Return_date<date.today()):
                b_title=Books.query.filter_by(Book_id=i.Book_id).first().Title
                revoke.append({"Book Title":b_title,"User_id":i.User_id})
        sections=Section.query.all()
        return render_template("admin_dashboard.html",requests=reqs,revoke=revoke,sections=sections,issues=issues)

@app.route('/user_dashboard/<user_name>',methods=['GET','POST'])
def user_dashb(user_name):
    if request.method=='GET':
        username=user_name
        books=Books.query.all()
        books.reverse()
        sections=Section.query.all()
        desc="Find all available books here!"
        book_ratings=[]
        for i in books:
            tot_rate = 0
            count = 0
            rate = Ratings.query.filter_by(Book_id=i.Book_id).all()
            if rate:
                for j in rate:
                    count += 1
                    tot_rate += j.Stars
                if count > 0:
                    book_ratings.append({"Book Title": i.Title, "Avg Rating": tot_rate / count})
            else:
                book_ratings.append({"Book Title": i.Title, "Avg Rating": 'No Ratings'})
        return render_template('user_dashboard.html',sections=sections,section="All Books",books=books,username=username,desc=desc,book_ratings=book_ratings)

@app.route("/<username>/books/section",methods=["GET","POST"])
def user_home(username):
    if request.method=="POST":
        books=Books.query.all()
        book_ratings=[]
        for i in books:
            tot_rate = 0
            count = 0
            rate = Ratings.query.filter_by(Book_id=i.Book_id).all()
            if rate:
                for j in rate:
                    count += 1
                    tot_rate += j.Stars
                if count > 0:
                    book_ratings.append({"Book Title": i.Title, "Avg Rating": tot_rate / count})
            else:
                book_ratings.append({"Book Title": i.Title, "Avg Rating": 'No Ratings'})
        if(request.form["section"]=="all_books"):
            sections=Section.query.all()
            books=Books.query.all()
            books.reverse()
            desc="Find all available books here!"
            return render_template("user_dashboard.html",books=books,sections=sections,section="Book List",username=username,desc=desc,book_ratings=book_ratings)
        else:
            section=request.form["section"]
            sections=Section.query.all()
            books=Books.query.filter_by(Section=section).all()
            books.reverse()
            desc=Section.query.filter_by(Name=section).first().Description
            return render_template("user_dashboard.html",books=books,sections=sections,section=section,username=username,desc=desc,book_ratings=book_ratings)



# BOOKS----------------------------------------------------------------------------------------------
@app.route("/add_books",methods=['GET','POST'])
def add_books():
    if request.method=='POST':
        b_title=request.form["title"]
        b_section=request.form["section"]
        b_author=request.form["author"]
        b_content=request.files["content"]
        b_cover=request.form["image"]
        b_cont=b_content.read()
        b_pages=int(get_pdf_page_count(b_content))
        books=Books.query.filter_by(Title=b_title).first()
        if(books!=None):
            return render_template("book_exists.html")
        else:
            newb=Books(Title=b_title,Content=b_cont,Authors=b_author,Section=b_section,Cover=b_cover,Pages=b_pages)
            db.session.add(newb)
            db.session.commit()
        
        return redirect('/admin_books')
    sec=Section.query.all()
    return render_template('add_books.html',sections=sec)

def get_pdf_page_count(file):
    reader = PyPDF2.PdfReader(file)
    return len(reader.pages)

@app.route("/edit_book/<book_title>",methods=["GET","POST"])
def edit_book(book_title):
    if request.method=='POST':
        #b_content=Books.query.filter_by(Title=book_title).first().Content
        b_pages=Books.query.filter_by(Title=book_title).first().Pages
        b_id=Books.query.filter_by(Title=book_title).first().Book_id
        b_title=request.form["title"]
        b_section=request.form["section"]
        b_author=request.form["author"]
        #b_content=request.files["content"]
        b_cover=request.form["image"]
        #b_cont=b_content.read()
        #b_pages=int(get_pdf_page_count(b_content))
        b=Books.query.filter_by(Book_id=b_id).first()
        #if(books!=None):
            #return render_template("book_exists.html")
        b.Title=b_title
        b.Authors=b_author
        b.Section=b_section
        b.Cover=b_cover
        b.Pages=b_pages
        #newb=Books(Title=b_title,Content=b_content,Authors=b_author,Section=b_section,Cover=b_cover,Pages=b_pages)
        db.session.add(b)
        db.session.commit()
        
        return redirect('/admin_books')
    sec=Section.query.all()
    book=Books.query.filter_by(Title=book_title).first()
    return render_template("edit_book.html",book=book,sections=sec)

@app.route("/del_book/<book_title>")
def del_book(book_title):
    book=Books.query.filter_by(Title=book_title).first()
    db.session.delete(book)
    db.session.commit()
    return redirect("/admin_books")

@app.route("/book/<int:book_id>")
def book_content(book_id):
    book=Books.query.filter_by(Book_id=book_id).first()
    return send_file(BytesIO(book.Content),mimetype='application/pdf')
    

# SECTIONS-------------------------------------------------------------------------------------------
@app.route("/add_section",methods=['GET','POST'])
def add_section():
    if request.method=="POST":
        name=request.form["name"]
        desc=request.form["description"]
        date=request.form["date_of_creation"]
        date_of_creation = datetime.strptime(date,'%Y-%m-%d').date()
    
        new_sec=Section(Name=name,Description=desc,Date_of_creation=date_of_creation)
        db.session.add(new_sec)
        db.session.commit()

        return redirect("/admin_books")
    return render_template("add_section.html")
@app.route("/delete/<sec_name>")
def del_section(sec_name):
    sec=Section.query.filter_by(Name=sec_name).first()
    db.session.delete(sec)
    db.session.commit()
    return redirect("/admin_dashboard")

@app.route("/edit/<sec_name>",methods=["GET","POST"])
def edit_sec(sec_name):
    if request.method=="POST":
        sec=Section.query.filter_by(Name=sec_name).first()
        
        desc=request.form["description"]
        date=request.form["date_of_creation"]
        date_of_creation = datetime.strptime(date,'%Y-%m-%d').date()
    
        sec.Name=sec_name
        sec.Description=desc
        sec.Date_of_creation=date_of_creation
        db.session.add(sec)
        db.session.commit()
        return redirect("/admin_dashboard")
    sec=Section.query.filter_by(Name=sec_name).first()
    return render_template("edit_sec.html",sec=sec)


# REQUEST BOOK--------------------------------------------------------------------------------------------
@app.route('/request/<username>/<book_title>')
def requests(username,book_title):
    u_id=User.query.filter_by(Username=username).first().User_id
    req_uid=Requests.query.filter_by(User_id=u_id).all()
    if(len(req_uid)>4):
        return render_template("max_books.html",username=username)
    else:
        req_book=Requests.query.filter_by(Book_title=book_title).all()
        for i in req_uid:
            for j in req_book:
                if(i.Request_id==j.Request_id):
                    return render_template("already_req.html",username=username)
            
        new_r=Requests(User_id=u_id,Book_title=book_title)
        db.session.add(new_r)
        db.session.commit()
        return redirect('/{0}/profile'.format(username))

@app.route("/delete/request/<username>/<book_title>")
def del_req(username,book_title):
    u_id=User.query.filter_by(Username=username).first().User_id
    req=Requests.query.filter_by(Book_title=book_title,User_id=u_id).first()
    db.session.delete(req)
    db.session.commit()
    return redirect('/{0}/profile'.format(username))


# USER PROFILE PAGE-----------------------------------------------------------------------------------
@app.route('/<username>/profile')
def user_books(username):
    req=[]
    print(username)
    u_id=User.query.filter_by(Username=username).first().User_id
    reqs=Requests.query.filter_by(User_id=u_id).all()
    if(reqs is not None):
        for i in reqs:
            b_name=i.Book_title
            b_author=Books.query.filter_by(Title=i.Book_title).first().Authors
            req.append({"Book Title":b_name,"Book Author":b_author})

    issue=Issued.query.filter_by(User_id=u_id).all()
    if(issue is not None):
        for i in issue:
            if(i.Return_date<date.today()):
                db.session.delete(i)
                db.session.commit()
    
    issued=[]
    x=Issued.query.filter_by(User_id=u_id).all()
    if(x is not None):
        for i in x:
            b_id=i.Book_id
            b_title=Books.query.filter_by(Book_id=b_id).first().Title
            b_auth=Books.query.filter_by(Book_id=b_id).first().Authors
            b_cover=Books.query.filter_by(Book_id=b_id).first().Cover
            b_pg=Books.query.filter_by(Book_id=b_id).first().Pages
            price=(b_pg//100)*100
            ret_date=Issued.query.filter_by(Book_id=b_id,User_id=u_id).first().Return_date
            issued.append({"Book Title":b_title,"Book Author":b_auth,"Book id":b_id,"Return_date":ret_date,"Cover":b_cover,"Price":price})
    
    payed_books=Payments.query.filter_by(User_id=u_id).all()
    d_books=[]
    if(payed_books is not None):
        for i in payed_books:
            b_id=i.Book_id
            b=Books.query.filter_by(Book_id=b_id).first()
            d_books.append(b)
    
    returns=[]
    book=Returned.query.filter_by(User_id=u_id).all()
    if(book is not None):
        for i in book:
            bk_id=i.Book_id
            bk=Books.query.filter_by(Book_id=bk_id).first()
            returns.append(bk)
    
    rej=Reject.query.filter_by(User_id=u_id).all()
    if(len(rej)!=0):
        for i in rej:
            buk=i.Book_title
    else:
        buk=None
    
    return render_template("user_profile.html",req=req,username=username,issued=issued,d_books=d_books,returns=returns,rejected_book=buk)
    

# STATISTICS-----------------------------------------------------------------------------------------
def generate_plots():
    with app.app_context():
        book_ratings = []
        books = Books.query.all()
        for i in books:
            tot_rate = 0
            count = 0
            rate = Ratings.query.filter_by(Book_id=i.Book_id).all()
            if rate:
                for j in rate:
                    count += 1
                    tot_rate += j.Stars
                if count > 0:
                    book_ratings.append({"Book Title": i.Title, "Avg Rating": tot_rate / count})
        highest_rated_books = sorted(book_ratings, key=lambda x: x["Avg Rating"], reverse=True)[:5]
        
        books_per_section = []
        sections = Section.query.all()
        for i in sections:
            bk = Books.query.filter_by(Section=i.Name).all()
            book = len(bk)
            books_per_section.append({"Sec_Name": i.Name, "Books": book})

        generate_bar(highest_rated_books)
        generate_pie(books_per_section)
        return highest_rated_books

def generate_bar(highest_rated_books):
    with app.app_context():
        plt.subplots(figsize=(22, 16), facecolor='#f2f2f2')
        plt.barh([book["Book Title"] for book in highest_rated_books],[book["Avg Rating"] for book in highest_rated_books], color='skyblue')
        plt.tick_params(axis='y', labelsize=18) 
        plt.xlabel('Rating')
        plt.ylabel('Book Title')
        plt.gca().invert_yaxis()  
        plt.savefig("./static/stats_barchart.png")
        plt.close()

def generate_pie(books_per_section):
    with app.app_context():
        b_by_s=sorted(books_per_section, key=lambda x: x["Books"])
        book_counts=[book["Books"] for book in b_by_s]
        sections=[book["Sec_Name"] for book in b_by_s]

        plt.subplots(figsize=(10, 8), facecolor='#f2f2f2')
        plt.pie(book_counts, labels=sections, autopct='%1.1f%%', startangle=140, textprops={'fontsize': 25})
        plt.axis('equal') 
        plt.savefig("./static/stats_piechart.png")
        plt.close()

@app.route("/admin_stats")
def admin_stats():
    thread = Thread(target=generate_plots)
    thread.start()
    highest_rated_books = generate_plots()
    return render_template("admin_stats.html", books=highest_rated_books)

@app.route("/user_stats/<username>")
def user_stats(username):
    thread = Thread(target=generate_plots)
    thread.start()
    highest_rated_books = generate_plots()
    return render_template("user_stats.html", username=username, books=highest_rated_books)
#-------------------------------------------------------------------------------------------------

@app.route("/admin_books")
def admin_books():
    sections=Section.query.all()
    books=Books.query.all()
    books.reverse()
    desc="Find all available books here!"
    book_ratings=[]
    for i in books:
        tot_rate = 0
        count = 0
        rate = Ratings.query.filter_by(Book_id=i.Book_id).all()
        if rate:
            for j in rate:
                count += 1
                tot_rate += j.Stars
            if count > 0:
                book_ratings.append({"Book Title": i.Title, "Avg Rating": tot_rate / count})
        else:
            book_ratings.append({"Book Title": i.Title, "Avg Rating": 'No Ratings'})
    return render_template("books.html",sections=sections,books=books,section="Book List",desc=desc,book_ratings=book_ratings)

@app.route("/books/section",methods=["GET","POST"])
def books():
    if request.method=="POST":
        books=Books.query.all()
        book_ratings=[]
        for i in books:
            tot_rate = 0
            count = 0
            rate = Ratings.query.filter_by(Book_id=i.Book_id).all()
            if rate:
                for j in rate:
                    count += 1
                    tot_rate += j.Stars
                if count > 0:
                    book_ratings.append({"Book Title": i.Title, "Avg Rating": tot_rate / count})
            else:
                book_ratings.append({"Book Title": i.Title, "Avg Rating": 'No Ratings'})
        if(request.form["section"]=="all_books"):
            sections=Section.query.all()
            books=Books.query.all()
            books.reverse()
            desc="Find all available books here!"
            
            return render_template("books.html",books=books,sections=sections,section="Book List",desc=desc,book_ratings=book_ratings)
        else:
            section=request.form["section"]
            sections=Section.query.all()
            books=Books.query.filter_by(Section=section).all()
            books.reverse()
            desc=Section.query.filter_by(Name=section).first().Description
            return render_template("books.html",books=books,sections=sections,section=section,desc=desc,book_ratings=book_ratings)
        

# GRANT/ISSUE BOOK---------------------------------------------------------------------------------------------
@app.route("/grant/<book_title>/<user_id>")
def grant(book_title,user_id):
    book_id=Books.query.filter_by(Title=book_title).first().Book_id
    date_issued=date.today()
    return_date=date_issued + timedelta(days=7)

    new_issue=Issued(Book_id=book_id,User_id=user_id,Date_issued=date_issued,Return_date=return_date)
    db.session.add(new_issue)

    req=Requests.query.filter_by(User_id=user_id,Book_title=book_title).first()
    
    db.session.delete(req)
    db.session.commit()
    return redirect("/admin_dashboard")


# DOWNLOAD BOOK-------------------------------------------------------------------------------------------
@app.route("/download/<username>/<book_id>", methods=["GET","POST"])
def download(username,book_id):
    book=Books.query.filter_by(Book_id=book_id).first()
    pg=book.Pages
    price=299
    return render_template("pay.html",price=price,username=username,book_title=book.Title,cover=book.Cover,book_id=book_id)

@app.route("/pay/<username>/<book_id>/<price>", methods=["GET","POST"])
def pay(username,book_id,price):
    if request.method=="POST":
        book=Books.query.filter_by(Book_id=book_id).first()
        u_id=User.query.filter_by(Username=username).first().User_id
        p=Payments(Book_id=book_id,User_id=u_id,Price=price)
        db.session.add(p)
        db.session.commit()
        return render_template("download.html",price=price,username=username,book_title=book.Title,cover=book.Cover,book_id=book_id)
    
@app.route("/download_book/<book_id>" ,methods=["GET","POST"])
def payed(book_id):
        if request.method=='POST':
            book=Books.query.filter_by(Book_id=book_id).first()
            return send_file(BytesIO(book.Content),mimetype='application/pdf',download_name=book.Title, as_attachment=True)


# REVOKE BOOK-----------------------------------------------------------------------------------------------
@app.route("/revoke/<book_title>/<user_id>")
def revoke(user_id,book_title):
    book_id=Books.query.filter_by(Title=book_title).first().Book_id
    book=Issued.query.filter_by(User_id=user_id,Book_id=book_id).first()
    
    db.session.delete(book)
    db.session.commit()
    return redirect("/admin_dashboard")


# RETURN BOOK----------------------------------------------------------------------------------------------
@app.route('/return/<username>/<book_id>',methods=["GET","POST"])
def return_book(username,book_id):
    u_id=User.query.filter_by(Username=username).first().User_id
    
    issued_book=Issued.query.filter_by(User_id=u_id,Book_id=book_id).first()
    db.session.delete(issued_book)
    db.session.commit()

    returned_book=Returned(User_id=u_id,Book_id=book_id,Date_returned=date.today())
    db.session.add(returned_book)
    db.session.commit()

    return redirect('/{0}/profile'.format(username))


# RATING BOOK-----------------------------------------------------------------------------------------------
@app.route('/rate/<username>/<book_id>', methods=["GET","POST"])
def rate_book(username,book_id):
    if request.method=="POST":
        rating=int(request.form["rating"])
        u_id=User.query.filter_by(Username=username).first().User_id
        book=Books.query.filter_by(Book_id=book_id).first()
        already_rated=Ratings.query.filter_by(User_id=u_id,Book_id=book_id).first()
        if(already_rated is not None):
            db.session.delete(already_rated)
        rate=Ratings(User_id=u_id,Book_id=book_id,Stars=rating)
        db.session.add(rate)
        db.session.commit()

        return redirect("/{0}/profile".format(username))
    
    book=Books.query.filter_by(Book_id=book_id).first()
    return render_template("rate.html",book=book,username=username)


# SEARCH ------------------------------------------------------------------------------------------------
@app.route("/search/<username>",methods=["GET","POST"])
def search_user(username):
    book_auth=request.form['search']

    all_books=Books.query.filter_by(Title=book_auth).all()
    all_auth=Books.query.filter_by(Authors=book_auth).all()
    all=all_books+all_auth

    books=Books.query.all()
    book_ratings=[]
    for i in books:
        tot_rate = 0
        count = 0
        rate = Ratings.query.filter_by(Book_id=i.Book_id).all()
        if rate:
            for j in rate:
                count += 1
                tot_rate += j.Stars
            if count > 0:
                book_ratings.append({"Book Title": i.Title, "Avg Rating": tot_rate / count})
        else:
            book_ratings.append({"Book Title": i.Title, "Avg Rating": 'No Ratings'})
    return render_template("user_search_results.html",books=all,username=username,book_ratings=book_ratings)

@app.route("/search",methods=["GET","POST"])
def search_admin():
    book_auth=request.form['search']

    all_books=Books.query.filter_by(Title=book_auth).all()
    all_auth=Books.query.filter_by(Authors=book_auth).all()
    all=all_books+all_auth

    books=Books.query.all()
    book_ratings=[]
    for i in books:
        tot_rate = 0
        count = 0
        rate = Ratings.query.filter_by(Book_id=i.Book_id).all()
        if rate:
            for j in rate:
                count += 1
                tot_rate += j.Stars
            if count > 0:
                book_ratings.append({"Book Title": i.Title, "Avg Rating": tot_rate / count})
        else:
            book_ratings.append({"Book Title": i.Title, "Avg Rating": 'No Ratings'})
    return render_template("admin_search_results.html",books=all,book_ratings=book_ratings)


# REJECT BOOK------------------------------------------------------------------------------------------
@app.route("/reject/<book_title>/<user_id>")
def reject(user_id,book_title):
    req=Requests.query.filter_by(User_id=user_id,Book_title=book_title).first()
    db.session.delete(req)
    db.session.commit()

    rej=Reject(User_id=user_id,Book_title=book_title)
    db.session.add(rej)
    db.session.commit()
    return redirect("/admin_dashboard")

if(__name__=='__main__'):
    app.run(debug=True)