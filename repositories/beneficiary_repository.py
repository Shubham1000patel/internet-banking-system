from database import create_connection


class BeneficiaryRepository:

    def create_beneficiary(
        self,
        customer_id,
        name,
        account_number,
        bank_name
    ):
        connection = create_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO beneficiaries
            (
                customer_id,
                name,
                account_number,
                bank_name
            )
            VALUES
            (%s, %s, %s, %s)
        """

        values = (
            customer_id,
            name,
            account_number,
            bank_name
        )

        cursor.execute(query, values)
        connection.commit()

        beneficiary_id = cursor.lastrowid

        cursor.close()
        connection.close()

        return beneficiary_id

    def get_beneficiaries_by_customer(self, customer_id):
        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT
                beneficiary_id,
                customer_id,
                name,
                account_number,
                bank_name,
                status,
                created_at
            FROM beneficiaries
            WHERE customer_id = %s
            ORDER BY created_at DESC
        """

        cursor.execute(query, (customer_id,))

        beneficiaries = cursor.fetchall()

        cursor.close()
        connection.close()

        return beneficiaries