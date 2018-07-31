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
application.config['MYSQL_DATABASE_USER'] = os.environ['RAILS_DATABASE_USERNAME']
application.config['MYSQL_DATABASE_PASSWORD'] = os.environ['RAILS_DATABASE_PASSWORD']
application.config['MYSQL_DATABASE_DB'] = 'Safecast'
application.config['MYSQL_DATABASE_HOST'] = 'localhost'

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
      return get_credibility_users(travel_data["id"],ids,results)

class Trip(Resource):
    def get(self):
      return {"algorithm": "local mean"}

    def post(self):
      travel_data = request.get_json()
      return predict(travel_data)

api.add_resource(User, '/')
api.add_resource(Trip, '/trip/')

if __name__ == '__main__':
    application.run(host='0.0.0.0')
