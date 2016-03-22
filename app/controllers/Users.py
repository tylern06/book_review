from system.core.controller import *

class Users(Controller):
    def __init__(self, action):
        super(Users, self).__init__(action)

        self.load_model('User')

    def index(self):
        #get request load
        #load homepage
        return self.load_view('index.html')

    def create(self):
        userdata = {
            'name' : request.form['name'],
            'alias' : request.form['alias'],
            'email' : request.form['email'],
            'password' : request.form['password'],
            'password2' : request.form['password2'],
        }
       
        #validate user info first before creating user
        create_status = self.models['User'].validate(userdata, register = True)
        if create_status['status'] == True:
            self.models['User'].create_user(userdata)
            session['name'] = userdata['name'] 
            return redirect('/users/books')
        else:
            for message in create_status['errors']:
                flash(message, "regis_errors")
        return redirect('/')

    def login(self):
        userdata = {
            'email' : request.form['email'],
            'password' : request.form['password']
        }

        login_status = self.models['User'].validate(userdata, register = False)
       
        if login_status['status'] == True:
            #separate login_status and user dictionary type
            user = login_status['user']
            session['name'] = user['name']
            session['id'] = user['id']
            print session['id']
            return redirect('/users/books')
        else:
            flash("You are not register in the system ")
            return redirect('/')

    def logout(self):
        session.clear();
        return redirect('/')

    def user_show(self,id):
        user = self.models['User'].get_user_reviews(id)
        userinfo = user['user']
        total_reviews = user['total_reviews'][0]
        return self.load_view('user.html', user=userinfo, total_reviews=total_reviews)

    def books(self):
        #displays all book review
        reviews = self.models['User'].get_all_reviews()
        print reviews
        return self.load_view('books.html', reviews=reviews)

    def books_show(self, id):
        #query book by id and get back all the reviews from the book id
        book = self.models['User'].get_book_reviews(id)
        if len(book) < 1:
            return redirect('/users/books')
        
        else:
            return self.load_view('show.html',book = book)

    def books_add(self):
        #check to see which author selection is chosen
        select = request.form['author2']
        if len(select) != 0:
            author = request.form['author2']
        else:
            author = request.form['author']

        #dictionary KEYS needs to match up with database names
        bookinfo = {
            'title' : request.form['title'],
            'author' : author,
            'review' : request.form['review'],
            'rating' : request.form['rating'],
            'user_id' : session['id']
        }
        #calls the method in Model
        #check if author exisits in database
        print (bookinfo['author'])
        print ("8" *80)
        author_status = self.models['User'].existingAuthor(bookinfo['author'])

        if author_status['status'] == False:
            # call create_books to post reviews by passing in bookinfo
            new_author_id = self.models['User'].get_author_id(bookinfo)
            self.models['User'].create_book(bookinfo, new_author_id)
        else:
            #author exist in system, uses the same author id
            print("author exist in system")
            author_id = author_status['author_id'][0]
            self.models['User'].create_book(bookinfo, author_id)


        book_id = self.models['User'].get_book_id(bookinfo['title'])[0]
        # print book_id

        # redirects to the show book route under routes
        #remember to include full route name! 
        return redirect('/users/books/' + str(book_id['id']))

    #renders the new book add html 
    def books_new(self):
        author_name = self.models['User'].get_author_name()
        
        print author_name
        return self.load_view('books_add.html',authors = author_name)

    def addReview(self,id):
        review = {
            'review' : request.form['add_review'],
            'rating' : request.form['rating'],
            'user_id' : session['id']
        }
        print len(review['review'])
        print("*" *80)
    
        if len(review['review']) < 2:
            flash("Review cannot be empty", "review_error")
            return redirect('/users/books/' + str(id))

        self.models['User'].add_review(review, id)

        return redirect('/users/books/' + str(id))

    def destroy_review(self,id):
        self.models['User'].destroy(id,session['id'])
        return redirect('/users/books/' + str(id))




      



       



