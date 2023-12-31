import numpy as np
import cv2
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from ttkthemes import ThemedTk

def colorize_image(input_path):
    print("Loading the colorized version")
    net = cv2.dnn.readNetFromCaffe("models/colorization_deploy_v2.prototxt", 'models/colorization_release_v2.caffemodel')
    pts = np.load('models/pts_in_hull.npy')

    class8 = net.getLayerId("class8_ab")
    conv8 = net.getLayerId("conv8_313_rh")
    pts = pts.transpose().reshape(2, 313, 1, 1)

    net.getLayer(class8).blobs = [pts.astype("float32")]
    net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype='float32')]

    image = cv2.imread(input_path)
    scaled = image.astype("float32") / 255.0
    lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)

    resized = cv2.resize(lab, (224, 224))
    L = cv2.split(resized)[0]
    L -= 50

    net.setInput(cv2.dnn.blobFromImage(L))
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))

    ab = cv2.resize(ab, (image.shape[1], image.shape[0]))

    L = cv2.split(lab)[0]
    colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)

    colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
    colorized = np.clip(colorized, 0, 1)

    colorized = (255 * colorized).astype("uint8")

    screen_width = 500
    screen_height = 500

    image = cv2.resize(image, (screen_width, screen_height))
    colorized = cv2.resize(colorized, (screen_width, screen_height))

    cv2.imshow("Original", image)
    cv2.imshow("Colorized", colorized)
    cv2.waitKey(0)

def browse_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        colorize_image(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Image Colorization")

    window_width = 450
    window_height = 200
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    style = ttk.Style()
    style.configure("TButton", padding=6, relief="flat", background="#6F4685", foreground="blue")
    browse_button = ttk.Button(root, text="Browse for an Image", command=browse_image, style="TButton")
    browse_button.pack(pady=30)

    root.mainloop()
