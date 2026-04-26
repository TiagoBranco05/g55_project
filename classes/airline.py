import sys
import datetime
from gclass import Gclass

class Airline(Gclass):

    obj  = dict()
    lst  = list()
    pos  = 0
    path = ''
    att  = ['airline_id', 'name', 'created_date']

    def __init__(self, airline_id, name, created_date):
        super().__init__()

        self.airline_id = Airline.get_id(airline_id)
        self.id         = self.airline_id
        self.name       = str(name)

        if isinstance(created_date, str):
            self.created_date = datetime.datetime.strptime(
                created_date, "%Y-%m-%d").date()
        else:
            self.created_date = created_date

        self._promotion_ids = []

        Airline.obj[self.airline_id] = self
        Airline.lst.append(self.airline_id)

    def link_promotion(self, promotion_id):
        pid = int(promotion_id)
        if pid not in self._promotion_ids:
            self._promotion_ids.append(pid)

    def get_promotions(self):
        from promotion import Promotion
        return [Promotion.obj[pid] for pid in self._promotion_ids
                if pid in Promotion.obj]

    @classmethod
    def load_db(cls, path: str) -> dict:
        import sqlite3
        from promotion  import Promotion
        from reward     import Reward
        from redemption import Redemption

        Reward.read(path)

        Promotion.read(path)

        cls.read(path)

        con = sqlite3.connect(path)
        rows = con.execute("SELECT airline_id, promotion_id FROM AirlinePromotion").fetchall()
        con.close()
        for airline_id, promotion_id in rows:
            airline   = cls.obj.get(airline_id)
            promotion = Promotion.obj.get(promotion_id)
            if airline and promotion:
                airline.link_promotion(promotion_id)
                promotion.link_airline(airline_id)

        Redemption.read(path)

        return {
            'rewards':     len(Reward.obj),
            'promotions':  len(Promotion.obj),
            'airlines':    len(cls.obj),
            'redemptions': len(Redemption.obj),
        }

    def __str__(self):
        return (f"Airline(id={self.airline_id}, "
                f"name='{self.name}', "
                f"created_date={self.created_date})")
