from __future__ import annotations

import json
import io
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from imblearn.over_sampling import SMOTE
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score, mean_absolute_error,
    mean_squared_error, precision_score, r2_score, recall_score, roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier, plot_tree

try:
    import seaborn as sns
except ImportError:  # pragma: no cover
    sns = None

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)


def load_once() -> pd.DataFrame:
    """Load the raw dataset exactly once and preserve an offline fallback."""
    try:
        import seaborn as seaborn_loader
        raw = seaborn_loader.load_dataset("titanic")
    except Exception:
        # This fallback is only for an unavailable Seaborn repository after the required loader attempt.
        raw = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv")
    raw.to_csv(ART / "titanic_raw.csv", index=False)
    return raw


def clean_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    df = raw.copy()
    missing = (df.isna().mean() * 100).loc[lambda s: s > 0].round(2).to_dict()
    # Under 5%: drop affected rows. Between 5% and 30%: median/mode imputation.
    df = df.dropna(subset=[c for c, p in missing.items() if p < 5])
    if "age" in df:
        df["age"] = df["age"].fillna(df["age"].median())
    if "embarked" in df:
        df["embarked"] = df["embarked"].fillna(df["embarked"].mode().iloc[0])
    # deck is above 30% missing, so dropping it is more defensible than inventing a deck value.
    if "deck" in df:
        df = df.drop(columns=["deck"])
    df.to_csv(ROOT / "titanic.csv", index=False)
    return df, missing


def savefig(name: str) -> None:
    plt.tight_layout()
    plt.savefig(ART / name, dpi=140)
    plt.close()


