# # import cv2
# # import numpy as np
# #
# #
# # def warp_perspective(image, vertical_warp, horizontal_warp):
# #     src_height, src_width = image.shape[:2]
# #
# #     dst_top_left = np.float32([0, 0])
# #     dst_top_right = np.float32([0, src_width])
# #     dst_bottom_left = np.float32([0, src_height])
# #     dst_bottom_right = np.float32([src_height, src_width])
# #
# #     mid_y = src_height // 2
# #     mid_x = src_width // 2
# #     if vertical_warp > 0:
# #         dst_top_right[1] = mid_y - mid_y * vertical_warp
# #         dst_bottom_right[1] = mid_y + mid_y * vertical_warp
# #     else:
# #         dst_top_left[1] = mid_y - mid_y * vertical_warp
# #         dst_bottom_left[1] = mid_y + mid_y * vertical_warp
# #
# #     if horizontal_warp > 0:
# #         dst_top_right[0] = mid_x + mid_x * horizontal_warp
# #         dst_top_left[0] = mid_x - mid_x * horizontal_warp
# #     else:
# #         dst_bottom_left[0] = mid_x - mid_x * horizontal_warp
# #         dst_bottom_right[0] = mid_x + mid_x * horizontal_warp
# #
# #     # Define corner points (adjust based on your image)
# #     src_top_left = np.float32([100, 50])  # Adjust these values as needed
# #     src_top_right = np.float32([300, 70])
# #     src_bottom_left = np.float32([50, 250])
# #     src_bottom_right = np.float32([400, 300])
# #
# #     # # Define destination points (adjust for desired warping)
# #     # dst_top_left = np.float32([100, 20])  # Adjust Y position if needed
# #     # dst_top_right = np.float32([500, 20])  # Stretch right side more by increasing X
# #     # dst_bottom_left = np.float32([50, 350])  # Stretch left side more by decreasing X slightly
# #     # dst_bottom_right = np.float32([550, 350])  # Increase X to stretch further
# #
# #     # Calculate perspective transform
# #     src_pts = np.float32([src_top_left, src_top_right, src_bottom_left, src_bottom_right])
# #     dst_pts = np.float32([dst_top_left, dst_top_right, dst_bottom_left, dst_bottom_right])
# #     M = cv2.getPerspectiveTransform(src_pts, dst_pts)
# #
# #     # Warp the image
# #     warped_image = cv2.warpPerspective(image, M, dsize=(image.shape[1], image.shape[1]))
# #
# #     # Display or save the warped image
# #     cv2.imshow("Original Image", image)
# #     cv2.imshow("Warped Image", warped_image)
# #     cv2.waitKey(0)
# #     cv2.destroyAllWindows()
# #
# #     return warped_image
# #
# #
# # # Replace with your image path
# # image = cv2.imread("images/image 2.jpg")
# # warped = warp_perspective(image, 1, 1)
# # # Optionally save the warped image
# # # cv2.imsave("warped_asymmetric.jpg", warped_image)
# # # cv2.waitKey(0)
#
#
# import cv2
# import numpy as np
#
# def warp_perspective(image, vertical_warp, horizontal_warp):
#     height, width = image.shape[:2]
#
#     # Define destination points based on warping
#     mid_y = height // 2
#     mid_x = width // 2
#     dst_top_left = np.float32([0, 0])
#     dst_top_right = np.float32([0, width])
#     dst_bottom_left = np.float32([0, height])
#     dst_bottom_right = np.float32([height, width])
#
#     if vertical_warp > 0:
#         dst_top_right[1] = mid_y - mid_y * vertical_warp
#         dst_bottom_right[1] = mid_y + mid_y * vertical_warp
#     else:
#         dst_top_left[1] = mid_y - mid_y * vertical_warp
#         dst_bottom_left[1] = mid_y + mid_y * vertical_warp
#
#     if horizontal_warp > 0:
#         dst_top_right[0] = mid_x + mid_x * horizontal_warp
#         dst_top_left[0] = mid_x - mid_x * horizontal_warp
#     else:
#         dst_bottom_left[0] = mid_x - mid_x * horizontal_warp
#         dst_bottom_right[0] = mid_x + mid_x * horizontal_warp
#
#     # Define source points (corners of the original image)
#     # src_pts = np.float32([[100, 50], [300, 70], [50, 250], [400, 300]])
#     src_pts = np.float32([[0, height], [width, ], []])
#
#     # Define destination points (adjusted for desired warping)
#     dst_pts = np.float32([dst_top_left, dst_top_right, dst_bottom_left, dst_bottom_right])
#
#     # Calculate perspective transform matrix
#     M = cv2.getPerspectiveTransform(src_pts, dst_pts)
#
#     # Warp the image
#     warped_image = cv2.warpPerspective(image, M, (width, height))
#
#     # Display or save the warped image
#     cv2.imshow("Original Image", image)
#     cv2.imshow("Warped Image", warped_image)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
#
#     return warped_image
#
# # Replace with your image path
# image = cv2.imread("images/image 2.jpg")
# warped = warp_perspective(image, 1, 1)
# # Optionally save the warped image
# # cv2.imwrite("warped_asymmetric.jpg", warped)
# # cv2.waitKey(0)


import cv2
import numpy as np


def warp_perspective(image, vertical_warp, horizontal_warp):
    height, width = image.shape[:2]

    # Define source points (corners of the input image)
    src_top_left = [0, 0]
    src_top_right = [width, 0]
    src_bottom_right = [width, height]
    src_bottom_left = [0, height]

    src_pts = np.float32([src_top_left, src_top_right, src_bottom_right, src_bottom_left])

    # Define destination points based on warping
    mid_y = height // 2
    mid_x = width // 2
    dst_top_left = np.float32([0, 0])
    dst_top_right = np.float32([width, 0])
    dst_bottom_right = np.float32([width, height])
    dst_bottom_left = np.float32([0, height])

    if vertical_warp > 0:
        dst_top_right[1] = mid_y - mid_y * vertical_warp
        dst_bottom_right[1] = mid_y + mid_y * vertical_warp
    else:
        dst_top_left[1] = mid_y - abs(mid_y * vertical_warp)
        dst_bottom_left[1] = mid_y + abs(mid_y * vertical_warp)

    if horizontal_warp > 0:
        dst_top_right[0] = mid_x + mid_x * horizontal_warp
        dst_top_left[0] = mid_x - mid_x * horizontal_warp
    else:
        dst_bottom_right[0] = mid_x + mid_x * abs(horizontal_warp)
        dst_bottom_left[0] = mid_x - mid_x * abs(horizontal_warp)

    print(src_top_left, src_top_right, src_bottom_right, src_bottom_left)
    print(dst_top_left, dst_top_right, dst_bottom_right, dst_bottom_left)

    # Define destination points (adjusted for desired warping)
    dst_pts = np.float32([dst_top_left, dst_top_right, dst_bottom_right, dst_bottom_left])

    # Calculate perspective transform matrix
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)

    # Warp the image
    warped_image = cv2.warpPerspective(image, M, (width, height))

    # Display or save the warped image
    cv2.imshow("Original Image", image)
    cv2.imshow("Warped Image", warped_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return warped_image


# Replace with your image path
image = cv2.imread("images/image 2.jpg")
warped = warp_perspective(image, -0.5, 1)
# Optionally save the warped image
# cv2.imwrite("warped_asymmetric.jpg", warped)
# cv2.waitKey(0)
