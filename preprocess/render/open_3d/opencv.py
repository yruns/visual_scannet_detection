import cv2
import numpy as np

import utils

# 创建一个空白图像
image = np.zeros((500, 500, 3), dtype="uint8")

image = utils.add_order_to_image(
    image=image, order=1, top_left=(100, 100), size=(100, 50)
)

# # 定义颜色块的位置和尺寸
# top_left_corner = (100, 100)  # 矩形左上角坐标
# width, height = 100, 50       # 矩形的宽度和高度
# bottom_right_corner = (top_left_corner[0] + width, top_left_corner[1] + height)
#
# # 定义颜色块的颜色和填充
# rectangle_color = (0, 0, 255)  # BGR格式的红色
#
# # 在图像上画一个矩形作为颜色块
# cv2.rectangle(image, top_left_corner, bottom_right_corner, rectangle_color, -1)  # -1 表示填充矩形
#
# # 添加数字
# font = cv2.FONT_HERSHEY_SIMPLEX
# text = "5"
# font_scale = 1
# font_color = (255, 255, 255)  # 白色
# font_thickness = 2
# text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
# text_x = top_left_corner[0] + (width - text_size[0]) // 2
# text_y = top_left_corner[1] + (height + text_size[1]) // 2
# cv2.putText(image, text, (text_x, text_y), font, font_scale, font_color, font_thickness)

# 显示图像
cv2.imshow('Image with Colored Block and Number', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