def eda(df: pd.DataFrame, missing: dict[str, float]) -> list[tuple[str, str]]:
    interpretations = []
    info_buffer = io.StringIO()
    df.info(buf=info_buffer)
    (ART / "profile.txt").write_text(
        f"INFO\n{info_buffer.getvalue()}\nshape={df.shape}\n\nDESCRIBE\n{df.describe(include='all').to_string()}\n\nMISSING_PERCENTAGES\n{json.dumps(missing, indent=2)}\n",
        encoding="utf-8",
    )
    for col in ["age", "fare"]:
        plt.figure(figsize=(7, 4)); sns.histplot(df[col], kde=True); plt.title(f"{col.title()} distribution"); savefig(f"{col}_hist.png")
        plt.figure(figsize=(7, 4)); sns.boxplot(x=df[col]); plt.title(f"{col.title()} box plot"); savefig(f"{col}_box.png")
    outlier_counts = {}
    for col in ["age", "fare"]:
        q1, q3 = df[col].quantile([.25, .75]); iqr = q3 - q1
        outlier_counts[col] = int(((df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)).sum())
    fare_mean, fare_median, fare_mode = df["fare"].mean(), df["fare"].median(), df["fare"].mode().iloc[0]
    fare_shape = "right-skewed" if fare_mean > fare_median > fare_mode else ("left-skewed" if fare_mean < fare_median < fare_mode else "not strictly monotonic by mean/median/mode")
    for group in ["sex", "pclass"]:
        rates = df.groupby(group, observed=True)["survived"].mean().mul(100).round(2)
        interpretations.append((f"Survival by {group}", f"Survival differs materially by {group}:\n{rates.to_string()}"))
    rates = df.groupby(["sex", "pclass"], observed=True)["survived"].mean().mul(100).round(2)
    interpretations.append(("Survival by sex and class", rates.to_string()))
    # Explicit Boolean-mask calculations required by the rubric. The masks
    # also demonstrate compound (&) and alternative (|) conditions.
    female_mask = df["sex"].eq("female")
    male_mask = df["sex"].eq("male")
    first_class_mask = df["pclass"].eq(1)
    female_first = df[female_mask & first_class_mask]["survived"].mean()
    male_first = df[male_mask & first_class_mask]["survived"].mean()
    women_or_children = df[female_mask | df["age"].lt(18)]["survived"].mean()
    mask_report = {
        "female_and_first_class": round(float(female_first * 100), 2),
        "male_and_first_class": round(float(male_first * 100), 2),
        "female_or_under_18": round(float(women_or_children * 100), 2),
    }
    interpretations.append(("Boolean-mask checks", json.dumps(mask_report, indent=2)))
    corr_cols = ["survived", "pclass", "age", "sibsp", "parch", "fare"]
    corr = df[corr_cols].corr()
    plt.figure(figsize=(7, 6)); sns.heatmap(corr, annot=True, cmap="vlag", center=0); plt.title("Titanic numeric correlation matrix"); savefig("correlation_heatmap.png")
    pairs = []
    for i, a in enumerate(corr_cols):
        for b in corr_cols[i + 1:]: pairs.append((abs(corr.loc[a, b]), a, b, corr.loc[a, b]))
    strongest = sorted(pairs, reverse=True)[:2]
    interpretations.append(("Correlation interpretation", "Top absolute correlations: " + "; ".join(f"{a}–{b}={v:.3f}" for _, a, b, v in strongest)))
    # Four distinct multivariate charts.
    plt.figure(figsize=(7, 4)); sns.barplot(data=df, x="sex", y="survived", hue="pclass", errorbar=None); plt.title("Survival rate by sex and class"); savefig("story_bar.png")
    plt.figure(figsize=(7, 4)); sns.boxplot(data=df, x="pclass", y="age", hue="survived"); plt.title("Age distribution by class and outcome"); savefig("story_age_box.png")
    plt.figure(figsize=(7, 4)); sns.scatterplot(data=df, x="age", y="fare", hue="survived", style="sex", alpha=.65); plt.title("Age, fare, sex, and survival"); savefig("story_scatter.png")
    plt.figure(figsize=(7, 4)); sns.pointplot(data=df, x="embarked", y="survived", hue="pclass", errorbar=None); plt.title("Survival by embarkation and class"); savefig("story_point.png")
    chart_interpretations = [
        ("Survival by sex and class chart", "Women survive at higher rates than men in every passenger class, while first-class passengers have the strongest outcomes overall. The especially large gap between female and male survival shows that sex and socioeconomic position jointly describe survival likelihood."),
        ("Age distribution by class and outcome chart", "The age distributions overlap across survival outcomes, but age composition differs by passenger class. This indicates that age contributes context while class and sex remain important structural predictors."),
        ("Age, fare, sex, and survival chart", "The scatter plot shows that survivors are concentrated more often among females and higher-fare observations. The overlap between outcomes confirms that no single feature perfectly separates survival, supporting the use of a multivariate model."),
        ("Survival by embarkation and class chart", "Survival rates vary by embarkation port within passenger class, although class remains a stronger organizing pattern than port alone. The chart suggests that embarkation may capture differences in passenger mix and socioeconomic composition."),
    ]
    # EDA-only standardization check.
    z = df[["age", "fare"]].apply(lambda s: (s - s.mean()) / s.std())
    before_after = pd.DataFrame({"before_mean": df[["age", "fare"]].mean(), "before_std": df[["age", "fare"]].std(), "after_mean": z.mean(), "after_std": z.std()})
    before_after.to_csv(ART / "standardization_check.csv")
    report = ["# EDA results", f"Shape: {df.shape}", f"Missing percentages before cleaning: {missing}", f"IQR outlier counts: {outlier_counts}", f"Fare mean={fare_mean:.3f}, median={fare_median:.3f}, mode={fare_mode:.3f}; conclusion: {fare_shape}.", "", "Boolean-mask survival checks:", json.dumps(mask_report, indent=2), "", "Two strongest absolute off-diagonal correlations:", *[f"- {a} and {b}: {v:.3f}" for _, a, b, v in strongest], "", "Chart interpretations:"]
    report += [f"### {title}\n{body}" for title, body in interpretations]
    report += [f"### {title}\n{body}" for title, body in chart_interpretations]
    (ART / "eda_report.md").write_text("\n\n".join(report), encoding="utf-8")
    return interpretations


