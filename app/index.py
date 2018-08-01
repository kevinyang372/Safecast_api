from flask import Flask, request
from flask_restful import Resource, Api
from flaskext.mysql import MySQL
import os
from user_credibility import get_credibility_users, get_all_users
from travel_calculation import request_file, local_mean, predict, test_point_in_one_travel

application = Flask(__name__)
api = Api(application)

mysql = MySQL()

# MySQL configurations
application.config['MYSQL_DATABASE_USER'] = os.environ['AWS_DATABASE_USERNAME']
application.config['MYSQL_DATABASE_PASSWORD'] = os.environ['AWS_DATABASE_PASSWORD']
application.config['MYSQL_DATABASE_DB'] = 'safecast'
application.config['MYSQL_DATABASE_HOST'] = 'safecast.cikwfffwrotj.us-east-2.rds.amazonaws.com'
application.config['MYSQL_DATABASE_PORT'] = 3306

mysql.init_app(application)

class User(Resource):
    def get(self):
        cur = mysql.connect().cursor()
        query = "SELECT user_id, result FROM user_credibility"
        cur.execute(query)
        ids = []
        results = []
        for i in cur.fetchall():
          ids.append(i[0])
          results.append(i[1])
        cur.close()
        return get_all_users(ids, results)

    def post(self):
      cur = mysql.connect().cursor()
      query = "SELECT user_id, result FROM user_credibility"
      cur.execute(query)
      ids = []
      results = []
      for i in cur.fetchall():
        ids.append(i[0])
        results.append(i[1])
      travel_data = request.get_json()
      cur.close()
      return get_credibility_users(travel_data["id"],ids,results)

class Trip(Resource):
    def get(self):
      get_request = request.get_json()

      user_id = 0
      drive_id = 0

      if "user" in get_request.keys():
        user_id = get_request["user"]

      if "drive" in get_request.keys():
        drive_id = get_request["drive"]

      cur = mysql.connect().cursor()
      if user_id == 0 and drive_id != 0:
        cur.execute("SELECT user_id, drive_id, approved, disproved FROM summary WHERE drive_id = %s", drive_id)
      elif user_id != 0 and drive_id == 0:
        cur.execute("SELECT user_id, drive_id, approved, disproved FROM summary WHERE user_id = %s", user_id)
      elif user_id != 0 and drive_id != 0:
        cur.execute("SELECT user_id, drive_id, approved, disproved FROM summary WHERE user_id = %s AND drive_id = %s", (user_id,drive_id))

      response = []
      for i in cur.fetchall():
        response.append({'user_id': str(i[0]), 'drive_id': str(i[1]), 'approved': str(i[2]), 'disproved': str(i[3])})
      return response

    def post(self):
      travel_data = request.get_json()
      prediction_result = predict(travel_data)

      user_id = prediction_result["user"]
      drive_id = prediction_result["drive"]
      lats = prediction_result["latitude"]
      lngs = prediction_result["longitude"]
      results = prediction_result["result"]
      ratios = prediction_result["ratio"]
      values = prediction_result["value"]

      c = mysql.connect()
      cur = c.cursor()
      for i in range(len(results)):
        if results[i] == 0:
          cur.execute("INSERT INTO verification_result (user_id, lat, lng, drive_id, value, ratio) VALUES (%s, %s, %s, %s, %s, %s)", (user_id, lats[i], lngs[i], drive_id, values[i], ratios[i]))

      approved_num = results.count(1)
      disproved_num = results.count(0)

      cur.execute("INSERT INTO summary (user_id, drive_id, approved, disproved) VALUES (%s, %s, %s, %s)", (user_id, drive_id, approved_num, disproved_num))

      c.commit()
      cur.close()
      c.close()


api.add_resource(User, '/')
api.add_resource(Trip, '/trip/')

if __name__ == '__main__':
    application.run(host='0.0.0.0')
