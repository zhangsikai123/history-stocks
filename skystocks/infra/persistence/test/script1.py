#!/usr/bin/env python
# -*- coding: utf-8 -*-
import database
import sys
from cache import caches
engine = database.engines['stocks']
rd = caches['stocks-redis']
def script_recover_field(start):
    batch_size = 10000
    STOCK_KEYS = "stocks_code:date"
    i = start
    batch = select_from_mysql(i, batch_size)
    count = 0
    while batch:
        keys = []
        for data in batch:
            key = data['code'] + ":" + str(data['date'])
            keys.append(key)
        rd.sadd(STOCK_KEYS, *keys)
        i += batch_size
        batch = select_from_mysql(i, batch_size)
        count += batch_size
        print("processed:{}".format(str(count)))
    print("DONE")

def select_from_mysql(start, batch_size):
    with engine.connect() as cli:
        ret = cli.execute("select code, date from stocks order by id limit {}, {}".format(str(start), str(batch_size)))
        return ret.fetchall()

def main():
    if len(sys.argv) > 1:
        start = int(sys.argv[1])
    else:
        start = 0
    script_recover_field(start)
if __name__ == "__main__":
    main()
