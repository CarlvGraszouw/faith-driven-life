"""Shared board layout for a03 (teacher) + a04 (questioners, drawn on the same board)."""
# Jesus seated on the lowest step of the Royal Stoa, right of centre, facing left (toward the questioners)
JX, JY, JS = 1065.0, 715.0, 1.0
STEP_TOP = JY - 88.0 * JS        # 627: top of the lowest step (his seat)
STEP_X0 = 972.0                  # left end of the step
STEP2_TOP = 566.0                # upper step (stylobate) front face top
STEP2_X0 = 1052.0
COLS = (1272.0, 1452.0)          # Royal Stoa columns on the stylobate (hatch only)
COL_W = 36.0
COL_TOP = 128.0
# listeners
WOMAN = (1236.0, 730.0, 0.98)    # standing to his right, in front of the step, facing left
ELDER = (1398.0, 724.0, 1.0)     # old man with a staff, standing behind her, facing left
FLOOR_Y = 715.0
# text "Taxes to Caesar?" at frame (960,190) size 96 -> keep art x 400-1200, y 100-270 clear
TEXT_BAND = (400.0, 100.0, 1200.0, 270.0)
