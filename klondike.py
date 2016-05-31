# -*- coding: utf-8 -*-

#
# 카드놀이
#


import random
import os
import platform
import time
import copy


def clear():
    if "Windows" in platform.system():
        os.system("cls")
    else:
        os.system("clear")


class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch().decode('utf-8')


getch = _Getch()

def colored(s, color):
    if "Windows" in platform.system():
        return s
    else:
        return color + "{}\033[00;00m".format(s)
        


class Card:
    def __init__(self, suit, rank):
        #self._suits = ("\N{White Heart Suit}", "\N{White Spade Suit}", "\N{White Diamond Suit}", "\N{White Club Suit}")
        self._suits = ("H", "S", "D", "C")
        self._ranks = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K")
        self.suit = self._suits[suit]
        self.rank = rank
        self.rankname = self._ranks[rank]
        self.opened = False

        #if self.suit == "\N{White Heart Suit}" or self.suit == "\N{White Diamond Suit}":
        if self.suit == "H" or self.suit == "D":
            self.color = "Red"
        else:
            self.color = "Black"

    def __str__(self):
        s = "[" + self.suit + " " + self.rankname + "]"

        if self.color == "Red":
            return colored(s, "\033[47;31m")
        else:
            return colored(s, "\033[47;30m")

    def __repr__(self):
        return self.__str__()


class Deck:
    def __init__(self):
        self._cards = []

        for i in range(4):
            for j in range(13):
                self._cards.append(Card(i, j))

    def top(self):
        if self._cards:
            return self._cards[-1] 

    def shuffle(self):
        random.shuffle(self._cards)

    def draw(self):
        return self._cards.pop()

    def draw_n(self, n):
        if len(self._cards) < n: # error
            return

        ncards = self._cards[len(self._cards) - n:]
        self._cards = self._cards[:len(self._cards) - n]
        return ncards

    def size(self):
        return len(self._cards)


class CardStack(Deck):
    def __init__(self, cards):
        self._cards = cards

    def put(self, card):
        self._cards.append(card)

    def put_n(self, cards):
        self._cards = self._cards + cards

    def get(self, n):
        if n > len(self._cards) or n < 1:
            return

        return self._cards[len(self._cards) - n]


