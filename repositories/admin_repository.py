from database import create_connection


class AdminRepository:

    def get_admin_by_email(self, email):

        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT
                admin_id,
                name,
                email,
                password_hash,
                role,
                status
            FROM admins
            WHERE email = %s
        """

        cursor.execute(query, (email,))

        admin = cursor.fetchone()

        cursor.close()
        connection.close()

        return admin

    def get_admin_by_id(self, admin_id):
        connection = create_connection()
        cursor = connection.cursor()

        query = """
            SELECT
                admin_id,
                name,
                email,
                password_hash,
                role,
                status
            FROM admins
            WHERE admin_id = %s
        """

        cursor.execute(query, (admin_id,))
        admin = cursor.fetchone()

        cursor.close()
        connection.close()

        return admin