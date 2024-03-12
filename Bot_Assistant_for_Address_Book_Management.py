import pickle
from collections import UserDict
import datetime

# Decorator for error handling


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as ve:
            return str(ve)
        except KeyError:
            return "Contact not found."
        except IndexError:
            if func.__name__ == 'add_contact':
                return "Please provide a name and phone number."
            elif func.__name__ == 'edit_contact':
                return "Please provide a name and new phone number."
            elif func.__name__ == 'show_phone':
                return "Please provide a name to search."
            else:
                return "Missing arguments."
    return inner

# Classes for managing the address book


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Invalid phone number format. Must be 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            self.birthday = datetime.datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid birthday format. Use DD.MM.YYYY.")
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                return
        raise ValueError("Phone number not found.")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = f", Birthday: {
            self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError("Record not found.")

    def get_birthdays_per_week(self):
        today = datetime.date.today()
        upcoming_birthdays = []
        for name, record in self.data.items():
            if hasattr(record, 'birthday') and record.birthday:
                birth_date = record.birthday.birthday.date()
                delta_days = (birth_date.replace(year=today.year) - today).days
                if 0 <= delta_days < 7:
                    upcoming_birthdays.append(name)
        return upcoming_birthdays

    def save_to_file(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)

    @staticmethod
    def load_from_file(filename):
        try:
            with open(filename, 'rb') as file:
                data = pickle.load(file)
                address_book = AddressBook()
                address_book.data.update(data)
                return address_book
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            return AddressBook()

    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())

# Functions for the virtual assistant


@input_error
def add_contact(book, user_input):
    name, phone = user_input.split()
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return "Contact added."


@input_error
def edit_contact(book, user_input):
    name, new_phone = user_input.split()
    record = book.find(name)
    if record is None:
        return "Contact not found."
    if record.phones:
        old_phone = record.phones[0].value
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    else:
        return "No phone number to change."


@input_error
def show_phone(book, username):
    record = book.find(username)
    if record is None:
        return "Contact not found."
    return str(record)


@input_error
def add_birthday(book, user_input):
    name, birthday = user_input.split()
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(book, username):
    record = book.find(username)
    if record is None:
        return "Contact not found."
    if hasattr(record, 'birthday') and record.birthday:
        return f"Birthday: {record.birthday.value}"
    else:
        return "Birthday not set."


def show_birthdays(book):
    birthdays = book.get_birthdays_per_week()
    if birthdays:
        return '\n'.join(birthdays)
    else:
        return "No birthdays next week."


def show_all_contacts(book):
    return str(book)


def parse_input(user_input):
    parts = user_input.split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    return cmd, args


def main():
    filename = 'address_book.data'
    book = AddressBook.load_from_file(filename)
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            book.save_to_file(filename)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(book, args))
        elif command == "change":
            print(edit_contact(book, args))
        elif command == "phone":
            if args:
                print(show_phone(book, args.strip()))
            else:
                print("Please provide a username.")
        elif command == "all":
            print(show_all_contacts(book))
        elif command == "add-birthday":
            print(add_birthday(book, args))
        elif command == "show-birthday":
            print(show_birthday(book, args.strip()))
        elif command == "birthdays":
            print(show_birthdays(book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
