from database import create_connection


class TransactionRepository:

    def create_transaction(
        self,
        from_account,
        to_account,
        transaction_type,
        amount,
        status,
        description
    ):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO transactions
            (
                from_account,
                to_account,
                transaction_type,
                amount,
                status,
                description
            )
            VALUES
            (%s, %s, %s, %s, %s, %s)
        """

        values = (
            from_account,
            to_account,
            transaction_type,
            amount,
            status,
            description
        )

        cursor.execute(query, values)

        connection.commit()

        transaction_id = cursor.lastrowid

        cursor.close()
        connection.close()

        return transaction_id


    def get_transactions_by_account(self, account_number):

            connection = create_connection()
            cursor = connection.cursor()

            query = """
                SELECT
                    transaction_id,
                    from_account,
                    to_account,
                    transaction_type,
                    amount,
                    status,
                    description,
                    transaction_date
                FROM transactions
                WHERE from_account = %s
                OR to_account = %s
                ORDER BY transaction_date DESC
            """

            cursor.execute(
                query,
                (account_number, account_number)
            )

            transactions = cursor.fetchall()

            cursor.close()
            connection.close()

            return transactions

    def create_transaction_with_connection(
        self,
        from_account,
        to_account,
        transaction_type,
        amount,
        status,
        description,
        connection
    ):
        cursor = connection.cursor()

        query = """
            INSERT INTO transactions
            (
                from_account,
                to_account,
                transaction_type,
                amount,
                status,
                description
            )
            VALUES
            (%s, %s, %s, %s, %s, %s)
        """

        values = (
            from_account,
            to_account,
            transaction_type,
            amount,
            status,
            description
        )

        cursor.execute(query, values)

        transaction_id = cursor.lastrowid

        cursor.close()

        return transaction_id

    def get_all_transactions(self):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT
                transaction_id,
                from_account,
                to_account,
                transaction_type,
                amount,
                status,
                description,
                transaction_date
            FROM transactions
            ORDER BY transaction_date DESC
        """

        cursor.execute(query)

        transactions = cursor.fetchall()

        cursor.close()
        connection.close()

        return transactions

    def search_transactions(
    self,
    account_number=None,
    transaction_type=None,
    status=None
):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT
                transaction_id,
                from_account,
                to_account,
                transaction_type,
                amount,
                status,
                description,
                transaction_date
            FROM transactions
            WHERE 1 = 1
        """

        values = []

        if account_number:
            query += """
                AND (
                    from_account = %s
                    OR to_account = %s
                )
            """
            values.extend([
                account_number,
                account_number
            ])

        if transaction_type:
            query += """
                AND transaction_type = %s
            """
            values.append(transaction_type)

        if status:
            query += """
                AND status = %s
            """
            values.append(status)

        query += """
            ORDER BY transaction_date DESC
        """

        cursor.execute(query, tuple(values))

        transactions = cursor.fetchall()

        cursor.close()
        connection.close()

        return transactions

    def get_transaction_summary(self):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT
                COUNT(*) AS total_transactions,
                COALESCE(SUM(amount), 0) AS total_amount,
                SUM(
                    CASE
                        WHEN status = 'SUCCESS'
                        THEN 1
                        ELSE 0
                    END
                ) AS successful_transactions,
                SUM(
                    CASE
                        WHEN status = 'FAILED'
                        THEN 1
                        ELSE 0
                    END
                ) AS failed_transactions
            FROM transactions
        """

        cursor.execute(query)

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return result


    def get_financial_summary(self):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT
                transaction_type,
                COUNT(*) AS transaction_count,
                COALESCE(SUM(amount), 0) AS total_amount
            FROM transactions
            WHERE status = 'SUCCESS'
            GROUP BY transaction_type
            ORDER BY transaction_type
        """

        cursor.execute(query)

        results = cursor.fetchall()

        cursor.close()
        connection.close()

        return results    