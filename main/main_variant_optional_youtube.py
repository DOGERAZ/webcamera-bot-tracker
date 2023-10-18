import face_recognition
from PIL import Image, ImageDraw, ImageFont
import pickle
import cv2
import numpy as np
import concurrent.futures
from pytube import YouTube

# Function to connect to a YouTube stream
def connect_to_youtube_stream(stream_url):
    yt = YouTube(stream_url)
    stream = yt.streams.filter(adaptive=True, file_extension="mp4").first()
    return cv2.VideoCapture(stream.url)

# Function to process frames and detect faces
def process_frames(video_capture, data):
    while True:
        ret, frame = video_capture.read()

        if not ret:
            break

        frame_with_annotations = detect_faces_in_frame(frame, data)
        cv2.imshow("Face Detection in Video", frame_with_annotations)

        k = cv2.waitKey(20)
        if k == ord("q"):
            print("Q pressed, closing the app")
            break

def draw_face_rectangles_pil(image, face_locations, names):
    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)
    
    font = ImageFont.truetype("arial.ttf", 24)
    text_color = (255, 255, 255)  # White color
    outline_color = (0, 0, 0)  # Black outline color

    for (top, right, bottom, left), name in zip(face_locations, names):
        if name == "Unknown":
            rect_color = (255, 0, 0)  # Red rectangle for unknown
        else:
            rect_color = (0, 255, 0)  # Green rectangle for recognized names

        thickness = 5
        draw.rectangle([left, top, right, bottom], outline=rect_color, width=thickness)
        
        # Draw the name above the rectangle with a thicker black outline
        text_position = (left, bottom + 40)
        draw.text(text_position, name, fill=outline_color, font=font)
        text_position = (left, bottom + 40)
        draw.text(text_position, name, fill=text_color, font=font)

    return np.array(pil_image)

def detect_faces_in_frame(frame, data):
    locations = face_recognition.face_locations(frame, model="hog")  # Use HOG model for faster processing
    encodings = face_recognition.face_encodings(frame, locations)

    recognized_names = []
    
    for face_encoding in encodings:
        results = face_recognition.compare_faces(data["encodings"], face_encoding)

        if any(results):
            index = results.index(True)
            recognized_names.append(data["name"])  # Append the recognized name

    unknown_names = ["Unknown"] * (len(locations) - len(recognized_names))

    names = recognized_names + unknown_names

    frame_with_annotations = draw_face_rectangles_pil(frame, locations, names)
    return frame_with_annotations

def main():
    with open("your_pickle", "rb") as file:
        data = pickle.load(file)
    
    # Uncomment the line below to process a regular video
    # video_path = "face_detection_venv/main/video/MrBeast Sigma Original Vs Edit.mp4"
    
    # Comment the line below when processing a regular video
    video_path = "your_url_youtube"
    
    video_capture = connect_to_youtube_stream(video_path)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:  # Limit the number of threads
        process_frames(video_capture, data)
        video_capture.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
