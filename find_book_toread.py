from goodreads import client
import re
import pickle
import os

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
    print("books: \n")
    print(books)
    print("\n")

    print("Ignored Shelf: \n")
    print(ignored_shelf)
    print("\n")

    print("Book Shelf \n")
    print(my_book_shelf)
    print("\n")

    print("Genre to ISBN Dict")
    print(genre_to_isbn_dict)
    print("\n")

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


def display_book(isbn, books):
    if isbn in books.keys():
        book = books.get(isbn)
        print("ID: " + book[ID])
        print("TITLE: " + book[TITLE])
        print("AUTHOR: " + str(book[AUTHOR]))
        print("NUM_RATING: " + book[NUM_RATING])
        print("RATINGS: " + book[RATINGS])
        print("NUM_PAGES: " + book[NUM_PAGES])
        print("GENRE: " + str(book[GENRE]))
        print("PUBLICATION_DATE: " + str(book[PUBLICATION_DATE]))
        print("DESCRIPTION: " + book[DESCRIPTION])
        print("GOODREAD_URL: " + book[GOODREAD_URL])
        

def get_shelves(shelves_list, ignoredShelf, my_book_shelf):
    my_shelf_list = set() #final list of shelves found
    for shelf in shelves_list:
        if len(my_shelf_list) >= 7:
            break
        shelf = canonicalize(shelf.name)

        #Bogus shelf, ignore it
        if shelf in ignoredShelf:
            continue
        #genuine shelf which have already been processed
        if shelf in my_book_shelf:
            my_shelf_list.add(my_book_shelf[shelf])
            continue
        #new unseen shelf
        print("Here are the book shelves seen so far:\n")
        for my_shelf in my_book_shelf.keys():
            print("\t" + my_shelf)
        user_input = input(shelf + " is new shelf: Following are the options:\n"
            + "\t 1. Ignore this shelf\n"
            + "\t 2. Same as seen earlier\n"
            + "\t 3. New book shelf\n"
              )
        # ignore this shelf
        if user_input == '1':
            ignoredShelf[shelf] = shelf
        # although new shelf but another name for some which has already been processed
        elif user_input == '2':
            which_shelf = input("Which self this matches to? ")
            my_shelf_list.add(my_book_shelf[which_shelf])
        # new unseen shelf
        else:
            name = input("Enter an appropriate name for this shelf")
            my_book_shelf[shelf] = name
            my_shelf_list.add(name)

    print("List of new shelves: " + str(my_shelf_list))
    return my_shelf_list


def createGenreDict(shelf_list, genre_dict, isbn):
    for shelf in shelf_list:
        if shelf in genre_dict.keys():
            genre_dict[shelf].append(isbn)
        else:
            genre_dict[shelf] = [isbn]


def fetch_book(gc, isbn, books, ignored_shelf, my_book_shelf, genre_dict):
    if len(books) > 0 and isbn in books.keys():
        print("This ISBN is already fetched:")
        display_book(isbn, books)
        return
    # otherwise fetch the book
    try:
        book = gc.book(isbn=isbn)
        my_book = {}
        my_book[ID] = book.gid
        my_book[TITLE] = book.title
        my_book[AUTHOR] = book.authors
        my_book[NUM_RATING] = book.ratings_count
        my_book[RATINGS] = book.average_rating
        my_book[NUM_PAGES] = book.num_pages
        my_book[GENRE] = get_shelves(book.popular_shelves, ignored_shelf, my_book_shelf)
        my_book[PUBLICATION_DATE] = book.publication_date
        my_book[DESCRIPTION] = book.description
        my_book[GOODREAD_URL] = book.link
        books[isbn] = my_book
        createGenreDict(my_book[GENRE], genre_dict, isbn)
        display_book(isbn, books)

    except client.GoodreadsClientException:
        print("Unable to fetch the ISBN: " + isbn)

def check_isbn(isbn):
    if len(isbn) > 10:
        print("Invalid ISBN")
        return 0
    return 1



def main():
    gc = client.GoodreadsClient('k80yuezhMkvjj7BldKJHA', 'MT72i1WNQyJODTxFXWyQ944yLjmaIysmoqp6PHdGM')

    books_file_name = "/Users/vgarg/repos/find_book_toread/books"
    ignored_shelf_file_name = "/Users/vgarg/repos/find_book_toread/ignored_shelves"
    my_book_shelf_file_name = "/Users/vgarg/repos/find_book_toread/book_shelves"
    genre_to_isbn_file_name = "/Users/vgarg/repos/find_book_toread/genre_to_isbn"

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
              + "Choose an option (Press q to quit): ")
        if user_response == '1':
            isbn=input("ISBN?: ")
            if(check_isbn(isbn) != 1):
                print("Enter valid ISBN(10 digit version)")
            else:
                fetch_book(gc, isbn, books, ignored_shelf, my_book_shelf, genre_to_isbn_dict)
        elif user_response == '2':
            print("Not working yet")
        elif user_response == 'q':
            serialize(books_file_name, books, ignored_shelf_file_name, ignored_shelf, my_book_shelf_file_name,
                      my_book_shelf, genre_to_isbn_file_name, genre_to_isbn_dict)
        else:
            print("Invalid choice!")


main()
