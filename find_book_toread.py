from goodreads import client

import os
import pickle
import re
import sys

#BookStruct
ID = 0
TITLE = 1
AUTHOR = 2 #list of authors
NUM_RATING = 3
RATINGS = 4
NUM_PAGES = 5
GENRE = 6 #list of genres
PUBLICATION_DATE = 7
DESCRIPTION = 8
GOODREAD_URL = 9

def expunge_bookshelf(my_book_shelf, shelf):
    if shelf in my_book_shelf:
        print("Found book shelf: " + shelf)
        del my_book_shelf[shelf]


def expunge_isbn(isbn, books, genre_to_isbn_dict):
    print("Expunging ISBN: " + isbn)
    genre_list = []
    if isbn in books.keys():
        print("FOUND ISBN: " + isbn)
        book = books[isbn]
        genre_list = book[GENRE]
        del books[isbn]
    for genre in genre_list:
        list_isbn = genre_to_isbn_dict[genre]
        list_isbn.remove(isbn)


def deserialize(books_file_name, ignored_shelf_file_name, my_book_shelf_file_name, genre_to_isbn_file_name):
    books_obj = {}
    ignored_shelf_obj = {}
    my_book_file_obj = {}
    genre_to_isbn_dict = {}
    if os.path.exists(books_file_name) and os.path.getsize(books_file_name) > 0:
        books_file = open(books_file_name, "rb")
        books_obj = pickle.load(books_file)
        books_file.close()

    if os.path.exists(ignored_shelf_file_name) and os.path.getsize(ignored_shelf_file_name) > 0:
        ignored_file = open(ignored_shelf_file_name, "rb")
        ignored_shelf_obj = pickle.load(ignored_file)
        ignored_file.close()

    if os.path.exists(my_book_shelf_file_name) and os.path.getsize(my_book_shelf_file_name) > 0:
        my_book_file = open(my_book_shelf_file_name, "rb")
        my_book_file_obj = pickle.load(my_book_file)
        my_book_file.close()

    if os.path.exists(genre_to_isbn_file_name) and os.path.getsize(genre_to_isbn_file_name) > 0:
        genre_to_isbn_file = open(genre_to_isbn_file_name, "rb")
        genre_to_isbn_dict = pickle.load(genre_to_isbn_file)
        genre_to_isbn_file.close()


    print("Deserialzed. Total number of books: " +  str(len(books_obj)))
    print("Deserialzed. Total number of ignored shelves : " +  str(len(ignored_shelf_obj)))
    print("Deserialzed. Total number of shelves : " +  str(len(my_book_file_obj)))
    print("Deserialzed. Total genre to isbn dictionary size: " +  str(len(genre_to_isbn_dict)))
    return [books_obj, ignored_shelf_obj, my_book_file_obj, genre_to_isbn_dict]


def serialize(books_file_name, books, ignored_shelf_file_name, ignored_shelf, my_book_shelf_file_name, my_book_shelf,
              genre_to_isbn_file_name, genre_to_isbn_dict):
    print("Serialzing...")
    books_file = open(books_file_name, "wb")
    pickle.dump(books, books_file)
    books_file.close()

    ignore_file = open(ignored_shelf_file_name, "wb")
    pickle.dump(ignored_shelf, ignore_file)
    ignore_file.close()

    my_book_shelf_file = open(my_book_shelf_file_name, "wb")
    pickle.dump(my_book_shelf, my_book_shelf_file)
    my_book_shelf_file.close()

    genre_to_isbn_file = open(genre_to_isbn_file_name, "wb")
    pickle.dump(genre_to_isbn_dict, genre_to_isbn_file)
    genre_to_isbn_file.close()

# cananocalization(shelf)
def canonicalize(shelf_name):
    # remove all characters but alpha-numeric and turn to lower case
    return re.sub('[^A-Za-z0-9]+', '', shelf_name).lower()


def display_books(isbn_list, books):
    print("ID\tTITLE\tAUTHOR\tNUM RATINGS\tRATINGS\tTOTAL PAGES\n")
    for isbn in isbn_list:
        display_book(isbn, books)



def display_book(isbn, books):
    if isbn in books.keys():
        book = books.get(isbn)
        print(book[ID] + "\t"  + book[TITLE] + "\t" + str(book[AUTHOR]) + "\t" + book[NUM_RATING] + "\t "+ book[RATINGS]
            + "\t" + book[NUM_PAGES])
            #+ "\t" + str(book[GENRE])
            #+ "\t" + str(book[PUBLICATION_DATE]))
        #print("DESCRIPTION: " + book[DESCRIPTION])
        #print("GOODREAD_URL: " + book[GOODREAD_URL])
        

