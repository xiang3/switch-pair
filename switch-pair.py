import sqlite3
from itertools import groupby

import time

SWITCH_FREQUEENS = 3


class Bro:
    def __init__(self, id, name, is_host, card_id):
        self.id = id
        self.name = name
        self.card_id = card_id
        self.is_host = is_host


class SwitchPair:
    def __init__(self, bros, is_switch_solo_card):
        self.bros = bros
        self.is_switch_solo_card = is_switch_solo_card

    def __get_solo_card_id(self):
        solo_card_ids = []
        card_id_map = groupby(sorted(self.bros, key=lambda bro: bro.card_id), lambda bro: bro.card_id)
        for card_id, bro in card_id_map:
            if len(list(bro)) != 2:
                solo_card_ids.append(card_id)
        return solo_card_ids

    def __get_join_switch_pair_bro_exclude_by_solo_card_ids(self, do_not_join_switch_card):
        join_switch_pair_bro = []
        for bro in self.bros:
            if bro.card_id in do_not_join_switch_card:
                continue
            join_switch_pair_bro.append(bro)
        return join_switch_pair_bro

    def __exchange_host_and_pair(self, do_not_join_switch_card):
        for bro in self.__get_join_switch_pair_bro_exclude_by_solo_card_ids(do_not_join_switch_card):
            bro.is_host = not bro.is_host

    def __get_pairs(self):
        return [bro for bro in filter(lambda bro: bro.is_host is False, self.bros)]

    def __switch_pair(self, switch_time):
        pairs = self.__get_pairs()
        is_move_left = switch_time % 2 == 0
        sorts = [bro.card_id for bro in pairs]
        if is_move_left:
            sorts.insert(0, sorts.pop())
        else:
            sorts.append(sorts.pop(0))
        for bro, sort in zip(pairs, sorts):
            bro.card_id = sort

    def __make_solo_bro_to_card_host(self, solo_card_ids):
        pairs = self.__get_pairs()
        for bro in pairs:
            if bro.card_id in solo_card_ids:
                bro.is_host = True

    def switch(self, switch_time, do_not_join_switch_card):
        solo_cards = self.__get_solo_card_id()
        self.__exchange_host_and_pair(do_not_join_switch_card + solo_cards)
        self.__switch_pair(switch_time)
        self.__make_solo_bro_to_card_host(solo_cards)

    def print_pair(self):
        hosts = sorted(filter(lambda bro: bro.is_host is True, self.bros), key=lambda bro: bro.card_id,
                   reverse=False)
        pairs = sorted(filter(lambda bro: bro.is_host is False, self.bros), key=lambda bro: bro.card_id,
                   reverse=False)
        for host in hosts:
            print(host.name, host.is_host, host.card_id, end='   ')
            is_solo = True
            for pair in pairs:
                if pair.card_id == host.card_id:
                    print(pair.name, pair.is_host, pair.card_id)
                    is_solo = False
            if is_solo:
                print()
        print()
        print()


def read_bros_from_db():
    db = sqlite3.connect("switch-pair.db")
    res = db.execute("select id, name, is_host, card_id from bros")
    return [Bro(id, name, is_host == 1, card_id) for id, name, is_host, card_id in res.fetchall()]


if __name__ == '__main__':
    bros = read_bros_from_db()
    switch_pair = SwitchPair(bros, True)
    # switch_pair.print_pair()
    # for i in range(5):
    #     switch_pair.switch(i, [])
    #     switch_pair.print_pair()
    switch_pair.switch(int((time.time() / 86400) / 3) % 2)
    switch_pair.print_pair()
    # notify_to_every_one(next_time_pair)
