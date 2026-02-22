#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <queue>
#include <stack>
#include <set>
#include <map>
#include <unordered_map>
#include <unordered_set>
#include <cmath>
#include <limits>
#include <cstring>

using namespace std;

// khai báo vị trí ô 
struct Point {
    int r, c;
};

class PikachuSolver {
public:
    vector<vector<int>> a;
    int R, C; // tổng các hàng/cột tính cả viền

    PikachuSolver(const vector<vector<int>>& board) : a(board) {
        R = (int)a.size();
        C = (int)a[0].size();
    }

    // hàm check xem vị trí ô có nằm trong board không
    bool inside(int r, int c) const {
        return r >= 0 && r < R && c >= 0 && c < C;
    }

    // hàm check xem vị trí ô có trống không
    // ô trống = 0 (= ngoài board hoặc đã bị xoá)
    bool emptyCell(int r, int c) const {
        return a[r][c] == 0;
    }

    // hàm check xem quãng đường ở row của hai điểm c1 và c2 có trống không (không tính 2 đầu mút)
    bool clearRow(int r, int c1, int c2) const {
        if (c1 > c2) swap(c1, c2); // đảm bảo thứ tự các cột là tăng dần để tránh cho việc không chạy được vòng for ở dưới
        for (int c = c1 + 1; c <= c2 - 1; c++) {
            if (a[r][c] != 0) return false;
        }
        return true;
    }

    // hàm check xem quãng đường ở col của hai điểm r1 và r2 có trống không (không tính 2 dầu mút)
    bool clearCol(int c, int r1, int r2) const {
        if (r1 > r2) swap(r1, r2); // đảm bảo thứ tự các hàng là tăng dần
        for (int r = r1 + 1; r <= r2 - 1; r++) {
            if (a[r][c] != 0) return false;
        }
        return true;
    }

    // hàm check đường đi thẳng (không rẽ)
    bool checkStraight(Point p1, Point p2) const {
        if (p1.r == p2.r) { // nếu 2 điểm cùng nằm ở một hàng
            return clearRow(p1.r, p1.c, p2.c);
        }
        if (p1.c == p2.c) { // nếu 2 điểm cùng nằm ở một cột 
            return clearCol(p1.c, p1.r, p2.r);
        }
        return false;
    }

    // hàm check 1 góc rẽ: A -> P -> B với P là (r1,c2) (đi ngang xong đi dọc) hoặc (r2,c1) (đi dọc xong đi ngang)
    bool checkL(Point p1, Point p2) const {
        // góc p(r1, c2)
        Point p = {p1.r, p2.c};
        if (inside(p.r, p.c) && emptyCell(p.r, p.c)) {
            if (checkStraight(p1, p) && checkStraight(p, p2)) return true;
        }
        // góc p (r2,c1)
        p = {p2.r, p1.c};
        if (inside(p.r, p.c) && emptyCell(p.r, p.c)) {
            if (checkStraight(p1, p) && checkStraight(p, p2)) return true;
        }
        return false;
    }

    // hàm check 2 góc rẽ: từ điểm p1 tỏa ra 4 phía, duyệt các điểm mid tìm được từ 4 phía đấy
    // tại mỗi điểm mid tìm được, checkL(p, B) để kiểm tra xem mid có nối chữ L tới B không
    bool checkZ(Point p1, Point p2) const {
        // row tăng -> đi xuống
        // col tăng -> đi sang phải
        static int dr[4] = {-1, 1, 0, 0}; // lên xuống trái phải của row
        static int dc[4] = {0, 0, -1, 1}; // lên xuống trái phải của col

        for (int dir = 0; dir < 4; dir++) {
            // r,c là tọa độ liền kề với p1 theo một hướng
            int r = p1.r + dr[dir];
            int c = p1.c + dc[dir];
            while (inside(r, c) && emptyCell(r, c)) {
                Point mid{r, c}; // góc rẽ đầu tiên     
                if (checkL(mid, p2)) return true; // (mid, p2) sẽ là góc rẽ thứ hai
                // tiếp tục mở rộng các phía 
                r += dr[dir]; 
                c += dc[dir];
            }
        }
        return false;
    }

