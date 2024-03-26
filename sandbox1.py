import os
import numpy as np
from scipy import ndimage
from skimage import measure


def mask_to_segmentation(mask):
    # Label connected components in the mask
    labeled_mask, num_labels = ndimage.label(mask)

    # Extract segmentation contours
    segmentation_contours = measure.find_contours(mask, 0.5)

    return labeled_mask, segmentation_contours


def convert_to_yolo_format(image_size, contour):
    # Convert contour to YOLO format
    yolo_format = [(contour[:, 1] / image_size[1]).tolist(), (contour[:, 0] / image_size[0]).tolist()]
    return yolo_format


def save_segmentation_as_text(segmentation_contours, image_size, filename):
    with open(filename, 'w') as file:
        for contour in segmentation_contours:
            yolo_format = convert_to_yolo_format(image_size, contour)
            file.write("0 " + " ".join(str(coord) for coord in yolo_format[0]) + " " + " ".join(
                str(coord) for coord in yolo_format[1]) + "\n")


def process_images_and_masks(parent_directory, output_directory):
    image_directory = os.path.join(parent_directory, 'images')
    mask_directory = os.path.join(parent_directory, 'masks')

    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    for image_filename in os.listdir(image_directory):
        if image_filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            image_path = os.path.join(image_directory, image_filename)
            mask_path = os.path.join(mask_directory, image_filename)

            # Load image and mask
            image = imread(image_path)
            mask = imread(mask_path)

            # Convert mask to segmentation
            labeled_mask, segmentation_contours = mask_to_segmentation(mask)

            # Save segmentation as text file in YOLO format
            segmentation_filename = os.path.splitext(image_filename)[0] + '.txt'
            segmentation_filepath = os.path.join(output_directory, segmentation_filename)
            save_segmentation_as_text(segmentation_contours, image.shape[:2], segmentation_filepath)


# Example usage:
parent_directory = "/path/to/parent_directory"
output_directory = "/path/to/output_directory"

process_images_and_masks(parent_directory, output_directory)
