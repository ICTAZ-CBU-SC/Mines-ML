import os
import shutil
from datetime import datetime
from ultralytics import YOLO


# Load a model
# model = YOLO('yolov8n-seg.pt')  # load a pretrained model (recommended for training)

# Train the model
# results = model.train(data='data.yaml', epochs=100, imgsz=640)


def copy_last_train_folder(*kwargs):
    """
      This function zips the contents of the last train folder and moves it to a new folder.

      Args:
      epoch: Current epoch number.
      results: Training results dictionary.
      weights: Path to the saved model weights.
    """
    # Get the runs folder path (modify if using a different path)
    runs_folder = "runs/segment"

    # Get a list of all subdirectories in the runs folder
    subdirs = [f.name for f in os.scandir(runs_folder) if f.is_dir()]

    # Sort subdirectories by name (assuming numerical naming)
    subdirs.sort()

    # Get the last subdirectory (assuming it's the latest train folder)
    last_train_folder = os.path.join(runs_folder, subdirs[-1])
    # Define the destination folder name (modify if desired)
    current_time = datetime.now().strftime('%d-%m-%y %H%M')
    destination_folder = f"Epochs/train{current_time}"

    # Create the destination folder if it doesn't exist
    # !mkdir -p "{destination_folder}"
    os.makedirs(destination_folder, exist_ok=True)

    # Copy folder
    shutil.copytree(last_train_folder, destination_folder, dirs_exist_ok=True)


model = YOLO(os.path.join("runs/segment", sorted(os.listdir("runs/segment"))[-1], "weights", "last.pt"))
model.add_callback("on_model_save", copy_last_train_folder)
model.train(resume=True)