    bool canConnect(Point p1, Point p2) const {
        if (p1.r == p2.r && p1.c == p2.c) return false; // nếu p1 và p2 trùng nhau -> false
        // chỉ xét các loại hình giống nhau (sau này chỗ này sẽ thay thế với selunium)
        int v1 = a[p1.r][p1.c];
        int v2 = a[p2.r][p2.c];
        if (v1 == 0 || v2 == 0 || v1 != v2) return false;

        // Đi từ hàm check dễ nhất trước
        if (checkStraight(p1, p2)) return true;
        if (checkL(p1, p2)) return true;
        if (checkZ(p1, p2)) return true;
        return false;
    }

    // Quét toàn bộ board hiện tại và tìm ra một cặp ô giống nhau có thể nối hợp lệ (thẳng/L/Z)
    // Tích hợp selenium
    bool findAnyMove(Point &outA, Point &outB) const {
        // khởi tạo unorder_map cho việc lưu trữ các cặp ô (có key-value) có cùng loại hình
        unordered_map<int, vector<Point>> pos;

        // gom vị trí tọa độ theo loại hình
        // key = a[r][c]
        // value = tọa độ của loại hình pos[a[r][c]]
        for (int r = 0; r < R; r++) {
            for (int c = 0; c < C; c++) {
                if (a[r][c] != 0) pos[a[r][c]].push_back({r,c});
            }
        }

        // với mỗi loại hình, thứ tất cả các cặp trong nhóm đó
        for (auto &kv : pos) {
            auto &v = kv.second; // danh sách các ô cùng loại
            int k = (int)v.size();
            for (int i = 0; i < k; i++) { // duyệt mọi cặp (i,j) trong danh sách đó, kiểm tra xem có nối được không
                for (int j = i + 1; j < k; j++) {
                    if (canConnect(v[i], v[j])) {
                        outA = v[i];
                        outB = v[j];
                        return true;
                    }
                }
            }
        }
        return false;
    }

    // vòng lặp điều khiển game: trong khi còn tồn tại cặp nối được -> xoá cặp đó đi -> tiếp tục tìm cặp mới trên board đã xoá
    // verbose: in log chi tiết
    int solveBoard(bool verbose = true) {
    int step = 0;
    Point A, B; // output của findAnyMove

    // nếu có tồn tại ít nhất một cặp còn nối được trên map -> tiếp tục chơi
    while (findAnyMove(A, B)) {
        step++;

        if (verbose) {
            // inner coordinates (loại bỏ viền)  
            cout << "Step " << step << ": remove inner ("
                << A.r - 1 << "," << A.c - 1 << ") <-> ("
                << B.r - 1 << "," << B.c - 1 << ")"
                << " value=" << a[A.r][A.c] << "\n";
                    }
        // xóa cặp -> sau đó findAnyMove sẽ chạy trên board mới
        a[A.r][A.c] = 0;
        a[B.r][B.c] = 0;
    }

    if (verbose) {
        cout << "Finished. Total steps = " << step << "\n";
    }

    return step;
}
};

// hàm thêm số 0 vào viền
vector<vector<int>> addBorder(const vector<vector<int>>& inner) {
    int n = (int)inner.size();
    int m = (int)inner[0].size();
    // kích thước bảng là (n+2) x (m+2) với viền bằng không
    vector<vector<int>> b(n + 2, vector<int>(m + 2, 0));
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            b[i + 1][j + 1] = inner[i][j];
    return b;
}

int main() {
    // board giả lập (0 = trống)
    vector<vector<int>> inner = {
        {1, 2, 3, 1},
        {0, 0, 0, 0},
        {4, 2, 3, 4},
        {0, 0, 0, 0}
    };

    auto board = addBorder(inner);
    // khởi tạo solver với board đã thêm viền
    //    r\c  0 1 2 3 4 5
    //    0    0 0 0 0 0 0
    //    1    0 1 2 3 1 0
    //    2    0 0 0 0 0 0
    //    3    0 4 2 3 4 0
    //    4    0 0 0 0 0 0
    //    5    0 0 0 0 0 0
    PikachuSolver solver(board);

    int steps = solver.solveBoard(true);
    cout << "Solved in " << steps << " moves.\n";

    Point A, B;
    if (solver.findAnyMove(A, B)) {
        cout << "Found a move: (" << A.r << "," << A.c << ") <-> (" << B.r << "," << B.c << ")\n";
        cout << "Value = " << board[A.r][A.c] << "\n";
        cout << "Inner coords: (" << A.r-1 << "," << A.c-1 << ") <-> (" << B.r-1 << "," << B.c-1 << ")\n";
    } else {
        cout << "No move found.\n";
    }

    return 0;
}
