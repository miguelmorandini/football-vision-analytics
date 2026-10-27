# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # ⚽ Football Vision Analytics - Databricks Cluster Pipeline
# MAGIC 
# MAGIC This notebook demonstrates how to run distributed / batch computer vision video processing
# MAGIC across soccer matches using **Databricks Clusters** and saving telemetry to **Delta Lake** or **DBFS / Volumes**.

# COMMAND ----------
# MAGIC %pip install ultralytics supervision opencv-python-headless scikit-learn matplotlib

# COMMAND ----------
import os
import json
import numpy as np
from pathlib import Path
from src.pipeline import FootballVideoPipeline
from src.tactics.formation_detector import FormationDetector
from src.vision.detector import FootballDetector

# COMMAND ----------
# Initialize Pipeline with GPU or CPU device
pipeline = FootballVideoPipeline(
    detector=FootballDetector(model_name="yolov8n.pt")
)
print("Pipeline successfully initialized in Databricks!")

# COMMAND ----------
# Process Sample Video from Databricks Volumes
# Sample Volume Path: /Volumes/main/default/football_videos/match_01.mp4
sample_video = "data/videos/sample.mp4"

if os.path.exists(sample_video):
    results = pipeline.process_video(
        video_path=sample_video,
        max_frames=120,
        frame_stride=2
    )
    print(f"Processed {results['processed_frames']} frames!")
    
    # Save to Databricks Delta Lake / DBFS
    # output_path = "/dbfs/football_analytics/telemetry.json"
    # with open(output_path, "w") as f:
    #     json.dump(results, f)
else:
    print("Video file not found. Ready for Databricks Volume input.")
