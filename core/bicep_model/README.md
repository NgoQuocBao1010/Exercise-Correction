<h2 align="center">BICEP CURL MODEL TRAINING PROCESS</h2>

### 1. Folder structure

```
bicep_model
│   1.data.ipynb - process collected videos
|   2.sklearn.ipynb - train models using Sklearn ML algo
│   3.deep_leaning.ipynb - train models using Deep Learning
│   4.evaluation.ipynb - evaluate trained models
│   5.detection.ipynb - detection on test videos
|   train.csv - train dataset after converted from videos
|   test.csv - test dataset after converted from videos
|   evaluation.csv - models' evaluation results
│
└───model/ - folder contains best trained models and input scaler
│   │
```

### 2. Important landmarks

There are 3 popular errors of bicep curl that will be targeted in this thesis:

-   Loose upper arm: when an arm moves upward during the exercise, the upper arm is moving instead of staying still.
-   Weak peak contraction: when an arm moves upward, it does not go high enough therefore not put enough contraction to the bicep.
-   Lean too far back: the performer’s torso leans back and fore during the exercise for momentum.

In my research and exploration, **_the important MediaPipe Pose landmarks_** for this exercise are: nose, left shoulder, right shoulder, right elbow, left elbow, right wrist, left wrist, right hip and left hip.

### 3. Error detection method

1. **Loose upper arm**: Can be detected by calculating the angle between the elbow, shoulder and the shoulder’s projection on the ground. Through my research, if the angle is over 40 degrees, the movement will be classified as a “loose upper arm” error

1. **Weak peak contraction**: Can be detected by calculating the angle between the wrist, elbow and shoulder when the performer’s arm is coming up. Through my research, if the angle is more than 60 degrees before the arm comes down, the movement will be classified as a “weak peak contraction” error.

1. **Lean too far back**: Due to its complexity, machine learning will be used for this detection. See this [notebook](./4.evaluation.ipynb) for a evaluation process for this model.
