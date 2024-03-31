from ultralytics import YOLO
import cv2
import os
from ultralytics.utils.plotting import Annotator  # ultralytics.yolo.utils.plotting is deprecated

# model = YOLO('modelv1.pt')
# model = YOLO(os.path.join("runs/segment", sorted(os.listdir("runs/segment"))[-1], "weights", "last.pt"))
# model = YOLO("Epochs segmentation/train31-03-24 0835/weights/last.pt")
# model = YOLO("Epochs/train-segment31-03-24 1322/weights/last.pt")
model = YOLO("Epochs/train-segment31-03-24 1648/weights/last.pt")

# results = model.val()
# print(results)
# input("Press enter to continue")

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

while True:
    _, frame = cap.read()

    # BGR to RGB conversion is performed under the hood
    # see: https://github.com/ultralytics/ultralytics/issues/2575
    results = model.predict(frame)

    for result in results:
        annotator = Annotator(frame)
        boxes = result.boxes
        for box in boxes:
            class_index = int(box.cls)
            confidence = float(box.conf)
            if confidence < 0.5:
                continue
            b = box.xyxy[0]  # get box coordinates in (left, top, right, bottom) format
            x1, y1, x2, y2 = b
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), thickness=2)
            annotator.box_label(b, f"{model.names[class_index]} {confidence}")
            # print(model.names[int(class_index)])

    # frame = annotator.result()
    cv2.imshow('YOLO V8 Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
