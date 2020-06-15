import os,json
import csv
import requests

from flask import Flask, session,logging,redirect,flash,url_for,g,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from flask import Flask, render_template, request,session

from passlib.hash import sha256_crypt


app = Flask(__name__)
Session(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine=create_engine("postgres://qifidfynugvdse:0fd76f4fb9e4712c5e4106824c9129a78981a1c0ce075472e19c42118e8bc5f0@ec2-3-208-50-226.compute-1.amazonaws.com:5432/de4rcssg9d7jp4")
db = scoped_session(sessionmaker(bind=engine))

app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"

@app.before_request
def before_request():
    g.user=None
    if 'user' in session:
        
        g.user=session['user']
@app.route("/")
def index():
  
  
    	
   return render_template("index.html")


@app.route("/register",methods=["GET","POST"])
def register():
    if g.user:
        
        return redirect(url_for('index'))
    else: 
    
        if request.method=="POST":
            
            username=request.form.get("username")
            email=request.form.get("email")
            password=request.form.get("password")
            confirm=request.form.get("confirm")
            secure_password=sha256_crypt.encrypt(str(password))

            usernamedata=db.execute("SELECT username FROM users WHERE username=:username",{"username":username}).fetchone()
            emaildata=db.execute("SELECT email FROM users WHERE email=:email",{"email":email}).fetchone()

            if usernamedata==None and emaildata==None :
                if password==confirm:
                    db.execute("INSERT INTO users(username,email,password) VALUES(:username,:email,:password)",{"username":username,"email":email,"password":secure_password})
                    db.commit()
                    flash("You are registered.Sign in to access your account","success")
                    return redirect(url_for('login'))
                        
                else:
                    flash("password does not match","danger")
                    return render_template('register.html')
        
                
            else:
                flash("username or email already exists","danger")
                return redirect(url_for('login'))
        return render_template('register.html')


@app.route("/reset",methods=["GET","POST"])
def reset():
    if g.user:
        
        return redirect(url_for('index'))
    else: 
        if request.method=="POST":
            
            username=request.form.get("username")
            email=request.form.get("email")
            password=request.form.get("password")
            confirm=request.form.get("confirm")
            secure_password=sha256_crypt.encrypt(str(password))

            
            
            compare=db.execute("SELECT * FROM users WHERE username=:username AND email=:email",{"username":username,"email":email}).fetchone()
            
            
                
            if compare is None:
                flash("incorrect username or email","danger")
                return render_template('reset.html')
            else:
                if password==confirm:
                    db.execute("UPDATE users SET password=:password WHERE username=:username",{"password":secure_password,"username":username})
                    db.commit()
                    flash("Password reset.Sign in to access your account","success")
                    return redirect(url_for('login'))
            
                else:
                    flash("password does not match","danger")
                    return render_template('reset.html')
        
                
        
        return render_template('reset.html')




@app.route("/login",methods=["GET","POST"])
def login():
    if g.user:
       
        return redirect(url_for('index'))
    else: 
        if request.method=="POST":
            username=request.form.get("username")
            password=request.form.get("password")

            usernamedata=db.execute("SELECT username FROM users WHERE username=:username",{"username":username}).fetchone()
            passworddata=db.execute("SELECT password FROM users WHERE username=:username",{"username":username}).fetchone()

            if usernamedata is None:
                flash("incorrect username or password","danger")
                return render_template('login.html')
            else:
                for passwor_data in passworddata:
                    if sha256_crypt.verify(password,passwor_data):
                        session['user'] = usernamedata
                    
                        return redirect(url_for('search'))
                        
                    else: 
                        flash("incorrect password ","danger")
                        return render_template('login.html')
                        
        return render_template('login.html')


@app.route("/search", methods=["GET","POST"])
def search():

    if g.user:
        if request.method=="POST":
            searchquerry=request.form.get("searchquerry")
          
            searchresult=db.execute("SELECT isbn,author,title FROM books WHERE isbn ILIKE :search OR author ILIKE :search OR title ILIKE :search ",{"search":"%"+searchquerry+"%"}).fetchall()


            resultcount=db.execute("SELECT COUNT(*) FROM books WHERE isbn ILIKE :search OR author ILIKE :search OR title ILIKE :search",{"search":"%"+searchquerry+"%"}).fetchone()
            session["books"]=[]
            for i in searchresult:
                session["books"].append(i)

            resultcount = resultcount[0]
            
            message=f"{resultcount} Matches Found for {searchquerry}"
            flash(message,"success")
            return render_template("search.html",books=session["books"],resultcount=resultcount,searchquerry=searchquerry,searchresult=searchresult)
     


        return render_template("search.html")

    else:
        flash("Please Sign in First","danger")
        return redirect(url_for('login'))
       
        

@app.route("/search/<string:isbn>",methods=["GET","POST"])
def book(isbn):

    if g.user:
        
        if request.method=="POST":
            currentUser = g.user.username
            
            # Fetch form data
            rating = request.form.get("rating")
            comment = request.form.get("comment")
            # Search book_id by ISBN
            row = db.execute("SELECT id FROM books WHERE isbn = :isbn",{"isbn": isbn})
            # Save id into variable
            bookId = row.fetchone() # (id,)
            bookId = bookId[0]
            row2 = db.execute("SELECT * FROM reviews WHERE username = :username AND book_id = :book_id",{"username": currentUser,"book_id": bookId})
              # A review already exists
            if row2.rowcount == 1:
                flash('You already submitted a review for this book', 'warning')
                return redirect("/search/" + isbn)
            # Convert to save into DB
            rating = int(rating)
            db.execute("INSERT INTO reviews (username, book_id, comment, rating) VALUES (:username, :book_id, :comment, :rating)",{"username": currentUser, "book_id": bookId, "comment": comment, "rating": rating})
            db.commit()

            flash('Review submitted!', 'info')
            return redirect("/search/" + isbn)


            
        

        row = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn = :isbn",{"isbn": isbn})

        bookInfo = row.fetchall()
        """ GOODREADS reviews """

       
        key = os.getenv("8mB1oH3g4EQwq3qUilykvg")
        
       
        query = requests.get("https://www.goodreads.com/book/review_counts.json",params={"key": key, "isbns": isbn})

        # Convert the response to JSON
        response = query.json()

        
        response = response['books'][0]

      
        bookInfo.append(response)
            
        """ Users reviews """

        # Search book_id by ISBN
        row = db.execute("SELECT id FROM books WHERE isbn = :isbn",
                        {"isbn": isbn})

         # Save id into variable
        book = row.fetchone() # (id,)
        book = book[0]

        results = db.execute("SELECT username, comment, rating FROM reviews WHERE book_id = :book",{"book": book})
        reviews = results.fetchall()
    
                  

        return render_template("book.html", bookInfo=bookInfo, reviews=reviews)

    else:
        
        return redirect(url_for('login'))
@app.route("/profile",methods=["GET"])
def profile():
    if g.user:
    
        currentUser = g.user.username
        reviewcount=db.execute("SELECT COUNT(*) FROM reviews WHERE username=:username",{"username":currentUser}).fetchone()
        
        reviewcount = reviewcount[0]

        
        results = db.execute("SELECT isbn,title,author,year ,comment,rating FROM books JOIN reviews ON reviews.book_id=books.id WHERE username = :username ",{"username": currentUser}).fetchall()

        email=db.execute("SELECT email FROM users WHERE username=:username",{"username":currentUser}).fetchone()
       
        email = email[0]

        return render_template("profile.html",results=results,email=email,reviewcount=reviewcount)
    else:
        flash("Please Sign First","danger")
        return redirect(url_for('login'))



@app.route("/emailreset",methods=["GET","POST"])
def emailreset():
    if g.user:
    
        if request.method=="POST":

        
            

            password=request.form.get("password")
            email=request.form.get("email")
            
            
            
            currentUser = g.user.username

            
            emaildata=db.execute("SELECT * FROM users WHERE email=:email",{"email":email}).fetchone()
            passworddata=db.execute("SELECT password FROM users WHERE username=:username",{"username":currentUser}).fetchone()
            
    

            if emaildata==None:
                for passwor_data in passworddata:
                    if sha256_crypt.verify(password,passwor_data):
                        db.execute("UPDATE users SET email=:email WHERE username=:username",{"email":email,"username":currentUser})
                        db.commit()
                        flash("email updated","success")
                        return redirect(url_for('profile'))
                        
                    else: 
                        flash("incorrect password ","danger")
                        return render_template('emailreset.html')
            else:
                flash("email exists","danger")
                return render_template('emailreset.html')

        return render_template('emailreset.html')        

    else:
        flash("Please Sign First","danger")
        return redirect(url_for('login'))




@app.route("/api/<ISBN>", methods=["GET"])
def api(ISBN):
    book = db.execute("SELECT * FROM books WHERE isbn = :ISBN", {"ISBN": ISBN}).fetchone()
    if book is None:
        return jsonify({"Error": "Book ISBN entered not available "}), 404
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book.id}).fetchall()
    count = 0
    rating = 0
    for review in reviews:
        count += 1
        rating += review.rating
    if count:
        average_rating = rating / count
    else:
        average_rating = 0

    return jsonify(
        title=book.title,
        author=book.author,
        year=book.year,
        isbn=book.isbn,
        review_count=count,
        average_score=average_rating
    )
                
        
        


@app.route("/sign-out")
def sign_out():

    session.pop('user', None)
    flash("Loged out","danger")

    return redirect(url_for("login"))


