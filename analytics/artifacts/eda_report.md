# EDA results

Shape: (889, 14)

Missing percentages before cleaning: {'age': 19.87, 'embarked': 0.22, 'deck': 77.22, 'embark_town': 0.22}

IQR outlier counts: {'age': 65, 'fare': 114}

Fare mean=32.097, median=14.454, mode=8.050; conclusion: right-skewed.



Boolean-mask survival checks:

{
  "female_and_first_class": 96.74,
  "male_and_first_class": 36.89,
  "female_or_under_18": 68.65
}



Two strongest absolute off-diagonal correlations:

- pclass and fare: -0.548

- sibsp and parch: 0.415



Chart interpretations:

### Survival by sex
Survival differs materially by sex:
sex
female    74.04
male      18.89

### Survival by pclass
Survival differs materially by pclass:
pclass
1    62.62
2    47.28
3    24.24

### Survival by sex and class
sex     pclass
female  1         96.74
        2         92.11
        3         50.00
male    1         36.89
        2         15.74
        3         13.54

### Boolean-mask checks
{
  "female_and_first_class": 96.74,
  "male_and_first_class": 36.89,
  "female_or_under_18": 68.65
}

### Correlation interpretation
Top absolute correlations: pclass–fare=-0.548; sibsp–parch=0.415

### Survival by sex and class chart
Women survive at higher rates than men in every passenger class, while first-class passengers have the strongest outcomes overall. The especially large gap between female and male survival shows that sex and socioeconomic position jointly describe survival likelihood.

### Age distribution by class and outcome chart
The age distributions overlap across survival outcomes, but age composition differs by passenger class. This indicates that age contributes context while class and sex remain important structural predictors.

### Age, fare, sex, and survival chart
The scatter plot shows that survivors are concentrated more often among females and higher-fare observations. The overlap between outcomes confirms that no single feature perfectly separates survival, supporting the use of a multivariate model.

### Survival by embarkation and class chart
Survival rates vary by embarkation port within passenger class, although class remains a stronger organizing pattern than port alone. The chart suggests that embarkation may capture differences in passenger mix and socioeconomic composition.