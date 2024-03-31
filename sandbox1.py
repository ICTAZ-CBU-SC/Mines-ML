import os

directory = "generated_dataset/labels/train"

for f in os.listdir(directory):
    filename = os.path.join(directory, f)
    with open(filename, "r") as file:
        content = file.read()
        data = content[:2] + content[4:]
        print(data)

    with open(filename, "w") as file:
        file.write(data)
