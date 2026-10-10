from database import create_connection


class CustomerRepository:

    def get_customer_by_id(self, customer_id):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT *
            FROM customers
            WHERE customer_id = %s
        """

        cursor.execute(query, (customer_id,))

        customer = cursor.fetchone()

        cursor.close()
        connection.close()

        return customer

    def get_customer_by_email(self, email):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT *
            FROM customers
            WHERE email = %s
        """

        cursor.execute(query, (email,))

        customer = cursor.fetchone()

        cursor.close()
        connection.close()

        return customer

    def create_customer(
        self,
        name,
        email,
        phone,
        address,
        date_of_birth,
        password_hash
    ):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO customers
            (
                name,
                email,
                phone,
                address,
                date_of_birth,
                password_hash
            )
            VALUES
            (%s, %s, %s, %s, %s, %s)
        """

        values = (
            name,
            email,
            phone,
            address,
            date_of_birth,
            password_hash
        )

        cursor.execute(query, values)

        connection.commit()

        customer_id = cursor.lastrowid

        cursor.close()
        connection.close()

        return customer_id


    def email_exists(self, email):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT customer_id
            FROM customers
            WHERE email = %s
        """

        cursor.execute(query, (email,))

        customer = cursor.fetchone()

        cursor.close()
        connection.close()

        return customer is not None

    def phone_exists(self, phone):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT customer_id
            FROM customers
            WHERE phone = %s
        """

        cursor.execute(query, (phone,))

        customer = cursor.fetchone()

        cursor.close()
        connection.close()

        return customer is not None   


    def get_all_customers(self):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT
                customer_id,
                name,
                email,
                phone,
                address,
                date_of_birth,
                status,
                created_at
            FROM customers
            ORDER BY customer_id
        """

        cursor.execute(query)

        customers = cursor.fetchall()

        cursor.close()
        connection.close()

        return customers 

    def update_customer_status(self, customer_id, status):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            UPDATE customers
            SET status = %s
            WHERE customer_id = %s
        """

        cursor.execute(
            query,
            (status, customer_id)
        )

        connection.commit()

        rows_updated = cursor.rowcount

        cursor.close()
        connection.close()

        return rows_updated


    def count_customers(self):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT COUNT(*)
            FROM customers
        """

        cursor.execute(query)

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return result[0]


    def update_password_hash(self, customer_id, password_hash):
        connection = create_connection()
        cursor = connection.cursor()

        query = """
            UPDATE customers
            SET password_hash = %s,
                password_changed_at = CURRENT_TIMESTAMP
            WHERE customer_id = %s
        """

        cursor.execute(query, (password_hash, customer_id))
        connection.commit()

        rows_updated = cursor.rowcount

        cursor.close()
        connection.close()

        return rows_updated
    

    def update_customer_profile(
    self,
    customer_id,
    phone,
    address
):
        connection = create_connection()
        cursor = connection.cursor()

        query = """
            UPDATE customers
            SET phone = %s,
                address = %s 
            WHERE customer_id = %s
        """

        cursor.execute(
            query,
            (phone, address, customer_id)
        )

        connection.commit()
        rows_updated = cursor.rowcount

        cursor.close()
        connection.close()

        return rows_updated
    

    def phone_exists_for_another_customer(self, phone, customer_id):
        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT customer_id
            FROM customers
            WHERE phone = %s
            AND customer_id != %s
        """

        cursor.execute(query, (phone, customer_id))
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return result is not None

    def get_password_changed_at(self, customer_id):
        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT password_changed_at
            FROM customers
            WHERE customer_id = %s
        """

        cursor.execute(query, (customer_id,))
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return result[0] if result else None