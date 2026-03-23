#include <stdio.h>
#include <stdbool.h>

// Cấu trúc để trao đổi dữ liệu với Python
typedef struct {
    int id;
    int arrival;
    int burst;
    int remaining;
    int start_time;
    int end_time;
} GanttSegment;

// 1. SJF KHÔNG CHO PHÉP DỪNG (Non-Preemptive)
__declspec(dllexport) int solve_sjf_non_preemptive(int ids[], int arrivals[], int bursts[], int n, GanttSegment result[]) {
    int curr_time = 0, completed = 0, count = 0;
    bool is_done[100] = {false};

    while (completed < n) {
        int idx = -1, min_b = 1e9;
        for (int i = 0; i < n; i++) {
            if (arrivals[i] <= curr_time && !is_done[i] && bursts[i] < min_b) {
                min_b = bursts[i];
                idx = i;
            }
        }

        if (idx != -1) {
            result[count].id = ids[idx];
            result[count].start_time = curr_time;
            curr_time += bursts[idx];
            result[count].end_time = curr_time;
            is_done[idx] = true;
            completed++;
            count++;
        } else curr_time++;
    }
    return count;
}

// 2. SJF CHO PHÉP DỪNG (Preemptive - SRTF)
__declspec(dllexport) int solve_sjf_preemptive(int ids[], int arrivals[], int bursts[], int n, GanttSegment result[]) {
    int remaining[100];
    for (int i = 0; i < n; i++) remaining[i] = bursts[i];

    int curr_time = 0, completed = 0, count = 0, last_id = -1;

    while (completed < n) {
        int idx = -1, min_r = 1e9;
        for (int i = 0; i < n; i++) {
            if (arrivals[i] <= curr_time && remaining[i] > 0 && remaining[i] < min_r) {
                min_r = remaining[i];
                idx = i;
            }
        }

        if (idx != -1) {
            if (last_id != ids[idx]) {
                if (count > 0) result[count-1].end_time = curr_time;
                result[count].id = ids[idx];
                result[count].start_time = curr_time;
                count++;
            }
            remaining[idx]--;
            curr_time++;
            last_id = ids[idx];
            if (remaining[idx] == 0) {
                completed++;
                result[count-1].end_time = curr_time;
                last_id = -1;
            }
        } else curr_time++;
    }
    return count;
}

// 3. THUẬT TOÁN ROUND ROBIN (RR)
__declspec(dllexport) int solve_round_robin(int ids[], int arrivals[], int bursts[], int n, int quantum, GanttSegment result[]) {
    int remaining[100];
    for (int i = 0; i < n; i++) remaining[i] = bursts[i];

    int curr_time = 0, completed = 0, count = 0;
    int queue[500], head = 0, tail = 0;
    bool in_queue[100] = {false};

    // Tìm tiến trình đầu tiên đến tại thời điểm 0
    for (int i = 0; i < n; i++) {
        if (arrivals[i] <= curr_time) {
            queue[tail++] = i;
            in_queue[i] = true;
        }
    }

    while (completed < n) {
        if (head == tail) { // Nếu hàng đợi rỗng, tăng thời gian
            curr_time++;
            for (int i = 0; i < n; i++) {
                if (arrivals[i] <= curr_time && !in_queue[i] && remaining[i] > 0) {
                    queue[tail++] = i;
                    in_queue[i] = true;
                }
            }
            continue;
        }

        int idx = queue[head++];
        int execute_time = (remaining[idx] > quantum) ? quantum : remaining[idx];

        // Ghi nhận mốc thời gian vào Gantt
        result[count].id = ids[idx];
        result[count].start_time = curr_time;
        curr_time += execute_time;
        result[count].end_time = curr_time;
        remaining[idx] -= execute_time;
        count++;

        // Kiểm tra xem có tiến trình nào mới đến trong lúc P đang chạy không
        for (int i = 0; i < n; i++) {
            if (arrivals[i] <= curr_time && !in_queue[i] && remaining[i] > 0) {
                queue[tail++] = i;
                in_queue[i] = true;
            }
        }

        if (remaining[idx] > 0) {
            queue[tail++] = idx; // Nếu chưa xong thì quay lại cuối hàng đợi
        } else {
            completed++;
        }
    }
    return count;
}