""" Roomba simulation curses"""
import curses
from random import randint
from random import choice
from time import sleep

from typing import Tuple

ROOMBA = "@"
DUST1 = "."
DUST2 = ":"
DUST3 = "&"
BASE = "["


class Roomba:
    def __init__(self, base_y: int, base_x: int,
                 width: int, height: int) -> None:
        self.base_y = base_y
        self.base_x = base_x
        self.y = base_y
        self.x = base_x + 1
        self.room_width = width - 1
        self.room_height = height - 3
        self.charge = 100
        self.recharge_rate = 5
        self.discharge_rate = 2
        self.battery_size = 100
        self.low_charge = 20
        self.state = "Ready"  # ready, cleaning, charging
        self.speed = 5
        self.speed_count = 0

    def operate(self, room: list) -> None:
        # checks the state do _move or _recharge
        if self.state == "Ready" or self.state == "Cleaning":
            if self.speed_count == self.speed:
                self.speed_count = 0
                self.charge -= self.discharge_rate
                room[self.y][self.x] = " "
                self._move()
                room[self.y][self.x] = ROOMBA
            else:
                room[self.y][self.x] = ROOMBA
                self.speed_count += 1
        elif self.state == "Charging":
            return self._charging()

    def get_statues(self) -> Tuple[float, str]:
        # returns the battery percent and state
        return (self.charge / self.battery_size) * 100, self.state

    def _move(self) -> None:
        # returns the next y,x location
        if self.charge <= self.low_charge:
            self._return_home()
        else:
            self.state = "Cleaning"
            directions = []
            if self.y > 0:
                if self.y - 1 != self.base_y and self.x != self.base_x:
                    directions.append((self.y - 1, self.x))

            if self.y > 0 and self.x < self.room_width:
                if self.y - 1 != self.base_y and self.x + 1 != self.base_x:
                    directions.append((self.y - 1, self.x + 1))

            if self.x < self.room_width:
                if self.x + 1 != self.base_x and self.y != self.base_y:
                    directions.append((self.y, self.x + 1))

            if self.x < self.room_width and self.y < self.room_height:
                if self.x + 1 != self.base_x and self.y + 1 != self.base_y:
                    directions.append((self.y + 1, self.x + 1))

            if self.y < self.room_height:
                if self.y + 1 != self.base_y and self.x != self.base_x:
                    directions.append((self.y + 1, self.x))

            if self.y < self.room_height and self.x > 0:
                if self.y + 1 != self.base_y and self.x - 1 != self.base_x:
                    directions.append((self.y + 1, self.x - 1))

            if self.x > 0:
                if self.x - 1 != self.base_x and self.y != self.base_y:
                    directions.append((self.y, self.x - 1))

            if self.x > 0 and self.y > 0:
                if self.y - 1 != self.base_y and self.x - 1 != self.base_x:
                    directions.append((self.y - 1, self.x - 1))

            self.y, self.x = choice(directions)

    def _return_home(self) -> Tuple[int, int]:
        if self.y > self.base_y:
            y = self.y - 1
        elif self.y < self.base_y:
            y = self.y + 1
        else:
            y = self.y
        if self.x > self.base_x + 1:
            x = self.x - 1
        elif self.x < self.base_x + 1:
            x = self.x + 1
        else:
            x = self.x
        if x == self.base_x + 1 and y == self.base_y:
            self.state = "Charging"
        self.y = y
        self.x = x
        return self.y, self.x

    def _charging(self) -> None:
        self.charge += self.recharge_rate
        if self.charge >= self.battery_size:
            self.charge = self.battery_size
            self.state = "Ready"


def add_dust(room: list, height: int, width: int) -> None:
    if randint(1, 3) <= 2:
        random_y = randint(0, height - 3)
        random_x = randint(0, width - 2)
        if room[random_y][random_x] == BASE:
            pass
        elif room[random_y][random_x] == ROOMBA:
            pass
        else:
            if room[random_y][random_x] == " ":
                room[random_y][random_x] = DUST1
            elif room[random_y][random_x] == DUST1:
                room[random_y][random_x] = DUST2
            elif room[random_y][random_x] == DUST2:
                room[random_y][random_x] = DUST3


def curses_main(screen) -> None:
    curses.curs_set(0)  # Set the cursor to off.
    screen.timeout(0)  # Turn blocking off for screen.getch().
    # curses.init_pair()
    screen_height, screen_width = screen.getmaxyx()
    room = [[" " for _ in range(screen_width - 1)] for _ in range(screen_height - 2)]
    roomba = Roomba(5, 0, screen_width, screen_height)
    room[5][0] = BASE
    running = True
    while running:
        screen.clear()
        add_dust(room, screen_height, screen_width)
        roomba.operate(room)
        for y, row in enumerate(room):
            for x, d in enumerate(row):
                if d == ROOMBA:
                    screen.addstr(y, x, d, curses.A_BOLD)
                else:
                    screen.addstr(y, x, d)
        battery, state = roomba.get_statues()
        msg = f" Battery: {battery:.1f}%   {state}"
        screen.addstr(screen_height - 1, 0, msg, curses.A_BOLD)
        screen.refresh()
        ch = screen.getch()
        if ch in [81, 113]:
            running = False
        sleep(0.25)


def main() -> int:
    curses.wrapper(curses_main)
    return 0


if __name__ == "__main__":
    exit(main())
