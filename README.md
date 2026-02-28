# NVIDIA Jetson Thor - Camera Video Capture & S3 Upload

A lightweight application for NVIDIA Jetson AGX Thor that records video from a connected USB camera and uploads it to an AWS S3 bucket.

## Overview

This project captures a short video clip from a USB camera (e.g., a webcam) connected to an NVIDIA Jetson AGX Thor Developer Kit, saves it locally, and then uploads it to AWS S3 for cloud storage. It is designed for IoT video capture, surveillance, remote monitoring, or any use case where you need automated camera-to-cloud video recording on edge hardware.

## Hardware

- **Board:** NVIDIA Jetson AGX Thor Developer Kit
- **Architecture:** aarch64 (ARM64)
- **JetPack / L4T:** R38.4.0
- **OS:** Ubuntu 24.04.3 LTS
- **Camera:** Any USB camera (UVC-compatible) connected via USB — uses `/dev/video0` by default

## Prerequisites

- Python 3.10+
- A USB camera connected and visible at `/dev/video0`
- AWS credentials configured (via `aws configure`, environment variables, or IAM role)
- Internet connectivity for S3 uploads

### Verify your camera is detected

```bash
v4l2-ctl --list-devices
```

You should see your USB camera listed with a `/dev/video0` entry.

### Verify AWS credentials

```bash
aws sts get-caller-identity
```

This should return your AWS account details without errors.

## Project Structure

```
.
├── record_video.py      # Main Python script — records video and uploads to S3
├── record.sh            # Bash wrapper — runs the script using the project venv
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment config (copy to .env and fill in)
├── .env                 # Your local environment config (not tracked in git)
├── .gitignore           # Git ignore rules
├── videos/              # Local output directory for recorded videos (auto-created)
└── venv/                # Python virtual environment (not tracked in git)
```

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd nvidia-jetson-thor-upload-camera-video-to-s3
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure the S3 bucket

```bash
cp .env.example .env
```

Edit `.env` and set your S3 bucket name:

```
S3_BUCKET=your-bucket-name
```

The `.env` file is gitignored so your bucket name stays out of version control. The `record.sh` wrapper loads it automatically.

If running `record_video.py` directly (without `record.sh`), export the variable first:

```bash
export S3_BUCKET="your-bucket-name"
```

### 4. Configure AWS credentials

If you haven't already, configure your AWS credentials:

```bash
aws configure
```

You will need:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-west-2`)

Alternatively, set environment variables:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"
```

## Usage

### Option 1: Using the shell wrapper (recommended)

```bash
./record.sh
```

### Option 2: Using Python directly

```bash
source venv/bin/activate
python record_video.py
```

### Expected output

```
Recording for 3 seconds...
Video saved to /path/to/videos/video_20260228_223835.avi
Uploading to s3://your-bucket-name/videos/video_20260228_223835.avi...
Upload complete.
```

## Configuration

The following constants can be modified at the top of `record_video.py`:

| Variable     | Source              | Default       | Description                           |
|------------- |---------------------|---------------|---------------------------------------|
| `S3_BUCKET`  | Environment / `.env`| *(required)*  | Target S3 bucket name                 |
| `DURATION`   | `record_video.py`   | `3`           | Recording duration in seconds         |
| `OUTPUT_DIR` | `record_video.py`   | `./videos/`   | Local directory for saved video files |

To change the camera device, modify the argument to `cv2.VideoCapture()` in `record_video.py`:

```python
cap = cv2.VideoCapture(0)  # Change 0 to another device index if needed
```

## How It Works

1. **Camera initialization** — Opens the USB camera at `/dev/video0` using OpenCV
2. **Frame capture** — Reads frames for the configured duration (default: 3 seconds)
3. **Local save** — Writes frames to an AVI file (XVID codec) in the `videos/` directory with a timestamp filename
4. **S3 upload** — Uploads the saved video to the configured S3 bucket under the `videos/` prefix using boto3
5. **Cleanup** — Releases camera and writer resources

### Video format

- **Container:** AVI
- **Codec:** XVID (MPEG-4 Part 2)
- **Resolution:** Native camera resolution (auto-detected)
- **Frame rate:** Native camera FPS (falls back to 30 FPS)

## Dependencies

| Package         | Version   | Purpose                          |
|-----------------|-----------|----------------------------------|
| boto3           | 1.42.50   | AWS SDK for S3 uploads           |
| opencv-python   | 4.13.0.92 | Video capture and encoding       |
| numpy           | 2.4.2     | Required by OpenCV               |

## Troubleshooting

### "Error: Could not open camera."

- Verify the camera is connected: `v4l2-ctl --list-devices`
- Check permissions: `ls -l /dev/video0` — your user should have read/write access
- Try adding your user to the `video` group: `sudo usermod -aG video $USER` (log out and back in)

### S3 upload fails with credentials error

- Run `aws sts get-caller-identity` to verify credentials are configured
- Ensure the IAM user/role has `s3:PutObject` permission on the target bucket
- Check that `S3_BUCKET` is set in your `.env` file or environment

### Low FPS or choppy video

- USB bandwidth may be limited — try a USB 3.0 port
- Reduce resolution by setting camera properties before recording:
  ```python
  cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
  ```

### "Error: Failed to read frame."

- The camera may have disconnected during recording
- Another process may be using the camera — check with `lsof /dev/video0`

## Automating with cron

To record and upload on a schedule, add a cron job:

```bash
crontab -e
```

Example — record every 5 minutes:

```
*/5 * * * * /home/chiwaichan/repos/nvidia-jetson-thor-upload-camera-video-to-s3/record.sh >> /tmp/record.log 2>&1
```

## License

This project is provided as-is for personal and educational use.
