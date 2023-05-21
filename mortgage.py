import yaml
import argparse
import numpy as np
import itertools
import pandas as pd
import copy
import os
import sys
from eval import estimate

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


def visualize(results_df, settings):
    print("##################################################")
    print("### Report")
    print("##################################################")

    os.makedirs(f'./results/{args.cfg}/', exist_ok=True)
    
    fig, ax = plt.subplots(1,1, figsize=(10,5))
    ax.plot(results_df.index, results_df['net_worth_mortgage'], label='With mortgage')
    ax.plot(results_df.index, results_df['net_worth_rent'], label='With rent')
    ax.set_xlabel('Time')
    ax.set_ylabel('Net worth ($)')
    ax.legend()
    ax.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    plt.savefig(f'./results/{args.cfg}/net_worth_temporal.png')
    plt.close()

    fig, ax = plt.subplots(1,1, figsize=(10,5))
    results_df[['savings_mortgage','house_profit','savings_rent','investments','roth','401k']].plot(ax=ax)
    ax.set_xlabel('Time')
    ax.set_ylabel('Dollars ($)')
    ax.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    plt.savefig(f'./results/{args.cfg}/net_worth_components_temporal.png')
    plt.close()

    mortgage_cols = ['savings_mortgage', 'investments', 'roth', '401k', 'house_profit']
    rent_cols = ['savings_rent', 'investments', 'roth', '401k']

    fig, axs = plt.subplots(1,2, figsize=(10,5))
    axs[0].pie(results_df[mortgage_cols].iloc[-1], labels=mortgage_cols, autopct='%1.1f%%')
    axs[1].pie(results_df[rent_cols].iloc[-1], labels=rent_cols, autopct='%1.1f%%')
    axs[0].set_title(f'Mortgage, net worth= ${results_df.iloc[-1]["net_worth_mortgage"]:,}')
    axs[1].set_title(f'Rent, net worth= ${results_df.iloc[-1]["net_worth_rent"]:,}')
    plt.savefig(f'./results/{args.cfg}/net_worth_piechart.png')
    plt.close()


    from fpdf import FPDF
    import datetime

    class PDF(FPDF):
        def __init__(self):
            super().__init__()
        def header(self):
            self.set_font('Arial', '', 12)
            self.cell(0, 10, f'Auto-generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 1, 1, 'C')
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', '', 12)
            self.cell(0, 10, 'Auto-generated using code available at https://www.github.com/MichaelHopwood/FinancialPlanning', 1, 0, 'C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(w=0, h=20, txt="Financial Expectations from {}-{} to {}-{}".format(
        settings['start_month_investigate'], settings['start_year_investigate'],
        settings['start_month_investigate'], settings['start_year_investigate']+settings['num_years_investigate']
    ), ln=1)

    ch=8
    def df_to_pdf(pdf, df, ch=8, fontsize=12):
        pdf.set_font('Arial', 'B', fontsize)
        cols = df.columns.tolist()
        # header
        for j, col in enumerate(cols):
            pdf.cell(w=20, h=ch, txt=col, border=1, ln=0, align='C')
        pdf.ln(ch)
        # contents
        pdf.set_font('Arial', '', fontsize)
        for i in range(0, len(df)):
            for j, col in enumerate(cols):
                pdf.set_fill_color(240, 256, 256)
                pdf.cell(w=20, h=ch, txt=str(df.iloc[i, j]), border=1, ln=0, align='C', fill=True)
            pdf.ln(ch)

    pdf.image(f'./results/{args.cfg}/net_worth_temporal.png', x=0, y=None, w=220, h=0, type='png')
    pdf.ln(ch*3)

    pdf.set_font('Arial', 'B', 12)
    pdf.multi_cell(w=0, h=ch, txt=f"Expected net worth components breakdown in {settings['start_month_investigate']}/{settings['start_year_investigate']+settings['num_years_investigate']}:")
    pdf.image(f'./results/{args.cfg}/net_worth_piechart.png', x=0, y=None, w=220, h=0, type='png')
    pdf.ln(ch*3)

    pdf.multi_cell(w=0, h=ch, txt=f"Net worth components:")
    pdf.image(f'./results/{args.cfg}/net_worth_components_temporal.png', x=0, y=None, w=220, h=0, type='png')
    pdf.ln(ch*3)

    pdf.set_font('Arial', 'B', 20)
    pdf.cell(w=0, h=20, txt="Annual results:")
    rdf = results_df.astype(float).round(2).groupby(results_df.index.year).last()
    rdf.index.name = 'year'
    rdf = rdf.reset_index()
    pdf.ln(ch*3)
    df_to_pdf(pdf, rdf, ch=8, fontsize=6)
    pdf.ln(ch*5)

    pdf.set_font('Arial', 'B', 20)
    pdf.cell(w=0, h=20, txt="Monthly results:")
    rdf = results_df
    rdf.index.name = 'date'
    rdf = rdf.reset_index()
    rdf['date'] = rdf['date'].apply(lambda x : x.strftime('%Y-%m-%d'))
    pdf.ln(ch*3)
    df_to_pdf(pdf, rdf, ch=8, fontsize=6)
    pdf.ln(ch)

    pdf.output(f'./results/{args.cfg}/report.pdf', 'F')


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
    all_settings = []
    for kwargs in grid_kwargs:
        iter_settings = copy.deepcopy(base_settings)
        for k,v in kwargs.items():
            iter_settings[k] = v
        nw, results_df = execute(**iter_settings)
        net_worths.append(nw)
        timeseries_dfs.append(results_df)
        all_settings.append(iter_settings)
    net_worths_df = pd.DataFrame(net_worths)

    res = pd.concat([param_df, net_worths_df], axis=1) \
                .sort_values(by='net_worth_mortgage', ascending=False)

    print( res.head(25) )
    print("Note: `NaN` values indicate that your cash savings balance "
          "had < $0 at some point in time.")

    results_df = timeseries_dfs[ res.index[0] ]
    settings = all_settings[ res.index[0] ]

    print("\n\nTimeseries results of best settings:\n")

    visualize(results_df, settings)

else:
    summary_dict, results_df = estimate(settings)

    visualize(results_df, settings)
