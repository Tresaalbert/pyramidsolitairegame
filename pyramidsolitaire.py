import tkinter as tk
from tkinter import messagebox
import random

# ── Exactly 13 unique cards: A 2 3 4 5 6 7 8 9 10 J Q K ──────────────────────
CARDS = [
    {"rank": "A",  "suit": "♠", "value": 1},
    {"rank": "2",  "suit": "♥", "value": 2},
    {"rank": "3",  "suit": "♦", "value": 3},
    {"rank": "4",  "suit": "♣", "value": 4},
    {"rank": "5",  "suit": "♠", "value": 5},
    {"rank": "6",  "suit": "♥", "value": 6},
    {"rank": "7",  "suit": "♦", "value": 7},
    {"rank": "8",  "suit": "♣", "value": 8},
    {"rank": "9",  "suit": "♠", "value": 9},
    {"rank": "10", "suit": "♥", "value": 10},
    {"rank": "J",  "suit": "♦", "value": 11},
    {"rank": "Q",  "suit": "♣", "value": 12},
    {"rank": "K",  "suit": "♠", "value": 13},
]
RED_SUITS = {"♥", "♦"}
ROW_SIZES = [1, 2, 3, 4, 3]   # total = 13

CARD_W = 82
CARD_H = 100
H_GAP  = 14
V_GAP  = 18
BG     = "#0a3d1f"
FELT   = "#145228"


