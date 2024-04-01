import os.path
from random import uniform, choice
from image_processing import *


def flatten_list_level1(nested_list):
    flattened_list = []
    for sublist in nested_list:
        for item in sublist:
            flattened_list.append(item)
    return flattened_list


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

    classes = {}

    for entry in os.listdir(instances_dir):
        full_path = os.path.abspath(os.path.join(instances_dir, entry))
        class_dir = full_path
        if os.path.isdir(full_path):
            class_data = entry.split()
            try:
                class_index = int(class_data[0])
                class_name = " ".join(class_data[1:])
                while class_index in classes:
                    class_index += 1
            except ValueError:
                # Assign a unique negative index if there's some weird stuff
                class_index = min([0] + [n for n in classes]) - 1
                class_name = entry

            classes[class_index] = [class_name, class_dir]

    instances = flatten_list_level1(
        [[(c_index, os.path.join(c_dir, inst)) for inst in os.listdir(c_dir)] for c_index, (c_name, c_dir) in
         classes.items()])
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
        image_class, image_dir = choice(instances)

        bg_dir = choice(backgrounds)
        h_shear, v_shear = uniform(-20, 20), uniform(-20, 20)
        h_warp, v_warp = uniform(0.65, 1) * choice([-1, 1]), uniform(0.65, 1) * choice([-1, 1])
        warped_image, seg = shear_and_warp(image_dir, h_shear, v_shear, v_warp, h_warp)
        warped_image = adjust_brightness(warped_image, uniform(0.2, 0.9))
        warped_bg, bg_seg = shear_and_warp(bg_dir, uniform(-5, 5), uniform(-5, 5),
                                           uniform(0.9, 1) * choice([-1, 1]), uniform(0.9, 1) * choice([-1, 1]))

        if (warped_image.width / warped_bg.width) > 0.5 or (warped_image.height / warped_bg.height) > 0.5:
            scale = max([(warped_image.width / warped_bg.width), (warped_image.height / warped_bg.height)]) * uniform(2,
                                                                                                                      4)
            warped_bg = scale_image(warped_bg, scale)

        warped_image, seg = overlay_images(warped_bg, warped_image, x=uniform(0, 1), y=uniform(0, 1), seg_points=seg)

        if i < train_samples:
            image_filename = os.path.join(train_images_dir, f"{i}.png")
            label_filename = os.path.join(train_labels_dir, f"{i}.txt")
        else:
            image_filename = os.path.join(val_images_dir, f"{i}.png")
            label_filename = os.path.join(val_labels_dir, f"{i}.txt")

        warped_image.save(image_filename)
        print(f"Processing {image_dir} and saving to {image_filename}")

        with open(label_filename, "w") as text_file:
            data = []
            for x, y in seg:
                data += [x, y]
            data = f"{image_class} " + " ".join([str(d) for d in data]) + "\n"
            text_file.write(data)

    with open("data.yaml", "w") as yaml_file:
        data = f"train: {os.path.abspath(os.path.join(dataset_dir, 'images', 'train'))} \n" \
               f"val: {os.path.abspath(os.path.join(dataset_dir, 'images', 'val'))} \n" \
               f"nc: {len(classes)} \n" \
               f"names: {[c_name for c_name, c_dir in classes.values()]}"
        yaml_file.write(data)


create_dataset("generated_dataset", "dataset generation inputs/instances", "dataset generation inputs/background",
               samples=1000, train_val_split=0.80)

