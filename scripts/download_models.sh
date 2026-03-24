#!/bin/bash

# Download pre-trained models for chess piece detection

MODEL_DIR="data/models"
mkdir -p "$MODEL_DIR"

echo "📥 Downloading chess detection models..."

# Download YOLOv8 nano (lightweight, fast)
if [ ! -f "$MODEL_DIR/yolov8n.pt" ]; then
    echo "Downloading YOLOv8n..."
    wget -O "$MODEL_DIR/yolov8n.pt" https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt
fi

# Download YOLOv8 medium (better accuracy)
if [ ! -f "$MODEL_DIR/yolov8m.pt" ]; then
    echo "Downloading YOLOv8m..."
    wget -O "$MODEL_DIR/yolov8m.pt" https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8m.pt
fi

echo "✅ Models downloaded to $MODEL_DIR"
echo ""
echo "Note: For chess-specific piece detection, you'll need a custom trained model."
echo "The default YOLO models can detect pieces but may need fine-tuning for best results."