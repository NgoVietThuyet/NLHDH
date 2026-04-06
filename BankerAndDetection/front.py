import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

class DeadlockSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Mô phỏng Quản lý Bế tắc - OS Simulator")
        self.root.geometry("1000x850")

        self.num_p = 5
        self.num_r = 3
        self.setup_ui()

    def setup_ui(self):
        # Frame cấu hình hệ thống
        config_frame = tk.LabelFrame(self.root, text="Cấu hình hệ thống", padx=10, pady=10)
        config_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(config_frame, text="Số tiến trình (n):").grid(row=0, column=0)
        self.entry_p = tk.Entry(config_frame, width=5)
        self.entry_p.insert(0, str(self.num_p))
        self.entry_p.grid(row=0, column=1, padx=5)

        tk.Label(config_frame, text="Số loại tài nguyên (m):").grid(row=0, column=2)
        self.entry_r = tk.Entry(config_frame, width=5)
        self.entry_r.insert(0, str(self.num_r))
        self.entry_r.grid(row=0, column=3, padx=5)

        tk.Button(config_frame, text="Khởi tạo lại bảng", command=self.init_tables).grid(row=0, column=4, padx=20)

        # Container chứa ma trận chính
        self.tables_container = tk.Frame(self.root)
        self.tables_container.pack(fill="both", expand=True, padx=20)
        self.init_tables()

        # Nút chức năng
        btn_frame = tk.Frame(self.root, pady=20)
        btn_frame.pack()

        tk.Button(btn_frame, text="Chuỗi an toàn (Banker)", bg="#2e7d32", fg="white", 
                  font=('Arial', 10, 'bold'), command=self.run_banker_safety).pack(side="left", padx=10)
        
        tk.Button(btn_frame, text="Yêu cầu tài nguyên (Banker Request)", bg="#f57c00", fg="white", 
                  font=('Arial', 10, 'bold'), command=self.open_banker_request_dialog).pack(side="left", padx=10)
        
        tk.Button(btn_frame, text="Chạy Nhận diện (Detection)", bg="#1565c0", fg="white", 
                  font=('Arial', 10, 'bold'), command=self.run_detection).pack(side="left", padx=10)

        # Hiển thị kết quả
        self.result_label = tk.Label(self.root, text="Trạng thái: Sẵn sàng", font=('Consolas', 11, 'bold'), 
                                     bg="#e0e0e0", relief="sunken", height=6, width=95, pady=10)
        self.result_label.pack(pady=10)

    def init_tables(self):
        for widget in self.tables_container.winfo_children(): widget.destroy()
        try:
            self.num_p = int(self.entry_p.get())
            self.num_r = int(self.entry_r.get())
        except: return

        # Tạo bảng Allocation
        f1 = tk.LabelFrame(self.tables_container, text="Ma trận Allocation (Đang giữ)")
        f1.grid(row=0, column=0, padx=10, pady=5)
        self.alloc_entries = self.create_grid(f1, self.num_p, self.num_r)

        # Tạo bảng Max / Request
        f2 = tk.LabelFrame(self.tables_container, text="Ma trận Max / Request (Nhu cầu tối đa hoặc Yêu cầu hiện tại)")
        f2.grid(row=0, column=1, padx=10, pady=5)
        self.second_grid_entries = self.create_grid(f2, self.num_p, self.num_r)

        # Tạo bảng Available
        f3 = tk.LabelFrame(self.tables_container, text="Vectơ Available (Tài nguyên sẵn có trong kho)")
        f3.grid(row=1, column=0, columnspan=2, pady=15)
        self.avail_entries = self.create_grid(f3, 1, self.num_r)

    def create_grid(self, parent, rows, cols):
        entries = []
        for i in range(rows):
            row_data = []
            for j in range(cols):
                e = tk.Entry(parent, width=6, justify='center')
                e.insert(0, "0")
                e.grid(row=i, column=j, padx=2, pady=2)
                row_data.append(e)
            entries.append(row_data)

        # Bind phím điều hướng
        for i in range(rows):
            for j in range(cols):
                e = entries[i][j]
                e.bind("<Return>", lambda ev, r=i, c=j, g=entries: self.move_focus(ev, r, c, g))
                e.bind("<Up>", lambda ev, r=i, c=j, g=entries: self.move_focus(ev, r, c, g))
                e.bind("<Down>", lambda ev, r=i, c=j, g=entries: self.move_focus(ev, r, c, g))
                e.bind("<Left>", lambda ev, r=i, c=j, g=entries: self.move_focus(ev, r, c, g))
                e.bind("<Right>", lambda ev, r=i, c=j, g=entries: self.move_focus(ev, r, c, g))
        return entries

    def move_focus(self, event, r, c, grid):
        rows, cols = len(grid), len(grid[0])
        if event.keysym in ["Return", "Right"]:
            if c < cols - 1: grid[r][c+1].focus_set()
            elif r < rows - 1: grid[r+1][0].focus_set()
        elif event.keysym == "Left":
            if c > 0: grid[r][c-1].focus_set()
            elif r > 0: grid[r-1][cols-1].focus_set()
        elif event.keysym == "Up" and r > 0: grid[r-1][c].focus_set()
        elif event.keysym == "Down" and r < rows - 1: grid[r+1][c].focus_set()

    def get_data(self):
        alloc = [[int(e.get()) for e in row] for row in self.alloc_entries]
        second = [[int(e.get()) for e in row] for row in self.second_grid_entries]
        avail = [int(e.get()) for e in self.avail_entries[0]]
        return alloc, second, avail

    def run_banker_safety(self):
        try:
            alloc, max_m, avail = self.get_data()
            need = [[max_m[i][j] - alloc[i][j] for j in range(self.num_r)] for i in range(self.num_p)]
            
            for i in range(self.num_p):
                if any(val < 0 for val in need[i]):
                    messagebox.showerror("Lỗi", f"Tiến trình P{i} có Allocation vượt quá Max!")
                    return

            success, seq = self.solve_safety(alloc, need, avail)
            if success:
                self.result_label.config(text=f"[BANKER SAFETY CHECK]\nTrạng thái: AN TOÀN\nChuỗi an toàn tìm được: {' -> '.join(seq)}", fg="#1b5e20")
            else:
                self.result_label.config(text="[BANKER SAFETY CHECK]\nTrạng thái: KHÔNG AN TOÀN\nHệ thống có nguy cơ bế tắc.", fg="#b71c1c")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def open_banker_request_dialog(self):
        """Mở popup xử lý yêu cầu thêm tài nguyên (Banker Request) - Giữ nguyên sau khi chạy"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Yêu cầu tài nguyên (Banker Request)")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="ID Tiến trình (0 đến n-1):", font=('Arial', 10, 'bold')).pack(pady=10)
        p_idx_entry = tk.Entry(dialog, width=10, justify='center')
        p_idx_entry.pack()

        tk.Label(dialog, text=f"Vectơ Yêu cầu thêm ({self.num_r} đơn vị):", font=('Arial', 10, 'bold')).pack(pady=10)
        req_entry = tk.Entry(dialog, width=30, justify='center')
        req_entry.pack()

        # Nhãn kết quả ngay trong popup
        popup_result = tk.Label(dialog, text="Đang đợi nhập dữ liệu...", font=('Consolas', 10), wraplength=450, pady=10)
        popup_result.pack()

        def handle_request():
            try:
                p_idx = int(p_idx_entry.get())
                request = [int(x) for x in req_entry.get().split()]
                if len(request) != self.num_r: raise ValueError
                
                alloc, max_m, avail = self.get_data()
                need = [[max_m[i][j] - alloc[i][j] for j in range(self.num_r)] for i in range(self.num_p)]

                # Logic kiểm tra Banker Request
                if not all(request[j] <= need[p_idx][j] for j in range(self.num_r)):
                    res_msg = f"[TỪ CHỐI]: P{p_idx} đòi quá nhu cầu tối đa (Max)!"
                    popup_result.config(text=res_msg, fg="orange")
                    self.result_label.config(text=f"[BANKER REQUEST] {res_msg}", fg="orange")
                    return

                if not all(request[j] <= avail[j] for j in range(self.num_r)):
                    res_msg = f"[CHỜ ĐỢI]: Kho (Available) không đủ đáp ứng ngay cho P{p_idx}."
                    popup_result.config(text=res_msg, fg="blue")
                    self.result_label.config(text=f"[BANKER REQUEST] {res_msg}", fg="blue")
                    return

                # Giả lập
                new_avail = [avail[j] - request[j] for j in range(self.num_r)]
                new_alloc = [row[:] for row in alloc]
                for j in range(self.num_r): new_alloc[p_idx][j] += request[j]
                new_need = [row[:] for row in need]
                for j in range(self.num_r): new_need[p_idx][j] -= request[j]

                success, seq = self.solve_safety(new_alloc, new_need, new_avail)
                if success:
                    res_msg = f"[CHẤP NHẬN]: Cấp phát thành công cho P{p_idx}.\nHệ thống vẫn an toàn.\nChuỗi: {' -> '.join(seq)}"
                    popup_result.config(text=res_msg, fg="green")
                    self.result_label.config(text=f"[BANKER REQUEST] {res_msg}", fg="green")
                else:
                    res_msg = f"[TỪ CHỐI]: Cấp phát cho P{p_idx} dẫn đến trạng thái không an toàn!"
                    popup_result.config(text=res_msg, fg="red")
                    self.result_label.config(text=f"[BANKER REQUEST] {res_msg}", fg="red")
                
            except Exception:
                messagebox.showerror("Lỗi", "Dữ liệu nhập không hợp lệ.")

        btn_container = tk.Frame(dialog)
        btn_container.pack(pady=20)

        tk.Button(btn_container, text="Kiểm tra", bg="#f57c00", fg="white", 
                  font=('Arial', 10, 'bold'), command=handle_request, width=15).pack(side="left", padx=5)
        
        tk.Button(btn_container, text="Đóng", command=dialog.destroy, width=15).pack(side="left", padx=5)

    def run_detection(self):
        """Chạy thuật toán nhận diện bế tắc (Detection) dựa trên bảng chính"""
        try:
            alloc, req_matrix, avail = self.get_data()
            work = list(avail)
            finish = [False] * self.num_p

            for i in range(self.num_p):
                finish[i] = not any(alloc[i][j] > 0 for j in range(self.num_r))

            while True:
                found = False
                for i in range(self.num_p):
                    if not finish[i] and all(req_matrix[i][j] <= work[j] for j in range(self.num_r)):
                        for j in range(self.num_r): work[j] += alloc[i][j]
                        finish[i] = True
                        found = True
                if not found: break

            deadlocked = [f"P{i}" for i, f in enumerate(finish) if not f]
            if not deadlocked:
                self.result_label.config(text="[DETECTION]\nTrạng thái: KHÔNG CÓ BẾ TẮC", fg="#1b5e20")
            else:
                self.result_label.config(text=f"[DETECTION]\nTrạng thái: PHÁT HIỆN BẾ TẮC!\nKẹt: {', '.join(deadlocked)}", fg="#b71c1c")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def solve_safety(self, alloc, need, avail):
        work = list(avail)
        finish = [False] * len(alloc)
        safe_seq = []
        while len(safe_seq) < len(alloc):
            found = False
            for i in range(len(alloc)):
                if not finish[i] and all(need[i][j] <= work[j] for j in range(len(avail))):
                    for j in range(len(avail)): work[j] += alloc[i][j]
                    finish[i] = True
                    safe_seq.append(f"P{i}")
                    found = True
            if not found: break
        return all(finish), safe_seq

if __name__ == "__main__":
    root = tk.Tk()
    app = DeadlockSimulator(root)
    root.mainloop()