class Game:
    def __init__(self):
        self.width = 100

        self.selected = [-1, -1]
        self.selected_cards = None

        self.deck = Deck()
        self.deck.shuffle()

        self.opened = CardStack(list())

        self.areas = [CardStack(list()) for x in range(4)]

        self.piles = []
        for i in range(1, 8):
            newpile = CardStack(self.deck.draw_n(i))
            newpile.top().opened = True
            self.piles.append(newpile)

        self.cursor = [0, 0]

        self._commands = "\n     --- Commands ---\n\n     B, b: 카드뭉치에서 새 카드 꺼내기\n\
                \r     W, w: 카드뭉치에서 꺼낸 카드 선택\n\
                \r     S, s: 아래 목록의 카드로 이동\n\
                \r     A, a: 왼쪽으로 이동\n\
                \r     D, d: 오른쪽으로 이동\n\
                \r     P, p: 카드 선택 or 카드를 선택한 곳으로 이동\n\
                \r     Q, q: 종료\n"

        self._warning = ""

        self.board = [list() for y in range(2 + max([x.size() for x in self.piles]))]
        self.board_size = [7, len(self.board)]

        self._update_board()

    def _update_board(self):
        self.board = [list() for y in range(2 + max([x.size() for x in self.piles]))]
        self.board_size = [7, len(self.board)]

        for i in range(7):
            self.board[1].append("     ")

        if self.deck.size():
            self.board[0].append("[ ? ]")
        else:
            self.board[0].append("[ X ]")

        if self.opened.size():
            self.board[0].append(str(self.opened.top()))
        else:
            self.board[0].append("[ X ]")

        self.board[0].append("     ")

        for i in range(4):
            if self.areas[i].size():
                self.board[0].append(str(self.areas[i].top()))
            else:
                self.board[0].append("[ X ]")

        for i in range(7): # stack number
            for j in range(2, 2 + max([x.size() for x in self.piles])): # line number
                if j - 1 > self.piles[i].size():
                    self.board[j].append("     ")
                elif self.piles[i].get(self.piles[i].size() - j + 2).opened:
                    self.board[j].append(str(self.piles[i].get(self.piles[i].size() - j + 2)))
                else:
                    self.board[j].append("[ - ]")

    def _insert_columns(self, board):
        result = []
        for line in board:
            temp = list()
            blanks = ["     "] * len(line)
            for x, y in zip(blanks, line):
                temp.append(x)
                temp.append(y)
            result.append(temp)

        board = result

        if self.cursor == self.selected:
            board[self.cursor[1]][self.cursor[0]*2] = "-->**"
        elif self.selected[0] < 0 and self.selected[1] < 0:
            board[self.cursor[1]][self.cursor[0]*2] = "-->  "
        else:
            board[self.cursor[1]][self.cursor[0]*2] = "-->  "
            board[self.selected[1]][self.selected[0]*2] = "   **"
        return board

    def print_board(self):
        board = copy.deepcopy(self.board)

        board = self._insert_columns(board)

        for line in board:
            print(" ".join(line))

    def print_commands(self):
        print(self._commands)

    def print_warning(self):
        print()
        print(self._warning)

    def print_game(self):
        print("-"*self.width)
        print()
        self.print_board()
        self.print_warning()
        self.print_commands()
        print("-"*self.width)
        print()

    def process(self, uinput):
        self._warning = ""
        if uinput == "b" or uinput == "B":
            try:
                card = self.deck.draw()
                card.opened = True
                self.opened.put(card)
            except:
                self._warning = colored("더이상 뒤집을 카드가 없습니다.", "\033[47;31m")
        elif uinput == "w" or uinput == "W":
            if self.cursor[1]:
                self.cursor[1] = self.cursor[1] - 1
            else:
                self.cursor[1] = self.board_size[1] - 1
        elif uinput == "d" or uinput == "D":
            if self.cursor[0] < self.board_size[0] - 1:
                self.cursor[0] = self.cursor[0] + 1
            else:
                self.cursor[0] = 0
        elif uinput == "s" or uinput == "S":
            if self.cursor[1] < self.board_size[1] - 1:
                self.cursor[1] = self.cursor[1] + 1
            else:
                self.cursor[1] = 0
        elif uinput == "a" or uinput == "A":
            if self.cursor[0]:
                self.cursor[0] = self.cursor[0] - 1
            else:
                self.cursor[0] = self.board_size[0] - 1
        elif uinput == "p" or uinput == "P":
            if self.selected[0] != -1 and self.selected[1] != -1: # 이미 선택된 것이 있음
                if self.cursor[1] < 2:
                    # AREA 로 옮기기
                    if self.cursor[1] == 0 and self.cursor[0] > 2:
                        selectedarea = self.areas[self.cursor[0] - 3]
                        if selectedarea.size(): # Area에 이미 카드 쌓는 중
                            if self.selected_cards[1] > 1: # 잘못된 경우
                                pass
                            elif self.selected[0] == 1 and self.selected[1] == 0: # from opened
                                if self.opened.top().suit == selectedarea.top().suit and \
                                        self.opened.top().rank == selectedarea.top().rank + 1:
                                            selectedarea.put(self.opened.draw())
                            elif self.piles[self.selected_cards[0]].top().suit == selectedarea.top().suit and \
                                    self.piles[self.selected_cards[0]].top().rank == selectedarea.top().rank + 1:
                                        selectedarea.put(self.piles[self.selected_cards[0]].draw())
                                        if self.piles[self.selected_cards[0]].size():
                                            self.piles[self.selected_cards[0]].top().opened = True
                            self.selected_cards = None
                            self.selected = [-1, -1]
                        else: # Area에 카드 없음
                            if self.selected_cards[1] > 1: # 잘못된 경우
                                pass
                            elif self.selected[0] == 1 and self.selected[1] == 0: # from opened
                                if self.opened.top().rank == 0:
                                    selectedarea.put(self.opened.draw())
                            elif self.piles[self.selected_cards[0]].top().rank == 0:
                                selectedarea.put(self.piles[self.selected_cards[0]].draw())
                                if self.piles[self.selected_cards[0]].size():
                                    self.piles[self.selected_cards[0]].top().opened = True
                    self.selected_cards = None
                    self.selected = [-1, -1]
                else:
                    if self.selected[0] == 1 and self.selected[1] == 0:
                        # opened 에서 다른 Pile로
                        selectedpile = self.piles[self.cursor[0]]
                        frompile = self.opened
                    else:
                        # Pile 에서 다른 Pile로
                        selectedpile = self.piles[self.cursor[0]]
                        frompile = self.piles[self.selected_cards[0]]

                    if not selectedpile.size():
                        selectedpile.put_n(frompile.draw_n(self.selected_cards[1]))
                        if frompile.size():
                            frompile.top().opened = True

                    elif frompile.get(self.selected_cards[1]).rank + 1 == \
                            selectedpile.top().rank and \
                            frompile.get(self.selected_cards[1]).color != \
                            selectedpile.top().color:
                                selectedpile.put_n(frompile.draw_n(self.selected_cards[1]))
                                if frompile.size():
                                    frompile.top().opened = True

                    self.selected_cards = None
                    self.selected = [-1, -1]
            else: # 선택된 것이 없음
                if self.cursor[1] < 2:
                    if self.cursor[1] == 0 and self.cursor[0] == 1: # open된 hint card
                        self.selected_cards = (self.cursor[0], 1)
                        self.selected = self.cursor[:]
                    else:
                        return
                else:
                    selectedpile = self.piles[self.cursor[0]]
                    if self.cursor[1] > selectedpile.size() + 1:
                        return
                    elif not selectedpile.get(selectedpile.size() - self.cursor[1] + 2).opened:
                        return
                    else:
                        self.selected_cards = (self.cursor[0], selectedpile.size() - self.cursor[1] + 2)
                        self.selected = self.cursor[:]

        self._update_board()

    def check_win(self):
        for area in self.areas:
            if area.size() != 13:
                return False
        return True

    def run(self):
        clear()
        print("\n\n\n\n\n\n\n카드 게임에 오신 것을 환영합니다.\n\n\n그럴싸하죠?\n\n")

        for i in range(7):
            time.sleep(1)
            print("\r게임 로딩중" + "."*i, end="")

        while True:
            clear()
            self.print_game()

            if self.check_win():
                print("\n\n\n " + colored("축하합니다! 승리하셨습니다!", "\033[32m") + " \n\n\n")
                break

            user_input = getch()
            if user_input == "q" or user_input == "Q":
                check = input("Really want to quit? [y/n] : ")
                if check == "Y" or check == "y":
                    break
                else:
                    continue
            self.process(user_input)


if __name__=="__main__":
    g = Game()
    g.run()