class PyramidGame:
    def __init__(self):
        self.new_game()

    def new_game(self):
        deck = [dict(c, removed=False) for c in CARDS]
        random.shuffle(deck)
        self.pyramid = []
        idx = 0
        for size in ROW_SIZES:
            row = [deck[idx + i] for i in range(size)]
            idx += size
            self.pyramid.append(row)
        self.selected = []
        self.moves    = 0
        self.won      = False

    def active(self):
        return [(ri, ci, c)
                for ri, row in enumerate(self.pyramid)
                for ci, c in enumerate(row)
                if not c["removed"]]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pyramid Solitaire")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.game = PyramidGame()
        self._build_ui()
        self._draw()

    # ── UI skeleton ───────────────────────────────────────────────────────────
    def _build_ui(self):
        tk.Label(self, text="♦  PYRAMID SOLITAIRE  ♦",
                 font=("Georgia", 17, "bold"), fg="#e8d5a3", bg=BG).pack(pady=(14, 3))

        self.stats_var = tk.StringVar()
        tk.Label(self, textvariable=self.stats_var,
                 font=("Georgia", 11), fg="#7fa8c0", bg=BG).pack()

        self.msg_var = tk.StringVar()
        self.msg_lbl = tk.Label(self, textvariable=self.msg_var,
                                font=("Georgia", 11, "italic"),
                                fg="#aed6b8", bg=BG, wraplength=540)
        self.msg_lbl.pack(pady=(4, 8))

        cw = 4 * CARD_W + 3 * H_GAP + 60
        ch = 5 * CARD_H + 4 * V_GAP + 30
        self.canvas = tk.Canvas(self, width=cw, height=ch,
                                bg=FELT, highlightthickness=0)
        self.canvas.pack(padx=20, pady=(0, 8))
        self.canvas.bind("<Button-1>", self._on_click)

        bf = tk.Frame(self, bg=BG)
        bf.pack(pady=(0, 12))
        tk.Button(bf, text="🔀  New Game",
                  font=("Georgia", 11), fg="#e8d5a3", bg="#1e4a6e",
                  activebackground="#2a6a9e", relief="flat",
                  padx=18, pady=6, command=self._new_game).pack()

        tk.Label(self,
                 text="13 unique cards: A 2 3 4 5 6 7 8 9 10 J Q K\n"
                      "Pick two cards that sum to 13  •  K removes alone",
                 font=("Georgia", 9), fg="#4a8a60", bg=BG).pack(pady=(0, 10))

        self._rects = {}   # (ri,ci) → (x1,y1,x2,y2)

    # ── Drawing ───────────────────────────────────────────────────────────────
    def _positions(self):
        """Centre each row's remaining cards on the canvas."""
        positions = {}
        cw = int(self.canvas["width"])
        for ri, row in enumerate(self.game.pyramid):
            live = [(ci, c) for ci, c in enumerate(row) if not c["removed"]]
            n = len(live)
            if n == 0:
                continue
            row_w   = n * CARD_W + (n - 1) * H_GAP
            start_x = (cw - row_w) // 2 + CARD_W // 2
            cy      = 15 + CARD_H // 2 + ri * (CARD_H + V_GAP)
            for slot, (ci, _) in enumerate(live):
                cx = start_x + slot * (CARD_W + H_GAP)
                positions[(ri, ci)] = (cx, cy)
        return positions

    def _draw(self):
        g = self.game
        self.canvas.delete("all")
        self._rects.clear()

        for (ri, ci), (cx, cy) in self._positions().items():
            card = g.pyramid[ri][ci]
            x1, y1 = cx - CARD_W // 2, cy - CARD_H // 2
            x2, y2 = cx + CARD_W // 2, cy + CARD_H // 2

            sel  = (ri, ci) in g.selected
            red  = card["suit"] in RED_SUITS
            tc   = "#c0392b" if red else "#1a1a2e"

            # Shadow
            self.canvas.create_rectangle(x1+3, y1+3, x2+3, y2+3,
                                         fill="#082015", outline="")
            # Card body
            fill    = "#fff176" if sel else "#fffdf5"
            outline = "#f9a825" if sel else "#aaaaaa"
            self.canvas.create_rectangle(x1, y1, x2, y2,
                                         fill=fill, outline=outline,
                                         width=3 if sel else 1)

            r, s = card["rank"], card["suit"]
            # Top-left corner
            self.canvas.create_text(x1+8, y1+10, text=r,
                                    font=("Georgia", 10, "bold"), fill=tc, anchor="nw")
            self.canvas.create_text(x1+8, y1+24, text=s,
                                    font=("Georgia", 9), fill=tc, anchor="nw")
            # Centre
            self.canvas.create_text(cx, cy - 10, text=r,
                                    font=("Georgia", 22, "bold"), fill=tc)
            self.canvas.create_text(cx, cy + 16, text=s,
                                    font=("Georgia", 18), fill=tc)

            self._rects[(ri, ci)] = (x1, y1, x2, y2)

        remaining = len(g.active())
        self.stats_var.set(f"Moves: {g.moves}        Cards left: {remaining}")

        if not self.msg_var.get():
            self._set_msg("Pick two cards that sum to 13  •  K removes alone")

    def _set_msg(self, text, kind="info"):
        self.msg_var.set(text)
        self.msg_lbl.configure(fg={"ok":"#7ed17e","err":"#e07070","info":"#aed6b8"}.get(kind,"#aed6b8"))

    # ── Interaction ───────────────────────────────────────────────────────────
    def _on_click(self, event):
        if self.game.won:
            return
        for (ri, ci), (x1, y1, x2, y2) in self._rects.items():
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self._handle(ri, ci)
                return

    def _handle(self, ri, ci):
        g, ref = self.game, (ri, ci)
        card   = g.pyramid[ri][ci]

        # Deselect
        if ref in g.selected:
            g.selected.remove(ref)
            self._set_msg("Pick two cards that sum to 13  •  K removes alone")
            self._draw()
            return

        # King → instant remove
        if card["value"] == 13:
            self._remove([ref])
            return

        g.selected.append(ref)

        if len(g.selected) == 2:
            (r1,c1),(r2,c2) = g.selected
            v1 = g.pyramid[r1][c1]["value"];  v2 = g.pyramid[r2][c2]["value"]
            n1 = g.pyramid[r1][c1]["rank"] + g.pyramid[r1][c1]["suit"]
            n2 = g.pyramid[r2][c2]["rank"] + g.pyramid[r2][c2]["suit"]
            if v1 + v2 == 13:
                self._remove(list(g.selected))
            else:
                self._set_msg(f"{n1}({v1}) + {n2}({v2}) = {v1+v2}  ✗  Must equal 13!", "err")
                g.selected = []
                self._draw()
        else:
            v = card["value"]
            self._set_msg(f"{card['rank']}{card['suit']} selected — need a {13-v} to pair.", "info")
            self._draw()

    def _remove(self, refs):
        g = self.game
        names = []
        for r, c in refs:
            g.pyramid[r][c]["removed"] = True
            names.append(g.pyramid[r][c]["rank"] + g.pyramid[r][c]["suit"])
        g.selected = []
        g.moves   += 1
        self._set_msg(f"Removed  {' + '.join(names)}  ✓", "ok")
        self._draw()
        if not g.active():
            g.won = True
            self.after(400, lambda: messagebox.showinfo(
                "You Win! 🎉",
                f"Congratulations!\nCleared all 13 cards in {g.moves} moves! 🎉"))

    def _new_game(self):
        self.game = PyramidGame()
        self.msg_var.set("")
        self._set_msg("Pick two cards that sum to 13  •  K removes alone")
        self._draw()


if __name__ == "__main__":
    App().mainloop()
