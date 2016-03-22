from system.core.model import Model
import re

class User(Model):
    def __init__(self):
        super(User, self).__init__()

    def create_user(self,info):
        password = info['password']
        pw_hash = self.bcrypt.generate_password_hash(password)
        query = "INSERT into users(name,alias,email,pw_hash,created_at,updated_at) \
                 VALUES('{}','{}','{}','{}',NOW(),NOW())".format(info['name'],info['alias'],info['email'],pw_hash)
        #insert query into db
        create_query = self.db.query_db(query)
        return create_query
    
    def create_book(self,info,author_id):
        #creates book and book review
        book_status = self.exisitingBook(info['title'])
        # print book_status
        if book_status['status'] == False:
            book_query = "INSERT into books (title,author_id,created_at,updated_at) VALUES( '{}','{}',NOW(),NOW()) ".format(info['title'],author_id['id'])
            self.db.query_db(book_query)
            query_book_id = "SELECT books.id FROM books where books.title = '{}'".format(info['title']) 
            book_id = self.db.query_db(query_book_id)[0]
            review_query = "INSERT into book_reviews(book_id,user_id,review,rating,created_at,updated_at) \
                            VALUES('{}','{}','{}','{}',NOW(),NOW())".format(book_id['id'],info['user_id'],info['review'],info['rating'])
            return self.db.query_db(review_query)    
        else:
            book_id = book_status['book_id'][0]
            print ("$" *80)
            print book_id
            review_query = "INSERT into book_reviews(book_id,user_id,review,rating,created_at,updated_at) \
                            VALUES('{}','{}','{}','{}',NOW(),NOW())".format(book_id['id'],info['user_id'],info['review'],info['rating'])
            
            return self.db.query_db(review_query)  

    #insert new author and returns the author_id
    def get_author_id(self, info):
        author_query = "INSERT into authors(name) VALUES('{}')".format(info['author'])
        self.db.query_db(author_query) 
        query_author_id = "SELECT authors.id FROM authors where authors.name = '{}'".format(info['author'])
        author_id = self.db.query_db(query_author_id)[0]
        return author_id

    def add_review(self,info, book_id):
        review_query = "INSERT into book_reviews(book_id,user_id,review,rating,created_at,updated_at) \
                            VALUES('{}','{}','{}','{}',NOW(),NOW())".format(book_id,info['user_id'],info['review'],info['rating'])
            
        return self.db.query_db(review_query)  

    def get_book_id(self,title):
        query = "SELECT books.id from books where title = '{}'".format(title)
        # self.get_book(id)
        return self.db.query_db(query)

    def get_book_reviews(self,id):
        query = "SELECT users.id as user_id,users.name as reviewers, books.id as book_id, books.title, authors.name as author_name, book_reviews.rating, book_reviews.review, book_reviews.created_at \
                 FROM users JOIN book_reviews ON users.id = book_reviews.user_id JOIN books \
                 ON book_reviews.book_id = books.id JOIN authors ON books.author_id = authors.id WHERE book_id = '{}' ORDER BY created_at DESC LIMIT 3".format(id)
        return self.db.query_db(query)
    def get_all_reviews(self):
        query = "SELECT users.id as user_id, users.name as reviewers, books.id as book_id, books.title, authors.name as author_name, book_reviews.rating, book_reviews.review, book_reviews.created_at \
                 FROM users JOIN book_reviews ON users.id = book_reviews.user_id JOIN books \
                 ON book_reviews.book_id = books.id JOIN authors ON books.author_id = authors.id ORDER BY created_at DESC"
        return self.db.query_db(query)

    def get_user_reviews(self,id):
        query = "SELECT users.id as user_id, users.alias, users.email, users.name, books.id as book_id, books.title \
                 FROM users JOIN book_reviews ON users.id = book_reviews.user_id JOIN books \
                 ON book_reviews.book_id = books.id JOIN authors ON books.author_id = authors.id WHERE user_id = '{}'".format(id)
        user = self.db.query_db(query)
        query2 = "SELECT user_id, count(*) as total_reviews FROM book_reviews WHERE user_id = '{}' GROUP BY user_id".format(id)
        total_reviews = self.db.query_db(query2)
        return {"user": user,'total_reviews':total_reviews}

    def get_book(self, id):
        query = "SELECT * from books where id = '{}'".format(id)
        return self.db.query_db(query)

    def get_author_name(self):
        query = "SELECT authors.name FROM authors"
        return self.db.query_db(query)

    def destroy(self,id, user_id):
        query = "DELETE FROM book_reviews WHERE book_id='{}' and user_id = '{}' ".format(id, user_id)
        return self.db.query_db(query)
      
    def validate(self, info, register):
        EMAIL_REGEX = re.compile(r'^[a-za-z0-9\.\+_-]+@[a-za-z0-9\._-]+\.[a-za-z]*$')
        errors = []

        #create user validation
        if register == True:
            if len(info['name']) == 0 or len(info[
                'alias']) == 0 or len(info['email']) == 0:
                errors.append("Theses entries cannot be empty")
            if not EMAIL_REGEX.match(info['email']):
                errors.append("This is not a valid email")
            if len(info['password']) < 8:
                errors.append("Password needs to be greater than 8 characters")
            if info['password'] != info['password2']:
                errors.append("Confirmation password does not match password")

            if len(errors) > 0:
                return {"status": False, "errors": errors}
            else:
                return {"status": True}
        else:
            #login validation
            print("I am in login validation")
            password = info['password']
            query = "SELECT * FROM users WHERE email = '{}' LIMIT 1".format(info['email'])
        
            # print("#" * 80)
            #fetch query from database
            user = self.db.query_db(query)
            print user
            if len(user) > 0:
               # check_password_hash() compares encrypted password in DB to one provided by user logging in
                if self.bcrypt.check_password_hash(user[0]['pw_hash'], password):
                   
                    return {"status" : True, "user" : user[0]}
            # Whether we did not find the email, or if the password did not match, either way return False
                else: 
                    print("User is not in database")
                    return {"status" : False}
            else: 
                return {"status" : False}
            
    def existingAuthor(self,name):
        query = "SELECT authors.id FROM authors WHERE name = '{}'".format(name)
        author_id = self.db.query_db(query)
        if len(author_id) == 0:
            return {"status" : False}
        else:
            #returns author name with author id
            return {"status": True, "author_id": author_id}

    def exisitingBook(self,title):
        query = "SELECT books.id FROM books WHERE title = '{}'".format(title)
        book_id = self.db.query_db(query)
        if len(book_id) == 0:
            return {"status" : False}
        else:
            #returns existing book_id
            return {"status": True, "book_id": book_id}
            


            


    
            
            
            


