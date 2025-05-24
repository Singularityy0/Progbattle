def next_move(state):
    ball = state["ball"]
    # Track direction without grid size
    offset = 2 if ball["dx"] > 0 else -2
    target = ball["x"] + offset

    if state["you"]["x"] > target:
        return "left"
    elif state["you"]["x"] + 1 < target:  # +1 for paddle width=2
        return "right"
    return "stay"