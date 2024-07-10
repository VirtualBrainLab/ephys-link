import time

from rich import box
from rich.live import Live
from rich.table import Table

table = Table(box=box.SIMPLE_HEAVY, highlight=True)
table.add_column("Row ID")
table.add_column("Description")
table.add_column("Level")

with Live(table):  # update 4 times a second to feel fluid
    for row in range(12):
        time.sleep(0.4)
        table.add_row(f"{row}", f"description {row}", "[bright_white on red] ERROR ")

    time.sleep(1)
    print(table.rows)
