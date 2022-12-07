<h2 align="center">BICEP CURL MODEL TRAINING PROCESS</h2>

### 1. Folder structure

```
plank_model
│   1.data.ipynb - process collected videos
|   2.sklearn.ipynb - train models using Sklearn ML algo
│   3.deep_leaning.ipynb - train models using Deep Learning
│   4.evaluation.ipynb - evaluate trained models
│   5.detection.ipynb - detection on test videos
|   kaggle.csv - data gathered from Kaggle dataset
|   train.csv - train dataset after converted from videos
|   test.csv - test dataset after converted from videos
|   evaluation.csv - models' evaluation results
│
└───model/ - folder contains best trained models and input scaler
│   │
```

### 2. Important landmarks

There are 3 popular errors of basic plank that will be targeted in this thesis:

-   High lower back: while performing the exercise, instead of keeping the lower back straight, it is raised too high.
-   Low lower back: while performing the exercise, instead of keeping the lower back straight, it is brought down too low.

In my research and exploration, **_the important MediaPipe Pose landmarks_** for this exercise are: nose, left shoulder, right shoulder, right elbow, left elbow, right wrist, left wrist, right hip, left hip, right knee, left knee, right ankle, left ankle, right heel, left heel, right foot index and left foot index

### 3. Error detection method

Machine learning will be used the errors of this exercise. See this [notebook](./4.evaluation.ipynb) for a evaluation process for this model.
