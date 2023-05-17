import yaml
import argparse
import numpy as np
import itertools
import pandas as pd
import copy
import os
import sys
from eval import estimate, YoureBrokeException

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

argparse.ArgumentParser(description='Mortgage calculator')
parser = argparse.ArgumentParser()
parser.add_argument('--cfg', type=str, default='settings_optimize.yml', help='yaml configuration file')
args = parser.parse_args()

def read_settings(nm):
    with open(nm, 'r') as file:
        settings = yaml.safe_load(file)
    return settings

settings = read_settings(args.cfg)
if 'base_settings' in settings:
    base_settings = read_settings(settings['base_settings'])
    del settings['base_settings']
    print(settings)
    param_grid = {}
    for k,v in settings.items():
        if isinstance(base_settings[k], dict):
            # then we expect value `v` to be a dictionary also, where its values are grid search parameters (either dict or list)
            if sum(['min' in v , 'max' in v, 'num' in v]) > 0: 
                raise Exception(f"Expected a dictionary for parameter {k} during grid search. Check base settings file.")

            for k1,v1 in v.items():
                if isinstance(v1, dict):
                    assert 'min' in v1
                    assert 'max' in v1
                    assert 'num' in v1
                    param_grid[f"{k}:{k1}"] = list(np.linspace(v1['min'], v1['max'], v1['num']))
                elif isinstance(v1, list):
                    param_grid[f"{k}:{k1}"] = v1
        else:
            if isinstance(v, dict):
                assert 'min' in v
                assert 'max' in v
                assert 'num' in v
                param_grid[k] = list(np.linspace(v['min'], v['max'], v['num']))
            elif isinstance(v, list):
                param_grid[k] = v

    param_keys = list(param_grid.keys())

    param_grid = list(itertools.product(*list(param_grid.values())))

    param_df = pd.DataFrame()
    for i, k in enumerate(param_keys):
        if ':' in k:
            colname, dictkey = k.split(':')
            if colname in param_df.columns:
                for (ind,row),d in zip( param_df.iterrows() , param_grid ):
                    row[colname][int(dictkey)] = d[i]
            else:
                param_df[colname] = [{int(dictkey) : d[i]} for d in param_grid]
        else:
            param_df[k] = [d[i] for d in param_grid]

    # list of **kwargs
    grid_kwargs = list(param_df.T.to_dict().values())

    def blockPrinting(func):
        def func_wrapper(*args, **kwargs):
            # block all printing to the console
            sys.stdout = open(os.devnull, 'w')
            # call the method in question
            value = func(*args, **kwargs)
            # enable all printing to the console
            sys.stdout = sys.__stdout__
            # pass the return value of the method back
            return value

        return func_wrapper

    @blockPrinting
    def execute(**kwargs):
        return estimate(kwargs)
    
    net_worths = []
    timeseries_dfs = []
    for kwargs in grid_kwargs:
        iter_settings = copy.deepcopy(base_settings)
        for k,v in kwargs.items():
            iter_settings[k] = v
        nw, results_df = execute(**iter_settings)
        net_worths.append(nw)
        timeseries_dfs.append(results_df)
    net_worths_df = pd.DataFrame(net_worths)

    res = pd.concat([param_df, net_worths_df], axis=1) \
                .sort_values(by='net_worth_mortgage', ascending=False)

    print( res.head(25) )
    print("Note: `NaN` values indicate that your cash savings balance "
          "had < $0 at some point in time.")

    results_df = timeseries_dfs[ res.index[0] ]

    fig, ax = plt.subplots(1,1, figsize=(10,5))
    ax.plot(results_df.index, results_df['net_worth_mortgage'], label='With mortgage')
    ax.plot(results_df.index, results_df['net_worth_rent'], label='With rent')
    ax.set_xlabel('Time')
    ax.set_ylabel('Net worth ($)')
    ax.legend()
    ax.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.grid('--')
    plt.show()

else:
    summary_dict, results_df = estimate(settings)

    print("\nMonthly results:")
    print(results_df)

    fig, ax = plt.subplots(1,1, figsize=(10,5))
    ax.plot(results_df.index, results_df['net_worth_mortgage'], label='With mortgage')
    ax.plot(results_df.index, results_df['net_worth_rent'], label='With rent')
    ax.set_xlabel('Time')
    ax.set_ylabel('Net worth ($)')
    ax.legend()
    ax.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    plt.show()

    fig, ax = plt.subplots(1,1, figsize=(10,5))
    results_df[['savings_mortgage','house_profit','savings_rent','investments','roth','401k']].plot(ax=ax)
    ax.set_xlabel('Time')
    ax.set_ylabel('Dollars ($)')
    ax.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    plt.show()
