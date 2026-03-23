# 🖥️ CPU Scheduling Simulator (SJF & Round Robin)

Dự án mô phỏng các thuật toán lập lịch CPU trong môn học **Hệ điều hành**. Ứng dụng kết hợp hiệu năng xử lý của **C** và giao diện trực quan của **Python (Tkinter/Matplotlib)** để mang lại cái nhìn chi tiết nhất về cách CPU điều phối tiến trình.

---

## 🌟 Tính năng nổi bật

- **Đa dạng thuật toán:**
  - **SJF (Non-Preemptive):** Lập lịch ngắn nhất không dừng.
  - **SRTF (Preemptive SJF):** Lập lịch ngắn nhất có cho phép dừng (chiếm quyền).
  - **Round Robin (RR):** Lập lịch vòng tròn với Time Quantum tùy chỉnh.
- **Mô phỏng động (Step-by-Step):** Biểu đồ Gantt được vẽ chậm rãi (600ms/bước) giúp quan sát rõ quá trình chuyển ngữ cảnh (Context Switch).
- **Thống kê chi tiết:** Tự động tính toán và hiển thị:
  - Thời gian chờ trung bình (Average Waiting Time).
  - Thời gian hoàn thành trung bình (Average Turnaround Time).
  - Thời gian phản hồi trung bình (Average Response Time).
- **UX Tối ưu:** Hỗ trợ phím tắt `Enter` để điều hướng nhanh giữa các ô nhập liệu mà không cần dùng chuột.

---

## 🛠️ Kiến trúc hệ thống

Dự án sử dụng mô hình **Hybrid Programming**:
1. **Core (C Language):** Đóng gói thành `sjf_core.dll`. Chịu trách nhiệm xử lý logic thuật toán và quản lý hàng đợi Ready Queue.
2. **GUI (Python):** Sử dụng thư viện `ctypes` để gọi hàm từ DLL và `matplotlib` để trực quan hóa dữ liệu.

---

## 🚀 Hướng dẫn cài đặt và khởi chạy

### 1. Yêu cầu hệ thống
- Hệ điều hành: **Windows**.
- Trình biên dịch: **GCC** (MinGW).
- Ngôn ngữ: **Python 3.x**.

### 2. Cài đặt thư viện Python
```bash
1. Biên dịch nhân C: gcc -shared -o sjf_core.dll sjf_core.c
2. Cài đặt thư viện: pip install matplotlib
3. Khởi chạy: python sjf_gui.py
4. Tương tác: Nhập ID/Arrival/Burst $\rightarrow$ Nhấn Enter $\rightarrow$ Chọn thuật toán $\rightarrow$ Xem kết quả.


