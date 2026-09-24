# Modeling results

## Classifiers

| model               |   accuracy |   precision |   recall |       f1 |      auc | confusion_matrix     |
|:--------------------|-----------:|------------:|---------:|---------:|---------:|:---------------------|
| Logistic Regression |   0.808989 |    0.783333 | 0.691176 | 0.734375 | 0.860963 | [[97, 13], [21, 47]] |
| Decision Tree       |   0.764045 |    0.76     | 0.558824 | 0.644068 | 0.837366 | [[98, 12], [30, 38]] |
| Random Forest       |   0.808989 |    0.765625 | 0.720588 | 0.742424 | 0.819586 | [[95, 15], [19, 49]] |



## Class balance

The classification target balance is: not_survived: 549 (61.8%); survived: 340 (38.2%). Stratification preserves this distribution in both train and test splits so evaluation is not distorted by a changed class mix.



## Imbalance comparison

| variant               |   precision |   recall |       f1 |
|:----------------------|------------:|---------:|---------:|
| baseline              |    0.777778 | 0.720588 | 0.748092 |
| class_weight_balanced |    0.73913  | 0.75     | 0.744526 |
| SMOTE_train_only      |    0.753846 | 0.720588 | 0.736842 |



## Grid search
Best parameters: `{'max_depth': 5, 'max_features': 'sqrt', 'n_estimators': 200}`
OOB score after refit: `0.8214`



## Regression

|     MAE |    RMSE |       R2 |   Adjusted_R2 |
|--------:|--------:|---------:|--------------:|
| 21.0986 | 41.7021 | 0.348163 |       0.30913 |

Residual absolute-magnitude correlation with fitted values: `0.135`. The residual plot does not show strong evidence of heteroscedasticity by the residual-magnitude correlation check.



## Final classifier recommendation

Deploy Random Forest: it has the strongest combined F1 (0.742) and AUC (0.820) among the evaluated classifiers. This recommendation prioritizes balanced classification quality while retaining discrimination performance. Confirm the operational error costs before production use.



Reload check predictions: `[0, 0, 0]`