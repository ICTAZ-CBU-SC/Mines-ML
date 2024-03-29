import cv2
import numpy as np
from PIL import Image, ImageEnhance


def overlay_images(_background_image, _overlay_image, x=0.0, y=0.0, seg_points=None):
    unedited_overlay = _overlay_image.copy()

    # If background image doesn't have an alpha channel, convert it to RGBA
    if _background_image.mode != 'RGBA':
        _background_image = _background_image.convert('RGBA')

    # If overlay image doesn't have an alpha channel, convert it to RGBA
    if _overlay_image.mode != 'RGBA':
        _overlay_image = _overlay_image.convert('RGBA')

    # Composite the images
    if _overlay_image.width > _background_image.width or _overlay_image.height > _background_image.height:
        raise RuntimeError("Overlay is larger than background")

    x_offset = int(x * (_background_image.width - _overlay_image.width))
    y_offset = int(y * (_background_image.height - _overlay_image.height))
    _overlay_image = add_padding(_overlay_image, left=x_offset, up=y_offset)

    width_pad = max([0, _background_image.width - _overlay_image.width])
    height_pad = max([0, _background_image.height - _overlay_image.height])
    _overlay_image = add_padding(_overlay_image, down=height_pad, right=width_pad)
    result = Image.alpha_composite(_background_image, _overlay_image)

    new_seg_points = []
    if seg_points is not None:
        for x, y in seg_points:
            # abs_x = x * unedited_overlay.width + x_offset
            # abs_x = y * unedited_overlay.height + y_offset
            new_x = (x * unedited_overlay.width + x_offset) / _background_image.width
            new_y = (y * unedited_overlay.height + y_offset) / _background_image.height
            new_seg_points.append((new_x, new_y))

    return result, new_seg_points


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


def shear_and_warp(image_path, shear_horizontal_angle, shear_vertical_angle, vertical_warp, horizontal_warp):
    # image_arr = cv2.imread(image_path)
    # image_arr = cv2.cvtColor(image_arr, cv2.COLOR_BGR2RGBA)
    image_arr = np.array(Image.open(image_path).convert("RGBA"))
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

    segmentation_points = [[x / new_width, y / new_height] for x, y in points]
    return warped_image_pil, segmentation_points


def scale_image(image_pil, scale_factor):
    # Get the new size
    width, height = image_pil.size
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)

    # Resize the image
    scaled_image = image_pil.resize((new_width, new_height))

    # Save the scaled image
    return scaled_image


def crop_image(image_pil, new_width, new_height):
    # Open the image

    # Crop the image
    cropped_image = image_pil.crop((new_width, 0, 0, new_height))

    # Save the cropped image
    return cropped_image


def adjust_brightness(image_pil, factor):
    # Create an ImageEnhance object
    enhancer = ImageEnhance.Brightness(image_pil)

    # Adjust the brightness
    enhanced_image = enhancer.enhance(factor)

    # Save the adjusted image
    return enhanced_image


if __name__ == "__main__":
    # Example usage:
    input_path = 'input_image.jpg'
    output_path = 'scaled_image.jpg'
    scale_factor = 0.5  # Scale factor (0.5 means halving the dimensions)

    scale_image(input_path, output_path, scale_factor)
