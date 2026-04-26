import re
import sys
import datetime
from gclass import Gclass

class Promotion(Gclass):

    obj  = dict()
    lst  = list()
    pos  = 0
    path = ''
    att  = ['promotion_id', 'name', 'min_miles', 'comments', 'reward_id']  # CORRIGIDO: sem underscores

    def __init__(self, promotion_id, name, min_miles, comments, reward_id):
        super().__init__()

        self.promotion_id = Promotion.get_id(promotion_id)
        self.id           = self.promotion_id
        self.name         = str(name)
        self.min_miles    = int(min_miles)
        self.comments     = str(comments)
        self.reward_id    = int(reward_id)
        self._airline_ids = []

        Promotion.obj[self.promotion_id] = self
        Promotion.lst.append(self.promotion_id)

    @staticmethod
    def parse_min_miles(comments: str) -> int:
        match = re.search(r'over\s+(\d+)\s+miles', str(comments))
        if match:
            return int(match.group(1))
        raise ValueError(f"Não foi possível extrair min_miles de: '{comments}'")

    @classmethod
    def from_csv_row(cls, row) -> 'Promotion':
        min_miles = cls.parse_min_miles(row['promotion_comments'])
        return cls(row['promotion_id'], row['promotion_name'],
                   min_miles, row['promotion_comments'], row['reward_id'])

    def link_airline(self, airline_id):
        aid = int(airline_id)
        if aid not in self._airline_ids:
            self._airline_ids.append(aid)

    def get_airlines(self):
        from airline import Airline
        return [Airline.obj[aid] for aid in self._airline_ids
                if aid in Airline.obj]

    def get_reward(self):
        from reward import Reward
        return Reward.obj.get(self.reward_id)

    def get_redemptions(self):
        from redemption import Redemption
        return [r for r in Redemption.obj.values()
                if r.promotion_id == self.promotion_id]

    def __str__(self):
        return (f"Promotion(id={self.promotion_id}, "
                f"name='{self.name}', "
                f"min_miles={self.min_miles}, "
                f"reward_id={self.reward_id})")
