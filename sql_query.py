import psycopg2

class QueryTool:
    def __init__(self):
        self._conn = None
        self._cursor = None

    def open_connection(self):
        try:
            self._conn = psycopg2.connect(dbname='hotel', user='postgres', password='123234', host='localhost')
            self._cursor = self._conn.cursor()
        except Exception:
            return False
        else:
            return True

    def reg_per(self, flname, pas, phone, mail):
        try:
            self._cursor.execute('SET search_path TO hotel')
            self._cursor.execute('CALL insert_info(\'%s\', \'%s\', \'%s\', \'%s\')' % (flname, pas, phone, mail))
        except Exception:
            return False
        else:
            return True

    def bk_active(self):
        try:
            self._cursor.execute('SET search_path TO hotel')
            self._cursor.execute('SELECT * FROM active_bookings')
        except Exception:
            return None
        else:
            return self._cursor.fetchall()

    def bk_change(self, type_of_client, name, date):
        try:
            self._cursor.execute('SET search_path TO hotel')
            self._cursor.execute('CALL change(\'%s\', \'%s\', date \'%s\')' % (type_of_client, name, date))
        except Exception:
            return False
        else:
            return True

    def ch_today(self):
        try:
            self._cursor.execute('SET search_path TO hotel')
            self._cursor.execute('SELECT * FROM today_check_in')
        except Exception:
            return None
        else:
            return self._cursor.fetchall()

    def ch_free(self):
        try:
            self._cursor.execute('SET search_path TO hotel')
            self._cursor.execute('SELECT * FROM free_rooms')
        except Exception:
            return None
        else:
            return self._cursor.fetchall()

    def ch_serv(self):
        try:
            self._cursor.execute('SET search_path TO hotel')
            self._cursor.execute('SELECT * FROM list_of_services')
        except Exception:
            return None
        else:
            return self._cursor.fetchall()

    def ord_zak(self, ch_id):
        try:
            self._cursor.execute('SET search_path TO hotel')
            self._cursor.execute('SELECT * FROM zakazy(\'%s\')' % (ch_id))
        except Exception:
            return None
        else:
            return self._cursor.fetchall()

    def ord_duty(self, ch_id):
        try:
            self._cursor.execute('SET search_path TO hotel')
            self._cursor.execute('CALL dolg(\'%s\', NULL, NULL)' % (ch_id))
        except Exception:
            return None
        else:
            return self._cursor.fetchall()

    def ord_add(self, flname, serv, stat, quantity):
        try:
            self._cursor.execute('SET search_path TO hotel')
            self._cursor.execute('CALL ord(\'%s\', \'%s\', \'%s\')' % (flname, serv, stat, quantity))
        except Exception:
            return False
        else:
            return True

    def ord_del(self, flname, serv):
        try:
            self._cursor.execute('SET search_path TO hotel')
            self._cursor.execute('CALL dele(\'%s\', \'%s\')' % (flname, serv))
        except Exception:
            return False
        else:
            return True

    def close_connection(self):
        self._cursor.close()
        self._conn.close()