# bot2.py | ts will lose everytime
import random
def next_move(game_state):

    ball_x = game_state["ball"]["x"]
    paddle_x = game_state["you"]["x"]

    if ball_x < paddle_x:
        return "left"
    elif ball_x >= paddle_x + 2:
        return "right"
    else:
        return "none"
