import random
import os

INFINITY = 30000
WIN_SCORE = 20000
LOSE_SCORE = -20000
DRAW_SCORE = 0
MAX_DEPTH = 5

os.makedirs("connect4-minmax-ai", exist_ok=True)
data_file = open("connect4-minmax-ai/Connect4SelfPlayData.txt", "w", encoding="utf-8")


# 盤面表示
def show_connect4_board(board):
    for i in range(6):
        print("-" * 15)
        print("|" + "|".join(board[i]) + "|")

    print("-" * 15)
    print(" " + " ".join(str(i) for i in range(1, 8)))


# 評価関数
def evaluate_board(board, two_score, three_score):
    score = 0

    directions = [
        (0, 1),
        (1, 0),
        (1, 1),
        (-1, 1)
    ]

    for i in range(6):
        for j in range(7):
            player = board[i][j]

            if player == " ":
                continue

            for di, dj in directions:
                count = 1

                ni = i + di
                nj = j + dj

                while (
                    0 <= ni < 6 and
                    0 <= nj < 7 and
                    board[ni][nj] == player
                ):
                    count += 1
                    ni += di
                    nj += dj

                open_end = False

                pi = i - di
                pj = j - dj

                if 0 <= pi < 6 and 0 <= pj < 7:
                    if board[pi][pj] == " ":
                        open_end = True

                if 0 <= ni < 6 and 0 <= nj < 7:
                    if board[ni][nj] == " ":
                        open_end = True

                if open_end:
                    if count == 2:
                        if player == "1":
                            score += two_score
                        else:
                            score -= two_score

                    elif count == 3:
                        if player == "1":
                            score += three_score
                        else:
                            score -= three_score

    return score


# 勝利判定
def check_winner(board, player):
    # 横
    for i in range(6):
        for j in range(4):
            if (
                board[i][j] == player and
                board[i][j + 1] == player and
                board[i][j + 2] == player and
                board[i][j + 3] == player
            ):
                return True

    # 縦
    for i in range(3):
        for j in range(7):
            if (
                board[i][j] == player and
                board[i + 1][j] == player and
                board[i + 2][j] == player and
                board[i + 3][j] == player
            ):
                return True

    # 左上 → 右下
    for i in range(3):
        for j in range(4):
            if (
                board[i][j] == player and
                board[i + 1][j + 1] == player and
                board[i + 2][j + 2] == player and
                board[i + 3][j + 3] == player
            ):
                return True

    # 左下 → 右上
    for i in range(3, 6):
        for j in range(4):
            if (
                board[i][j] == player and
                board[i - 1][j + 1] == player and
                board[i - 2][j + 2] == player and
                board[i - 3][j + 3] == player
            ):
                return True

    return False


# MinMax探索
def decide_minmax_ai_move(
    board,
    max_player,
    now_player,
    depth,
    two_score,
    three_score
):
    opponent = "1" if now_player == "2" else "2"

    available = []

    for j in range(7):
        if board[0][j] == " ":
            available.append(j)

    # 引き分け
    if len(available) == 0:
        return DRAW_SCORE

    # 深さ制限
    if depth >= MAX_DEPTH:
        score = evaluate_board(
            board,
            two_score,
            three_score
        )

        if max_player == "2":
            score = -score

        return score

    if now_player == max_player:
        best_score = -INFINITY
    else:
        best_score = INFINITY

    best_move = None

    for col in available:
        # 石を置く
        for i in range(5, -1, -1):
            if board[i][col] == " ":
                board[i][col] = now_player
                row = i
                break

        # 勝利判定
        if check_winner(board, now_player):
            if now_player == max_player:
                score = WIN_SCORE
            else:
                score = LOSE_SCORE
        else:
            score = decide_minmax_ai_move(
                board,
                max_player,
                opponent,
                depth + 1,
                two_score,
                three_score
            )

        # 手を戻す
        board[row][col] = " "

        # MAX
        if now_player == max_player:
            if (
                score > best_score or
                (
                    score == best_score and
                    random.randint(0, 1) == 0
                )
            ):
                best_score = score

                if depth == 0:
                    best_move = col

        # MIN
        else:
            if (
                score < best_score or
                (
                    score == best_score and
                    random.randint(0, 1) == 0
                )
            ):
                best_score = score

    if depth == 0:
        return best_move

    return best_score


