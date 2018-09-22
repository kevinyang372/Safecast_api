from flask import Flask, request
from flask_restful import Resource, Api
from flaskext.mysql import MySQL
import os
import random
from user_credibility import get_credibility_users, get_all_users
from travel_calculation import request_file, local_mean, predict, test_point_in_one_travel
from blackjack import text_to_list, list_to_text, generate_deck, sum_blackjack

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

class Blackjack(Resource):
    def get(self):
        cur = mysql.connect().cursor()
        query = "SELECT name, points FROM leaderboard ORDER BY points DESC LIMIT 5 "
        cur.execute(query)
        names = []
        points = []
        for i in cur.fetchall():
          names.append(i[0])
          points.append(i[1])
        cur.close()

        response = []
        for i in range(len(names)):
            response.append({'name': str(names[i]), 'point': str(points[i])})
        return response

    def post(self):

      def reset_game(name):
        deck = generate_deck()
        this_player_hand = deck[:2].copy()
        this_dealer_hand = deck[2:4].copy()
        this_player_deck = deck[4:10].copy()
        this_dealer_deck = deck[10:16].copy()

        while sum_blackjack(this_dealer_hand) < 17:
          this_dealer_hand.append(this_dealer_deck.pop())

        ph_data = list_to_text(this_player_hand)
        dh_data = list_to_text(this_dealer_hand)
        pd_data = list_to_text(this_player_deck)
        dd_data = list_to_text(this_dealer_deck)

        return this_player_hand, this_dealer_hand, this_player_deck, this_dealer_deck, ph_data, dh_data, pd_data, dd_data

      get_request = request.get_json()
      c = mysql.connect()
      cur = c.cursor()
      query = "SELECT name, player_hand, dealer_hand, player_deck, dealer_deck FROM player_data"
      cur.execute(query)
      names = []
      player_hand = []
      dealer_hand = []
      player_deck = []
      dealer_deck = []
      for i in cur.fetchall():
        names.append(i[0])
        player_hand.append(text_to_list(i[1]))
        dealer_hand.append(text_to_list(i[2]))
        player_deck.append(text_to_list(i[3]))
        dealer_deck.append(text_to_list(i[4]))

      card_dict = {11:"J",12:"Q",13:"K"}

      if "name" in get_request.keys():
        name = get_request["name"]
        if name in names:
          index = names.index(name)
          this_player_hand = player_hand[index]
          this_dealer_hand = dealer_hand[index]
          this_player_deck = player_deck[index]
          this_dealer_deck = dealer_deck[index]
        else:
          this_player_hand, this_dealer_hand, this_player_deck, this_dealer_deck, ph_data, dh_data, pd_data, dd_data = reset_game(name)

          cur.execute("INSERT INTO player_data (player_hand, dealer_hand, player_deck, dealer_deck, name) VALUES (%s, %s, %s, %s, %s)", (ph_data, dh_data, pd_data, dd_data, name))
          cur.execute("INSERT INTO leaderboard (name, points) VALUES (%s, %s)", (name, 500))

          c.commit()
          cur.close()
          c.close()

          for i in range(len(this_player_hand)):
            if this_player_hand[i] > 10:
              this_player_hand[i] = card_dict[this_player_hand[i]]

          if this_dealer_hand[1] > 10:
            this_dealer_hand[1] = card_dict[this_dealer_hand[1]]

          return {'name': name, 'dealer_hand': str(this_dealer_hand[1]), 'player_hand': [str(this_player_hand[0]), str(this_player_hand[1])]}
      else:
        return {'Error':'please specify player\'s name'}

      if "action" in get_request.keys():
        action = get_request["action"]
        if action == "hit":

          draw = this_player_deck.pop()
          this_player_hand.append(draw)

          if sum_blackjack(this_player_hand) > 20:
            if sum_blackjack(this_player_hand) == 21:
              if sum_blackjack(this_dealer_hand) == 21:
                json_result = {'result': 'Stand-off!'}
              else:
                json_result = {'result': 'Blackjack!'}
                cur.execute("UPDATE leaderboard SET points = points + 150 WHERE name = %s",(name))
            elif sum_blackjack(this_player_hand) > 21:
              json_result = {'result': 'Busted!'}
              cur.execute("UPDATE leaderboard SET points = points - 100 WHERE name = %s",(name))

            this_player_hand, this_dealer_hand, this_player_deck, this_dealer_deck, ph_data, dh_data, pd_data, dd_data = reset_game(name)
            cur.execute("UPDATE player_data SET player_hand = %s, player_deck = %s, dealer_hand = %s, dealer_deck = %s WHERE name= %s", (ph_data, pd_data, dh_data, dd_data, name))
            c.commit()
            cur.close()
            c.close()

            return json_result
          
          ph_data = list_to_text(this_player_hand)
          pd_data = list_to_text(this_player_deck)
          cur.execute("UPDATE player_data SET player_hand = %s, player_deck = %s WHERE name= %s", (ph_data, pd_data, name))
          c.commit()
          cur.close()
          c.close()

          for i in range(len(this_player_hand)):
            if this_player_hand[i] > 10:
              this_player_hand[i] = card_dict[this_player_hand[i]]
            else:
              this_player_hand[i] = str(this_player_hand[i])

          for i in range(len(this_dealer_hand)):
            if this_dealer_hand[i] > 10:
              this_dealer_hand[i] = card_dict[this_dealer_hand[i]]
            else:
              this_dealer_hand[i] = str(this_dealer_hand[i])

          return {'name': name, 'dealer_hand': str(this_dealer_hand[1]), 'player_hand': this_player_hand}

        elif action == "stand":

          translated_player_hand = this_player_hand.copy()
          translated_dealer_hand = this_dealer_hand.copy()

          for i in range(len(this_player_hand)):
            if this_player_hand[i] > 10:
              translated_player_hand[i] = card_dict[this_player_hand[i]]
            else:
              translated_player_hand[i] = str(this_player_hand[i])

          for i in range(len(this_dealer_hand)):
            if this_dealer_hand[i] > 10:
              translated_dealer_hand[i] = card_dict[this_dealer_hand[i]]
            else:
              translated_dealer_hand[i] = str(this_dealer_hand[i])

          if sum_blackjack(this_dealer_hand) > 21:
            json_result =  {'result': 'You Win', 'dealer_hand': translated_dealer_hand, 'player_hand': translated_player_hand}
            cur.execute("UPDATE leaderboard SET points = points + 100 WHERE name = %s",(name))
          elif sum_blackjack(this_dealer_hand) <= sum_blackjack(this_player_hand):
            json_result =  {'result': 'You Win', 'dealer_hand': translated_dealer_hand, 'player_hand': translated_player_hand}
            cur.execute("UPDATE leaderboard SET points = points + 100 WHERE name = %s",(name))
          else:
            json_result =  {'result': 'You Lose', 'dealer_hand': translated_dealer_hand, 'player_hand': translated_player_hand}
            cur.execute("UPDATE leaderboard SET points = points - 100 WHERE name = %s",(name))

          this_player_hand, this_dealer_hand, this_player_deck, this_dealer_deck, ph_data, dh_data, pd_data, dd_data = reset_game(name)
          cur.execute("UPDATE player_data SET player_hand = %s, player_deck = %s, dealer_hand = %s, dealer_deck = %s WHERE name= %s", (ph_data, pd_data, dh_data, dd_data, name))
          c.commit()
          cur.close()
          c.close()

          return json_result

      else:
        cur.close()
        c.close()
        for i in range(len(this_player_hand)):
            if this_player_hand[i] > 10:
              this_player_hand[i] = card_dict[this_player_hand[i]]
            else:
              this_player_hand[i] = str(this_player_hand[i])

        if this_dealer_hand[1] > 10:
          this_dealer_hand[1] = card_dict[this_dealer_hand[1]]
        return {'name': name, 'dealer_hand': str(this_dealer_hand[1]), 'player_hand': this_player_hand}



api.add_resource(User, '/')
api.add_resource(Trip, '/trip/')
api.add_resource(Blackjack, '/blackjack/')

if __name__ == '__main__':
    application.run(host='0.0.0.0')
