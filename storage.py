import sqlite3
from collections import defaultdict
from contextlib import contextmanager

from model import Rate, Question


class Storage:
    def __init__(self, db_path):
        self.db_path = db_path

    @contextmanager
    def get_cursor(self):
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('PRAGMA foreign_keys = ON;')
            yield cursor
            conn.commit()
        except:
            conn.close()

    def init_db(self):
        with self.get_cursor() as cursor:
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS users
                (
                    userid text PRIMARY KEY
                );
                '''
            )
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS rates
                (
                    userid text,
                    mydate text,
                    kind text,
                    rate integer,
                    FOREIGN KEY (userid) REFERENCES users (userid) ON DELETE CASCADE,
                    PRIMARY KEY (userid, mydate, kind)
                );
                '''
            )

    def get_rates(self, user, date_beginning, date_end):
        with self.get_cursor() as cursor:
            cursor.execute(
                '''
                SELECT mydate, kind, rate FROM rates
                WHERE userid = ?
                AND mydate >= ?
                AND mydate <= ?
                ''',
                (user, date_beginning, date_end)
            )
            return [Rate(user, date, kind, value) for date, kind, value in cursor.fetchall()]

    def avg_rate(self, user, kind, date_beginning, date_end):
        with self.get_cursor() as cursor:
            cursor.execute(
                '''
                SELECT AVG(rate) FROM rates
                WHERE userid = ?
                AND kind = ?
                AND mydate >= ?
                AND mydate <= ?
                ''',
                (user, kind, date_beginning, date_end)
            )
            return cursor.fetchall()[0][0]

    def store_rate(self, rate: Rate):
        with self.get_cursor() as cursor:
            cursor.execute(
                'INSERT OR REPLACE INTO rates (userid, mydate, kind, rate) VALUES (?,?,?,?)',
                (rate.user, rate.date, rate.kind, rate.value)
            )

    def store_user(self, user):
        with self.get_cursor() as cursor:
            cursor.execute(
                'INSERT OR IGNORE INTO users (userid) VALUES (?)',
                (user,)
            )

    def remove_user(self, user):
        with self.get_cursor() as cursor:
            cursor.execute(
                'DELETE FROM users WHERE userid=?',
                (user,)
            )

    def get_users(self):
        with self.get_cursor() as cursor:
            cursor.execute('SELECT userid FROM users')
            return [row[0] for row in cursor.fetchall()]

    def get_stats(self, start_date, end_date, user_id):
        rates = self.get_rates(
            user_id, start_date, end_date
        )
        values_by_kind = defaultdict(list)
        for rate in rates:
            values_by_kind[rate.kind].append(rate)
        return values_by_kind


QUESTIONS = [
    Question("качество еды", "избыточная", "здоровая"),
    Question("сон", "недостаточный", "нормальный"),
    Question("употребление алкоголя", "выпил много", "не пил"),
    Question("физические нагрузки", "сидел весь день", "хорошо потренировался"),
]


def question_by_kind(kind):
    for q in QUESTIONS:
        if kind == q.kind:
            return q
    return Question('?', '?', '?')


def test_pls():
    s = Storage(':memory:')
    s.init_db()
    rate = Rate('u', 'ddd', 'my kind', 3)
    s.store_rate(rate)
    assert len(s.get_rates('u', 'a', 'b')) == 0
    r = s.get_rates('u', 'a', 'z')
    assert len(r) == 1
    assert r[0] == rate
