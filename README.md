# FinancialPlanning
Financial planning, especially for those in tech looking to buy a house.

Feel free to submit an issue or PR if you find areas for improvement.


## How to run

### 1. Install packages
```cmd
pip install -r requirements.txt
```

### 2. Run financial scenario
```cmd
python mortgage.py --cfg settings.yml
```

### 3. Run a grid search across a financial scenario

This allows you to changes values on the parameters within `settings.yml` and observe how it effects net worth.

```cmd
python mortgage.py --cfg settings_optimize.yml
```


***

## Example output

The current code assumes you sell at same price that you bought it, considering the most probable "worst" case. Certainly, this is unlikely.

```cmd
##################################################
Savings if buying a house and selling even
##################################################
      Avg Monthly Savings  Annual Savings    Savings  MoneyBackFromHouse     Savings w/I        NetWorth
Year
1                 9396.81       112761.74  112761.74            66071.49   119527.444400   185598.934400
2                 9396.81       112761.74  225523.48            84155.75   253398.182128   337553.932128
3                 2438.02        29256.24  254779.72           103331.54   303446.722996   406778.262996
4                 2438.02        29256.24  284035.96           123664.76   358588.855311   482253.615311
5                 2938.02        35256.24  319292.20           145225.23   427284.988768   572510.218768
6                 2938.02        35256.24  354548.44           168087.07   502933.738361   671020.808361
7                 2938.02        35256.24  389804.68           192328.79   586122.111944   778450.901944
8                 2938.02        35256.24  425060.92           218033.70   677482.528900   895516.228900
9                 2938.02        35256.24  460317.16           245290.10   777696.156288  1022986.256288
10                2938.02        35256.24  495573.40           274191.66   887496.481858  1161688.141858
11                2938.02        35256.24  530829.64           304837.63  1007673.140334  1312510.770334
12                2938.02        35256.24  566085.88           337333.35  1139076.010492  1476409.360492
13                2938.02        35256.24  601342.12           371790.47  1282619.601764  1654410.071764
14                2938.02        35256.24  636598.36           408327.33  1439287.750351  1847615.080351
15                2938.02        35256.24  671854.60           447069.48  1610138.646202  2057208.126202


##################################################
Savings if not buying a house
##################################################
      Avg Monthly Savings  Annual Savings    Savings     Savings w/I        NetWorth
Year
1                17545.96        210551.5   210551.5   223184.590000   223184.590000
2                10879.29        130551.5   341103.0   383263.330800   383263.330800
3                 3920.50         47046.0   388149.0   462291.669384   462291.669384
4                 3920.50         47046.0   435195.0   549423.660607   549423.660607
5                 4420.50         53046.0   488241.0   653376.594233   653376.594233
6                 4420.50         53046.0   541287.0   767825.954716   767825.954716
7                 4420.50         53046.0   594333.0   893657.082717   893657.082717
8                 4420.50         53046.0   647379.0  1031823.772642  1031823.772642
9                 4420.50         53046.0   700425.0  1183353.299859  1183353.299859
10                4420.50         53046.0   753471.0  1349351.804762  1349351.804762
11                4420.50         53046.0   806517.0  1531010.058373  1531010.058373
12                4420.50         53046.0   859563.0  1729609.635920  1729609.635920
13                4420.50         53046.0   912609.0  1946529.526563  1946529.526563
14                4420.50         53046.0   965655.0  2183253.209394  2183253.209394
15                4420.50         53046.0  1018701.0  2441376.227869  2441376.227869
Total savings is cash savings = 1018701.0. And 100000 total RSUs (have to pay capital gain/loss when sell)
Also likely doesn't come with parking spot (i.e. $200/mo extra)
```


## Example optimization

The below experiments run the same analysis seen above but for different parameterizations. The resulting analysis shows the effect of choosing the right house financing plan. The `SumViolatedMonthlyLowEarnings` column is a custom column made to notate the total amount of monthly savings below $2000 for all months in the evaluation period. In an effort to be safe financially (and not spend all of income), we'd want this column to be as low as possible, designating the build-up of liquid cash.

```cmd
          onetime_extra_payment  loan_duration   net_worth  net_worth_rent  SumViolatedMonthlyLowEarnings  SumViolatedMonthlyLowEarnings_rent
0             {0: 0.0, 12: 0.0}             10  2198810.47      2441376.23                        3043.36                                 0.0
1             {0: 0.0, 12: 0.0}             15  2057208.13      2441376.23                           0.00                                 0.0
2             {0: 0.0, 12: 0.0}             20  2077661.16      2441376.23                           0.00                                 0.0
3             {0: 0.0, 12: 0.0}             30  2091714.74      2441376.23                           0.00                                 0.0
4        {0: 0.0, 12: 100000.0}             10  1959154.65      2441376.23                        5173.32                                 0.0
5        {0: 0.0, 12: 100000.0}             15  1817552.31      2441376.23                         936.52                                 0.0
6        {0: 0.0, 12: 100000.0}             20  1838005.34      2441376.23                         540.97                                 0.0
7        {0: 0.0, 12: 100000.0}             30  1852058.93      2441376.23                         182.44                                 0.0
8        {0: 100000.0, 12: 0.0}             10  1959154.65      2441376.23                        5173.32                                 0.0
9        {0: 100000.0, 12: 0.0}             15  1817552.31      2441376.23                         936.52                                 0.0
10       {0: 100000.0, 12: 0.0}             20  1838005.34      2441376.23                         540.97                                 0.0
11       {0: 100000.0, 12: 0.0}             30  1852058.93      2441376.23                         182.44                                 0.0
12  {0: 100000.0, 12: 100000.0}             10  1719498.83      2441376.23                        7303.28                                 0.0
13  {0: 100000.0, 12: 100000.0}             15  1577896.49      2441376.23                        1873.04                                 0.0
14  {0: 100000.0, 12: 100000.0}             20  1598349.52      2441376.23                        1081.94                                 0.0
15  {0: 100000.0, 12: 100000.0}             30  1612403.11      2441376.23                         364.88                                 0.0
```
