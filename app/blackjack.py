import random

def text_to_list(text):
  num = text.split(',')
  return list(map(int, num))

def list_to_text(lists):
  return ','.join(str(x) for x in lists)

def generate_deck():
    deck = []
    for t in range(1,14):
        for m in range(4):
            deck.append(t)
    random.shuffle(deck)
    return deck

def sum_blackjack(cards):
    sums = 0
    num_1 = 0
    for i in cards:
        if i == 1:
            num_1 += 1
        elif i > 10:
            sums += 10
        else:
            sums += i
    for i in range(num_1):
        if sums > 11:
            sums += 1
        else:
            sums += 10
    return sums