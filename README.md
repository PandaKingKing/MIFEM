### License: GPL

***


## Microfauna Image Feature Extraction Model (MIFEM)


This feature extraction model is primarily based on two advanced deep learning image models and one traditional computer vision technique:

1.	The YOLOv5 model for object detection, available at ultralytics/yolov5 on GitHub.
2.	The DeepSORT model for object tracking, available at mikel-brostrom/yolo_tracking on GitHub.
3.	The frame differencing method for detecting moving objects.


### Data Sources

***
The key resources for the feature extraction model are the trainable datasets. Manually annotated image datasets available for training can be found here:  
Annotation files (in TXT format): https://doi.org/10.5281/zenodo.8223381  
Corresponding image files: https://doi.org/10.5281/zenodo.8220629

### Models

***

best5.pt: https://doi.org/10.5281/zenodo.11207952

ckpt.t7: https://github.com/Sharpiless/Yolov5-Deepsort/blob/main/deep_sort/deep_sort/deep/checkpoint  
This file is derived from the publicly available open-source DeepSORT code.

### Installation of MIFEM

***
First, place the downloaded files for the object detection and object tracking models into their respective directories. Put the best5.pt file in the yolo_detect/weights folder and the ckpt.t7 file in the yolo_detect/DeepSORT/deep_sort/deep/checkpoint folder.


To reproduce **MIFEM**, we suggest first create a conda environment by:

```
conda create -n mic_venv python=3.9
conda activate mic_venv
```

and then install **pytorch** according to the CUDA version, take CUDA 11.7 (Windows) as an example:

```
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
```

and then run the following code to install the required package:

```
pip install -r requirements.txt
```

### Usage

***

First, place the video to be detected in the input directory, and then run the following code to enter the MIFEM directory and run the main function.

```
cd MIFEM
python main.py
```

### Directories

***



| Directory      | Description                                                  |
| :------------: | :----------------------------------------------------------: |
| big_microfauna   | Store of the big microfauna manager and the manager for all objects. |
| input          | Input directory for data.                                     |
| log            | Store log information files.                                  |
| output         | Output directory for data.                                   |
| small_protozoa | Store the small protozoa detector and manager.                     |
| tools          | Utility function packages.                                     |
| video          | Manage result videos.                                         |
| writer         | Save data files.                                              |
| yolo_detect    | Detection of the big microfauna.                                 |

### Parameters

***

|                Location                 |          Parameter          |                         Description                          |
| :-------------------------------------: | :-------------------------: | :----------------------------------------------------------: |
|     big_microfauna/abstract_bug.py      |        SURVIVAL_TIME        | Pre-set maximum duration of predictive information for big microfauna. |
|     big_microfauna/abstract_bug.py      |    SCREENSHOT_SAVE_TIME     |     Time duration for storing images of big microfauna.      |
|      small_protozoa/bugs_filter.py      |          BBOX_TIME          |  Existence duration of detection boxes for big microfauna.   |
|      small_protozoa/bugs_filter.py      |           OFFSET            | Threshold for boundary jitter amplitude in detection boxes of big microfauna. |
| small_protozoa/small_protozoa_detect.py |         NOISY_LIST          |              Filtering of lens noise locations.              |
|         small_protozoa/track.py         |           MAX_AGE           | Pre-set maximum duration of predictive information for small protozoa. |
|         small_protozoa/track.py         |      MISSING_THRESHOLD      | Frame threshold for determining if the tracking of small protozoa is lost. |
|        small_protozoa/tracker.py        | TRACKING_DISTANCE_THRESHOLD | Distance threshold for determining whether to merge tracked small protozoa targets. |

#### Configuration file

filter_config.json: configuration file for the threshold of authenticity verification for large bugs.

```
// INTERVAL_FRAME_NUMBER
// INTERVAL_NUM
// FRAME_THRESHOLD       
// INTERVAL_THRESHOLD    
{
  "Ar": {
    "INTERVAL_FRAME_NUMBER": 10,
    "INTERVAL_NUM": 5,
    "FRAME_THRESHOLD": 7,
    "INTERVAL_THRESHOLD": 3
  },
  "Gs": {
    "INTERVAL_FRAME_NUMBER": 10,
    "INTERVAL_NUM": 5,
    "FRAME_THRESHOLD": 4,
    "INTERVAL_THRESHOLD": 3
  },
  "Do": {
    "INTERVAL_FRAME_NUMBER": 10,
    "INTERVAL_NUM": 1,
    "FRAME_THRESHOLD": 8,
    "INTERVAL_THRESHOLD": 1
  },
  "Mo": {
    "INTERVAL_FRAME_NUMBER": 10,
    "INTERVAL_NUM": 1,
    "FRAME_THRESHOLD": 8,
    "INTERVAL_THRESHOLD": 1
  },
  "Eu": {
    "INTERVAL_FRAME_NUMBER": 10,
    "INTERVAL_NUM": 5,
    "FRAME_THRESHOLD": 4,
    "INTERVAL_THRESHOLD": 3
  },
  "Ne": {
    "INTERVAL_FRAME_NUMBER": 10,
    "INTERVAL_NUM": 5,
    "FRAME_THRESHOLD": 4,
    "INTERVAL_THRESHOLD": 3
  }
}
```

conf_config.json

```json
{
  "Gs": 0.25,
  "Mo": 0.25,
  "Do": 0.25,
  "Eu": 0.25,
  "Ne": 0.25,
  "Ar": 0.25
}
```
