import sqlite3
from datetime import datetime

DB_NAME = "library.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        year INTEGER,
        status TEXT DEFAULT 'Available'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS borrow_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER,
        member_id INTEGER,
        borrow_date TEXT,
        return_date TEXT,
        status TEXT DEFAULT 'Borrowed',
        FOREIGN KEY(book_id) REFERENCES books(id),
        FOREIGN KEY(member_id) REFERENCES members(id)
    )
    """)

    conn.commit()
    conn.close()


def add_book():
    title = input("Book title: ")
    author = input("Author: ")
    year = input("Year: ")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO books (title, author, year, status) VALUES (?, ?, ?, ?)",
        (title, author, year, "Available")
    )
    conn.commit()
    conn.close()
    print("Book added successfully.")


def view_books():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    conn.close()

    print("\n--- Books ---")
    if not books:
        print("No books found.")
    else:
        for book in books:
            print(f"ID: {book[0]} | Title: {book[1]} | Author: {book[2]} | Year: {book[3]} | Status: {book[4]}")


def update_book():
    view_books()
    book_id = input("Enter book ID to update: ")
    title = input("New title: ")
    author = input("New author: ")
    year = input("New year: ")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE books SET title = ?, author = ?, year = ? WHERE id = ?",
        (title, author, year, book_id)
    )
    conn.commit()
    conn.close()
    print("Book updated successfully.")


def delete_book():
    view_books()
    book_id = input("Enter book ID to delete: ")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    print("Book deleted successfully.")


def add_member():
    name = input("Member name: ")
    email = input("Member email: ")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO members (name, email) VALUES (?, ?)",
        (name, email)
    )
    conn.commit()
    conn.close()
    print("Member added successfully.")


def view_members():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()
    conn.close()

    print("\n--- Members ---")
    if not members:
        print("No members found.")
    else:
        for member in members:
            print(f"ID: {member[0]} | Name: {member[1]} | Email: {member[2]}")


def delete_member():
    view_members()
    member_id = input("Enter member ID to delete: ")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()
    print("Member deleted successfully.")


def borrow_book():
    view_books()
    book_id = input("Enter book ID to borrow: ")

    view_members()
    member_id = input("Enter member ID: ")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT status FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()

    if book is None:
        print("Book not found.")
        conn.close()
        return

    if book[0] != "Available":
        print("This book is already borrowed.")
        conn.close()
        return

    borrow_date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        "INSERT INTO borrow_records (book_id, member_id, borrow_date, status) VALUES (?, ?, ?, ?)",
        (book_id, member_id, borrow_date, "Borrowed")
    )

    cursor.execute(
        "UPDATE books SET status = ? WHERE id = ?",
        ("Borrowed", book_id)
    )

    conn.commit()
    conn.close()
    print("Book borrowed successfully.")


def return_book():
    view_borrow_records()
    record_id = input("Enter borrow record ID to return: ")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT book_id FROM borrow_records WHERE id = ? AND status = ?", (record_id, "Borrowed"))
    record = cursor.fetchone()

    if record is None:
        print("Borrow record not found or already returned.")
        conn.close()
        return

    book_id = record[0]
    return_date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        "UPDATE borrow_records SET return_date = ?, status = ? WHERE id = ?",
        (return_date, "Returned", record_id)
    )

    cursor.execute(
        "UPDATE books SET status = ? WHERE id = ?",
        ("Available", book_id)
    )

    conn.commit()
    conn.close()
    print("Book returned successfully.")


def view_borrow_records():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT borrow_records.id, books.title, members.name, borrow_records.borrow_date,
           borrow_records.return_date, borrow_records.status
    FROM borrow_records
    JOIN books ON borrow_records.book_id = books.id
    JOIN members ON borrow_records.member_id = members.id
    """)

    records = cursor.fetchall()
    conn.close()

    print("\n--- Borrow Records ---")
    if not records:
        print("No borrow records found.")
    else:
        for record in records:
            print(
                f"Record ID: {record[0]} | Book: {record[1]} | Member: {record[2]} | "
                f"Borrow Date: {record[3]} | Return Date: {record[4]} | Status: {record[5]}"
            )


def search_books():
    keyword = input("Enter book title or author to search: ")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM books WHERE title LIKE ? OR author LIKE ?",
        (f"%{keyword}%", f"%{keyword}%")
    )
    books = cursor.fetchall()
    conn.close()

    print("\n--- Search Results ---")
    if not books:
        print("No matching books found.")
    else:
        for book in books:
            print(f"ID: {book[0]} | Title: {book[1]} | Author: {book[2]} | Year: {book[3]} | Status: {book[4]}")


def menu():
    create_tables()

    while True:
        print("\n=== LIBRARY MANAGEMENT SYSTEM ===")
        print("1. Add Book")
        print("2. View Books")
        print("3. Update Book")
        print("4. Delete Book")
        print("5. Add Member")
        print("6. View Members")
        print("7. Delete Member")
        print("8. Borrow Book")
        print("9. Return Book")
        print("10. View Borrow Records")
        print("11. Search Books")
        print("12. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            add_book()
        elif choice == "2":
            view_books()
        elif choice == "3":
            update_book()
        elif choice == "4":
            delete_book()
        elif choice == "5":
            add_member()
        elif choice == "6":
            view_members()
        elif choice == "7":
            delete_member()
        elif choice == "8":
            borrow_book()
        elif choice == "9":
            return_book()
        elif choice == "10":
            view_borrow_records()
        elif choice == "11":
            search_books()
        elif choice == "12":
            print("Exiting system. Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")


menu()