import math
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich.text import Text

console = Console()

class MancalaBoard:
    def __init__(self, board=None):
        if board:
            self.board = board[:]
        else:
            self.board = [4]*6 + [0] + [4]*6 + [0]

    def clone(self):
        return MancalaBoard(self.board[:])

    def stones_visual(self, count):
        if count == 0:
            return " " * 3 + "[dim]-[/]"
        symbol = "⚪"
        if count <= 2:
            return " ".join([symbol] * count)
        elif count <= 4:
            top = " ".join([symbol] * min(2, count))
            bottom = " ".join([symbol] * max(0, count - 2))
            return f"{top}\n{bottom}"
        elif count <= 6:
            top = " ".join([symbol] * 3)
            bottom = " ".join([symbol] * (count - 3))
            return f"{top}\n{bottom}"
        else:
            return f"{symbol}x{count}"

    def print_board(self):
        console.clear()

        table = Table.grid(expand=True, padding=(1, 3))
        for _ in range(7):
            table.add_column(justify="center")

        ai_row = [f"[bold red]{self.stones_visual(self.board[i])}[/]" for i in range(12, 6, -1)]
        player_row = [f"[bold yellow]{self.stones_visual(self.board[i])}[/]" for i in range(0, 6)]

        ai_labels = ["[dim]6[/]", "[dim]5[/]", "[dim]4[/]", "[dim]3[/]", "[dim]2[/]", "[dim]1[/]"]
        player_labels = ["[dim]1[/]", "[dim]2[/]", "[dim]3[/]", "[dim]4[/]", "[dim]5[/]", "[dim]6[/]"]

        table.add_row(*ai_labels)
        table.add_row(*ai_row)
        table.add_row("")
        table.add_row(*player_row)
        table.add_row(*player_labels)

        store_panel = Panel.fit(
            f"[red bold]AI Store[/]: {self.board[13]} ⚪\n"
            f"[green bold]Your Store[/]: {self.board[6]} ⚪",
            border_style="bright_cyan",
            title="🏠 STORES",
            padding=(1, 3)
        )

        console.print(Panel(table, title="CONGKLAK AI - Optimized Algorithm", border_style="magenta"))
        console.print(store_panel)

    def move(self, pit, player, animate=False, player_name=""):
        if self.board[pit] == 0:
            return self, False

        new_board = self.clone()
        b = new_board.board
        stones = b[pit]
        b[pit] = 0
        i = pit

        while stones > 0:
            i = (i + 1) % 14
            if (player == 0 and i == 13) or (player == 1 and i == 6):
                continue
            b[i] += 1
            stones -= 1

            if animate:
                console.clear()
                console.print(Panel(f"🎮 {player_name} Menyebarkan Batu...", border_style="magenta"))
                new_board.print_board()
                console.print(f"[cyan]💎 Batu tersisa: {stones}[/]")
                time.sleep(0.4)

        if player == 0 and 0 <= i <= 5 and b[i] == 1:
            opp = 12 - i
            if b[opp] > 0:
                b[6] += b[i] + b[opp]
                b[i] = b[opp] = 0
                if animate:
                    console.print("[green]✨ Capture![/]")
                    time.sleep(0.5)
        elif player == 1 and 7 <= i <= 12 and b[i] == 1:
            opp = 12 - i
            if b[opp] > 0:
                b[13] += b[i] + b[opp]
                b[i] = b[opp] = 0
                if animate:
                    console.print("[red]✨ AI Capture![/]")
                    time.sleep(0.5)

        extra_turn = (i == (6 if player == 0 else 13))
        return new_board, extra_turn

    def valid_moves(self, player):
        return [i for i in (range(0, 6) if player == 0 else range(7, 13)) if self.board[i] > 0]

    def is_game_over(self):
        return all(self.board[i] == 0 for i in range(0, 6)) or all(self.board[i] == 0 for i in range(7, 13))

    def collect_remaining(self):
        if all(self.board[i] == 0 for i in range(0, 6)):
            for i in range(7, 13):
                self.board[13] += self.board[i]
                self.board[i] = 0

        elif all(self.board[i] == 0 for i in range(7, 13)):
            for i in range(0, 6):
                self.board[6] += self.board[i] 
                self.board[i] = 0


