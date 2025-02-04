import cv2
import numpy as np
import pyautogui
import time
import threading
from pynput import keyboard, mouse

# Disable the fail-safe (not recommended)
pyautogui.FAILSAFE = False

# Flag to control the scanning loop
running = True

def listen_for_exit():
    def on_press(key):
        global running
        try:
            if key.char == 'e':
                running = False
                print("\n[INFO] 'Ctrl + E' pressed. Exiting the scanner...")
        except AttributeError:
            pass

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

# Start the listener thread
listener_thread = threading.Thread(target=listen_for_exit, daemon=True)
listener_thread.start()

# -----------------------------
# Configuration
# -----------------------------

# Define the color range for the target color in HSV
target_color_lower = np.array([40, 70, 70])   # Lower bound of green in HSV
target_color_upper = np.array([80, 255, 255]) # Upper bound of green in HSV

# Set the capture region (left, top, width, height)
capture_region = (0, 0, 1920, 1080)  # Full screen

# Set the mouse movement speed (pixels per second)
movement_speed = 500

# Example boundaries
MIN_X, MIN_Y = 100, 100
MAX_X, MAX_Y = 1820, 980  # Assuming a 1920x1080 screen

# Set the minimum distance (pixels) to move the mouse
min_distance = 10

# -----------------------------
# Helper Functions
# -----------------------------

def move_mouse_to_target(target_x, target_y):
    # Ensure target is within boundaries
    target_x = max(MIN_X, min(target_x, MAX_X))
    target_y = max(MIN_Y, min(target_y, MAX_Y))
    
    current_x, current_y = pyautogui.position()
    distance = np.hypot(target_x - current_x, target_y - current_y)

    if distance < min_distance:
        return  # No need to move

    time_to_move = distance / movement_speed
    pyautogui.moveTo(target_x, target_y, duration=time_to_move, tween=pyautogui.easeInOutQuad)

def process_frame(screenshot):
    """
    Process the captured frame to detect the target color and return the center coordinates.
    """
    # Convert the screenshot to a NumPy array and then to HSV color space
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)

    # Create a mask for the target color range
    mask = cv2.inRange(frame, target_color_lower, target_color_upper)

    # Optional: Apply some morphological operations to remove noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=2)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Find the largest contour (assuming it's the target)
        largest_contour = max(contours, key=cv2.contourArea)

        # Get the bounding rectangle of the largest contour
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Calculate the center of the largest contour
        center_x = x + w // 2
        center_y = y + h // 2

        return mask, (center_x, center_y)
    else:
        return mask, None

# -----------------------------
# Main Scanning Function
# -----------------------------

def scan_screen():
    global running

    # Initialize the screen capture region
    left, top, width, height = capture_region

    while running:
        start_time = time.time()

        # Capture the screen
        screenshot = pyautogui.screenshot(region=capture_region)

        # Process the captured frame
        mask, center = process_frame(screenshot)

        # Move the mouse to the detected center
        if center:
            move_mouse_to_target(center[0] + left, center[1] + top)

        # Display the mask and live feed with detected point
        mask_display = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        # Draw a circle on the detected center
        if center:
            cv2.circle(mask_display, (center[0], center[1]), 10, (0, 0, 255), 2)

        cv2.imshow("Detection Feed", mask_display)

        # Calculate elapsed time and sleep if necessary to control frame rate
        elapsed_time = time.time() - start_time
        sleep_time = max(0.01, 0.05 - elapsed_time)  # Aim for ~20 FPS
        time.sleep(sleep_time)

        # Exit if 'q' is pressed (alternative termination method)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
            break

    cv2.destroyAllWindows()

# -----------------------------
# Entry Point
# -----------------------------

if __name__ == "__main__":
    print("[INFO] Starting the Tool...")
    print("[INFO] Press 'q' at any time to quit.")

    # Start scanning
    scan_screen()

    print("[INFO] Scanner terminated gracefully.")
