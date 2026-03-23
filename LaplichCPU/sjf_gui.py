import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
from ctypes import Structure, c_int, POINTER
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 1. Khai báo cấu trúc trao đổi dữ liệu với C
class GanttSegment(Structure):
    _fields_ = [("id", c_int), ("arrival", c_int), ("burst", c_int), 
                ("remaining", c_int), ("start_time", c_int), ("end_time", c_int)]

# 2. Kết nối thư viện C
try:
    sjf_lib = ctypes.CDLL('./sjf_core.dll')
    # Khai báo kiểu dữ liệu cho hàm Round Robin trong C
    sjf_lib.solve_round_robin.argtypes = [POINTER(c_int), POINTER(c_int), POINTER(c_int), c_int, c_int, POINTER(GanttSegment)]
except Exception as e:
    print(f"Lỗi kết nối DLL: {e}")

class SJF_Simulator_Pro:
    def __init__(self, root):
        self.root = root
        self.root.title("Phần mềm Mô phỏng Lập lịch CPU - Thuyết OS")
        self.root.geometry("1000x850")
        self.processes = []

        # --- KHUNG NHẬP LIỆU ---
        input_frame = tk.LabelFrame(root, text=" 1. Nhập danh sách tiến trình (Sử dụng Enter để chuyển ô) ", padx=15, pady=15, fg="blue", font=("Arial", 10, "bold"))
        input_frame.pack(fill=tk.X, padx=20, pady=10)

        # Labels hướng dẫn
        fields = [("ID Tiến trình:", "Ví dụ: 1, 2..."), ("Thời điểm đến:", "Giây thứ mấy đến"), ("Thời gian chạy:", "Cần bao nhiêu giây")]
        self.entries = []
        
        for i, (label_text, hint) in enumerate(fields):
            sub_frame = tk.Frame(input_frame)
            sub_frame.grid(row=0, column=i, padx=10)
            
            tk.Label(sub_frame, text=label_text, font=("Arial", 9, "bold")).pack()
            ent = tk.Entry(sub_frame, width=15, justify='center', font=("Arial", 10))
            ent.pack()
            tk.Label(sub_frame, text=hint, fg="gray", font=("Arial", 8)).pack()
            
            # Gán sự kiện phím Enter
            ent.bind("<Return>", lambda event, idx=i: self.focus_next(idx))
            self.entries.append(ent)

        # Ô nhập Quantum cho Round Robin
        tk.Label(input_frame, text="Quantum (RR):", font=("Arial", 9, "bold")).grid(row=0, column=3, padx=5)
        self.ent_q = tk.Entry(input_frame, width=8, justify='center')
        self.ent_q.insert(0, "2")
        self.ent_q.grid(row=0, column=4)

        # Nút chức năng nhập
        btn_add = tk.Button(input_frame, text="THÊM +", command=self.add_process, bg="#28a745", fg="white", width=12, font=("Arial", 9, "bold"))
        btn_add.grid(row=0, column=5, padx=20)
        
        tk.Button(input_frame, text="LÀM MỚI", command=self.reset_all, bg="#dc3545", fg="white").grid(row=0, column=6)

        # --- BẢNG DANH SÁCH ---
        self.tree = ttk.Treeview(root, columns=("ID", "Arr", "Burst"), show='headings', height=6)
        self.tree.heading("ID", text="Tiến trình"); self.tree.heading("Arr", text="Thời điểm đến (Arrival)"); self.tree.heading("Burst", text="Thời gian chạy (Burst)")
        self.tree.column("ID", anchor="center"); self.tree.column("Arr", anchor="center"); self.tree.column("Burst", anchor="center")
        self.tree.pack(fill=tk.X, padx=20, pady=5)

        # --- ĐIỀU KHIỂN THUẬT TOÁN ---
        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)
        
        btns = [
            ("SJF KHÔNG DỪNG", "NP", "#ffc107"),
            ("SJF CÓ DỪNG (SRTF)", "P", "#17a2b8"),
            ("ROUND ROBIN", "RR", "#e83e8c")
        ]
        for text, mode, color in btns:
            tk.Button(control_frame, text=text, command=lambda m=mode: self.start_simulation(m), 
                      bg=color, fg="black", font=("Arial", 9, "bold"), padx=10, pady=5).pack(side=tk.LEFT, padx=10)

        # --- KHU VỰC ĐỒ HỌA ---
        self.chart_frame = tk.Frame(root)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        # --- THỐNG KÊ ---
        self.stat_frame = tk.LabelFrame(root, text=" 2. Kết quả Thống kê chi tiết ", padx=15, pady=10, fg="#28a745", font=("Arial", 10, "bold"))
        self.stat_frame.pack(fill=tk.X, padx=20, pady=15)
        self.lbl_stats = tk.Label(self.stat_frame, text="Đang chờ nhập dữ liệu và chạy thuật toán...", font=("Consolas", 10), justify=tk.LEFT)
        self.lbl_stats.pack(side=tk.LEFT)

    def focus_next(self, index):
        if index < 2:
            self.entries[index+1].focus_set()
        else:
            self.add_process()
            self.entries[0].focus_set()

    def add_process(self):
        try:
            pid, arr, bst = int(self.entries[0].get()), int(self.entries[1].get()), int(self.entries[2].get())
            self.processes.append({'id': pid, 'arr': arr, 'burst': bst})
            self.tree.insert("", tk.END, values=(f"P{pid}", arr, bst))
            for e in self.entries: e.delete(0, tk.END)
        except:
            messagebox.showwarning("Nhập liệu", "Vui lòng chỉ nhập số nguyên!")

    def reset_all(self):
        self.processes = []
        for i in self.tree.get_children(): self.tree.delete(i)
        for w in self.chart_frame.winfo_children(): w.destroy()
        self.lbl_stats.config(text="Đã xóa dữ liệu.")

    def start_simulation(self, mode):
        if not self.processes: return
        n = len(self.processes)
        ids = (c_int * n)(*[p['id'] for p in self.processes])
        arrs = (c_int * n)(*[p['arr'] for p in self.processes])
        bursts = (c_int * n)(*[p['burst'] for p in self.processes])
        self.res_arr = (GanttSegment * 500)() 

        if mode == "NP":
            self.num_seg = sjf_lib.solve_sjf_non_preemptive(ids, arrs, bursts, n, self.res_arr)
            t = "SJF Không dừng"
        elif mode == "P":
            self.num_seg = sjf_lib.solve_sjf_preemptive(ids, arrs, bursts, n, self.res_arr)
            t = "SJF Có dừng (SRTF)"
        else:
            q = int(self.ent_q.get())
            self.num_seg = sjf_lib.solve_round_robin(ids, arrs, bursts, n, q, self.res_arr)
            t = f"Round Robin (q={q})"

        self.animate(0, t)

    def animate(self, step, title):
        if step == 0:
            for w in self.chart_frame.winfo_children(): w.destroy()
            self.fig, self.ax = plt.subplots(figsize=(9, 2.5))
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
            self.canvas.get_tk_widget().pack()

        if step < self.num_seg:
            s = self.res_arr[step]
            self.ax.broken_barh([(s.start_time, s.end_time-s.start_time)], (10, 9), facecolors=('tab:blue' if step%2==0 else 'tab:orange'))
            self.ax.text(s.start_time + (s.end_time-s.start_time)/2, 14.5, f"P{s.id}", ha='center', va='center', color='white', weight='bold')
            self.ax.set_title(title); self.ax.set_yticks([]); self.ax.grid(True, axis='x', ls='--', alpha=0.5)
            self.canvas.draw()
            # Tốc độ chạy chậm: 600ms mỗi bước
            self.root.after(600, lambda: self.animate(step + 1, title))
        else:
            self.show_stats()

    def show_stats(self):
        f_times, s_times = {}, {}
        for i in range(self.num_seg):
            seg = self.res_arr[i]
            f_times[seg.id] = seg.end_time
            if seg.id not in s_times: s_times[seg.id] = seg.start_time

        n = len(self.processes)
        tw, tt, tr = 0, 0, 0
        report = "BÁO CÁO KẾT QUẢ CHẠY THUẬT TOÁN:\n" + "-"*50 + "\n"
        
        for p in self.processes:
            tat = f_times[p['id']] - p['arr']
            wait = tat - p['burst']
            res = s_times[p['id']] - p['arr']
            tw += wait; tt += tat; tr += res
            report += f"Tiến trình P{p['id']}: Đợi = {wait}ms | Hoàn thành = {tat}ms | Phản hồi = {res}ms\n"

        report += "-"*50 + f"\n=> TRUNG BÌNH: Chờ: {tw/n:.2f}ms | Hoàn thành: {tt/n:.2f}ms | Phản hồi: {tr/n:.2f}ms"
        self.lbl_stats.config(text=report)

if __name__ == "__main__":
    root = tk.Tk()
    app = SJF_Simulator_Pro(root)
    root.mainloop()