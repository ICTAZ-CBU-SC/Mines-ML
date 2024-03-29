import os.path
import random
from random import uniform
from secrets import choice

import cv2
import numpy as np
from PIL import Image


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
    image_arr = cv2.imread(image_path)
    image_arr = cv2.cvtColor(image_arr, cv2.COLOR_BGR2RGBA)
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


def create_dataset(dataset_dir, instances_dir, background_dir, samples=100, train_val_split=0.8):
    def create_directory(directory_path):
        """
        Creates a directory if it doesn't exist.

        Args:
            directory_path (str): The path to the directory to create.
        """
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            print(f"Directory created: {directory_path}")
        else:
            print(f"Directory already exists: {directory_path}")

    instances = [os.path.join(instances_dir, f) for f in os.listdir(instances_dir)]
    backgrounds = [os.path.join(background_dir, f) for f in os.listdir(background_dir)]

    images_dir = os.path.join(dataset_dir, "images")
    train_images_dir = os.path.join(images_dir, "train")
    val_images_dir = os.path.join(images_dir, "val")

    labels_dir = os.path.join(dataset_dir, "labels")
    train_labels_dir = os.path.join(labels_dir, "train")
    val_labels_dir = os.path.join(labels_dir, "val")

    for d in [train_images_dir, val_images_dir, train_labels_dir, val_labels_dir]:
        create_directory(d)

    train_samples = int(samples * train_val_split)

    for i in range(samples):
        image_dir = choice(instances)
        bg_dir = choice(backgrounds)
        h_shear, v_shear = uniform(-20, 20), uniform(-20, 20)
        h_warp, v_warp = uniform(0.65, 1) * choice([-1, 1]), uniform(0.65, 1) * choice([-1, 1])
        warped_image, seg = shear_and_warp(image_dir, h_shear, v_shear, v_warp, h_warp)
        warped_bg, bg_seg = shear_and_warp(bg_dir, uniform(-20, 20), uniform(-20, 20),
                                           uniform(0.65, 1) * choice([-1, 1]), uniform(0.65, 1) * choice([-1, 1]))

        if i <= train_samples:
            image_filename = os.path.join(train_images_dir, f"{i}.png")
            label_filename = os.path.join(train_labels_dir, f"{i}.txt")
            bg_image_filename = os.path.join(train_images_dir, f"bg{i}.png")
            bg_label_filename = os.path.join(train_labels_dir, f"bg{i}.png")
        else:
            image_filename = os.path.join(val_images_dir, f"{i}.png")
            label_filename = os.path.join(val_labels_dir, f"{i}.txt")
            bg_image_filename = os.path.join(val_images_dir, f"bg{i}.png")
            bg_label_filename = os.path.join(val_images_dir, f"bg{i}.png")

        warped_image.save(image_filename)
        warped_bg.save(bg_image_filename)

        with open(label_filename, "w") as text_file:
            data = [0]
            for x, y in seg:
                data += [x, y]
            data = " ".join([str(d) for d in data]) + "\n"
            text_file.write(data)

        with open(bg_label_filename, "w") as text_file:
            text_file.write("")

    with open("data.yaml", "w") as yaml_file:
        data = f"train: {os.path.abspath(os.path.join(dataset_dir, 'train'))} \n" \
               f"val: {os.path.abspath(os.path.join(dataset_dir, 'val'))} \n" \
               f"nc: 1 \nnames: ['sign']"
        yaml_file.write(data)


create_dataset("generated_dataset", "MINING SAFETY SET/ACTIVE MINE", "MINING SAFETY SET/BACKGROUND", samples=2000)

# dataset_dir = "Warning Signs Dataset"
# instances_dir = "MINING SAFETY SET/ACTIVE MINE"
# background_dir = "MINING SAFETY SET/BACKGROUND"
