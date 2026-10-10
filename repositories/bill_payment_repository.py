from database import create_connection


class BillPaymentRepository:

    def create_bill_payment(
        self,
        customer_id,
        account_number,
        bill_type,
        bill_number,
        provider_name,
        amount,
        status="PENDING",
        transaction_id=None
    ):
        connection = create_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO bill_payments
            (
                customer_id,
                account_number,
                bill_type,
                bill_number,
                provider_name,
                amount,
                status,
                transaction_id
            )
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            customer_id,
            account_number,
            bill_type,
            bill_number,
            provider_name,
            amount,
            status,
            transaction_id
        )

        cursor.execute(query, values)
        connection.commit()

        bill_payment_id = cursor.lastrowid

        cursor.close()
        connection.close()

        return bill_payment_id

    def get_bill_payments_by_customer(self, customer_id):
        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT
                bill_payment_id,
                customer_id,
                account_number,
                bill_type,
                bill_number,
                provider_name,
                amount,
                status,
                transaction_id,
                payment_date
            FROM bill_payments
            WHERE customer_id = %s
            ORDER BY payment_date DESC
        """

        cursor.execute(query, (customer_id,))

        bill_payments = cursor.fetchall()

        cursor.close()
        connection.close()

        return bill_payments

    def get_bill_payment_by_id(self, bill_payment_id):
        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT
                bill_payment_id,
                customer_id,
                account_number,
                bill_type,
                bill_number,
                provider_name,
                amount,
                status,
                transaction_id,
                payment_date
            FROM bill_payments
            WHERE bill_payment_id = %s
        """

        cursor.execute(
            query,
            (bill_payment_id,)
        )

        bill_payment = cursor.fetchone()

        cursor.close()
        connection.close()

        return bill_payment


    def create_bill_payment_with_connection(
    self,
    customer_id,
    account_number,
    bill_type,
    bill_number,
    provider_name,
    amount,
    status,
    transaction_id,
    connection
):
        cursor = connection.cursor()

        query = """
            INSERT INTO bill_payments
            (
                customer_id,
                account_number,
                bill_type,
                bill_number,
                provider_name,
                amount,
                status,
                transaction_id
            )
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            customer_id,
            account_number,
            bill_type,
            bill_number,
            provider_name,
            amount,
            status,
            transaction_id
        )

        cursor.execute(
            query,
            values
        )

        bill_payment_id = cursor.lastrowid

        cursor.close()

        return bill_payment_id