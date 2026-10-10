from database import create_connection


class IdempotencyRepository:

    def get_by_customer_and_key(
        self,
        customer_id,
        idempotency_key,
        connection
    ):
        cursor = connection.cursor()

        query = """
            SELECT
                id,
                request_hash,
                response_json,
                status
            FROM idempotency_keys
            WHERE customer_id = %s
              AND idempotency_key = %s
        """

        cursor.execute(
            query,
            (customer_id, idempotency_key)
        )

        result = cursor.fetchone()
        cursor.close()

        return result

    def create_key(
        self,
        customer_id,
        idempotency_key,
        request_hash,
        connection
    ):
        cursor = connection.cursor()

        query = """
            INSERT INTO idempotency_keys
            (
                customer_id,
                idempotency_key,
                request_hash,
                status
            )
            VALUES (%s, %s, %s, 'PROCESSING')
        """

        cursor.execute(
            query,
            (customer_id, idempotency_key, request_hash)
        )

        record_id = cursor.lastrowid
        cursor.close()

        return record_id

    def complete_key(
        self,
        customer_id,
        idempotency_key,
        response_json,
        connection
    ):
        cursor = connection.cursor()

        query = """
            UPDATE idempotency_keys
            SET response_json = %s,
                status = 'COMPLETED'
            WHERE customer_id = %s
              AND idempotency_key = %s
        """

        cursor.execute(
            query,
            (
                response_json,
                customer_id,
                idempotency_key
            )
        )

        cursor.close()