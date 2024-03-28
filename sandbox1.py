import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps


def paste_segmentation_onto_transparent(segmentation_image_path, transparent_image_path, segmentation_points):
    """
    Crops out an image segmentation based on provided points and pastes it onto a transparent image.

    Args:
        segmentation_image_path (str): Path to the segmentation image.
        transparent_image_path (str): Path to the transparent image.
        segmentation_points (list): A list of (x, y) coordinates representing the points outlining the segmentation.

    Returns:
        None
    """

    try:
        segmentation_image = Image.open(segmentation_image_path)
        transparent_image = Image.open(transparent_image_path)

        # Check compatibility
        if segmentation_image.mode != transparent_image.mode:
            raise ValueError("Image modes are not compatible.")

        # Get bounding box from segmentation points
        min_x, min_y = min(segmentation_points, key=lambda p: p[0])[0], min(segmentation_points, key=lambda p: p[1])[1]
        max_x, max_y = max(segmentation_points, key=lambda p: p[0])[0], max(segmentation_points, key=lambda p: p[1])[1]
        bbox = (min_x, min_y, max_x, max_y)

        # Crop segmentation image
        cropped_segmentation = segmentation_image.crop(bbox).convert("RGBA")

        # Paste onto transparent image
        transparent_image.paste(cropped_segmentation, mask=cropped_segmentation)

        # Save final image
        transparent_image.save("final_image.png", "PNG")
        transparent_image.show()

    except FileNotFoundError as e:
        print(f"Error: File not found: {e}")
    except ValueError as e:
        print(e)


def extract_masked_parts(original_image_path, mask_image_path):
    # Read the original image and the mask image
    original_image = cv2.imread(original_image_path)
    mask_image = cv2.imread(mask_image_path, cv2.IMREAD_GRAYSCALE)

    # Ensure that the mask image is binary (0 or 255)
    _, mask_image = cv2.threshold(mask_image, 128, 255, cv2.THRESH_BINARY)

    # Invert the mask (black becomes white and vice versa) to create a mask for the masked parts
    inverted_mask = cv2.bitwise_not(mask_image)

    # Create an alpha channel for the masked parts
    alpha_channel = np.zeros_like(inverted_mask)

    # Stack the original image with the alpha channel to create an RGBA image
    original_image_with_alpha = cv2.merge([original_image, alpha_channel])

    # Set the alpha channel values for the masked parts to 0 (fully transparent)
    original_image_with_alpha[:, :, 3] = inverted_mask

    return original_image_with_alpha


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

    # Define destination points (adjusted for desired warping)
    dst_pts = np.float32([dst_top_left, dst_top_right, dst_bottom_right, dst_bottom_left])

    # Calculate perspective transform matrix
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)

    # Warp the image
    warped_image = cv2.warpPerspective(_image, M, (width, height))
    warped_pil = Image.fromarray(cv2.cvtColor(warped_image, cv2.COLOR_BGR2RGB))
    warped_pil = warped_pil.convert("RGBA")

    # Create a new image with a transparent background
    transparent_background = Image.new("RGBA", warped_pil.size, (0, 0, 0, 0))

    # Draw the segmentation points onto the transparent background
    draw = ImageDraw.Draw(transparent_background)
    draw.polygon(dst_pts, fill=(255, 255, 255, 255))  # Fills the region with white color and full opacity
    warped_image = cv2.cvtColor(warped_image, cv2.COLOR_BGR2BGRA)

    transparent_arr = np.array(transparent_background)
    h, w = transparent_arr.shape[:2]
    for y in range(height):
        for x in range(width):
            if transparent_arr[y, x, 3] == 255:
                transparent_arr[y, x] = warped_image[y, x]
    cv2.imshow("123456", transparent_arr)
    cv2.imwrite("test_image.png", transparent_arr)
    cv2.waitKey(0)
    return Image.fromarray(transparent_arr)


def crop_and_paste(image_path, segmentation_points, output_path):
    # Open the original image
    original_image = Image.open(image_path)

    # Create a new image with a transparent background
    transparent_background = Image.new("RGBA", original_image.size, (255, 255, 255, 0))

    # Draw the segmentation points onto the transparent background
    draw = ImageDraw.Draw(transparent_background)
    draw.polygon(segmentation_points, fill=(255, 255, 255, 255))  # Fills the region with white color and full opacity

    # Extract the object from the original image using the drawn segmentation points
    object_image = Image.alpha_composite(original_image.convert("RGBA"), transparent_background)

    # Save the result to the output path
    object_image.save(output_path)


image = cv2.imread("images/image 2.jpg")
warped = warp_perspective(image, -0.5, 1)
warped.show()
# Optionally save the warped image
# cv2.imwrite("warped_asymmetric.jpg", warped)
# cv2.waitKey(0)
