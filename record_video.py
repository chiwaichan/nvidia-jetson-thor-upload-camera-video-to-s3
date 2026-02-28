import cv2
import os
import sys
import time
from datetime import datetime
import boto3

DURATION = 3
S3_BUCKET = os.environ.get("S3_BUCKET")
if not S3_BUCKET:
    print("Error: S3_BUCKET environment variable is not set.")
    sys.exit(1)
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos")

os.makedirs(OUTPUT_DIR, exist_ok=True)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit(1)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = os.path.join(OUTPUT_DIR, f"video_{timestamp}.avi")

fourcc = cv2.VideoWriter_fourcc(*"XVID")
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

print(f"Recording for {DURATION} seconds...")
start = time.time()
while time.time() - start < DURATION:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read frame.")
        break
    out.write(frame)

cap.release()
out.release()
print(f"Video saved to {output_path}")

s3_key = f"videos/video_{timestamp}.avi"
print(f"Uploading to s3://{S3_BUCKET}/{s3_key}...")
s3 = boto3.client("s3")
s3.upload_file(output_path, S3_BUCKET, s3_key)
print("Upload complete.")
