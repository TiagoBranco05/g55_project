import sys
import datetime
from gclass import Gclass


class Redemption(Gclass):

    obj  = dict()
    lst  = list()
    pos  = 0
    path = ''
    att  = ['redemption_id', 'redemption_date', 'passenger_id',
            'miles_used', 'promotion_id']

    def __init__(self, redemption_id, redemption_date, passenger_id,
                 miles_used, promotion_id):
        super().__init__()

        self.redemption_id = Redemption.get_id(redemption_id)
        self.id            = self.redemption_id
        self.passenger_id  = int(passenger_id)
        self.miles_used    = int(miles_used)
        self.promotion_id  = int(promotion_id)

        if isinstance(redemption_date, str):
            self.redemption_date = datetime.datetime.strptime(
                redemption_date, "%Y-%m-%d").date()
        else:
            self.redemption_date = redemption_date

        Redemption.obj[self.redemption_id] = self
        Redemption.lst.append(self.redemption_id)

    def get_promotion(self):
        from promotion import Promotion
        return Promotion.obj.get(self.promotion_id)

    def __str__(self):
        return (f"Redemption(id={self.redemption_id}, "
                f"date={self.redemption_date}, "
                f"passenger_id={self.passenger_id}, "
                f"miles_used={self.miles_used}, "
                f"promotion_id={self.promotion_id})")
