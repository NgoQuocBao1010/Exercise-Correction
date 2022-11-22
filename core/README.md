<h2 align="center">Build Machine Learning Model</h2>

### 1. Plank

Work models:

1. [Sklearn LR model](./plank_model/model/LR_model.pkl)
1. [Sklearn RF model](./plank_model/model/RF_model.pkl)
1. [Deep leaning model](./plank_model/model/plank_model_deep_learning.pkl)

3 models work fine, but I'll choose the LR as it is easier to deploy for website.

### 2. Bicep

Work models:

1. [Sklearn KNN model](./bicep_model/model/KNN_model.pkl)
1. [Deep leaning model](./bicep_model/model/bicep_model_deep_learning.pkl)

As from the test results, the KNN model yield better predictions.

### 3. Squat

Work models:

1. [Sklearn KNN model](./squat_model/model/KNN_model.pkl)

As from the test results, the KNN model yield better predictions.

### 4. Lunge

Work models for error detection:

1. [Sklearn LR model](./lunge_model/model/sklearn/err_LR_model.pkl)
1. [Deep leaning model](./lunge_model/model/dp/err_lunge_dp.pkl)

Work models for stage prediction:

1. [SKlearn KNN model](./lunge_model/model/sklearn/stage_KNN_model.pkl)
