import streamlit as st
import random

st.set_page_config(
    page_title="Pyramid Solitaire",
    page_icon="♦",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Georgia&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #0a3d1f;
    color: #e8d5a3;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

.block-container { padding: 1.5rem 2rem !important; }

.title {
    text-align: center;
    font-size: 1.8rem;
    font-weight: bold;
    color: #e8d5a3;
    letter-spacing: 0.1em;
    margin-bottom: 0.2rem;
}
.subtitle {
    text-align: center;
    font-size: 0.8rem;
    color: #4a8a60;
    margin-bottom: 1rem;
}
.msg-box {
    text-align: center;
    font-size: 1rem;
    font-style: italic;
    color: #aed6b8;
    background: #0f2d16;
    border: 1px solid #1e5c30;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    margin-bottom: 1rem;
}
.msg-ok  { color: #7ed17e !important; border-color: #2d7a3a !important; }
.msg-err { color: #e07070 !important; border-color: #7a2d2d !important; }

.stats {
    text-align: center;
    color: #7fa8c0;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

.card-btn {
    display: inline-block;
    width: 72px;
    height: 95px;
    border-radius: 8px;
    border: 2px solid #aaa;
    background: #fffdf5;
    text-align: center;
    line-height: 1.1;
    cursor: pointer;
    font-weight: bold;
    padding-top: 6px;
    font-size: 1rem;
    margin: 4px;
    vertical-align: top;
    transition: transform 0.1s;
}
.card-btn.selected {
    border-color: #f9a825;
    background: #fff176;
}
.card-btn.red { color: #c0392b; }
.card-btn.black { color: #1a1a2e; }

.pyramid-row {
    display: flex;
    justify-content: center;
    margin-bottom: 4px;
}

.stButton > button {
    background: #1e4a6e !important;
    color: #e8d5a3 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: bold !important;
    padding: 0.5rem 1.5rem !important;
}
.stButton > button:hover {
    background: #2a6a9e !important;
}
</style>
""", unsafe_allow_html=True)

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
RED_SUITS  = {"♥", "♦"}
ROW_SIZES  = [1, 2, 3, 4, 3]

def new_game():
    deck = [dict(c, removed=False) for c in CARDS]
    random.shuffle(deck)
    pyramid = []
    idx = 0
    for size in ROW_SIZES:
        pyramid.append([deck[idx + i] for i in range(size)])
        idx += size
    return pyramid

def active_cards(pyramid):
    return [
        (ri, ci)
        for ri, row in enumerate(pyramid)
        for ci, c in enumerate(row)
        if not c["removed"]
    ]

# ── Session state init ────────────────────────────────────────────────────────
if "pyramid" not in st.session_state:
    st.session_state.pyramid  = new_game()
    st.session_state.selected = []
    st.session_state.moves    = 0
    st.session_state.msg      = ("Pick two cards that sum to 13  •  K removes alone", "info")
    st.session_state.won      = False

# ── Title ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="title">♦ PYRAMID SOLITAIRE ♦</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">13 unique cards • Pick pairs that sum to 13 • K removes alone</div>', unsafe_allow_html=True)

remaining = len(active_cards(st.session_state.pyramid))
st.markdown(f'<div class="stats">Moves: {st.session_state.moves} &nbsp;&nbsp;|&nbsp;&nbsp; Cards left: {remaining}</div>', unsafe_allow_html=True)

msg_text, msg_kind = st.session_state.msg
msg_class = {"ok": "msg-ok", "err": "msg-err", "info": ""}.get(msg_kind, "")
st.markdown(f'<div class="msg-box {msg_class}">{msg_text}</div>', unsafe_allow_html=True)

# ── Win check ─────────────────────────────────────────────────────────────────
if st.session_state.won:
    st.success(f"🎉 Congratulations! You cleared all 13 cards in {st.session_state.moves} moves!")

# ── Pyramid rendering ─────────────────────────────────────────────────────────
pyramid = st.session_state.pyramid
selected = st.session_state.selected

for ri, row in enumerate(pyramid):
    live = [(ci, c) for ci, c in enumerate(row) if not c["removed"]]
    if not live:
        continue

    cols = st.columns([1] * len(live), gap="small")
    # Centre the row using empty columns
    total_slots = max(len(r) for r in pyramid if any(not c["removed"] for c in r))
    padding = (total_slots - len(live)) // 2

    padded_cols = st.columns([1] * (len(live) + padding * 2), gap="small")

    for slot, (ci, card) in enumerate(live):
        col = padded_cols[padding + slot]
        with col:
            is_selected = (ri, ci) in selected
            suit_color  = "red" if card["suit"] in RED_SUITS else "black"
            border_color = "#f9a825" if is_selected else "#aaaaaa"
            bg_color     = "#fff176" if is_selected else "#fffdf5"
            text_color   = "#c0392b" if suit_color == "red" else "#1a1a2e"

            card_html = f"""
            <div style="
                width:72px; height:95px; border-radius:8px;
                border:2px solid {border_color};
                background:{bg_color};
                color:{text_color};
                display:flex; flex-direction:column;
                align-items:center; justify-content:center;
                font-weight:bold; font-size:1.1rem;
                margin:auto;
            ">
                <div style="font-size:1.3rem;">{card['rank']}</div>
                <div style="font-size:1.1rem;">{card['suit']}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

            btn_label = f"{card['rank']}{card['suit']}"
            if st.button(btn_label, key=f"card_{ri}_{ci}", disabled=st.session_state.won):
                g = st.session_state

                if (ri, ci) in g.selected:
                    g.selected.remove((ri, ci))
                    g.msg = ("Pick two cards that sum to 13  •  K removes alone", "info")

                elif card["value"] == 13:
                    pyramid[ri][ci]["removed"] = True
                    g.moves += 1
                    g.msg = (f"Removed K{card['suit']} alone ✓", "ok")
                    g.selected = []
                    if not active_cards(pyramid):
                        g.won = True

                else:
                    g.selected.append((ri, ci))
                    if len(g.selected) == 2:
                        (r1, c1), (r2, c2) = g.selected
                        v1 = pyramid[r1][c1]["value"]
                        v2 = pyramid[r2][c2]["value"]
                        n1 = pyramid[r1][c1]["rank"] + pyramid[r1][c1]["suit"]
                        n2 = pyramid[r2][c2]["rank"] + pyramid[r2][c2]["suit"]
                        if v1 + v2 == 13:
                            pyramid[r1][c1]["removed"] = True
                            pyramid[r2][c2]["removed"] = True
                            g.moves += 1
                            g.msg = (f"Removed {n1} + {n2} ✓", "ok")
                            g.selected = []
                            if not active_cards(pyramid):
                                g.won = True
                        else:
                            g.msg = (f"{n1}({v1}) + {n2}({v2}) = {v1+v2}  ✗  Must equal 13!", "err")
                            g.selected = []
                    else:
                        v = card["value"]
                        g.msg = (f"{card['rank']}{card['suit']} selected — need a {13 - v} to pair.", "info")

                st.rerun()

# ── New Game button ───────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🔀 New Game", use_container_width=True):
        st.session_state.pyramid  = new_game()
        st.session_state.selected = []
        st.session_state.moves    = 0
        st.session_state.msg      = ("Pick two cards that sum to 13  •  K removes alone", "info")
        st.session_state.won      = False
        st.rerun()