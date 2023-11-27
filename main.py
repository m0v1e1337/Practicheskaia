import hashlib
import sqlite3

from django.contrib.auth.models import User


class Book:
    def __init__(self, title, author, year, available):
        self.title = title
        self.author = author
        self.year = year
        self.available = available


class Library:
    def __init__(self):
        self.conn = sqlite3.connect('library.db')
        self.c = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                author TEXT,
                year INTEGER,
                available INTEGER
            )
        ''')
        self.conn.commit()

    def add_book(self, book):
        self.c.execute('''
            INSERT INTO books (title, author, year, available)
            VALUES (?, ?, ?, ?)
        ''', (book.title, book.author, book.year, book.available))
        self.conn.commit()

    def update_book(self, book_id, title, author, year, available):
        self.c.execute('''
            UPDATE books
            SET title = ?, author = ?, year = ?, available = ?
            WHERE id = ?
        ''', (title, author, year, available, book_id))
        self.conn.commit()

    def delete_book(self, book_id):
        self.c.execute('''
            DELETE FROM books
            WHERE id = ?
        ''', (book_id,))
        self.conn.commit()

    def get_all_books(self):
        self.c.execute('SELECT * FROM books')
        rows = self.c.fetchall()
        books = []
        for row in rows:
            book = Book(row[1], row[2], row[3], row[4])
            books.append(book)
        return books

    def search_books(self, keyword):
        self.c.execute('''
            SELECT * FROM books
            WHERE title LIKE ? OR author LIKE ?
        ''', ('%'+keyword+'%', '%'+keyword+'%'))
        rows = self.c.fetchall()
        books = []
        for row in rows:
            book = Book(row[1], row[2], row[3], row[4])
            books.append(book)
        return books

    def close(self):
        self.conn.close()


class Cart:
    def __init__(self):
        self.books = []

    def add_book(self, book):
        self.books.append(book)

    def remove_book(self, book):
        self.books.remove(book)

    def clear(self):
        self.books = []

    def get_total_price(self):
        total_price = 0
        for book in self.books:
            total_price += book.price
        return total_price


class Order:
    def __init__(self, cart, user):
        self.cart = cart
        self.user = user

    def place_order(self):
        # Проверяем, есть ли товары в корзине
        if len(self.cart.books) == 0:
            print("Ошибка: Корзина пуста. Заказ не может быть оформлен.")
            return

        # Проверяем, авторизован ли пользователь
        if not self.user.is_authenticated():
            print("Ошибка: Пользователь не авторизован. Пожалуйста, авторизуйтесь, чтобы оформить заказ.")
            return

        def create_order_in_database(self):
            self.conn = sqlite3.connect('orders.db')
            self.c = self.conn.cursor()

            # Создаем таблицу, если она уже не существует
            self.c.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    book_id INTEGER,
                    status TEXT
                )
            ''')
            self.conn.commit()

            # Добавляем запись о заказе в базу данных
            order_id = self.c.execute('''
                INSERT INTO orders (user_id, book_id, status)
                VALUES (?, ?, ?)
            ''', (self.user.id, self.cart.books[0].id, 'В ожидании')).lastrowid
            self.conn.commit()

            self.conn.close()
            return order_id

        def send_order_confirmation(self):
            # Отправка уведомления пользователю о заказе
            print("Уведомление: Ваш заказ успешно оформлен")

        def cancel_order_in_database(self, order_id):
            self.conn = sqlite3.connect('orders.db')
            self.c = self.conn.cursor()
            self.c.execute('''
                UPDATE orders
                SET status = ?
                WHERE id = ?
            ''', ('Отменено', order_id))
            self.conn.commit()
            self.conn.close()

        def send_order_cancellation(self, order_id):
            # Отправка уведомления пользователю об отмене заказа
            print(f"Уведомление: Заказ с номером {order_id} был отменен")

            # Проверяем, существует ли заказ с указанным номером
            if not self.check_order_exists(order_id):
                print(f"Ошибка: Заказ с номером {order_id} не существует. Пожалуйста, проверьте номер заказа.")
                return

            # Проверяем, зафиксирован ли уже платеж по данному заказу
            if self.check_payment_status(order_id):
                print(f"Ошибка: Заказ с номером {order_id} уже был оплачен и не может быть отменен.")
                return

            # Запрашиваем подтверждение от пользователя для отмены заказа
            confirmation = input("Вы действительно хотите отменить заказ? (Да/Нет): ")
            if confirmation.lower() == "да":
                # Отменяем заказ
                self.update_order_status(order_id, "Отменен")
                self.send_order_cancellation(order_id)
                print(f"Заказ с номером {order_id} успешно отменен.")
            else:
                print("Отмена заказа отменена.")

    def cancel_order(self, order_id):
        # Проверяем, существует ли заказ с указанным номером
        if not self.check_order_exists(order_id):
            print(f"Ошибка: Заказ с номером {order_id} не существует. Пожалуйста, проверьте номер заказа.")
            return

        # Проверяем, зафиксирован ли уже платеж по данному заказу
        if self.check_payment_status(order_id):
            print(f"Ошибка: Заказ с номером {order_id} уже был оплачен и не может быть отменен.")
            return

        # Запрашиваем подтверждение от пользователя для отмены заказа
        confirmation = input("Вы действительно хотите отменить заказ? (Да/Нет): ")
        if confirmation.lower() == "да":
            # Отменяем заказ
            self.cancel_order_in_database(order_id)
            self.send_order_cancellation(order_id)
            print(f"Заказ с номером {order_id} успешно отменен.")
        else:
            print("Отмена заказа отменена.")
        pass

    def check_payment_status(self, order_id):
        pass

    def cancel_order_in_database(self, order_id):
        pass

    def send_order_cancellation(self, order_id):
        pass


def _hash_password(password):

    # Хеширование пароля для безопасного хранения в базе данных
    return hashlib.sha256(password.encode()).hexdigest()


class Users:
    def __init__(self, username, password):
        self.username = username
        self.password = _hash_password(password)

    def register(self):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        c.execute('''
                    SELECT * FROM users
                    WHERE username = ?
                ''', (self.username,))
        user = c.fetchone()
        if user:
            print("Ошибка: Пользователь с таким именем уже существует.")
            conn.close()
            return

        c.execute('''
                    INSERT INTO users (username, password)
                    VALUES (?, ?)
                ''', (self.username, self.password))
        conn.commit()
        conn.close()
        print("Регистрация прошла успешно.")

    def login(self):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        c.execute('''
                    SELECT * FROM users
                    WHERE username = ? AND password = ?
                ''', (self.username, self.password))
        user = c.fetchone()
        if user:
            print("Авторизация прошла успешно.")
        else:
            print("Ошибка: Неверные имя пользователя или пароль.")
        conn.close()

        # Пример использования

    library = Library()
    book = Book("Book 1", "Author 1", 2021, True)
    library.add_book(book)

    cart = Cart()
    cart.add_book(book)

    user = User("user1", "password1")
    order = Order(cart, user)
    order.place_order()

    order_id = 12345
    order.cancel_order(order_id)

    library.close()
