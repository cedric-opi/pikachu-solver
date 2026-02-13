class Point:
    def __init__(self, r, c):
        self.r = r
        self.c = c

    def __repr__(self):
        return f"({self.r}, {self.c})"

class PikachuSolver:
    def __init__(self, board):
        # board ở đây nên là ma trận đã được add_border
        self.a = board
        self.R = len(board)
        self.C = len(board[0])

    def inside(self, r, c):
        return 0 <= r < self.R and 0 <= c < self.C

    def empty_cell(self, r, c):
        return self.a[r][c] == 0

    def clear_row(self, r, c1, c2):
        start, end = min(c1, c2), max(c1, c2)
        for c in range(start + 1, end):
            if self.a[r][c] != 0:
                return False
        return True

    def clear_col(self, c, r1, r2):
        start, end = min(r1, r2), max(r1, r2)
        for r in range(start + 1, end):
            if self.a[r][c] != 0:
                return False
        return True

    def check_straight(self, p1, p2):
        if p1.r == p2.r:
            return self.clear_row(p1.r, p1.c, p2.c)
        if p1.c == p2.c:
            return self.clear_col(p1.c, p1.r, p2.r)
        return False

    def check_L(self, p1, p2):
        # Điểm góc thứ nhất (r1, c2)
        p = Point(p1.r, p2.c)
        if self.inside(p.r, p.c) and self.empty_cell(p.r, p.c):
            if self.check_straight(p1, p) and self.check_straight(p, p2):
                return True
        # Điểm góc thứ hai (r2, c1)
        p = Point(p2.r, p1.c)
        if self.inside(p.r, p.c) and self.empty_cell(p.r, p.c):
            if self.check_straight(p1, p) and self.check_straight(p, p2):
                return True
        return False

    def check_Z(self, p1, p2):
        dr = [-1, 1, 0, 0]
        dc = [0, 0, -1, 1]
        for i in range(4):
            r, c = p1.r + dr[i], p1.c + dc[i]
            while self.inside(r, c) and self.empty_cell(r, c):
                mid = Point(r, c)
                if self.check_L(mid, p2):
                    return True
                r += dr[i]
                c += dc[i]
        return False

    def can_connect(self, p1, p2):
        if p1.r == p2.r and p1.c == p2.c:
            return False
        v1 = self.a[p1.r][p1.c]
        v2 = self.a[p2.r][p2.c]
        if v1 == 0 or v2 == 0 or v1 != v2:
            return False

        if self.check_straight(p1, p2): return True
        if self.check_L(p1, p2): return True
        if self.check_Z(p1, p2): return True
        return False

    def find_any_move(self):
        # Gom các vị trí có cùng loại hình
        positions = {}
        for r in range(self.R):
            for c in range(self.C):
                val = self.a[r][c]
                if val != 0:
                    if val not in positions:
                        positions[val] = []
                    positions[val].append(Point(r, c))

        # Thử tìm cặp nối được
        for val in positions:
            pts = positions[val]
            for i in range(len(pts)):
                for j in range(i + 1, len(pts)):
                    if self.can_connect(pts[i], pts[j]):
                        return pts[i], pts[j]
        return None

def add_border(inner_matrix):
    rows = len(inner_matrix)
    cols = len(inner_matrix[0])
    # Tạo bảng mới (n+2)x(m+2) toàn số 0
    new_board = [[0 for _ in range(cols + 2)] for _ in range(rows + 2)]
    for r in range(rows):
        for c in range(cols):
            new_board[r + 1][c + 1] = inner_matrix[r][c]
    return new_board