import sqlite3

def add_detector(account_id, key):
    conn = sqlite3.connect('detectors.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO detectors (account_id, key) VALUES (?, ?)", (account_id, key))
    conn.commit()
    conn.close()

# Ajouter un détecteur
add_detector("1122000", "KeyFor1122")
