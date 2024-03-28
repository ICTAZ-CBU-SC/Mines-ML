from PIL import Image


def overlay_image(background_image, overlay_image, x, y):
    # Open both images
    background = Image.open(background_image)
    overlay = Image.open(overlay_image)

    # Convert overlay image to RGBA mode if not already
    if overlay.mode != 'RGBA':
        overlay = overlay.convert('RGBA')

    # Paste the overlay image onto the background at specified coordinates
    background.paste(overlay, (x, y), overlay)

    # Return the resulting image
    return background


# Example usage:
background_image = Image.open('MINING SAFETY SET/BACKGROUND/Underground-mine-ramp.jpg)')
overlay_image = warp_persp'overlay.png'
x_coordinate = 100
y_coordinate = 50

result_image = overlay_image(background_image_path, overlay_image_path, x_coordinate, y_coordinate)
result_image.show()  # Display the result