def get_shelves(shelves_list, ignoredShelf, my_book_shelf):
    my_shelf_list = set() #final list of shelves found
    for shelf in shelves_list:
        if len(my_shelf_list) >= 7:
            break
        shelf = canonicalize(shelf.name)

        if(shelf == ''): # could be due to presence of all non alpha numeric
            continue

        #Bogus shelf, ignore it
        if shelf in ignoredShelf:
            continue
        #genuine shelf which have already been processed
        elif shelf in my_book_shelf:
            my_shelf_list.add(my_book_shelf[shelf])
            continue
        #new unseen shelf
        print("\n******************************************************")
        print("All book shelves seen so far: ", end= " ")
        relevant_shelf = []
        for my_shelf in sorted(my_book_shelf.keys()):
            if my_shelf[0] == shelf[0]:
                relevant_shelf.append(my_shelf)
            else:
                print(my_shelf, end=" ")
        print("\nAll relevant shelves seen so far: ", end= " ")
        for my_shelf in relevant_shelf:
            print(my_shelf, end=" ")
        user_input = input("\n\n" + " CURRENT SHELF: " + shelf
                           + "\n Options: " + "\t Ignore this shelf(1)" + "\t Same as seen earlier(2)"+ "\t New book shelf(3)\n")
        # ignore this shelf
        if user_input == '1':
            ignoredShelf[shelf] = shelf
        # although new shelf but another name for some which has already been processed
        elif user_input == '2':
            which_shelf = input("\nWhich self this matches to?:  ")
            if which_shelf not in my_shelf_list:
                my_shelf_list.add(my_book_shelf[which_shelf])
            my_book_shelf[shelf] = my_book_shelf[which_shelf]
        # new unseen shelf
        else:
            name = input("\nEnter an appropriate name for this shelf: ")
            if name == '':
                name = shelf.title()
                print("\nNew shelf: " + name, end='', flush=True)
            my_book_shelf[shelf] = name
            my_shelf_list.add(name)

    print("\nList of new shelves: " + str(my_shelf_list), end=" ")
    return my_shelf_list


def createGenreDict(shelf_list, genre_dict, isbn):
    for shelf in shelf_list:
        if shelf in genre_dict.keys():
            genre_dict[shelf].append(isbn)
        else:
            genre_dict[shelf] = [isbn]

#def expunge_isbn(isbn, books, ignored_shelf, my_book_shelf, genre_dict):
    # TODO 0812968581
    # delete from books
    # delete all corresponding shelves from my_book_shel
    # delete all corresponding entries from genre_dict
    # Keep ignored_shelf


def fetch_book(gc, isbn, books, ignored_shelf, my_book_shelf, genre_dict):
    if(check_isbn(isbn) != 1):
        print("\nEnter valid ISBN(10 digit version)")
        return
    if len(books) > 0 and isbn in books.keys():
        print("This ISBN is already fetched:")
        display_book(isbn, books)
        return
    # otherwise fetch the book
    try:
        book = gc.book(isbn=isbn)
        print("\n Fetched ISBN: " + isbn)
        my_book = {}
        my_book[ID] = book.gid
        my_book[TITLE] = book.title
        my_book[AUTHOR] = str(book.authors)
        my_book[NUM_RATING] = book.ratings_count
        my_book[RATINGS] = book.average_rating
        my_book[NUM_PAGES] = '0' if book.num_pages==None else book.num_pages
        my_book[GENRE] = get_shelves(book.popular_shelves, ignored_shelf, my_book_shelf)
        my_book[PUBLICATION_DATE] = book.publication_date
        my_book[DESCRIPTION] = book.description
        my_book[GOODREAD_URL] = book.link
        books[isbn] = my_book
        createGenreDict(my_book[GENRE], genre_dict, isbn)
        #display_book(isbn, books)

    except client.GoodreadsClientException:
        print("Unable to fetch the ISBN: " + isbn)

def check_isbn(isbn):
    if len(isbn) > 10:
        print("Invalid ISBN")
        return 0
    return 1


