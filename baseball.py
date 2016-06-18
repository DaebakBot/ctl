from random import sample

def make_goal():
    candidates = '1234567890'
    goal = ''.join(sample(candidates, 4))
    return goal

def check_value(guess, goal):
    strike = 0
    ball = 0
    for i in range(4):
        if guess[i] == goal[i]:
            strike = strike + 1
        elif guess[i] in goal:
            ball = ball + 1
    return (strike, ball)

tries = 0
goal = make_goal()
rule = """
숫자야구 규칙
1. 0~9사이의 숫자로 이루어진 4자리 숫자를 맞춰야 합니다.
2. 각 자리의 숫자는 중복되지 않습니다.
3. 숫자와 숫자의 위치가 일치하면 strike
4. 숫자의 위치만 틀렸으면 ball 입니다.
5. 종료하려면 q를 입력하세요.

"""

print(rule)
if 'raw_input' in dir(__builtins__):
    input = raw_input

while True:
    guess = input("Guess 4 numbers (to terminate, enter 'q'): ")

    if guess == 'q':
        break

    try:
        int(guess)
    except:
        print("4자리 숫자나 q만 입력하세요")
        continue

    if 4 != len(guess):
        print("4자리 숫자를 입력하세요")
        continue

    if len(set(guess)) != len(guess):
        print("중복 없는 숫자를 입력하세요")
        continue

    s, b = check_value(guess, goal)
    tries = tries + 1
    
    if s == 4:
        print("Great!")
        print("Number of tries {0}".format(tries))
        break
    
    print("{0} strikes, {1} balls".format(s, b))
    print("Number of tries {0}".format(tries))
