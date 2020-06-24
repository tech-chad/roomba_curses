""" Roomba simulation curses"""
import curses
from random import randint
from random import choice
from time import sleep

from typing import Tuple
from typing import Union

ROOMBA = "@"
DUST = "."
BASE = "["


class Roomba:
    def __init__(self, base_y, base_x, ) -> None:
        self.base_y = base_y
        self.base_x = base_x
        self.current_y = base_y
        self.current_x = base_x + 1
        self.room_width = 0
        self.room_height = 0
        self.charge = 100
        self.recharge_rate = 0
        self.battery_size = 100
        self.low_charge = 0
        self.state = "ready"  # ready, cleaning, charging
        self.speed = 0
        self.speed_count = 0

    def operate(self) -> Union[Tuple[int, int], None]:
        # checks the state do _move or _recharge
        if self.state == "ready" or self.state == "cleaning":
            return self._move()
        elif self.state == "charging":
            return self._charging()

    def get_statues(self) -> Tuple[float, str]:
        # returns the battery percent and state
        return (self.charge / self.battery_size) * 100, self.state

    def _move(self) -> Tuple[int, int]:
        # returns the next y,x location
        if self.charge <= self.low_charge:
            return self._return_home()
        else:
            self.state = "cleaning"
            directions = []
            if self.current_y > 0:
                directions.append((self.current_y - 1, self.current_x))

            if self.current_y > 0 and self.current_x < self.room_width:
                directions.append((self.current_y - 1, self.current_x + 1))

            if self.current_x < self.room_width:
                directions.append((self.current_y, self.current_x + 1))

            if self.current_x < self.room_width and self.current_y < self.room_height:
                directions.append((self.current_y + 1, self.current_x + 1))

            if self.current_y < self.room_height:
                directions.append((self.current_y + 1, self.current_x))

            if self.current_y < self.room_height and self.current_x > 0:
                directions.append((self.current_y + 1, self.current_x - 1))

            if self.current_x > 0:
                directions.append((self.current_y, self.current_x - 1))

            if self.current_x > 0 and self.current_y > 0:
                directions.append((self.current_y - 1, self.current_x - 1))

            self.current_y, self.current_x = choice(directions)
            return self.current_y, self.current_x

    def _return_home(self) -> Tuple[int, int]:
        if self.current_y > self.base_y:
            y = self.current_y - 1
        elif self.current_y < self.base_y:
            y = self.current_y + 1
        else:
            y = self.current_y
        if self.current_x > self.base_x + 1:
            x = self.current_x - 1
        elif self.current_x < self.base_x + 1:
            x = self.current_x + 1
        else:
            x = self.current_x
        if x == self.base_x + 1 and y == self.base_y:
            self.state = "charging"
        self.current_y = y
        self.current_x = x
        return self.current_y, self.current_x

    def _charging(self) -> None:
        self.charge += self.recharge_rate
        if self.charge >= self.battery_size:
            self.charge = self.battery_size
            self.state = "ready"


def curses_main(screen) -> None:
    curses.curs_set(0)  # Set the cursor to off.
    screen.timeout(0)  # Turn blocking off for screen.getch().
    screen_height, screen_width = screen.getmaxyx()
    room = [[" " for _ in range(screen_width - 1)] for _ in range(screen_height - 2)]
    roomba = Roomba(5, 0)
    roomba.room_height = screen_height
    roomba.room_width = screen_width
    room[5][0] = BASE
    running = True
    while running:
        screen.clear()
        random_y = randint(0, screen_height - 3)
        random_x = randint(0, screen_width - 2)
        if room[random_y][random_x] == BASE:
            pass
        else:
            room[random_y][random_x] = DUST
        ry, rx = roomba.operate()
        room[ry][rx] = " "
        for y, row in enumerate(room):
            for x, d in enumerate(row):
                screen.addstr(y, x, d)
        screen.addstr(ry, rx, ROOMBA)
        screen.addstr(5, 0, BASE)
        screen.refresh()
        ch = screen.getch()
        if ch in [81, 113]:
            running = False
        sleep(0.50)


def main() -> int:
    curses.wrapper(curses_main)
    return 0


if __name__ == "__main__":
    exit(main())
