<h2 align="center">Build Machine Learning Model</h2>

Brief overview about the methodology of building models for exercise pose detection.
To go in depth on each exercise, click the link below:

-   [Bicep Curl](./bicep_model/README.md)
-   [Plank](./plank_model/README.md)
-   [Basic Squat](./squat_model/README.md)
-   [Lunge](./lunge_model/README.md)

### 1. Simple error detection

For some simple errors (for example, the feet placement error in squat), the detection method is either measuring the distance/angle between different joints during the exercise with the coordinate outputs from MediaPipe Pose.

-   **_Distance Calculation_**
    Assume there are 2 points with the following coordinates: Point 1 (x1,y1) and Point 2 (x2,y2), below is the formula to calculate the distance between 2 points.

    ```
    distance= √((x1-x2)^2 +(y1-y2) ^2 )
    ```

-   **_Angle Calculation_**
    Assume there are 3 points with the following coordinates: Point 1 (x1,y1), Point 2 (x2,y2) and Point 3 (x3,y3), below is the formula to calculate the angle created by 3 points.
    ```
    angle_in_radian =arctan2⁡(y3-y2,x3-x2) -arctan2(y1-y2,x1-x2)
    angle_in_degree=(angle_in_rad \* 180)/Π
    ```

### 2. Model Training for Error Detection

#### 1. Pick important landmarks

For each exercise, there will be different poses/body’s position, therefore it is essential to identify which parts (shoulder, hip, …) of a body are contribute to the exercise. The important landmarks identified for each exercise are utilized to extract body part’s position while exercising using MediaPipe.

#### 2. Data Processing

 <p align="center"><img src="../images/data_processing.png" alt="Logo" width="70%" style="background-color:#f5f5f5"></p>

#### 3. Model training

There are 2 methods used in this thesis for model training. For each exercise, the models trained for each method will be compared and the best model will be chosen.

-   Classification with Scikit-learn. (Decision Tree/Random Forest (RF), K-Nearest Neighbors (KNN), C-Support Vector (SVC), Logistic Regression classifier (LR) and Stochastic Gradient Descent classifier (SGDC)).
-   Building a Neural Network for classification with Keras.

### 3. Evaluation results of all models

1. Bicep Curl - _lean back error_
 <p align="center"><img src="../images/bicep_curl_eval_3.png" alt="Logo" width="70%"></p>

2. Plank - _all errors_
 <p align="center"><img src="../images/plank_eval_3.png" alt="Logo" width="70%"></p>

3. Basic Squat - _stage_
 <p align="center"><img src="../images/squat_eval_3.png" alt="Logo" width="70%"></p>

4. Lunge - _knee over toe error_
 <p align="center"><img src="../images/lunge_eval_3.png" alt="Logo" width="70%"></p>