def evaluate(board, player):
    b = board.board
    my_store = b[6] if player == 0 else b[13]
    opp_store = b[13] if player == 0 else b[6]
    my_idx = range(0, 6) if player == 0 else range(7, 13)
    opp_idx = range(7, 13) if player == 0 else range(0, 6)
    
    my_side = sum(b[i] for i in my_idx)
    opp_side = sum(b[i] for i in opp_idx)
    total_stones = my_side + opp_side
    
    game_phase = 1.0 - (total_stones / 48.0)
    
    store_diff = (my_store - opp_store) / 48.0
    store_weight = 10.0 + game_phase * 15.0
    
    if total_stones > 0:
        side_diff = (my_side - opp_side) / total_stones
    else:
        side_diff = 0.0
    side_weight = 3.0 * (1.0 - game_phase * 0.5)
    
    my_moves = len(board.valid_moves(player))
    opp_moves = len(board.valid_moves(1 - player))
    mobility_diff = (my_moves - opp_moves) / 6.0
    mobility_weight = 2.5 * (1.0 - game_phase * 0.7)
    
    my_store_pos = 6 if player == 0 else 13
    opp_store_pos = 13 if player == 0 else 6
    extra_count = 0
    
    for i in my_idx:
        if b[i] > 0:
            pos = i
            stones_left = b[i]
            while stones_left > 0:
                pos = (pos + 1) % 14
                if pos == opp_store_pos:
                    continue
                stones_left -= 1
            if pos == my_store_pos:
                extra_count += 1
    
    extra_score = math.tanh(extra_count / 3.0)
    extra_weight = 4.0
    
    capture_value = 0
    for i in my_idx:
        if b[i] > 0:
            pos = i
            stones_left = b[i]
            while stones_left > 0:
                pos = (pos + 1) % 14
                if pos == opp_store_pos:
                    continue
                stones_left -= 1
            
            if pos in my_idx and b[pos] == 0:
                opp_pit = 12 - pos
                capture_value += b[opp_pit]
    
    capture_score = math.tanh(capture_value / 10.0)
    capture_weight = 5.0
    
    opp_extra_count = 0
    for j in opp_idx:
        if b[j] > 0:
            pos = j
            stones_left = b[j]
            my_store_check = 6 if player == 0 else 13
            while stones_left > 0:
                pos = (pos + 1) % 14
                if pos == my_store_check:
                    continue
                stones_left -= 1
            if pos == opp_store_pos:
                opp_extra_count += 1
    
    threat_score = -math.tanh(opp_extra_count / 3.0)
    threat_weight = 3.5
    
    total = (
        store_weight * store_diff +
        side_weight * side_diff +
        mobility_weight * mobility_diff +
        extra_weight * extra_score +
        capture_weight * capture_score +
        threat_weight * threat_score
    )
    
    return math.tanh(total / 12.0)


def alphabeta(board, depth, alpha, beta, current_player, root_player, start_time, time_limit):
    if time.time() - start_time > time_limit:
        return evaluate(board, root_player), None
    
    if depth == 0 or board.is_game_over():
        return evaluate(board, root_player), None

    valid = board.valid_moves(current_player)
    if not valid:
        return evaluate(board, root_player), None

    if depth > 2:
        move_evals = []
        for m in valid:
            new_board, _ = board.move(m, current_player)
            quick_eval = evaluate(new_board, root_player)
            move_evals.append((quick_eval, m))
        
        maximizing = (current_player == root_player)
        move_evals.sort(reverse=maximizing)
        valid = [m for _, m in move_evals]

    maximizing = (current_player == root_player)
    best_move = None

    if maximizing:
        value = -math.inf
        for m in valid:
            new_board, extra = board.move(m, current_player)
            next_player = current_player if extra else (1 - current_player)
            
            val, _ = alphabeta(new_board, depth - 1, alpha, beta, next_player, root_player, start_time, time_limit)
            
            if val > value:
                value, best_move = val, m
            alpha = max(alpha, value)
            if beta <= alpha or time.time() - start_time > time_limit:
                break
        return value, best_move
    else:
        value = math.inf
        for m in valid:
            new_board, extra = board.move(m, current_player)
            next_player = current_player if extra else (1 - current_player)
            
            val, _ = alphabeta(new_board, depth - 1, alpha, beta, next_player, root_player, start_time, time_limit)
            
            if val < value:
                value, best_move = val, m
            beta = min(beta, value)
            if beta <= alpha or time.time() - start_time > time_limit:
                break
        return value, best_move


def alpha_beta_timed(board, player, max_time=2.0, max_depth=12):
    start = time.time()
    best_move = None
    best_value = -math.inf
    reached_depth = 0

    for depth in range(1, max_depth + 1):
        if time.time() - start > max_time * 0.85:
            break
        
        val, move = alphabeta(board, depth, -math.inf, math.inf, player, player, start, max_time)
        
        if time.time() - start > max_time * 0.85:
            break
        
        if move is not None:
            best_value, best_move = val, move
            reached_depth = depth
            
    return best_value, best_move, reached_depth

