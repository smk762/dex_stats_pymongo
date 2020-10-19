import os
import time
import sqlite3

# Create table if not existing
def create_tbl():
    with sqlite3.connect(os.environ['HOME'] + "/rm_faucet/db/rm_faucet.db") as conn:
        cursor = conn.cursor() 
        cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='faucet';''')
        if len(cursor.fetchall()) == 0 : 
            print('Table does not exist.')
            cursor.execute('''
                    CREATE TABLE faucet (
                        id INTEGER PRIMARY KEY,
                        coin text,
                        address text,
                        last_refill int,
                        txid text,
                        status text)
                ''')
            conn.commit()

def insert_addr_db(values):
    with sqlite3.connect(os.environ['HOME'] + "/rm_faucet/db/rm_faucet.db") as conn:
        cursor = conn.cursor() 
        cursor.execute("INSERT INTO faucet(coin, address, last_refill, txid, status) VALUES(?,?,?,?,?)", values)
        conn.commit()

def update_addr_db(address, values):
    with sqlite3.connect(os.environ['HOME'] + "/rm_faucet/db/rm_faucet.db") as conn:
        cursor = conn.cursor() 
        sql = " \
            UPDATE faucet \
                SET last_refill = ? \
                    status = ? \
                WHERE address = "+address
        cursor.execute(sql, values)
        conn.commit()
    
def dump_db():
    with sqlite3.connect(os.environ['HOME'] + "/rm_faucet/db/rm_faucet.db") as conn:
        cursor = conn.cursor() 
        rows = cursor.execute("SELECT * FROM faucet LIMIT 1000;").fetchall()
        return rows
    
def select_addr_from_db(addr):
    with sqlite3.connect(os.environ['HOME'] + "/rm_faucet/db/rm_faucet.db") as conn:
        cursor = conn.cursor() 
        sql = "SELECT * FROM faucet WHERE address = ?"
        rows = cursor.execute(sql, (addr,)).fetchall()
        return rows

def is_in_queue(coin, addr):
    with sqlite3.connect(os.environ['HOME'] + "/rm_faucet/db/rm_faucet.db") as conn:
        cursor = conn.cursor() 
        sql = "SELECT * FROM faucet WHERE coin = ? AND address = ? AND status = 'pending'"
        rows = cursor.execute(sql, (coin, addr)).fetchall()
        if len(rows) > 0:
            return True
        return False

def is_dry(coin):
    with sqlite3.connect(os.environ['HOME'] + "/rm_faucet/db/rm_faucet.db") as conn:
        cursor = conn.cursor() 
        last_drip = str(int(time.time())-60*60*4)
        sql = "SELECT COUNT(*) FROM faucet WHERE coin = ? AND last_refill > "+last_drip
        count = cursor.execute(sql, (coin,)).fetchone()
        if count[0] > 100:
            return True
        return False

def is_recently_filled(coin, addr):
    with sqlite3.connect(os.environ['HOME'] + "/rm_faucet/db/rm_faucet.db") as conn:
        cursor = conn.cursor() 
        last_drip = str(int(time.time())-60*60*4)
        sql = "SELECT * FROM faucet WHERE  coin = ? AND address = ? AND last_refill > "+last_drip
        rows = cursor.execute(sql, (coin, addr)).fetchall()
        if len(rows) > 0:
            return True
        return False

def queue_drop(coin, addr):
    values = (coin, addr, int(time.time()), '', "pending")
    insert_addr_db(values)

create_tbl()