# EDA results

Shape: (889, 14)

Missing percentages before cleaning: {'age': 19.87, 'embarked': 0.22, 'deck': 77.22, 'embark_town': 0.22}

IQR outlier counts: {'age': 65, 'fare': 114}

Fare mean=32.097, median=14.454, mode=8.050; conclusion: right-skewed.



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

### Correlation interpretation
Top absolute correlations: pclass–fare=-0.548; sibsp–parch=0.415