def player_vs_ai():
    console.print(Panel(
        "[bold magenta]Welcome to Congklak AI - Optimized Algorithm [/]\n"
        "[dim]Powered by Advanced Alpha-Beta Pruning with Game-Phase Heuristics[/]",
        style="bright_yellow"
    ))
    
    difficulty_text = Text()
    difficulty_text.append("Select AI Difficulty:\n", style="bold cyan")
    difficulty_text.append("  1. ", style="dim")
    difficulty_text.append("Easy", style="green")
    difficulty_text.append(" (Depth 4-6, 1.0s)\n", style="dim")
    difficulty_text.append("  2. ", style="dim")
    difficulty_text.append("Medium", style="yellow")
    difficulty_text.append(" (Depth 6-8, 1.5s)\n", style="dim")
    difficulty_text.append("  3. ", style="dim")
    difficulty_text.append("Hard", style="red")
    difficulty_text.append(" (Depth 8-10, 2.0s)\n", style="dim")
    difficulty_text.append("  4. ", style="dim")
    difficulty_text.append("Expert", style="magenta bold")
    difficulty_text.append(" (Depth 10-12, 3.0s)", style="dim")
    
    console.print(Panel(difficulty_text, border_style="cyan"))
    
    choice = console.input("[bold cyan]Your choice (1-4): [/]")
    
    difficulty_map = {
        "1": (6, 1.0, "Easy"),
        "2": (8, 1.5, "Medium"),
        "3": (10, 2.0, "Hard"),
        "4": (12, 3.0, "Expert")
    }
    
    max_depth, time_limit, diff_name = difficulty_map.get(choice, (8, 1.5, "Medium"))
    
    console.print(f"\n[green]✓ Difficulty set to: {diff_name}[/]")
    time.sleep(1)
    
    game = MancalaBoard()
    game.print_board()
    
    move_count = 0
    player_time = 0
    ai_time = 0

    while not game.is_game_over():
        move_count += 1
        
        console.print(f"\n[bold yellow]═══ Move #{move_count} - YOUR TURN ═══[/]")
        
        while True:
            if game.is_game_over():
                break
            
            valid_pits = [i + 1 for i in range(6) if game.board[i] > 0]
            console.print(f"[dim]Valid pits: {valid_pits}[/]")
            
            move_input = console.input("[yellow bold]Choose your pit (1-6): [/]")
            
            if not move_input.isdigit():
                console.print("[red]Please enter a number.[/]")
                continue
            
            move = int(move_input)
            pit_index = move - 1
            
            if move < 1 or move > 6 or game.board[pit_index] == 0:
                console.print("[red]Invalid pit. Choose a pit with stones.[/]")
                continue
            
            start_move = time.time()
            game, extra = game.move(pit_index, 0, animate=True, player_name="PLAYER")
            player_time += time.time() - start_move
            
            game.print_board()
            
            if extra:
                console.print("[green bold]Extra turn! Go again![/]")
                time.sleep(1)
            else:
                break

        if game.is_game_over():
            break

        console.print(f"\n[bold red]═══ Move #{move_count} - AI TURN ═══[/]")
        
        while True:
            if game.is_game_over():
                break
            
            console.print("[bold cyan]AI is thinking...[/]")
            
            with Progress() as progress:
                task = progress.add_task("[cyan]Analyzing best move...[/]", total=100)
                ai_start = time.time()
                
                for i in range(85):
                    time.sleep(time_limit * 0.01)
                    progress.update(task, advance=1)
                
                _, ai_move, depth_reached = alpha_beta_timed(game, 1, time_limit, max_depth)
                
                ai_elapsed = time.time() - ai_start
                ai_time += ai_elapsed
                
                for i in range(85, 100):
                    progress.update(task, advance=1)
            
            if ai_move is None:
                console.print("[red]⚠️ AI has no valid moves![/]")
                break
            
            ai_human_index = 13 - ai_move
            
            console.print(f"[bold red]🤖 AI chooses pit {ai_human_index}[/] [dim](depth: {depth_reached}, time: {ai_elapsed:.2f}s)[/]")
            
            game, extra = game.move(ai_move, 1, animate=True, player_name="AI 🤖")
            game.print_board()
            
            if extra:
                console.print("[bold red]🤖 AI gets an extra turn![/]")
                time.sleep(1)
            else:
                break

    game.collect_remaining()
    
    ai_score = game.board[13]
    player_score = game.board[6]
    
    game.print_board()
    
    stats_text = Text()
    stats_text.append(f"Total Moves: {move_count}\n", style="cyan")
    stats_text.append(f"Your Time: {player_time:.2f}s\n", style="yellow")
    stats_text.append(f"AI Time: {ai_time:.2f}s\n", style="red")
    stats_text.append(f"\nYour Score: ", style="bold yellow")
    stats_text.append(f"{player_score} ⚪\n", style="bold white")
    stats_text.append(f"AI Score: ", style="bold red")
    stats_text.append(f"{ai_score} ⚪", style="bold white")
    
    console.print(Panel(stats_text, title="GAME STATISTICS", border_style="cyan"))
    
    if ai_score > player_score:
        console.print(Panel(
            "[red bold]🤖 AI WINS![/]\n"
            f"[dim]Score: {ai_score} - {player_score}[/]",
            title="🏁 GAME OVER",
            border_style="red"
        ))
    elif ai_score < player_score:
        console.print(Panel(
            "[green bold]🎉 YOU WIN![/]\n"
            f"[dim]Score: {player_score} - {ai_score}[/]",
            title="🏁 GAME OVER",
            border_style="green"
        ))
    else:
        console.print(Panel(
            "[cyan bold]IT'S A DRAW![/]\n"
            f"[dim]Score: {player_score} - {ai_score}[/]",
            title="🏁 GAME OVER",
            border_style="cyan"
        ))


if __name__ == "__main__":
    try:
        player_vs_ai()
    except KeyboardInterrupt:
        console.print("\n[yellow]Game interrupted. Thanks for playing![/]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
