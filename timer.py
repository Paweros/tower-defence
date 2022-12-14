def new_timer(ticks):
    while True:
        for i in range(ticks):
            yield True if i == 0 else False