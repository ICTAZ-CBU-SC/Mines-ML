from ultralytics import YOLO

# Load a model
# model = YOLO('train11-03-24 06_03/weights/best.pt')
model = YOLO('best (1).pt')  # pretrained YOLOv8n model

# Run batched inference on a list of images
results = model.predict('test_images')  # return a list of Results objects

# model(0)
# Process results list
for i, result in enumerate(results):
    boxes = result.boxes  # Boxes object for bounding box outputs
    masks = result.masks  # Masks object for segmentation masks outputs
    keypoints = result.keypoints  # Keypoints object for pose outputs
    probs = result.probs  # Probs object for classification outputs
    # result.show()  # display to screen
    result.save(filename=f'results/result{i}.jpg')  # save to disk
