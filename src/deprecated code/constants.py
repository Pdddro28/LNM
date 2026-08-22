from dataclasses import dataclass

# Region Of Interest:


#  x1,y1-----------------
#  |                    |
#  |                    |
#  |                    |
#  -------------------x2,y2   


# --- DATA STRUCTURES ---
@dataclass
class ROI:
    x1: int; y1: int
    x2: int; y2: int

# --- DIRECTION TARGETS AND STEERING CONSTANTS ---
RIGHT = 0
LEFT = 180
CENTER = 90

RED_TARGET = 110 
GREEN_TARGET = 530

# --- VISION COORDINATES AND REGIONS OF INTEREST ---
CENTER_X = int(640 / 2)
CENTER_Y = int(480 / 2) + 30

OPEN_ROI_CENTER = ROI(CENTER_X - 120, CENTER_Y - 14, CENTER_X + 120, 450)
ROI_LINES = ROI(200, 370, 440, 470)

CLOSED_LEFT_ROI = ROI(0, CENTER_Y - 30, int(640 / 3), 480)
CLOSED_RIGHT_ROI = ROI(640 - int(640 / 3), CENTER_Y - 30, 640, 480)
CLOSED_CENTER_ROI = ROI(int(640 / 3), CENTER_Y - 30, 640 - int(640 / 3), 480)
CLOSED_GENERAL_ROI = ROI(0, CENTER_Y - 30, 640, 480)

# --- THRESHOLDS ---
TURN_THRESH = 30000.0
TURN_EXIT_THRESH = 10400.0

# --- LAB COLORSPACE MASKS ---
mask_red = [[0, 153, 140], [131, 198, 171]]
mask_green = [[0, 45, 0], [255, 117, 153]]

mask_blue = [[54, 124, 25], [148, 164, 121]]
mask_blue_test = [[0, 61, 17], [114, 170, 126]]

mask_orange = [[0, 163, 163], [255, 191, 204]]
mask_orange_test = [[35, 135, 86], [175, 160, 177]]

mask_black = [[0, 109, 113], [59, 137, 150]]
mask_black_test = [[0, 58, 17], [108, 169, 137]]
