from PIL import Image, ImageDraw
import numpy as np
import cv2


def add_padding(image, up=0, down=0, left=0, right=0):
    """
    Add transparent padding to the input image.

    Args:
    image (PIL.Image.Image): Input image.
    up (int): Padding pixels to add to the top (upper). Default is 0.
    down (int): Padding pixels to add to the bottom (lower). Default is 0.
    left (int): Padding pixels to add to the left. Default is 0.
    right (int): Padding pixels to add to the right. Default is 0.

    Returns:
    PIL.Image.Image: Image with added transparent padding.
    """
    # Get input image dimensions
    width, height = image.size

    # Calculate new dimensions with padding
    new_width = width + left + right
    new_height = height + up + down

    # Create a new blank image with the new dimensions and fill it with transparent pixels
    padded_image = Image.new('RGBA', (new_width, new_height), color=(0, 0, 0, 0))

    # Paste the original image onto the padded image with the specified offsets
    padded_image.paste(image, (left, up))

    return padded_image


def shear_image(warped_image_pil, shear_horizontal_angle=0, shear_vertical_angle=0):
    """
    Shears the image horizontally and/or vertically based on the provided angles.

    Args:
    image_path (str): Path to the input image file.
    shear_horizontal_angle (float): Horizontal shear angle in degrees. Default is 0.
    shear_vertical_angle (float): Vertical shear angle in degrees. Default is 0.

    Returns:
    PIL.Image.Image: Skewed image.
    """
    # # Open the image
    # image_pil = Image.open(image_path)
    # Calculate new image dimensions
    width, height = warped_image_pil.size

    # Convert angles to radians
    shear_horizontal_radians = np.radians(shear_horizontal_angle)
    shear_vertical_radians = np.radians(shear_vertical_angle)

    up_pad, down_pad, left_pad, right_pad = 0, 0, 0, 0

    h_pad = abs(int(height * np.tan(shear_horizontal_radians)))
    v_pad = abs(int(width * np.tan(shear_vertical_radians)))

    if shear_vertical_angle > 0:
        up_pad = v_pad
    else:
        down_pad = v_pad

    if shear_horizontal_angle < 0:
        right_pad = h_pad
    else:
        left_pad = h_pad

    warped_image_pil = add_padding(warped_image_pil, up=up_pad, down=down_pad, left=left_pad, right=right_pad)

    new_width, new_height = width + h_pad, height + v_pad

    # Define the transformation matrix
    shear_matrix = (1, np.tan(shear_horizontal_radians), 0,
                    np.tan(shear_vertical_radians), 1, 0)

    # Shear the image
    skewed_image = warped_image_pil.transform((new_width, new_height), Image.AFFINE, shear_matrix,
                                              resample=Image.BICUBIC)

    return skewed_image


def warp_perspective(_image, vertical_warp, horizontal_warp):
    height, width = _image.shape[:2]

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

    # print(src_top_left, src_top_right, src_bottom_right, src_bottom_left)
    # print(dst_top_left, dst_top_right, dst_bottom_right, dst_bottom_left)

    # Define destination points (adjusted for desired warping)
    dst_pts = np.float32([dst_top_left, dst_top_right, dst_bottom_right, dst_bottom_left])

    # Calculate perspective transform matrix
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)

    # Warp the image
    _warped_image = cv2.warpPerspective(_image, M, (width, height))

    # Display or save the warped image
    # cv2.imshow("Original Image", _image)
    # cv2.imshow("Warped Image", warped_image)
    # cv2.waitKey(0)
    cv2.destroyAllWindows()

    _warped_image = Image.fromarray(_warped_image)
    print(_warped_image.size)
    draw = ImageDraw.Draw(_warped_image, "RGBA")
    for i, start_point in enumerate(dst_pts.tolist()):
        if i == len(dst_pts.tolist()) - 1:
            end_point = dst_pts.tolist()[0]
        else:
            end_point = dst_pts.tolist()[i + 1]
        print(start_point, end_point)
        # draw.line()
        _warped_image = draw_line(_warped_image, start_point, end_point)

    return _warped_image


def draw_line(image, start_point, end_point, line_color=(0, 0, 255), thickness=2):
    """
    Draw a line on the image.

    Args:
    image (PIL.Image.Image): Input image.
    start_point (tuple): Tuple containing the coordinates of the start point (x, y).
    end_point (tuple): Tuple containing the coordinates of the end point (x, y).
    line_color (tuple): Tuple containing the RGB values of the line color. Default is red (255, 0, 0).
    thickness (int): Thickness of the line. Default is 1.

    Returns:
    PIL.Image.Image: Image with the drawn line.
    """
    # Create a draw object
    draw = ImageDraw.Draw(image)

    # Draw the line on the image
    draw.line([*start_point, *end_point], fill=line_color, width=thickness)

    return image


def shear_and_warp(image_path, shear_horizontal_angle, shear_vertical_angle, vertical_warp, horizontal_warp):
    image_arr = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
    height, width = image_arr.shape[:2]

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

    # Convert angles to radians
    shear_horizontal_radians = np.radians(shear_horizontal_angle)
    shear_vertical_radians = np.radians(shear_vertical_angle)

    up_pad, down_pad, left_pad, right_pad = 0, 0, 0, 0

    h_pad = abs(int(height * np.tan(shear_horizontal_radians)))
    v_pad = abs(int(width * np.tan(shear_vertical_radians)))

    if shear_vertical_angle > 0:
        up_pad = v_pad
        dst_top_left[1] += v_pad
        dst_bottom_left[1] += v_pad
    else:
        down_pad = v_pad
        dst_top_right[1] += v_pad
        dst_bottom_right[1] += v_pad

    if shear_horizontal_angle > 0:
        left_pad = h_pad
        dst_top_right[0] += h_pad
        dst_top_left[0] += h_pad
    else:
        right_pad = h_pad
        dst_bottom_right[0] += h_pad
        dst_bottom_left[0] += h_pad

    image_pil = add_padding(Image.fromarray(image_arr), up=up_pad, down=down_pad, left=left_pad, right=right_pad)

    # Define source points (corners of the input image)
    src_top_left = [left_pad, up_pad]
    src_top_right = [width + left_pad, up_pad]
    src_bottom_right = [width + left_pad, height + up_pad]
    src_bottom_left = [left_pad, height + up_pad]

    src_pts = np.float32([src_top_left, src_top_right, src_bottom_right, src_bottom_left])

    new_width, new_height = width + h_pad, height + v_pad

    # Define destination points (adjusted for desired warping)
    points = [dst_top_left, dst_top_right, dst_bottom_right, dst_bottom_left]

    # Calculate perspective transform matrix
    transform_matrix = cv2.getPerspectiveTransform(src_pts, np.array([np.float32([x, y]) for x, y in points]))

    # Warp the image
    warped_image_arr = cv2.warpPerspective(np.array(image_pil), transform_matrix, (new_width, new_height))

    warped_image_pil = Image.fromarray(warped_image_arr)

    # for i, start_point in enumerate(points):
    #     if i == len(points) - 1:
    #         end_point = points[0]
    #     else:
    #         end_point = points[i + 1]
    #     warped_image_pil = draw_line(warped_image_pil, start_point, end_point)
    return warped_image_pil, points


# Example usage:
input_image_path = 'images/image 1.jpg'

my_image, seg = shear_and_warp(input_image_path, -20, -20, 0.9, 1)

# Display the original and sheared images
my_image.show()
