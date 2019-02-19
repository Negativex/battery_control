import datetime

import mysql.connector


class RobotsDB:
    def __init__(self, host, username, password):
        self.host = host
        self.password = password
        self.username = username
        self.db = None

    def connect(self):
        print("Trying to connect to {} as {}".format(self.host, self.username))
        self.db = mysql.connector.connect(host=self.host,
                                          user=self.username,
                                          passwd=self.password,
                                          database='rav')
        if self.db is not None:
            print("Success")

    def get_robots(self, ids=None):
        c = self.db.cursor(dictionary=True)
        if ids is None:
            c.execute("SELECT * FROM robots")
            return c.fetchall()
        else:
            r = []
            for x in ids:
                c.execute("SELECT * FROM robots where id = %s", (x,))
                r.append(c.fetchall()[0])
            return r

    def get_batteries(self, ids=None):
        c = self.db.cursor(dictionary=True)
        if ids is None:
            c.execute("SELECT * FROM batteries")
            return c.fetchall()
        else:
            r = []
            print(ids)
            for x in ids:
                c.execute("SELECT * FROM batteries where id = %s", (x,))
                r.append(c.fetchall()[0])
            return r

    def get_dives(self, ids=None):
        c = self.db.cursor(dictionary=True)
        if ids is None:
            c.execute("SELECT * FROM dives")
            return c.fetchall()
        else:
            r = []
            for x in ids:
                c.execute("SELECT * FROM dives where id = %s", (x,))
                r.append(c.fetchall()[0])
            return r

    def get_dives_table(self):
        c = self.db.cursor(dictionary=True)
        c.execute(
            "SELECT dives.id AS dive_id, robots.name AS robot_name,"
            "time_started, time_finished, duration, running FROM dives "
            "LEFT OUTER JOIN robots ON robots.id = dives.robot_id")
        return c.fetchall()

    def get_dives_batteries(self, dive_id=None, names=True):
        c = self.db.cursor()
        c.execute(
            "SELECT d.id, b.id, b.name FROM dives d "
            "LEFT OUTER JOIN batteries_in_dives bd on dive_id = d.id "
            "LEFT OUTER JOIN batteries b ON b.id = battery_id")
        if dive_id is None:
            r = c.fetchall()
            if names:
                return [[q[2] for q in r if q[0] == rr] for rr in set(x[0] for x in r)]
            else:
                return [[q[1] for q in r if q[0] == rr] for rr in set(x[0] for x in r)]
        else:
            r = c.fetchall()
            if names:
                return [[q[2] for q in r if q[0] == dive_id]]
            else:
                return [[q[1] for q in r if q[0] == dive_id]]

    def insert_robot(self, data):
        c = self.db.cursor(dictionary=True)
        c.execute("INSERT INTO robots (name) VALUES (%s)",
                  (data['name'],))
        self.db.commit()

    def insert_battery(self, data):
        c = self.db.cursor(dictionary=True)
        c.execute("INSERT INTO batteries (name, voltage) VALUES (%s, %s)",
                  (data['name'], data['voltage']))
        self.db.commit()

    def insert_dive(self, data):
        c = self.db.cursor(dictionary=True)
        if data['time_finished'] is None:
            c.execute("INSERT INTO dives (time_started, time_finished, duration, robot_id, running)"
                      "VALUES (%s, null, null, %s, true)",
                      (data['time_started'],
                       data['robot_id']))
        else:
            c.execute("INSERT INTO dives (time_started, time_finished, duration, robot_id)"
                      "VALUES (%s, %s, %s, %s)",
                      (data['time_started'], data['time_finished'],
                       (data['time_finished'] - data['time_started']).total_seconds(),
                       data['robot_id']))
        dive_id = c.lastrowid
        c.executemany("INSERT INTO batteries_in_dives (dive_id, battery_id) VALUES (%s, %s)",
                      [(dive_id, b) for b in data['batteries']])
        self.db.commit()

    def stop_dive(self, data):
        c = self.db.cursor(dictionary=True)
        dive = self.get_dives(ids=[data['id']])[0]
        now = datetime.datetime.now()
        c.execute("UPDATE dives SET time_finished = %s, duration = %s, running = false WHERE id = %s",
                  (data['time_finished'], (data['time_finished'] - dive['time_started']).total_seconds(),
                   data['id']))
        self.db.commit()

    def update_robot(self, data):
        c = self.db.cursor(dictionary=True)
        c.execute("UPDATE robots SET name = %s, total_time = %s WHERE id = %s",
                  (data['name'], data['total_time'], data['id']))
        self.db.commit()

    def update_battery(self, data):
        c = self.db.cursor(dictionary=True)
        c.execute("UPDATE batteries SET name = %s, voltage = %s, total_time = %s WHERE id = %s",
                  (data['name'], data['voltage'], data['total_time'], data['id']))
        self.db.commit()

    def update_dive(self):
        pass

    def delete_robot(self, robot_id):
        c = self.db.cursor(dictionary=True)
        c.execute("DELETE FROM robots WHERE id = %s", (robot_id,))
        self.db.commit()

    def delete_dive(self, dive_id):
        c = self.db.cursor(dictionary=True)
        c.execute("DELETE FROM dives WHERE id = %s", (dive_id,))
        c.execute("DELETE FROM batteries_in_dives WHERE dive_id = %s", (dive_id,))
        self.db.commit()

    def delete_battery(self, battery_id):
        c = self.db.cursor(dictionary=True)
        c.execute("DELETE FROM batteries WHERE id = %s", (battery_id,))
        self.db.commit()
