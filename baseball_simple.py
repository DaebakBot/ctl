from random import sample

candidates = '1234567890'
goal = ''.join(sample(candidates, 4))

while True:
    guess = input("Guess 4 numbers (to terminate, enter 'q'): ")

    if guess == 'q':
        break

    strike = 0
    ball = 0
    for i in range(4):
        if guess[i] == goal[i]:
            strike = strike + 1
        elif guess[i] in goal:
            ball = ball + 1

    if strike == 4:
        break
 
    print("{0} strikes, {1} balls".format(strike, ball))
