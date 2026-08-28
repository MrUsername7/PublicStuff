import _thread
import time
import machine
import sys
from Bit import begin, display

# Shared state
frame_counter = 0
fps_to_display = 0
running = True

begin()


def report_loop():
    """Calculates FPS every second."""
    global frame_counter, fps_to_display
    while running:
        time.sleep(1)
        fps_to_display = frame_counter
        frame_counter = 0


def frequency_input_loop():
    """Listens for user input to set clock speed."""
    global running
    print("\n--- Frequency Control Active ---")
    print("Enter frequency in MHz (e.g., 80, 160, 240):")
    while running:
        try:
            # sys.stdin.readline is safer for threads than input()
            line = sys.stdin.readline()
            if line:
                mhz = int(line.strip())
                new_freq = mhz * 1_000_000
                machine.freq(new_freq)
                print(f"Frequency set to: {machine.freq() // 1_000_000} MHz")
        except Exception as e:
            print(f"Invalid input: {e}")


def run_bench():
    """Main rendering loop."""
    global frame_counter
    # Local references for speed
    d_fill = display.fill
    d_text = display.text
    d_commit = display.commit

    print("Starting FPS benchmark...")
    while running:
        d_fill(0)
        d_text("FPS Benchmark", 0, 0, 65535)
        # Using string concatenation/formatting
        d_text(str(fps_to_display) + ' fps', 0, 8, 65535)
        d_commit()
        frame_counter += 1


# Start threads
_thread.start_new_thread(report_loop, ())
_thread.start_new_thread(frequency_input_loop, ())

try:
    run_bench()
except KeyboardInterrupt:
    running = False
    print("\nBenchmark stopped.")