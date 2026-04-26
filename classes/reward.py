import re
import sys
import datetime
from gclass import Gclass


class Reward(Gclass):

    obj  = dict()
    lst  = list()
    pos  = 0
    path = ''
    att  = ['reward_id', 'name', 'expiry_days']

    def __init__(self, reward_id, name, expiry_days):
        super().__init__()

        self.reward_id   = Reward.get_id(reward_id)
        self.id          = self.reward_id
        self.name        = str(name)
        self.expiry_days = int(expiry_days)

        Reward.obj[self.reward_id] = self
        Reward.lst.append(self.reward_id)

    @staticmethod
    def parse_expiry_days(comments: str) -> int:
        match = re.search(r'(\d+)\s+days', str(comments))
        if match:
            return int(match.group(1))
        raise ValueError(f"Não foi possível extrair expiry_days de: '{comments}'")

    @classmethod
    def from_csv_row(cls, row) -> 'Reward':
        expiry_days = cls.parse_expiry_days(row['reward_comments'])
        return cls(row['reward_id'], row['reward_name'], expiry_days)

    def get_promotions(self):
        from promotion import Promotion
        return [p for p in Promotion.obj.values()
                if p.reward_id == self.reward_id]

    def __str__(self):
        return (f"Reward(id={self.reward_id}, "
                f"name='{self.name}', "
                f"expiry_days={self.expiry_days})")
