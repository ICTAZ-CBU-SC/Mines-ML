# from PIL import Image, ImageOps
# import numpy as np
#
#
# def shear_image(image_path, shear_horizontal_angle=0, shear_vertical_angle=0):
#     """
#     Shears the image horizontally and/or vertically based on the provided angles.
#
#     Args:
#     image_path (str): Path to the input image file.
#     shear_horizontal_angle (float): Horizontal shear angle in degrees. Default is 0.
#     shear_vertical_angle (float): Vertical shear angle in degrees. Default is 0.
#
#     Returns:
#     PIL.Image.Image: Skewed image.
#     """
#     # Open the image
#     image = Image.open(image_path)
#
#     # Convert angles to radians
#     shear_horizontal_radians = np.radians(shear_horizontal_angle)
#     shear_vertical_radians = np.radians(shear_vertical_angle)
#
#     # Calculate new image dimensions
#     width, height = image.size
#     new_width = int(width + abs(height * np.tan(shear_horizontal_radians)))
#     new_height = int(height + abs(width * np.tan(shear_vertical_radians)))
#
#     # Create a new blank canvas with black background
#     new_image = Image.new("RGB", (new_width, new_height), color="black")
#
#     # Calculate offsets based on shear angles
#     offset_horizontal = int(abs(height * np.tan(shear_horizontal_radians)))
#     offset_vertical = int(abs(width * np.tan(shear_vertical_radians)))
#
#     # Paste the original image onto the new canvas with offset
#     if shear_horizontal_angle >= 0:
#         new_image.paste(image, (offset_horizontal, 0))
#     else:
#         new_image.paste(image, (0, 0))
#
#     if shear_vertical_angle >= 0:
#         new_image.paste(image, (0, offset_vertical))
#     else:
#         new_image.paste(image, (0, 0))
#
#     return new_image
#
#
# # Example usage:
# input_image_path = 'images/sign_1.jpg'
# sheared_image = shear_image(input_image_path, shear_horizontal_angle=30, shear_vertical_angle=0)
#
# # Display the sheared image
# sheared_image.show()


from PIL import Image
import numpy as np


def add_padding(image, u=0, p=0, l=0, r=0):
    """
    Add black padding to the input image.

    Args:
    image (PIL.Image.Image): Input image.
    u (int): Padding pixels to add to the top (upper). Default is 0.
    p (int): Padding pixels to add to the bottom (lower). Default is 0.
    l (int): Padding pixels to add to the left. Default is 0.
    r (int): Padding pixels to add to the right. Default is 0.

    Returns:
    PIL.Image.Image: Image with added black padding.
    """
    # Get input image dimensions
    width, height = image.size

    # Calculate new dimensions with padding
    new_width = width + l + r
    new_height = height + u + p

    # Create a new blank image with the new dimensions and fill it with black
    padded_image = Image.new('RGB', (new_width, new_height), color='black')

    # Paste the original image onto the padded image with the specified offsets
    padded_image.paste(image, (l, u))

    return padded_image


# Example usage:
input_image_path = 'images/image 1.jpg'
input_image = Image.open(input_image_path)

# Add padding of 20 pixels to the top and bottom, and 10 pixels to the left and right
padded_image = add_padding(input_image, u=0, p=0, l=0, r=400)

# Display the padded image
padded_image.show()
