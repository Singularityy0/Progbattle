def next_move(state):
    my_x = state["you"]["x"]
    # Derive center using paddle width (2)
    center = 14  # (30//2 - 1) since paddle spans 2 units

    if my_x > center:
        return "left"
    elif my_x < center:
        return "right"
    else:
        return "stay"