import sqlite3
from dataclasses import dataclass


@dataclass
class Rate:
    user: str
    date: str
    kind: str
    value: int


class RateStorage:
    def __init__(self, db_path):
        self.db_path = db_path

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS rates
                (
                    userid text,
                    mydate text,
                    kind text,
                    rate integer
                )
                '''
            )
            conn.commit()

    def get_rates(self, user, date_beginning, date_end):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
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

    def store_rate(self, rate: Rate):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM rates WHERE userid=? AND mydate=? AND kind=?',
                (rate.user, rate.date, rate.kind)
            )
            cursor.execute(
                'INSERT INTO rates (userid, mydate, kind, rate) VALUES (?,?,?,?)',
                (rate.user, rate.date, rate.kind, rate.value)
            )
            conn.commit()


def test_pls():
    s = RateStorage(':memory:')
    s.init_db()
    rate = Rate('u', 'ddd', 'my kind', 3)
    s.store_rate(rate)
    assert len(s.get_rates('u', 'a', 'b')) == 0
    r = s.get_rates('u', 'a', 'z')
    assert len(r) == 1
    assert r[0] == rate
