#include <stdio.h>
#include <stdbool.h>

/**
 * banker_core.c
 * Triển khai cả hai thuật toán:
 * 1. Thuật toán Banker (Tránh bế tắc - Avoidance)
 * 2. Thuật toán Nhận diện (Phát hiện bế tắc - Detection)
 */

#define MAX_P 10
#define MAX_R 10

typedef struct {
    int P_count; // Số lượng tiến trình
    int R_count; // Số lượng loại tài nguyên
    int allocation[MAX_P][MAX_R];
    int max[MAX_P][MAX_R];
    int need[MAX_P][MAX_R];
    int request[MAX_P][MAX_R];
    int available[MAX_R];
} SystemState;

/**
 * ---------------------------------------------------------
 * 1. THUẬT TOÁN BANKER (AN TOÀN)
 * Mục tiêu: Tìm chuỗi an toàn dựa trên nhu cầu tối đa (Need)
 * ---------------------------------------------------------
 */
bool bankerSafetyCheck(SystemState state, int safeSeq[]) {
    int work[MAX_R];
    bool finish[MAX_P];
    int count = 0;

    // Khởi tạo Work = Available
    for (int i = 0; i < state.R_count; i++) work[i] = state.available[i];

    // Khởi tạo Finish = false cho tất cả (Banker's assumption)
    for (int i = 0; i < state.P_count; i++) finish[i] = false;

    bool found;
    do {
        found = false;
        for (int i = 0; i < state.P_count; i++) {
            if (!finish[i]) {
                bool canProceed = true;
                for (int j = 0; j < state.R_count; j++) {
                    if (state.need[i][j] > work[j]) {
                        canProceed = false;
                        break;
                    }
                }

                if (canProceed) {
                    for (int j = 0; j < state.R_count; j++) work[j] += state.allocation[i][j];
                    safeSeq[count++] = i;
                    finish[i] = true;
                    found = true;
                }
            }
        }
    } while (found);

    return (count == state.P_count);
}

/**
 * ---------------------------------------------------------
 * 2. THUẬT TOÁN NHẬN DIỆN (DETECTION)
 * Mục tiêu: Phát hiện bế tắc đang xảy ra dựa trên yêu cầu (Request)
 * ---------------------------------------------------------
 */
bool deadlockDetection(SystemState state, int deadlockedProcesses[], int *deadlockCount) {
    int work[MAX_R];
    bool finish[MAX_P];
    *deadlockCount = 0;

    // BƯỚC 1: Khởi tạo
    // (a) Work = Available
    for (int i = 0; i < state.R_count; i++) work[i] = state.available[i];

    // (b) Finish[i] = false nếu Allocation_i != 0, ngược lại true
    for (int i = 0; i < state.P_count; i++) {
        bool hasAllocation = false;
        for (int j = 0; j < state.R_count; j++) {
            if (state.allocation[i][j] > 0) {
                hasAllocation = true;
                break;
            }
        }
        finish[i] = !hasAllocation;
    }

    // BƯỚC 2 & 3: Tìm i sao cho Finish[i] == false và Request_i <= Work
    bool found;
    do {
        found = false;
        for (int i = 0; i < state.P_count; i++) {
            if (!finish[i]) {
                bool canProceed = true;
                for (int j = 0; j < state.R_count; j++) {
                    if (state.request[i][j] > work[j]) {
                        canProceed = false;
                        break;
                    }
                }

                if (canProceed) {
                    // BƯỚC 3: Work = Work + Allocation_i; Finish[i] = true
                    for (int j = 0; j < state.R_count; j++) work[j] += state.allocation[i][j];
                    finish[i] = true;
                    found = true;
                }
            }
        }
    } while (found);

    // BƯỚC 4: Kết luận
    bool isDeadlocked = false;
    for (int i = 0; i < state.P_count; i++) {
        if (!finish[i]) {
            deadlockedProcesses[(*deadlockCount)++] = i;
            isDeadlocked = true;
        }
    }

    return isDeadlocked;
}

/**
 * Hàm hỗ trợ mô phỏng yêu cầu tài nguyên (Banker's Resource-Request)
 */
bool bankerRequestResource(SystemState *state, int p_id, int requestVector[]) {
    // 1. Kiểm tra Request <= Need
    for (int j = 0; j < state->R_count; j++) {
        if (requestVector[j] > state->need[p_id][j]) return false;
    }

    // 2. Kiểm tra Request <= Available
    for (int j = 0; j < state->R_count; j++) {
        if (requestVector[j] > state->available[j]) return false;
    }

    // 3. Giả lập cấp phát
    for (int j = 0; j < state->R_count; j++) {
        state->available[j] -= requestVector[j];
        state->allocation[p_id][j] += requestVector[j];
        state->need[p_id][j] -= requestVector[j];
    }

    int safeSeq[MAX_P];
    if (bankerSafetyCheck(*state, safeSeq)) {
        return true;
    } else {
        // Hoàn tác nếu không an toàn
        for (int j = 0; j < state->R_count; j++) {
            state->available[j] += requestVector[j];
            state->allocation[p_id][j] -= requestVector[j];
            state->need[p_id][j] += requestVector[j];
        }
        return false;
    }
}

int main() {
    printf("Banker Core Logic (Avoidance & Detection) ready.\n");
    return 0;
}