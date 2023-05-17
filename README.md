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

The key columns to look at here are `net_worth_mortgage` and `net_worth_rent`. The other columns break down the components of net worth. The `net_worth_mortgage` column adds all values except `savings_rent`. If you have substantial savings or investments that you want to be counted in the net worth computation, then specify the parameters in `settings.yml` placed under the "Current net-worth settings" title.

```cmd
Annual results:
      savings_mortgage  house_profit  savings_rent  investments       roth        401k  net_worth_mortgage  net_worth_rent
2023          29480.49     -21645.97      58928.18     64287.01    3342.92    11571.66            87036.12       138129.78
2024          96490.99      -5253.45     146082.35    137574.21   10730.79    37145.04           276687.58       331532.39
2025         132094.52      11806.93     203393.93    220806.61   19136.57    66241.98           450086.61       509579.09
2026         170597.74      29562.38     265056.69    315017.43   28666.59    99230.49           643074.63       707971.20
2027         233983.12      48041.21     350985.81    337068.65   39437.03   136512.80           795042.81       864004.29
2028         302166.36      67272.90     443365.16    360663.45   51574.87   178528.41           960206.00      1034131.90
2029         375429.90      87288.11     542573.28    385909.90   65218.77   225757.29          1139603.97      1219459.24
2030         454071.05     108118.78     649008.67    412923.59   80520.10   278723.42          1334356.94      1421175.78
2031         538402.80     129798.12     763090.77    441828.24   97644.04   337998.60          1545671.81      1640561.65
2032         628754.58     152360.71     885261.02    472756.22  116770.79   404206.57          1774848.86      1878994.59
2033         725473.06     175842.53    1015983.96    505849.15  138096.82   478027.45          2023289.01      2137957.37
2034         828923.01     200281.04    1155748.30    541258.59  161836.32   560202.64          2292501.61      2419045.86
2035         939488.20     225715.22    1305068.22    579146.69  188222.68   651540.03          2584112.82      2723977.62
2036        1057572.33     252185.62    1464484.54    619686.96  217510.12   752919.66          2899874.69      3054601.29
2037        1183600.01     279734.46    1634566.05    663065.05  249975.52   865299.89          3241674.93      3412906.52
2038        1352962.63     308405.69    1815910.91    709479.60  285920.28   989724.05          3646492.25      3801034.84
2039        1570312.65     338245.03    2009148.06    759143.18  325672.42  1127327.62          4120700.89      4221291.27
2040        1802885.93     369300.06    2214938.71    812283.20  369588.86  1279346.04          4633404.08      4676156.80
2041        2051552.57     401620.33    2433977.98    869143.02  418057.79  1447123.13          5187496.85      5168301.93
2042        2317227.92     435257.38    2666996.50    929983.03  471501.40  1632120.22          5786089.96      5700601.15
2043        2462814.28     452586.38    2795057.87    961981.93  500230.60  1731567.47          6109180.66      5988837.88

Monthly results:
            savings_mortgage  house_profit  savings_rent  investments       roth        401k  net_worth_mortgage  net_worth_rent
2023-07-01          29833.77     -28285.33      51328.83     62500.00     541.67     1875.00            66465.11       116245.50
2023-08-01          29764.67     -26966.28      52830.05     62853.38    1089.46     3771.20            70512.43       120544.10
2023-09-01          29694.80     -25642.84      54340.55     63208.77    1643.43     5688.79            74592.94       124881.54
2023-10-01          29624.14     -24314.98      55860.38     63566.16    2203.63     7627.94            78706.89       129258.10
2023-11-01          29552.71     -22982.70      57389.57     63925.57    2770.11     9588.84            82854.53       133674.08
...                      ...           ...           ...          ...        ...         ...                 ...             ...
2043-02-01        2365225.19     440995.31    2709242.89    940529.28  480923.97  1664736.83          5892410.59      5795432.98
2043-03-01        2389422.23     443878.63    2730530.62    945847.17  485692.52  1681243.35          5946083.90      5843313.67
2043-04-01        2413752.35     446771.56    2751928.70    951195.13  490499.62  1697883.31          6000101.96      5891506.76
2043-05-01        2438216.16     449674.13    2773437.62    956573.33  495345.55  1714657.69          6054466.85      5940014.18
2043-06-01        2462814.28     452586.38    2795057.87    961981.93  500230.60  1731567.47          6109180.66      5988837.88
```

where 

`net_worth_mortgage = savings_mortgage + house_profit + investments + roth + 401k`

`net_worth_rent = savings_rent + investments + roth + 401k`

These numbers are visualized below (plots conducted inside `mortgage.py`):

<img src="imgs/net_worth_plot.png" alt="Net worth plot" title="Net worth plot">
<img src="imgs/net_worth_components_plot.png" alt="Net components worth plot" title="Net components worth plot">


**Note:** if you are curious about the estimations from more specific components of the savings_mortgage or savings_rent (etc.), more resolute termainal printouts are available if you increase the `verbose` parameter in your `settings.yml` file.

***


## 3. Run a grid search across a financial scenario

Using `settings_optimize.yml` (for example), changes to values on the parameters within `settings.yml` can be conducted to observe how it effects net worth.

```cmd
python mortgage.py --cfg settings_optimize.yml
```

For example, one can grid search the best loan duration, down payment, and optimal time to purchase a home.

```cmd
     amount_down  loan_duration  housePurchase_year_investigate  housePurchase_month_investigate  net_worth_mortgage  net_worth_rent
481     100000.0             10                            2024                                6          6232012.82      5988837.88
401      90000.0             10                            2024                                6          6224094.56      5988837.88
160      60000.0             10                            2024                                3          6217506.31      5988837.88
321      80000.0             10                            2024                                6          6216176.04      5988837.88
482     100000.0             10                            2024                                9          6211392.17      5988837.88
80       50000.0             10                            2024                                3          6208014.39      5988837.88
241      70000.0             10                            2024                                6          6206292.21      5988837.88
402      90000.0             10                            2024                                9          6203473.92      5988837.88
0        40000.0             10                            2024                                3          6198523.48      5988837.88
161      60000.0             10                            2024                                6          6196801.44      5988837.88
322      80000.0             10                            2024                                9          6195555.40      5988837.88
483     100000.0             10                            2024                               12          6190854.92      5988837.88
81       50000.0             10                            2024                                6          6187309.52      5988837.88
242      70000.0             10                            2024                                9          6185671.56      5988837.88
403      90000.0             10                            2024                               12          6182936.67      5988837.88
1        40000.0             10                            2024                                6          6177818.61      5988837.88
162      60000.0             10                            2024                                9          6176180.80      5988837.88
323      80000.0             10                            2024                               12          6175018.15      5988837.88
484     100000.0             10                            2025                                3          6170400.24      5988837.88
82       50000.0             10                            2024                                9          6166688.88      5988837.88
243      70000.0             10                            2024                               12          6165134.31      5988837.88
404      90000.0             10                            2025                                3          6162481.98      5988837.88
2        40000.0             10                            2024                                9          6157197.97      5988837.88
163      60000.0             10                            2024                               12          6155643.55      5988837.88
324      80000.0             10                            2025                                3          6154563.46      5988837.88
Note: `NaN` values indicate that your cash savings balance had < $0 at some point in time.
```
