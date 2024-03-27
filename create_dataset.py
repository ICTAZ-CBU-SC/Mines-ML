from PIL import Image
import numpy as np


def add_padding(image, u=0, d=0, l=0, r=0):
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
    new_height = height + u + d

    # Create a new blank image with the new dimensions and fill it with black
    padded_image = Image.new('RGB', (new_width, new_height), color='black')

    # Paste the original image onto the padded image with the specified offsets
    padded_image.paste(image, (l, u))

    return padded_image


def shear_image(image_path, shear_horizontal_angle=0, shear_vertical_angle=0):
    """
    Shears the image horizontally and/or vertically based on the provided angles.

    Args:
    image_path (str): Path to the input image file.
    shear_horizontal_angle (float): Horizontal shear angle in degrees. Default is 0.
    shear_vertical_angle (float): Vertical shear angle in degrees. Default is 0.

    Returns:
    PIL.Image.Image: Skewed image.
    """
    # Open the image
    image = Image.open(image_path)
    # Calculate new image dimensions
    width, height = image.size

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

    print(up_pad, down_pad, left_pad, right_pad)

    image = add_padding(image, u=up_pad, d=down_pad, l=left_pad, r=right_pad)

    new_width, new_height = width + h_pad, height + v_pad

    # Define the transformation matrix
    shear_matrix = (1, np.tan(shear_horizontal_radians), 0,
                    np.tan(shear_vertical_radians), 1, 0)

    # Shear the image
    skewed_image = image.transform((new_width, new_height), Image.AFFINE, shear_matrix,
                                   resample=Image.BICUBIC)

    return skewed_image


# Example usage:
input_image_path = 'images/sign_1.jpg'
sheared_image = shear_image(input_image_path, shear_horizontal_angle=0, shear_vertical_angle=30)

# Display the original and sheared images
sheared_image.show()
