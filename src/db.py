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

    def get_robots(self):
        c = self.db.cursor(dictionary=True)
        c.execute("SELECT * FROM robots")
        return c.fetchall()

    def get_batteries(self):
        c = self.db.cursor(dictionary=True)
        c.execute("SELECT * FROM batteries")
        return c.fetchall()

    def get_dives(self):
        c = self.db.cursor(dictionary=True)
        c.execute("SELECT * FROM dives")
        return c.fetchall()

    def get_dives_batteries(self):
        c = self.db.cursor()
        c.execute(
            "SELECT d.id, b.name FROM dives d "
            "INNER JOIN batteries_in_dives bd on dive_id = d.id "
            "INNER JOIN batteries b ON b.id = battery_id")
        r = c.fetchall()
        return [[q[1] for q in r if q[0] == rr] for rr in set(x[0] for x in r)]

    def insert_robot(self, robot_name):
        c = self.db.cursor(dictionary=True)
        c.execute("INSERT INTO robots (name) VALUES (%s)", (robot_name,))
        self.db.commit()

    def insert_battery(self, battery_name, battery_v):
        c = self.db.cursor(dictionary=True)
        c.execute("INSERT INTO batteries (name, voltage) VALUES (%s, %s)", (battery_name, battery_v))
        self.db.commit()

    def insert_dive(self, robot_id, time_started, time_finished, batteries):
        c = self.db.cursor(dictionary=True)
        c.execute("INSERT INTO dives (time_started, time_finished, duration, robot_id)"
                  "VALUES (%s, %s, %s, %s)",
                  (time_started, time_finished, (time_finished - time_started).total_seconds(),
                   robot_id))
        dive_id = c.lastrowid
        c.executemany("INSERT INTO batteries_in_dives (dive_id, battery_id) VALUES (%s, %s)",
                      [(dive_id, b) for b in batteries])
        self.db.commit()
