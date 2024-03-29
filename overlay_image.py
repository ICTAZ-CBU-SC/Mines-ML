from PIL import Image, ImageEnhance


def crop_image(image_pil, new_width, new_height):
    # Open the image

    # Crop the image
    cropped_image = image_pil.crop((new_width, 0, 0, new_height))

    # Save the cropped image
    return cropped_image


def adjust_brightness(image_path, output_path, factor):
    # Open the image
    image = Image.open(image_path)

    # Create an ImageEnhance object
    enhancer = ImageEnhance.Brightness(image)

    # Adjust the brightness
    enhanced_image = enhancer.enhance(factor)

    # Save the adjusted image
    enhanced_image.save(output_path)


def add_padding(image_pil, up=0, down=0, left=0, right=0):
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
    width, height = image_pil.size

    # Calculate new dimensions with padding
    new_width = width + left + right
    new_height = height + up + down

    # Create a new blank image with the new dimensions and fill it with transparent pixels
    padded_image = Image.new('RGBA', (new_width, new_height), color=(0, 0, 0, 0))

    # Paste the original image onto the padded image with the specified offsets
    padded_image.paste(image_pil, (left, up))

    return padded_image


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


# Example usage:
background_image = Image.open("MINING SAFETY SET/BACKGROUND/miners-working-safe-in-coppermine_How-miners-work-safely.jpg")
overlay_image = Image.open("generated_dataset/images/train/1.png")
output_path = 'result.png'

result_image, seg = overlay_images(background_image, overlay_image, 0.5, 0.5, seg_points=[(0.5, 0.5)])
print(seg)
result_image.show()
