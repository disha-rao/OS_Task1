"""
Matrix Multiplication - Threads + TensorFlow + Live Animation
-----------------------------------------------------------------
This does the same 100x100 multiplication as matrix_multiplication_final.py
(thread pool + TensorFlow), but also keeps track of the actual order in
which threads finish each cell. Once the real computation is done, that
recorded order is played back as an animation - so what you see moving
on screen is genuinely what happened during execution, not something
scripted to look nice.

Left panel  -> Matrix A, with a moving marker showing the row currently in use
Middle panel -> Matrix B, with a moving marker showing the column currently in use
Right panel -> Matrix C (the result), filling in live with real computed values
"""

import time
import os
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

MATRIX_SIZE = 100


class ExecutionRecorder:
    """Keeps a thread-safe record of the order cells were actually
    completed in, so the animation can replay real execution."""

    def __init__(self):
        self._log = deque()
        self._lock = threading.Lock()

    def record(self, row_index, col_index):
        with self._lock:
            self._log.append((row_index, col_index))

    def as_list(self):
        return list(self._log)


class CellComputer:
    def __init__(self, matrix_a, matrix_b, result_matrix, recorder):
        self.matrix_a = matrix_a
        self.matrix_b = matrix_b
        self.result_matrix = result_matrix
        self.recorder = recorder

    def __call__(self, position):
        row_index, col_index = position
        row_vector = self.matrix_a[row_index, :]
        col_vector = self.matrix_b[:, col_index]
        dot_product = tf.tensordot(row_vector, col_vector, axes=1)
        self.result_matrix[row_index][col_index] = int(dot_product.numpy())
        self.recorder.record(row_index, col_index)


def build_matrix(size):
    return tf.random.uniform((size, size), minval=1, maxval=20, dtype=tf.int32)


def run_computation():
    matrix_x = build_matrix(MATRIX_SIZE)
    matrix_y = build_matrix(MATRIX_SIZE)
    result_matrix = [[0] * MATRIX_SIZE for _ in range(MATRIX_SIZE)]
    recorder = ExecutionRecorder()

    compute_cell = CellComputer(matrix_x, matrix_y, result_matrix, recorder)
    all_positions = [(r, c) for r in range(MATRIX_SIZE) for c in range(MATRIX_SIZE)]
    thread_count = os.cpu_count() or 4

    print(f"Running the real multiplication first, using {thread_count} threads...")
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        pending = [executor.submit(compute_cell, pos) for pos in all_positions]
        for future in as_completed(pending):
            future.result()
    end_time = time.time()

    print("Computation complete. The Time taken:", round((end_time - start_time) * 1000, 2), "ms")
    print("Sample of the result (top-left 3x3):")
    for row in result_matrix[:3]:
        print(row[:3])

    return matrix_x, matrix_y, result_matrix, recorder.as_list()


def play_animation(matrix_x, matrix_y, result_matrix, execution_log):
    matrix_x_display = matrix_x.numpy()
    matrix_y_display = matrix_y.numpy()
    matrix_c_display = np.full((MATRIX_SIZE, MATRIX_SIZE), np.nan)

    fig, (panel_x, panel_y, panel_c) = plt.subplots(1, 3, figsize=(15, 5.5))

    panel_x.imshow(matrix_x_display, cmap='Blues', vmin=1, vmax=20)
    panel_x.set_title("Matrix A")
    panel_x.set_xticks([]); panel_x.set_yticks([])

    panel_y.imshow(matrix_y_display, cmap='Greens', vmin=1, vmax=20)
    panel_y.set_title("Matrix B")
    panel_y.set_xticks([]); panel_y.set_yticks([])

    row_marker = plt.Rectangle((-0.5, -0.5), MATRIX_SIZE, 1, fill=False, edgecolor='crimson', linewidth=2)
    col_marker = plt.Rectangle((-0.5, -0.5), 1, MATRIX_SIZE, fill=False, edgecolor='crimson', linewidth=2)
    panel_x.add_patch(row_marker)
    panel_y.add_patch(col_marker)

    c_min = min(min(r) for r in result_matrix)
    c_max = max(max(r) for r in result_matrix)
    c_image = panel_c.imshow(matrix_c_display, cmap='Oranges', vmin=c_min, vmax=c_max)
    panel_c.set_title("Matrix C (building live)")
    panel_c.set_xticks([]); panel_c.set_yticks([])

    fig.suptitle("The Matrix Multiplication in Action (100x100, real thread + TensorFlow run)",
                 fontsize=13, fontweight='bold')
    progress_label = fig.text(0.5, 0.02, "", ha="center", fontsize=11)

    steps_per_frame = 25
    frame_total = (len(execution_log) // steps_per_frame) + 1
    position_tracker = {"row": 0, "col": 0}

    def animate(frame_num):
        begin = frame_num * steps_per_frame
        finish = min(begin + steps_per_frame, len(execution_log))

        for i in range(begin, finish):
            r, c = execution_log[i]
            matrix_c_display[r][c] = result_matrix[r][c]
            position_tracker["row"], position_tracker["col"] = r, c

        c_image.set_data(matrix_c_display)
        row_marker.set_xy((-0.5, position_tracker["row"] - 0.5))
        col_marker.set_xy((position_tracker["col"] - 0.5, -0.5))
        progress_label.set_text(
            f"Progress: {finish}/{len(execution_log)} cells done   |   "
            f"Working on C[{position_tracker['row']}][{position_tracker['col']}]"
        )
        return [c_image, row_marker, col_marker, progress_label]

    anim = FuncAnimation(fig, animate, frames=frame_total, interval=40, repeat=False)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    x, y, result, log = run_computation()
    play_animation(x, y, result, log)