# Given existing genre dictionary and a list of isbns
# this creates new dictionary of genre based on list of ISBNs
def create_new_genre_dict(list_isbn, books):
    new_genre_dict = {}
    for isbn in list_isbn:
        book = books[isbn]
        book_genre_list = book[GENRE]
        createGenreDict(book_genre_list, new_genre_dict, isbn)

    return new_genre_dict


def display_genres(genre_to_isbn_dict, books):
    # get top 10 genres
    for k in sorted(genre_to_isbn_dict, key=lambda k: len(genre_to_isbn_dict[k]), reverse=True):
        print(k + ":" + str(len(genre_to_isbn_dict[k])))
    user_response = 'y'
    user_response = input("Enter a genre (or q to quit): ")
    if user_response != 'q':
        isbn_list = genre_to_isbn_dict[user_response]
        new_genre_dict = create_new_genre_dict(isbn_list, books)
        option = input("Display books(b) or filter genre?: ")
        if option == 'b':
            display_books(isbn_list, books)
        else:
            display_genres(new_genre_dict, books)


def main(api_key, api_sceret):
    try:
        gc = client.GoodreadsClient(api_key, api_sceret)
    except client.GoodreadsRequestException:
        print("Unable to connect too Goodreads. Make sure api key and secret is correct")
        return
    except Exception:
        print("Something went wrong while connecting to goodreads")
        return


    files_dir = "./data/"
    books_file_name = files_dir + "books"
    ignored_shelf_file_name = files_dir + "ignored_shelves"
    my_book_shelf_file_name = files_dir + "book_shelves"
    genre_to_isbn_file_name = files_dir + "genre_to_isbn"
    isbn_file = files_dir + "isbn.list"

    obj_list = deserialize(books_file_name, ignored_shelf_file_name, my_book_shelf_file_name, genre_to_isbn_file_name)
    books = obj_list[0]
    ignored_shelf = obj_list[1]
    my_book_shelf = obj_list[2]
    genre_to_isbn_dict = obj_list[3]

    user_response = 'y'
    while user_response != 'q':
        user_response = input("Following are the options: \n"
              + "\t 1. Add new book (using ISBN) \n"
              + "\t 2. Find book to read \n"
              + "\t 3. Delete an ISBN \n"
              + "Choose an option (Press q to quit): ")
        if user_response == '1':
            isbn=input("ISBN?: ")
            if(check_isbn(isbn) != 1):
                print("\nEnter valid ISBN(10 digit version)")
            else:
                try:
                    fetch_book(gc, isbn, books, ignored_shelf, my_book_shelf, genre_to_isbn_dict)
                except:
                    print("Something wrong happend")
                    serialize(books_file_name, books, ignored_shelf_file_name, ignored_shelf, my_book_shelf_file_name,
                      my_book_shelf, genre_to_isbn_file_name, genre_to_isbn_dict)
        elif user_response == '2':
            display_genres(genre_to_isbn_dict, books)
        elif user_response == 'q':
            print("\nquitting...")
        elif user_response == '3':
            isbn = input("ISBN?: ")
            expunge_isbn(isbn, books, genre_to_isbn_dict)
        elif user_response == '4':
            with open(isbn_file) as f:
                isbn = f.readline()
                while isbn:
                    try:
                        fetch_book(gc, isbn.rstrip(), books, ignored_shelf, my_book_shelf, genre_to_isbn_dict)
                        should_continue = input("\nShould continue with next ISBN?: ")
                        if should_continue == 'n':
                            f.close()
                            serialize(books_file_name, books, ignored_shelf_file_name, ignored_shelf, my_book_shelf_file_name,
                                  my_book_shelf, genre_to_isbn_file_name, genre_to_isbn_dict)
                            break
                        else:
                            isbn = f.readline()
                    except:
                        f.close()
                        print("Something went wrong while fetching..")
                        serialize(books_file_name, books, ignored_shelf_file_name, ignored_shelf, my_book_shelf_file_name,
                                  my_book_shelf, genre_to_isbn_file_name, genre_to_isbn_dict)
                        break;

        elif user_response == '5':
            shelf=input("Shelf to delete? ")
            expunge_bookshelf(my_book_shelf, shelf)
        else:
            print("Invalid choice!")

    serialize(books_file_name, books, ignored_shelf_file_name, ignored_shelf, my_book_shelf_file_name,
                      my_book_shelf, genre_to_isbn_file_name, genre_to_isbn_dict)


main(sys.argv[1], sys.argv[2])
