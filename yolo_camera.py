import requests
import cv2
import numpy as np
from threading import Thread
import cv2
from ultralytics import YOLO
import glob
import os
import time


model = YOLO("./checkpoint/best.pt")
# Get list of image paths
# image_paths = glob.glob("./*.jpg")

# Create the output directory if it doesn't exist
output_dir = "./output"
output_txt_path = "./output_text/output.txt"
os.makedirs(output_dir, exist_ok=True)

# TODO: IP Webcam 地址，替換成你手機的 IP 地址
ip_webcam_url = "http://your_ip:8080/video"
first_detection = False
detection_time = None

def detect_objects(frame):
    
    names = []
    xs = []
    ys = []
    zs = []
    zzs = []

    results = model.predict(frame, save=True, conf=0.25, verbose=False)

    for det in results:
        boxes = det.boxes.xyxy  # Assuming xyxy is a tensor
        classes = det.boxes.cls  # Get the class ID
        for i in range(boxes.size(0)):
            xyxy = boxes[i]
            cls = classes[i]
            # print(f"Class ID: {cls}, Box: {xyxy}")
            name = None
            if cls == 0:
                name = "donat"
            elif cls == 1:
                name = "grape"
            elif cls == 2:
                name = "square"
            elif cls == 3:
                name = "strawberry"
            elif cls == 4:
                name = "pudding"
            elif cls == 5:
                name = "meat_floss"
            elif cls == 6:
                name = "pizza"
            elif cls == 7:
                name = "matcha"
            elif cls == 8:
                name = "sugar"
            elif cls == 9:
                name = "strawberry_donat"
            elif cls == 10:
                name = "black_eye"

            names.append(name)
            xs.append(xyxy[0])
            ys.append(xyxy[1])
            zs.append(xyxy[2])
            zzs.append(xyxy[3])
            frame = cv2.rectangle(
                frame,
                (int(xyxy[0]), int(xyxy[1])),
                (int(xyxy[2]), int(xyxy[3])),
                (0, 0, 255),
                2,
            )
            frame = cv2.putText(
                frame,
                name,
                (int(xyxy[0]), int(xyxy[1] - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2,
            )
    return frame, names, xs, ys, zs, zzs


def get_video_stream():
    global first_detection, detection_time
    stream = requests.get(ip_webcam_url, stream=True)
    if stream.status_code == 200:
        bytes_stream = bytes()
        for chunk in stream.iter_content(chunk_size=1024):
            bytes_stream += chunk
            a = bytes_stream.find(b"\xff\xd8")  # Start of image flag
            b = bytes_stream.find(b"\xff\xd9")  # End of image flag
            if a != -1 and b != -1:
                jpg = bytes_stream[a : b + 2]
                bytes_stream = bytes_stream[b + 2 :]
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                # Object detection
                frame_with_objects, name, x, y, z, zz = detect_objects(frame)

                if not first_detection and len(name) != 0:
                    first_detection = True
                    detection_time = time.time()

                if first_detection and (time.time() - detection_time > 3):
                    # Save the frame after 3 seconds
                    cv2.imwrite(f"{output_dir}/detected_frame.jpg", frame_with_objects)
                    # Perform prediction on the saved frame
                    # ... [add code for prediction using the model]
                    frame_with_objects, name, x, y, z, zz = detect_objects(frame)
                    # print(len(name))
                    # if len(name):
                    #     with open(output_txt_path, 'w') as f:
                    #         for i in range(len(name)):
                    #             f.write(f"{name[i]} {x[i]} {y[i]} {z[i]} {zz[i]}\n")
                    first_detection = False  # Reset flag if you want to detect again

                cv2.imshow("Object Detection", frame_with_objects)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    else:
        print("Unable to connect to IP Webcam. Check URL.")


# 使用多線程執行
# thread = Thread(target=get_video_stream)
# thread.start()

# 等待所有線程完成
# thread.join()
get_video_stream()

# 關閉視窗和釋放資源
cv2.destroyAllWindows()