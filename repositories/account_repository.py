from database import create_connection


class AccountRepository:

    def get_account_by_number(self, account_number):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT *
            FROM accounts
            WHERE account_number = %s
        """

        cursor.execute(query, (account_number,))

        account = cursor.fetchone()

        cursor.close()
        connection.close()

        return account

    def get_accounts_by_customer(self, customer_id):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT *
            FROM accounts
            WHERE customer_id = %s
        """

        cursor.execute(query, (customer_id,))

        accounts = cursor.fetchall()

        cursor.close()
        connection.close()

        return accounts

    def create_account(
        self,
        account_number,
        customer_id,
        account_type,
        balance=0.00
    ):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO accounts
            (
                account_number,
                customer_id,
                account_type,
                balance
            )
            VALUES
            (%s, %s, %s, %s)
        """

        values = (
            account_number,
            customer_id,
            account_type,
            balance
        )

        cursor.execute(query, values)

        connection.commit()

        account_id = cursor.lastrowid

        cursor.close()
        connection.close()

        return account_id  


    def update_balance(
        self,
        account_number,
        new_balance,
        connection
    ):
        cursor = connection.cursor()

        query = """
            UPDATE accounts
            SET balance = %s
            WHERE account_number = %s
        """

        cursor.execute(
            query,
            (new_balance, account_number)
        )

        cursor.close()          



    def get_all_accounts(self):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT
                account_id,
                account_number,
                customer_id,
                account_type,
                balance,
                status,
                created_at
            FROM accounts
            ORDER BY account_id
        """

        cursor.execute(query)

        accounts = cursor.fetchall()

        cursor.close()
        connection.close()

        return accounts   


    def update_account_status(self, account_number, status):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            UPDATE accounts
            SET status = %s
            WHERE account_number = %s
        """

        cursor.execute(
            query,
            (status, account_number)
        )

        connection.commit()

        rows_updated = cursor.rowcount

        cursor.close()
        connection.close()

        return rows_updated 

    def count_accounts(self):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT COUNT(*)
            FROM accounts
        """

        cursor.execute(query)

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return result[0]


    def get_account_by_number_for_update(self, account_number, connection):
        cursor = connection.cursor()

        query = """
            SELECT
                account_id,
                account_number,
                customer_id,
                account_type,
                balance,
                status,
                created_at
            FROM accounts
            WHERE account_number = %s
            FOR UPDATE
        """

        cursor.execute(query, (account_number,))
        account = cursor.fetchone()
        cursor.close()

        return account