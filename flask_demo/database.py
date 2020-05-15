import mysql.connector
from models import User
from models import Credential
from models import Request
import time
import sys

class Database:
    def __init__(self, config):
        self.__dbUser = config['mysql']['user']
        self.__dbPassword = config['mysql']['password']
        self.__dbHost = config['mysql']['host']
        self.__database = config['mysql']['database']
        self.__turn_off_timeout = int(config['host']['turn-off-timeout-seconds'])

    def _connect(self):
        return mysql.connector.connect(
            host=self.__dbHost,
            user=self.__dbUser,
            passwd=self.__dbPassword,
            database=self.__database
        )

    def create_database(self):
        returned = ""
        mydb = mysql.connector.connect(
            host=self.__dbHost,
            user=self.__dbUser,
            passwd=self.__dbPassword
        )

        mycursor = mydb.cursor()
        try:
            mycursor.execute("CREATE DATABASE " + self.__database)
            returned += "Database created.\n"
        except Exception as e:
            returned += str(e) + "\n"

        mydb = self._connect()
        mycursor = mydb.cursor()
        try:
            mycursor.execute(
                "CREATE TABLE `user` (`id` int(8) unsigned NOT NULL AUTO_INCREMENT,`username` varchar(30) NOT NULL,`turned_off` int(20) DEFAULT NULL,PRIMARY KEY (`id`),UNIQUE KEY `username` (`username`))")
            returned += "Table user created\n"
        except Exception as e:
            returned += str(e) + "\n"
        try:
            mycursor.execute(
                "CREATE TABLE `credential` (`id` int(11) NOT NULL,`ukey` varchar(2083) NOT NULL,`credential_id` varchar(2083) NOT NULL,`display_name` varchar(2083) NOT NULL,`pub_key` varchar(2083) DEFAULT NULL,`sign_count` int(11) DEFAULT NULL,`username` varchar(2083) NOT NULL,`rp_id` varchar(2083) NOT NULL,`icon_url` varchar(2083) NOT NULL,PRIMARY KEY (`id`),UNIQUE KEY `ukey` (`ukey`),UNIQUE KEY `credential_id` (`credential_id`),UNIQUE KEY `pub_key` (`pub_key`))")
            returned += "Table credential created\n"
        except Exception as e:
            returned += str(e) + "\n"
        try:
            mycursor.execute(
                "CREATE TABLE `request` (`id` int(11) NOT NULL AUTO_INCREMENT,`nonce` varchar(255) DEFAULT NULL,`time` varchar(255) DEFAULT NULL,`user_id` varchar(255) DEFAULT NULL,`success` int(11) DEFAULT NULL,PRIMARY KEY (`id`),UNIQUE KEY `nonce` (`nonce`))")
            returned += "Table request created\n"
        except Exception as e:
            returned += str(e) + "\n"
        return returned

    def user_exists(self, username):
        if not self.get_user(username):
            return False
        return True

    def credential_exists(self, credential_id):
        credential_id = str(credential_id, "utf-8")
        mydb = self._connect()
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM credential WHERE credential_id = '" + credential_id + "'")
        mycursor.fetchall()
        if mycursor.rowcount > 0:
            return True
        return False

    def delete_credential(self, cred_id):
        mydb = self._connect()
        mycursor = mydb.cursor()
        mycursor.execute("DELETE FROM credential WHERE credential_id = '" + cred_id + "'")
        mydb.commit()

    def get_credentials(self, username):
        mydb = self._connect()
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("SELECT * FROM credential WHERE username = '" + username + "'")
        rows = mycursor.fetchall()
        if mycursor.rowcount > 0:
            return self._parse_credentials(rows)
        return []

    def get_user(self, username):
        mydb = self._connect()
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("SELECT * FROM user WHERE username = '" + username + "'")
        rows = mycursor.fetchall()
        if mycursor.rowcount > 0:
            return self._parse_user(rows)
        return False

    def get_credential(self, credential_id):
        mydb = self._connect()
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("SELECT * FROM credential WHERE credential_id = '" + credential_id + "'")
        rows = mycursor.fetchall()
        if mycursor.rowcount > 0:
            return self._parse_credential(rows)
        return False

    def _parse_user(self, data):
        user = User()
        for row in data:
            user.databaseId = row["id"]
            user.id = row["username"]
            user.turned_off = row["turned_off"]
        return user

    def _parse_credential(self, data):
        credential = Credential()
        for row in data:
            credential.id = row["id"]
            credential.ukey = row["ukey"]
            credential.credential_id = row["credential_id"]
            credential.display_name = row["display_name"]
            credential.pub_key = row["pub_key"]
            credential.sign_count = row["sign_count"]
            credential.username = row["username"]
            credential.rp_id = row["rp_id"]
            credential.icon_url = row["icon_url"]
        return credential

    def _parse_credentials(self, data):
        credentials = []
        for row in data:
            credential = Credential()
            credential.id = row["id"]
            credential.ukey = row["ukey"]
            credential.credential_id = row["credential_id"]
            credential.display_name = row["display_name"]
            credential.pub_key = row["pub_key"]
            credential.sign_count = row["sign_count"]
            credential.username = row["username"]
            credential.rp_id = row["rp_id"]
            credential.icon_url = row["icon_url"]
            credentials.append(credential)
        return credentials

    def save_credential(self, credential):
        mydb = self._connect()
        mycursor = mydb.cursor()
        # raise Exception(type(user.id).__name__ + ";" +type(user.id).__name__ + ";" +type(user.ukey).__name__ + ";" +type(user.credential_id).__name__ + ";" +type(user.pub_key).__name__ + ";" +type(user.sign_count).__name__ + ";" +type(user.username).__name__ + ";" +type(user.rp_id).__name__ + ";" +type(user.icon_url).__name__)
        mycursor.execute(
            "INSERT INTO credential (id, ukey, credential_id, display_name, pub_key, sign_count, username, rp_id, icon_url) VALUES (" + str(
                credential.id) + ", '" + str(
                credential.ukey) + "', '" + credential.credential_id + "', '" + credential.display_name + "', '" + credential.pub_key + "', " + str(
                credential.sign_count) + ", '" + credential.username + "', '" + credential.rp_id + "', '" + credential.icon_url + "')")
        mydb.commit()

    def save_user(self, username):
        mydb = self._connect()
        mycursor = mydb.cursor()
        # raise Exception(type(user.id).__name__ + ";" +type(user.id).__name__ + ";" +type(user.ukey).__name__ + ";" +type(user.credential_id).__name__ + ";" +type(user.pub_key).__name__ + ";" +type(user.sign_count).__name__ + ";" +type(user.username).__name__ + ";" +type(user.rp_id).__name__ + ";" +type(user.icon_url).__name__)
        mycursor.execute("INSERT INTO user (username) VALUES ('" + username + "')")
        mydb.commit()

    def increment_sign_count(self, user):
        mydb = self._connect()
        mycursor = mydb.cursor()
        mycursor.execute("UPDATE credential SET sign_count = " + str(
            user.sign_count) + " WHERE credential_id = '" + user.credential_id + "'")
        mydb.commit()

    def save_request(self, request: Request):
        mydb = self._connect()
        mycursor = mydb.cursor()
        mycursor.execute("INSERT INTO request (user_id, nonce, time, success) VALUES ('" + str(
            request.userId) + "' , '" + request.nonce + "', '" + request.time + "', 0)")
        mydb.commit()

    def request_exists(self, request: Request):
        mydb = self._connect()
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM request WHERE nonce = '" + request.nonce + "'")
        mycursor.fetchall()
        if mycursor.rowcount > 0:
            return True
        return False

    def get_request(self, nonce):
        mydb = self._connect()
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("SELECT * FROM request WHERE nonce = '" + nonce + "' ORDER BY `id` DESC LIMIT 1")
        rows = mycursor.fetchall()
        if mycursor.rowcount > 0:
            return self._parse_request(rows)
        return False

    def make_success(self, request):
        mydb = self._connect()
        mycursor = mydb.cursor()
        mycursor.execute(
            "UPDATE request SET success = 1 WHERE success != 2 AND user_id = '" + request.userId + "' ORDER BY `id` DESC LIMIT 1")
        mydb.commit()

    def make_invalid(self, request):
        mydb = self._connect()
        mycursor = mydb.cursor()
        mycursor.execute(
            "UPDATE request SET success = 2 WHERE user_id = '" + request.userId + "' ORDER BY `id` DESC LIMIT 1")
        mydb.commit()

    def _parse_request(self, data):
        request = Request()
        for row in data:
            request.id = row["id"]
            request.nonce = row["nonce"]
            request.time = row["time"]
            request.userId = row["user_id"]
            request.success = row["success"]
        return request

    def turn_off(self, username):
        if self.user_exists(username):
            current_time = int(time.time())
            mydb = self._connect()
            mycursor = mydb.cursor()
            mycursor.execute(
                "UPDATE user SET turned_off = " + str(current_time) + " WHERE username = '" + username + "'")
            mydb.commit()
            return True
        return False

    def turn_on(self, username):
        if self.user_exists(username):
            mydb = self._connect()
            mycursor = mydb.cursor()
            mycursor.execute(
                "UPDATE user SET turned_off = 0 WHERE username = '" + username + "'")
            mydb.commit()
            return True
        return False

    def is_turned_off(self, username):
        user = self.get_user(username)
        if user.turned_off == None:
            return False
        if user.turned_off + self.__turn_off_timeout > int(time.time()):
            return True
        return False