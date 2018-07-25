from flask import Flask, request
from flask_restful import Resource, Api
from user_credibility import get_credibility_users, get_all_users
from travel_calculation import request_file, local_mean, predict, test_point_in_one_travel

app = Flask(__name__)
api = Api(app)

class User(Resource):
    def get(self):
        return get_all_users()

    def post(self):
      travel_data = request.get_json()
      return get_credibility_users(travel_data["id"])

class Trip(Resource):
    def get(self):
      return {"algorithm": "local mean"}

    def post(self):
      travel_data = request.get_json()
      return predict(travel_data)

api.add_resource(User, '/')
api.add_resource(Trip, '/trip/')

if __name__ == '__main__':
    app.run(debug=True)