# 評価値取得
def get_move_score(
    board,
    player,
    col,
    two_score,
    three_score
):
    opponent = "1" if player == "2" else "2"

    for i in range(5, -1, -1):
        if board[i][col] == " ":
            board[i][col] = player
            row = i
            break

    if check_winner(board, player):
        if player == "1":
            score = WIN_SCORE
        else:
            score = LOSE_SCORE
    else:
        score = decide_minmax_ai_move(
            board,
            player,
            opponent,
            1,
            two_score,
            three_score
        )

    board[row][col] = " "

    return score


# AIクラス
class MinMaxAI:
    def __init__(self, two_score, three_score):
        self.two_score = two_score
        self.three_score = three_score

    def get_move(self, board, player):
        return decide_minmax_ai_move(
            board,
            player,
            player,
            0,
            self.two_score,
            self.three_score
        )


# AI設定
ai_three_focus = MinMaxAI(10, 50)
ai_two_focus = MinMaxAI(30, 40)

three_focus_win = 0
two_focus_win = 0
draw = 0


# 100試合
for game in range(100):
    print(f"Starting game number {game + 1} ...")

    data_file.write(
        f"Starting game number {game + 1} ...\n"
    )

    # 盤面初期化
    board = [[" " for _ in range(7)] for _ in range(6)]

    player = "1"
    move_num = 1

    # 先手後手交代
    if game % 2 == 0:
        ai1 = ai_three_focus
        ai2 = ai_two_focus

        player1_name = "Three-focus AI"
        player2_name = "Two-focus AI"

    else:
        ai1 = ai_two_focus
        ai2 = ai_three_focus

        player1_name = "Two-focus AI"
        player2_name = "Three-focus AI"

    print(f"Player 1: {player1_name}")
    print(f"Player 2: {player2_name}")

    data_file.write(f"Player 1: {player1_name}\n")
    data_file.write(f"Player 2: {player2_name}\n")

    # 初期盤面
    for k in range(6):
        data_file.write("-" * 15 + "\n")
        data_file.write("|" + "|".join(board[k]) + "|\n")

    data_file.write("-" * 15 + "\n")
    data_file.write(
        " " + " ".join(str(i) for i in range(1, 8)) + "\n"
    )

    data_file.write(f"Player 1 ({player1_name}) to move\n")

    while True:
        # 手を決める
        if player == "1":
            col = ai1.get_move(board, player)

            score = get_move_score(
                board,
                player,
                col,
                ai1.two_score,
                ai1.three_score
            )

            current_player_name = player1_name

        else:
            col = ai2.get_move(board, player)

            score = get_move_score(
                board,
                player,
                col,
                ai2.two_score,
                ai2.three_score
            )

            current_player_name = player2_name

        data_file.write(
            f"Move {move_num}: Player {player} ({current_player_name}) "
            f"chose column {col + 1} ({score})\n"
        )

        # 石を置く
        for i in range(5, -1, -1):
            if board[i][col] == " ":
                board[i][col] = player
                break

        # 盤面出力
        for k in range(6):
            data_file.write("-" * 15 + "\n")
            data_file.write("|" + "|".join(board[k]) + "|\n")

        data_file.write("-" * 15 + "\n")
        data_file.write(
            " " + " ".join(str(i) for i in range(1, 8)) + "\n"
        )

        # 勝利判定
        if check_winner(board, player):
            if current_player_name == "Three-focus AI":
                three_focus_win += 1
            else:
                two_focus_win += 1

            print(f"Game over: {current_player_name} wins")
            data_file.write(f"Game over: {current_player_name} wins\n")

            print(
                f"Current score: Three-focus AI - Two-focus AI "
                f"{three_focus_win} - {two_focus_win} "
                f"(Draws: {draw})"
            )

            break

        # 引き分け判定
        full = True

        for j in range(7):
            if board[0][j] == " ":
                full = False
                break

        if full:
            draw += 1

            print("Game over: Draw")
            data_file.write("Game over: Draw\n")

            print(
                f"Current score: Three-focus AI - Two-focus AI "
                f"{three_focus_win} - {two_focus_win} "
                f"(Draws: {draw})"
            )

            break

        # 手番交代
        if player == "1":
            player = "2"
            data_file.write(f"Player 2 ({player2_name}) to move\n")
        else:
            player = "1"
            data_file.write(f"Player 1 ({player1_name}) to move\n")

        move_num += 1


# 最終結果
print("===================================")
print("Three-focus AI wins :", three_focus_win)
print("Two-focus AI wins :", two_focus_win)
print("Draw :", draw)

data_file.write("===================================\n")
data_file.write(f"Three-focus AI wins : {three_focus_win}\n")
data_file.write(f"Two-focus AI wins : {two_focus_win}\n")
data_file.write(f"Draw : {draw}\n")

data_file.close()