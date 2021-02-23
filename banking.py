import random
import sqlite3


class BankAccount:
    def __init__(self):
        self.conn = sqlite3.connect('card.s3db')
        self.conn.row_factory = lambda cursor, row: row[0]
        self.cur = self.conn.cursor()
        self.card_number = None
        self.card_pin = None
        self.entered_card_number = None
        self.entered_card_pin = None
        self.answer = None
        self.balance = 0
        self._checksum = 0

    @staticmethod
    def print_main_banner():
        print("1. Create an account\n2. Log into account\n0. Exit")

    @staticmethod
    def print_second_banner():
        print("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit")

    def get_balance(self):
        new_balance = self.cur.execute("select balance from card where number = ?",
                                       (self.entered_card_number,)).fetchone()
        self.balance = new_balance

    def create_table(self):
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY AUTOINCREMENT, number TEXT, pin TEXT, 
            balance INTEGER DEFAULT 0);"""
        )
        self.conn.commit()

    def save_card(self):
        self.cur.execute("INSERT INTO card (number, pin) VALUES (?, ?);", (self.card_number, self.card_pin))
        self.conn.commit()

    def close_db(self):
        self.conn.close()

    def create_card_number(self):
        self.card_number = "400000" + str(random.randint(1, 999999999)).zfill(9)
        self._checksum = 0
        for element, number in enumerate(self.card_number, 1):
            number = int(number)
            if element % 2 != 0:
                number *= 2
                if number > 9:
                    number -= 9
                    self._checksum += number
                else:
                    self._checksum += number
            else:
                self._checksum += number
        self._checksum = str([0 if self._checksum % 10 == 0 else 10 - self._checksum % 10][0])
        self.card_number += self._checksum

    @staticmethod
    def check_card_no(cardno):
        checksum = int(str(cardno)[-1])
        cardno = [int(char) for char in str(cardno)[:-1]]
        cardno = [k*2 if i%2==0 else k for i,k in enumerate(cardno,0)]
        cardno = [number-9 if number>9 else number for number in cardno]
        if (sum(cardno)+checksum) % 10 == 0:
            return True
        return False

    def create_card_pin(self):
        self.card_pin = str(random.randint(0, 9999)).zfill(4)

    def add_income(self, amount):
        self.get_balance()
        self.balance += amount
        self.cur.execute("update card set balance = ? where number =?", (self.balance, self.entered_card_number))
        self.conn.commit()

    def enter_card_details(self):
        print("Enter your card number:")
        self.entered_card_number = str(input())
        print("Enter your PIN:")
        self.entered_card_pin = str(input())

    def delete_account(self):
        self.cur.execute("delete from card where number = ?", (self.entered_card_number,))
        self.conn.commit()

    def transfer_balance(self):
        self.get_balance()
        print("Transfer")
        target_account = input("Enter card number:")
        existing_account = self.cur.execute("select number from card").fetchall()
        if self.check_card_no(target_account):
            if target_account in existing_account:
                money_to_be_transferred = int(input("Enter how much money you want to transfer:"))
                if self.balance > money_to_be_transferred:
                    # Deducting Host Balance
                    self.balance -= money_to_be_transferred
                    self.cur.execute("update card set balance = ? where number =?",
                                     (self.balance, self.entered_card_number))
                    self.conn.commit()
                    # Adding recipient Balance
                    target_account_balance = self.cur.execute("select balance from card where number = ?",
                                                              (target_account,)).fetchone()
                    target_account_balance += money_to_be_transferred
                    self.cur.execute("update card set balance = ? where number =?",
                                     (target_account_balance, target_account))
                    self.conn.commit()
                    print("Success!")
                    self.account_menu()
                else:
                    print("Not enough money!")
                    self.account_menu()
            else:
                print("Such a card does not exist.")
                self.account_menu()
        else:
            print("Probably you made a mistake in the card number. Please try again!")

    def credential_check(self, card_no, pin_no):
        self.cur.execute("select number from card")
        available_cards = self.cur.fetchall()
        self.cur.execute("select pin from card where number = {}".format(card_no))
        pin_verify = self.cur.fetchone()
        if card_no in available_cards and pin_no == pin_verify:
            return True

    def main_menu(self):
        self.create_table()
        self.print_main_banner()
        self.answer = int(input())

        if self.answer == 1:
            self.create_card_number()
            self.create_card_pin()
            print("Your card has been created")
            print(f"Your card number:\n{self.card_number}")
            print(f"Your card PIN:\n{self.card_pin}")
            self.save_card()
            self.main_menu()
        elif self.answer == 2:
            self.enter_card_details()
            if self.credential_check(self.entered_card_number, self.entered_card_pin):
                print("You have successfully logged in!")
                self.account_menu()
            else:
                print("Wrong card number or PIN!")
                self.main_menu()
        elif self.answer == 0:
            print("Bye!")
            self.close_db()
        else:
            self.main_menu()

    def account_menu(self):
        self.print_second_banner()
        self.answer = int(input())
        if self.answer == 1:
            self.get_balance()
            print(f"Balance: {self.balance}")
            self.account_menu()
        elif self.answer == 2:
            income = int(input("Enter income:"))
            self.add_income(income)
            print("Income was added!")
            self.account_menu()
        elif self.answer == 3:
            self.transfer_balance()
            self.account_menu()
        elif self.answer == 4:
            self.delete_account()
            print("The account has been closed!")
            self.main_menu()
        elif self.answer == 5:
            print("You have successfully logged out!")
            self.main_menu()
        elif self.answer == 0:
            print("Bye!")
            exit()
            self.close_db()
        else:
            self.account_menu()


bank_account = BankAccount()
bank_account.main_menu()
