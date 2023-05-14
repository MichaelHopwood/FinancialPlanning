# FinancialPlanning
Financial planning, especially for those in tech looking to buy a house.

Feel free to submit an issue or PR if you find areas for improvement.

## 1. Install packages
```cmd
pip install -r requirements.txt
```

## 2. Run financial scenario
```cmd
python mortgage.py --cfg settings.yml
```

The current code assumes you sell at same price that you bought it, considering the most probable "worst" case. Certainly, this is unlikely.

```cmd
Annual results:
      savings_mortgage  house_worth_postsale  savings_rent  investments      roth      401k  net_worth_mortgage  net_worth_rent
2023          29988.73              -1578.51      59436.41      62500.0    2750.0   11250.0           104910.22       135936.41
2024          98076.70              15187.13     147668.05     125000.0    8250.0   33750.0           280263.83       314668.05
2025         134843.07              32964.72     206142.48     187500.0   13750.0   56250.0           425307.79       463642.48
2026         174599.64              51815.33     269058.59     250000.0   19250.0   78750.0           574414.97       617058.59
2027         239334.22              71803.74     356336.91     250000.0   24750.0  101250.0           687137.96       732336.91
2028         308968.21              92998.61     450167.00     250000.0   30250.0  123750.0           805966.82       854167.00
2029         383789.98             115472.74     550933.36     250000.0   35750.0  146250.0           931262.72       982933.36
2030         464103.15             139303.38     659040.77     250000.0   41250.0  168750.0          1063406.53      1119040.77
2031         550227.31             164572.39     774915.27     250000.0   46750.0  191250.0          1202799.70      1262915.27
2032         642498.83             191366.59     899005.27     250000.0   52250.0  213750.0          1349865.42      1415005.27
2033         741271.71             219778.04    1031782.60     250000.0   57750.0  236250.0          1505049.75      1575782.60
2034         846918.43             249904.38    1173743.71     250000.0   63250.0  258750.0          1668822.81      1745743.71
2035         959830.84             281849.07    1325410.86     250000.0   68750.0  281250.0          1841679.91      1925410.86
2036        1080421.18             315721.86    1487333.39     250000.0   74250.0  303750.0          2024143.04      2115333.39
2037        1209123.02             351639.15    1660089.07     250000.0   79750.0  326250.0          2216762.17      2316089.07
2038        1381337.19             370400.00    1844285.47     250000.0   85250.0  348750.0          2435737.19      2528285.47
2039        1601726.03             370400.00    2040561.43     250000.0   90750.0  371250.0          2684126.03      2752561.43
2040        1837535.83             370400.00    2249588.62     250000.0   96250.0  393750.0          2947935.83      2989588.62
2041        2089647.66             370400.00    2472073.08     250000.0  101750.0  416250.0          3228047.66      3240073.08
2042        2358988.38             370400.00    2708756.96     250000.0  107250.0  438750.0          3525388.38      3504756.96
2043        2506493.75             370400.00    2838737.34     250000.0  110000.0  450000.0          3686893.75      3648737.34

Monthly results:
            savings_mortgage  house_worth_postsale  savings_rent  investments       roth      401k  net_worth_mortgage  net_worth_rent
2023-07-01          29917.11              -8279.36      51412.17      62500.0     458.33    1875.0            86471.08       116245.50
2023-08-01          29931.88              -6952.25      52997.27      62500.0     916.67    3750.0            90146.30       120163.93
2023-09-01          29946.44              -5618.64      54592.19      62500.0    1375.00    5625.0            93827.80       124092.19
2023-10-01          29960.76              -4278.50      56197.00      62500.0    1833.33    7500.0            97515.60       128030.33
2023-11-01          29974.86              -2931.80      57811.72      62500.0    2291.67    9375.0           101209.73       131978.39
...                      ...                   ...           ...          ...        ...       ...                 ...             ...
2043-02-01        2407618.80             370400.00    2751636.49     250000.0  108166.67  442500.0          3578685.46      3552303.16
2043-03-01        2432134.84             370400.00    2773243.23     250000.0  108625.00  444375.0          3605534.84      3576243.23
2043-04-01        2456785.60             370400.00    2794961.95     250000.0  109083.33  446250.0          3632518.94      3600295.29
2043-05-01        2481571.70             370400.00    2816793.15     250000.0  109541.67  448125.0          3659638.36      3624459.82
2043-06-01        2506493.75             370400.00    2838737.34     250000.0  110000.00  450000.0          3686893.75      3648737.34
```


## 3. Run a grid search across a financial scenario

This allows you to changes values on the parameters within `settings.yml` and observe how it effects net worth.

```cmd
python mortgage.py --cfg settings_optimize.yml
```

For example, let's see how different mortgage payment plans impact the net worth.

```cmd
          onetime_extra_payment  loan_duration  net_worth_mortgage  net_worth_rent
0             {0: 0.0, 12: 0.0}             10          3813279.44      3648737.34
1             {0: 0.0, 12: 0.0}             15          3686893.75      3648737.34
2             {0: 0.0, 12: 0.0}             20          3457974.09      3648737.34
3             {0: 0.0, 12: 0.0}             30          3397480.97      3648737.34
4        {0: 0.0, 12: 100000.0}             10                 NaN      3648737.34
5        {0: 0.0, 12: 100000.0}             15                 NaN      3648737.34
6        {0: 0.0, 12: 100000.0}             20                 NaN      3648737.34
7        {0: 0.0, 12: 100000.0}             30                 NaN      3648737.34
8        {0: 100000.0, 12: 0.0}             10                 NaN      3648737.34
9        {0: 100000.0, 12: 0.0}             15                 NaN      3648737.34
10       {0: 100000.0, 12: 0.0}             20                 NaN      3648737.34
11       {0: 100000.0, 12: 0.0}             30                 NaN      3648737.34
12  {0: 100000.0, 12: 100000.0}             10                 NaN      3648737.34
13  {0: 100000.0, 12: 100000.0}             15                 NaN      3648737.34
14  {0: 100000.0, 12: 100000.0}             20                 NaN      3648737.34
15  {0: 100000.0, 12: 100000.0}             30                 NaN      3648737.34
Note: `NaN` values indicate that your cash savings balance had < $0 at some point in time.
```
