from PIL import Image

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


paste_segmentation_onto_transparent()
