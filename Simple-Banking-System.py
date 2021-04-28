import sqlite3  # database for SQLite
from sqlite3 import Error  # libraries
from random import randrange

class Bank:
        issuer_identification_number = str(400000)  # IIN
        id = 'null'

        def __init__(self):
                """
                Initiates generation of connection to the SQL database - path and file name.
                """
                #self.connection = Bank.create_connection("bank_accounts.db")  # ordinary base
                self.connection = Bank.create_connection("card.s3db")
                Bank.database(self)
                self.decision = 0

        def create_connection(path):  # connection with libraries
                """
                Generates and checks connection with the database - if there is an error, it prints it.
                """
                connection = None
                try:
                        connection = sqlite3.connect(path)
                        print("Connection to SQLite DB successful")
                except Error as e:
                        print(f"The error '{e}' occurred")

                return connection

        def execute_query(connection, query):  # cursor position
                """
                Executes SQL queries.
                """
                cursor = connection.cursor()
                try:
                        cursor.execute(query)
                        connection.commit()
                        print("Query executed successfully")
                except Error as e:
                        print(f"The error '{e}' occurred")

        @staticmethod
        def database(self):
                """
                Creates a database of bank accounts with a PIN number and account balance.
                """
                #delete_table = ("DROP TABLE IF EXISTS card;")
                #Bank.execute_query(self.connection, delete_table)

                create_users_table = (""" 
                CREATE TABLE IF NOT EXISTS card (
                    id INTEGER PRIMARY KEY ASC,
                    number TEXT,
                    pin TEXT,
                    balance INTEGER DEFAULT 0
                )""")

                Bank.execute_query(self.connection, create_users_table)  # saves changes

        def main_options(self):  # Main menu
                """
                Main menu of the program: creates accounts and allows to log in to them.
                """
                self.choose = input('1. Create an account\n'
                                    '2. Log into account\n'
                                    '3. Help\n'
                                    '0. Exit\n')
                if self.choose == '1':
                        print('\nYour card has been created')
                        self.decision = 0
                        Bank.card_code(self)
                        Bank.__str__(self)
                        Bank.main_options(self)
                elif self.choose == '2':
                        Bank.log_in(self)
                elif self.choose == '3':
                        help(Bank)
                        Bank.main_options(self)
                elif self.choose == '0':
                        Bank.exit()
                else:
                        print('\nWrong command number. Choose a different number.\n')
                        Bank.main_options(self)

        def __str__(self):  # Displaying messages
                """
                Prints the created account number and PIN.
                """
                if self.choose == '1':
                        print(f'Your card number:\n''{}\nYour card pin:\n{}\n'.format(self.card_number,
                                                                                      self.pin_number))

        def log_in(self):  # Account login menu
                """
                Logging in to the created account - enter the PIN number.
                """
                self.account_number = input('\nEnter your card number:\n')
                pin_number = input('Enter your PIN:\n')
                account = [x[0] for x in self.connection.execute("SELECT number FROM card")]
                if self.account_number in account:
                        for data_pin in self.connection.execute("SELECT pin FROM card WHERE number={0}".format(self.account_number)):
                                account_pin = list(data_pin)
                        if account_pin[0] == pin_number:
                                print('\nYou have successfully logged in!\n')
                                Bank.account_balance_menu(self)
                        else:
                                print('\nWrong PIN number!\n')
                                Bank.main_options(self)
                else:
                        print('\nWrong card number!\n')
                        Bank.main_options(self)

        def exit():
                """
                Exit the program.
                """
                print('\nBye!')
                exit()

        def account_balance_menu(self):
                """
                Internal menu after logging into the account - allows to: make payments, transfer money and close the account.
                """
                self.choose = input('1. Balance\n'
                                    '2. Add income\n'
                                    '3. Do transfer\n'
                                    '4. Close account\n'
                                    '5. Log out\n'
                                    '6. Help\n'
                                    '0. Exit\n')
                if self.choose == '1':
                        for balance_amount in self.connection.execute("SELECT balance FROM card WHERE number={0}".format(self.account_number)):
                                print(f'\nBalance: {balance_amount[0]}\n')
                        Bank.account_balance_menu(self)
                elif self.choose == '2':
                        Bank.add_income(self)
                        Bank.account_balance_menu(self)
                elif self.choose == '3':
                        self.decision = 1
                        Bank.transfer(self)
                elif self.choose == '4':
                        Bank.delete(self)
                        Bank.main_options(self)
                elif self.choose == '5':
                        print('\nYou have successfully logged out!\n')
                        Bank.main_options(self)
                elif self.choose == '6':
                        help(Bank)
                        Bank.account_balance_menu(self)
                elif self.choose == '0':
                        Bank.exit()
                else:
                        print('\nWrong command number. Choose a different number.\n')
                        Bank.account_balance_menu(self)

        def verification(self):  # if such an account number exists, create it again
                """
                Checks if the randomly generated account number is already in the database.
                """
                verification = [x[0] for x in self.connection.execute("SELECT number FROM card")]
                for number in verification:
                        if int(number) == self.card_number:
                                Bank.card_code(self)

        def card_code(self):  # Create a 9-digit account number and assign a PIN to it
                """
                Generates a 16-digit account number and enters the data (account number, PIN, default balance) to the database - if correct.
                """
                self.customer_account_number = (str(randrange(999999999))).zfill(9)
                self.digits_for_luhn = Bank.issuer_identification_number + self.customer_account_number
                self.card_number = Bank.checksum(self)
                Bank.pin_code(self)
                Bank.verification(self)
                self.balance = 0
                self.connection.execute("INSERT INTO card (number, pin, balance) VALUES ({0}, {1}, {2})".format(self.card_number, str(self.pin_number), self.balance))
                self.connection.commit()
                self.connection.execute("""UPDATE card SET pin=(CASE when length(pin) < 4 then '0' || pin else pin end)""")  # inserts a 0 on the left side when a PIN is less than 4 numbers
                self.connection.commit()
                return self.card_number, self.pin_number

        def checksum(self):
                """
                Invoked by def card_code - enters the 16th number of the account number. Invokes the Luhn argorithm.
                """
                sum_list = Bank.luhn_algorithm(self)
                digit_sum = 0
                for digit in sum_list:
                        digit_sum += int(digit)
                if digit_sum % 10 == 0:
                        control_number = 0
                else:
                        control_number = digit_sum % 10
                if control_number == 0:
                        if self.decision == 0:
                                card_number = Bank.issuer_identification_number + self.customer_account_number + '0'
                        elif self.decision == 1:
                                card_number = self.transfer_account[:-1] + '0'
                else:
                        Luhn_number = 10 - control_number
                        if self.decision == 0:
                                card_number = Bank.issuer_identification_number + self.customer_account_number + str(Luhn_number)
                        elif self.decision == 1:
                                card_number = self.transfer_account[:-1] + str(Luhn_number)
                return card_number

        def luhn_algorithm(self):
                """
                Invoked by def checksum - prepares a sequence of 15 numbers for checksum, to account number was correct.
                """
                digit_list = []
                for digit in self.digits_for_luhn:
                        digit_list += digit
                for i in range(0, 15):  # Multiply odd digits by 2:
                        if (i % 2) == 0:
                                digit_list[int(i)] = str(int(digit_list[int(i)]) * 2)
                for i in range(0, 15):  # Subtract 9 to numbers over 9:
                        if int(digit_list[int(i)]) > 9:
                                digit_list[int(i)] = str(int(digit_list[int(i)]) - 9)
                return digit_list

        def pin_code(self):  # Create a 4 digit PIN
                """
                Generates a random 4-digit PIN for each new account.
                """
                self.pin_number = (str(randrange(9999))).zfill(4)
                return self.pin_number

        def add_income(self):
                """
                After logging in to the account and selecting "Add income", updates the account balance of the entered amount.
                """
                payment = input('\nEnter income:\n')
                self.connection.execute("UPDATE card SET balance=balance + {0} WHERE number={1}".format(int(payment), self.account_number))
                self.connection.commit()
                print('Income was added!\n')

        def transfer(self):
                """
                Transfer money from the "balance" of one account to another account indicated, if the conditions are met.

                Conditions:
                - account must contain the amount indicated in the transaction
                - transfer must take place between 2 different accounts
                - account number for the transfer must pass the Luhn algorithm
                - account number for the transfer must exist in the database
                """
                print("\nTransfer")
                self.transfer_account = input('Enter card number:\n')
                second_account = [x[0] for x in self.connection.execute("SELECT number FROM card")]
                self.digits_for_luhn = self.transfer_account[:-1]
                result = (Bank.checksum(self))
                if self.account_number == self.transfer_account:  # 2 condition
                        print("You can't transfer money to the same account!\n")
                        Bank.account_balance_menu(self)
                elif result != self.transfer_account:  # 3 condition
                        print('Probably you made a mistake in the card number. Please try again!\n')
                        Bank.account_balance_menu(self)
                elif self.transfer_account not in second_account:  # 4 condition
                        print('Such a card does not exist.\n')
                        Bank.account_balance_menu(self)
                else:
                        self.transfer_money = input('Enter how much money you want to transfer:\n')
                        money = [x[0] for x in self.connection.execute("SELECT balance FROM card WHERE number={0}".format(self.account_number))]
                        self.connection.commit()
                        if money[0] >= int(self.transfer_money):  # 1 condition
                                self.connection.execute("UPDATE card SET balance=balance + {0} WHERE number={1}".format(int(self.transfer_money), self.transfer_account))
                                self.connection.execute("UPDATE card SET balance=balance - {0} WHERE number={1}".format(int(self.transfer_money), self.account_number))
                                self.connection.commit()
                                print('Success!\n')
                                Bank.account_balance_menu(self)
                        else:
                                print('Not enough money!\n')
                                Bank.account_balance_menu(self)

        def delete(self):
                """
                After logging in to the account and selecting "Close account", deletes the account number with the remaining data.
                """
                self.connection.execute("DELETE FROM card WHERE number={0}".format(self.account_number))
                self.connection.commit()
                print('\nThe account has been closed!\n')

bank = Bank()
bank.main_options()