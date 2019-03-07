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
            # print("ids ", ids)
            for x in ids:
                c.execute("SELECT * FROM batteries where id = %s", (x,))
                fetchall = c.fetchall()
                # print(fetchall)
                r.append(fetchall[0])
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
        r = c.fetchall()
        for dive in r:
            dive['batteries'] = self.get_dives_batteries(dive_id=dive['dive_id'], names=True)
        return r

    def get_dives_batteries(self, dive_id=None, names=True):
        c = self.db.cursor(dictionary=True)
        if dive_id is None:
            c.execute(
                "SELECT dives.id as dive_id, batteries.id as battery_id, batteries.name as battery_name "
                "FROM (dives "
                "LEFT OUTER JOIN batteries_in_dives bd on dive_id = dives.id "
                "LEFT OUTER JOIN batteries ON batteries.id = battery_id) ")
            r = c.fetchall()
            if names:
                return [[q['battery_name'] for q in r if q['dive_id'] == rr] for rr in set(x['dive_id'] for x in r)]
            else:
                return [[q['battery_id'] for q in r if q['dive_id'] == rr] for rr in set(x['dive_id'] for x in r)]
        else:
            c.execute(
                "SELECT dives.id as dive_id, batteries.id as battery_id, batteries.name as battery_name "
                "FROM (dives "
                "LEFT OUTER JOIN batteries_in_dives bd on dive_id = dives.id "
                "LEFT OUTER JOIN batteries ON batteries.id = battery_id) "
                "WHERE dive_id = %s", (dive_id,))
            if names:
                return [q['battery_name'] for q in c.fetchall()]
            else:
                return [q['battery_id'] for q in c.fetchall()]

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
        batteries = self.get_batteries(ids=data['batteries'])
        c.executemany("INSERT INTO batteries_in_dives (dive_id, battery_id, voltage_start) VALUES (%s, %s, %s)",
                      [(dive_id, b, batteries[i]['voltage']) for i, b in enumerate(data['batteries'])])
        self.db.commit()

    def stop_dive(self, dive_id, voltages):
        c = self.db.cursor(dictionary=True)
        dive = self.get_dives(ids=[dive_id])[0]
        now = datetime.datetime.now()
        duration = (now - dive['time_started']).total_seconds()
        c.execute("UPDATE dives SET time_finished = %s, duration = %s, running = false WHERE id = %s",
                  (now, duration, dive_id))
        c.executemany("UPDATE batteries_in_dives SET voltage_finish = %s WHERE battery_id = %s && dive_id = %s",
                      [(v, b, dive_id) for b, v in voltages])
        c.executemany("UPDATE batteries SET voltage = %s, total_time = total_time + %s WHERE id = %s",
                      [(v, duration, b) for b, v in voltages])
        c.execute("UPDATE robots SET total_time = total_time + %s WHERE id = %s",
                  (duration, dive['robot_id']))
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

    def start_charge(self, data):
        c = self.db.cursor(dictionary=True)
        c.execute("INSERT INTO charges (battery_id, voltage_start, time_start) VALUES "
                  "(%s, %s, %s)", (data['battery_id'], data['voltage_start'], data['time_start']))
        charge_id = c.lastrowid
        c.execute("UPDATE batteries SET charging = %s, charge_id = %s WHERE id = %s",
                  (True, charge_id, data['battery_id']))
        self.db.commit()
        pass

    def stop_charge(self, data):
        c = self.db.cursor(dictionary=True)
        now = datetime.datetime.now()
        battery = self.get_batteries(ids=[data['battery_id']])[0]
        c.execute("SELECT * FROM charges WHERE id = %s", (battery['charge_id'],))
        charge = c.fetchall()[0]
        duration = (now - charge['time_start']).total_seconds()
        c.execute(
            "UPDATE batteries SET charging = FALSE, charge_id = NULL, total_time_charging = %s, voltage = %s"
            " WHERE id = %s",
            (battery['total_time_charging'] + duration, data['voltage'], data['battery_id']))
        c.execute("UPDATE charges SET time_finish = %s, voltage_finish = %s WHERE id = %s",
                  (now, data['voltage'], battery['charge_id']))
        self.db.commit()
