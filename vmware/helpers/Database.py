from typing import List


class Database:
    @staticmethod
    def asDict(cursor) -> List[dict]:
        # Returns all rows from a cursor as a dict.
        r = []
        columns = []

        if cursor:
            for col in cursor.description:
                columns.append(col[0])

            for row in cursor.fetchall():
                r.append(dict(zip(columns, row)))

        return r



    @staticmethod
    def columnAsList(cursor) -> list:
        # Returns all rows from a cursor as a dict.
        r = []
        for row in cursor.fetchall():
            r.append(row[0])

        return r


    @staticmethod
    def columnAsSet(cursor) -> set:
        # Returns all rows from a cursor as a dict.
        r = set()
        for row in cursor.fetchall():
            r.add(row[0])

        return r