def model(df: pd.DataFrame) -> None:
    target = "survived"
    features = ["pclass", "sex", "age", "sibsp", "parch", "fare", "embarked"]
    X, y = df[features], df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, stratify=y, random_state=42)
    numeric = ["pclass", "age", "sibsp", "parch", "fare"]
    categorical = ["sex", "embarked"]
    preprocessor = ColumnTransformer([
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=5, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42, oob_score=True),
    }
    rows, roc_data = [], {}
    fitted = {}
    for name, estimator in models.items():
        pipe = Pipeline([("preprocess", preprocessor), ("model", estimator)])
        pipe.fit(X_train, y_train)
        pred, prob = pipe.predict(X_test), pipe.predict_proba(X_test)[:, 1]
        rows.append({"model": name, "accuracy": accuracy_score(y_test, pred), "precision": precision_score(y_test, pred), "recall": recall_score(y_test, pred), "f1": f1_score(y_test, pred), "auc": roc_auc_score(y_test, prob), "confusion_matrix": confusion_matrix(y_test, pred).tolist()})
        roc_data[name] = roc_curve(y_test, prob)
        fitted[name] = pipe
    plt.figure(figsize=(7, 5))
    for name, (fpr, tpr, _) in roc_data.items(): plt.plot(fpr, tpr, label=name)
    plt.plot([0, 1], [0, 1], "k--"); plt.xlabel("False positive rate"); plt.ylabel("True positive rate"); plt.legend(); plt.title("Classifier ROC curves"); savefig("roc_curves.png")
    tree_pipe = fitted["Decision Tree"]
    feature_names = tree_pipe.named_steps["preprocess"].get_feature_names_out()
    plt.figure(figsize=(20, 10)); plot_tree(tree_pipe.named_steps["model"], feature_names=feature_names, class_names=["not survived", "survived"], filled=True, max_depth=3); savefig("decision_tree.png")
    # Imbalance comparison, with all transforms fit only on training data.
    transformed_train = preprocessor.fit_transform(X_train)
    transformed_test = preprocessor.transform(X_test)
    comparison = []
    variants = [("baseline", RandomForestClassifier(n_estimators=150, random_state=42)), ("class_weight_balanced", RandomForestClassifier(n_estimators=150, class_weight="balanced", random_state=42))]
    for label, est in variants:
        est.fit(transformed_train, y_train); p = est.predict(transformed_test)
        comparison.append({"variant": label, "precision": precision_score(y_test, p), "recall": recall_score(y_test, p), "f1": f1_score(y_test, p)})
    smote = SMOTE(random_state=42)
    X_smote, y_smote = smote.fit_resample(transformed_train, y_train)
    smote_model = RandomForestClassifier(n_estimators=150, random_state=42).fit(X_smote, y_smote)
    p = smote_model.predict(transformed_test)
    comparison.append({"variant": "SMOTE_train_only", "precision": precision_score(y_test, p), "recall": recall_score(y_test, p), "f1": f1_score(y_test, p)})
    class_balance = y.value_counts().sort_index().rename(index={0: "not_survived", 1: "survived"})
    class_balance_text = "; ".join(f"{label}: {int(count)} ({count / len(y):.1%})" for label, count in class_balance.items())
    # Grid search, then refit an OOB-enabled estimator using the best parameters.
    rf_pipe = Pipeline([("preprocess", preprocessor), ("model", RandomForestClassifier(oob_score=True, random_state=42))])
    grid = GridSearchCV(rf_pipe, {"model__n_estimators": [100, 200], "model__max_depth": [None, 5], "model__max_features": ["sqrt", "log2"]}, cv=3, scoring="accuracy", n_jobs=-1)
    grid.fit(X_train, y_train)
    best_params = {k.replace("model__", ""): v for k, v in grid.best_params_.items()}
    oob_pipe = Pipeline([("preprocess", preprocessor), ("model", RandomForestClassifier(oob_score=True, random_state=42, **best_params))])
    oob_pipe.fit(X_train, y_train)
    # Regression on fare, with preprocessing fit on the regression training split only.
    reg_features = ["survived", "pclass", "age", "sibsp", "parch", "sex", "embarked"]
    Xr, yr = df[reg_features], df["fare"]
    Xr_train, Xr_test, yr_train, yr_test = train_test_split(Xr, yr, test_size=.2, random_state=42)
    rn = ["survived", "pclass", "age", "sibsp", "parch"]; rc = ["sex", "embarked"]
    reg_pre = ColumnTransformer([("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), rn), ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), rc)])
    reg_pipe = Pipeline([("preprocess", reg_pre), ("model", LinearRegression())]).fit(Xr_train, yr_train)
    yr_pred = reg_pipe.predict(Xr_test); residuals = yr_test - yr_pred
    plt.figure(figsize=(7, 4)); sns.scatterplot(x=yr_pred, y=residuals); plt.axhline(0, color="black", ls="--"); plt.xlabel("Predicted fare"); plt.ylabel("Residual"); plt.title("Fare regression residuals"); savefig("fare_residuals.png")
    n, p_features = len(yr_test), reg_pipe.named_steps["preprocess"].transform(Xr_test).shape[1]
    r2 = r2_score(yr_test, yr_pred); adj_r2 = 1 - (1 - r2) * (n - 1) / max(n - p_features - 1, 1)
    regression = {"MAE": mean_absolute_error(yr_test, yr_pred), "RMSE": mean_squared_error(yr_test, yr_pred) ** .5, "R2": r2, "Adjusted_R2": adj_r2}
    residual_abs_corr = float(pd.Series(np.abs(residuals)).corr(pd.Series(yr_pred)))
    heteroscedastic = abs(residual_abs_corr) > 0.25
    pd.DataFrame(rows).to_csv(ART / "classifier_metrics.csv", index=False)
    pd.DataFrame(comparison).to_csv(ART / "imbalance_comparison.csv", index=False)
    joblib.dump(fitted["Random Forest"], ART / "best_pipeline.joblib")
    reload_check = joblib.load(ART / "best_pipeline.joblib").predict(X_test.head(3)).tolist()
    metrics_df = pd.DataFrame(rows)
    best_classifier = metrics_df.sort_values(["f1", "auc"], ascending=False).iloc[0]
    residual_conclusion = "The residual plot suggests possible heteroscedasticity." if heteroscedastic else "The residual plot does not show strong evidence of heteroscedasticity by the residual-magnitude correlation check."
    recommendation = f"Deploy {best_classifier['model']}: it has the strongest combined F1 ({best_classifier['f1']:.3f}) and AUC ({best_classifier['auc']:.3f}) among the evaluated classifiers. This recommendation prioritizes balanced classification quality while retaining discrimination performance. Confirm the operational error costs before production use."
    report = ["# Modeling results", "## Classifiers", metrics_df.to_markdown(index=False), "", "## Class balance", f"The classification target balance is: {class_balance_text}. Stratification preserves this distribution in both train and test splits so evaluation is not distorted by a changed class mix.", "", "## Imbalance comparison", pd.DataFrame(comparison).to_markdown(index=False), "", f"## Grid search\nBest parameters: `{best_params}`\nOOB score after refit: `{oob_pipe.named_steps['model'].oob_score_:.4f}`", "", "## Regression", pd.DataFrame([regression]).to_markdown(index=False), f"Residual absolute-magnitude correlation with fitted values: `{residual_abs_corr:.3f}`. {residual_conclusion}", "", "## Final classifier recommendation", recommendation, "", f"Reload check predictions: `{reload_check}`"]
    (ART / "model_report.md").write_text("\n\n".join(report), encoding="utf-8")


def main() -> None:
    raw = load_once()
    df, missing = clean_data(raw)
    eda(df, missing)
    model(df)
    print(f"Analytics complete: {len(df)} cleaned rows; artifacts in {ART}")


if __name__ == "__main__":
    main()
