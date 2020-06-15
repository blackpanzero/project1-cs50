
import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


engine=create_engine('postgres://gispjfpiepjviq:718f1e68549e2cab5a9e548d5e8afab9b5d9f2ba29f50b52d610de0498283d23@ec2-35-174-127-63.compute-1.amazonaws.com:5432/dfhjqrd1g62t9v')
db=scoped_session(sessionmaker(bind=engine))

def main():
    f=open("/home/blackpanzero/Downloads/Compressed/project1/books.csv")
    reader= csv.reader(f) 
    next(reader)

    for isbn,title,author,year in reader:
        db.execute("INSERT INTO books (isbn,title,author,year) VALUES (:isbn, :title, :author,:year)",{"isbn":isbn, "title":title,"author":author,"year":year})
        print(f"Added book with ISBN: {isbn} Title: {title}  Author: {author}  Year: {year}")
        db.commit()
    

if __name__ == "__main__":
    main()

