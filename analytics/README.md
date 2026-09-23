# Analytics Pipeline

Run `python analytics/analysis.py` from the repository root. The script calls `sns.load_dataset('titanic')` once, saves the raw offline copy as `artifacts/titanic_raw.csv`, applies the documented missing-value strategies, and saves the cleaned continuation dataset as `analytics/titanic.csv`.

Missingness below 5% is handled by dropping affected rows. Missingness between 5% and 30% is imputed: median for `age` and mode for `embarked`. The high-missingness `deck` column is dropped because imputing it would not be reliable. The report records the measured percentages.

The script writes EDA charts, the exact six-column correlation heatmap, standardization checks, classifier metrics, imbalance comparisons, ROC curves, a labeled decision-tree visualization, a fare residual plot, a grid-search/OOB report, and `artifacts/best_pipeline.joblib`. The saved joblib artifact includes preprocessing and the estimator together and is reloaded against raw test rows as a check.

All modeling preprocessing is fit on the training split only. The train/test split is stratified on `survived`, and SMOTE is applied only after transforming the training fold. Classifier metrics and regression metrics are reported as separate groups.

## References

[1]: https://seaborn.pydata.org/generated/seaborn.load_dataset.html "Seaborn dataset loader"
[2]: https://scikit-learn.org/stable/modules/compose.html "Scikit-learn pipelines and column transformers"
[3]: https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.SMOTE.html "Imbalanced-learn SMOTE documentation"
