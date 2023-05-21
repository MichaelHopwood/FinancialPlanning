import pandas as pd
import numpy as np
import datetime
import copy
import decimal
import warnings

DOLLAR_QUANTIZE = decimal.Decimal('.01')

def dollar(f, round=decimal.ROUND_CEILING):
    """
    This function rounds the passed float to 2 decimal places.
    """
    if not isinstance(f, decimal.Decimal):
        f = decimal.Decimal(str(f))
    return f.quantize(DOLLAR_QUANTIZE, rounding=round)


class Mortgage:
    def __init__(self, interest, months, amount):
        self._interest = float(interest)
        self._months = int(months)
        self._amount = dollar(amount)

    def rate(self):
        return self._interest

    def month_growth(self):
        return 1. + self._interest / 12

    def apy(self):
        return self.month_growth() ** 12 - 1

    def loan_years(self):
        return float(self._months) / 12

    def loan_months(self):
        return self._months

    def amount(self):
        return self._amount

    def monthly_payment(self):
        pre_amt = float(self.amount()) * self.rate() / (float(12) * (1.-(1./self.month_growth()) ** self.loan_months()))
        return dollar(pre_amt, round=decimal.ROUND_CEILING)

    def total_value(self, m_payment):
        return m_payment / self.rate() * (float(12) * (1.-(1./self.month_growth()) ** self.loan_months()))

    def annual_payment(self):
        return self.monthly_payment() * 12

    def total_payout(self, extra_principle_payments=[]):
        if extra_principle_payments == []:
            # should use sum([sum(m) for m in monthly_payments]) but i m too lazy
            return self.monthly_payment() * self.loan_months()
        else:
            monthly_payments = list(self.monthly_payment_schedule(extra_principle_payments=extra_principle_payments))
            return sum([sum(m) for m in monthly_payments])

    def monthly_payment_schedule(self, extra_principle_payments=[]):
        monthly = self.monthly_payment()
        balance = dollar(self.amount())
        rate = decimal.Decimal(str(self.rate())).quantize(decimal.Decimal('.000001'))
        epps = [dollar(e)  for e in extra_principle_payments]
        while True:
            try:
                extra_principle = epps.pop(0)
            except IndexError as e:
                extra_principle = dollar(0)

            interest_unrounded = balance * rate * decimal.Decimal(1)/12
            interest = dollar(interest_unrounded, round=decimal.ROUND_HALF_UP)

            if monthly >= balance + interest:
                # should add warning
                # reset the extra_principle = 0 since there is no point to pay
                yield balance, interest, extra_principle
                break

            principle = monthly - interest
            yield principle, interest, extra_principle
            balance = balance - principle - extra_principle


def get_extra_principle_payments(num_months, extra_monthly_pay, lump_dumps, return_lump_separately=False):
    extra_principle_payments = [0] * int(num_months)
    extra_principle_payments = np.array(extra_principle_payments)
    for extra_monthly_rate_update in extra_monthly_pay:
        month_start, rate = extra_monthly_rate_update
        extra_principle_payments[month_start:] = rate
    if return_lump_separately:
        lumpextra_principle_payments = [0] * int(num_months)
        lumpextra_principle_payments = np.array(lumpextra_principle_payments)
        for itermonth,iteramount in lump_dumps:
            lumpextra_principle_payments[itermonth] += iteramount
        lumpextra_principle_payments = list(lumpextra_principle_payments)
        return extra_principle_payments , lumpextra_principle_payments   
    else:
        for itermonth,iteramount in lump_dumps:
            extra_principle_payments[itermonth] += iteramount
        extra_principle_payments = list(extra_principle_payments)
        return extra_principle_payments



def annot(scenario='all'):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return {
                    "name": func.__name__,
                    "scenario": scenario,
                    "value": func(*args, **kwargs)
                    }
        return wrapper
    return decorator


class Estimator:

    def __init__(self, settings):
        for k,v in settings.items():
            setattr(self, k, v)

        now = datetime.datetime.now()
        now = now.replace(year=int(self.start_year_investigate), 
                          month=int(self.start_month_investigate))
        
        buy_house_date = copy.copy(now)
        self.buy_house_date = buy_house_date.replace(year=int(self.housePurchase_year_investigate), 
                                                     month=int(self.housePurchase_month_investigate) )

        end = copy.copy(now)
        end = end.replace(year=now.year + self.num_years_investigate)

        self.month_series = pd.date_range(now.strftime('%Y-%m'), 
                                          end.strftime('%Y-%m'), 
                                          freq='1M').strftime('%Y-%m')
        self.month_series = pd.to_datetime(self.month_series)

        mortgage_month_mask = (self.month_series.year == self.buy_house_date.year) & \
                             (self.month_series.month == self.buy_house_date.month)

        if sum( mortgage_month_mask ) == 0:
            raise Exception("House buy date is not within inspection range. "
                            "`start_year_investigate` and `start_month_investigate` must indicate "
                           f"a date between {self.month_series[0]} and {self.month_series[-1]}")
        
        mortgage_month_idx = np.where(mortgage_month_mask)[0][0]

        self.pre_mortgage_month_series = self.month_series[:mortgage_month_idx]
        self.mortgage_month_series = self.month_series[mortgage_month_idx:]


    @annot(scenario='mortgage')
    def pre_mortgage_rent_and_rental_insurance(self):
        # if you are delaying when you start to buy a house
        # this functionality allows us to calculate when may be the 
        # most opportune time to buy a house (mostly centered around
        # when you will have the appropriate down payment)
        return pd.Series(data= -(self.prehouse_rent_monthly + self.rental_insurance_monthly), 
                         index=self.pre_mortgage_month_series)

    @annot(scenario='mortgage')
    def mortgage_payments(self):
        interest = self.loan_interest_rate[self.loan_duration]
        num_months = float(self.loan_duration) * 12

        extra_principle_payments = get_extra_principle_payments(
                num_months=num_months,
                extra_monthly_pay=[(k, v) for k, v in self.monthly_extra_payment.items()],
                lump_dumps=[(k, v) for k, v in self.onetime_extra_payment.items()],
                return_lump_separately=False
            )
        
        # lump_payments = pd.Series(data=lump_payments, index=self.month_series)
        # extra_principle_payments = pd.Series(data=extra_principle_payments, index=self.month_series)
        
        m = Mortgage(float(interest) / 100 , num_months, self.house_cost - self.amount_down)

        payments = list(m.monthly_payment_schedule(extra_principle_payments))

        if len(payments) < len(self.mortgage_month_series):
            payments.extend([[0,0,0]]*(len(self.mortgage_month_series)-len(payments)))
            extra_principle_payments.extend([0]*(len(self.mortgage_month_series)-len(payments)))
        else:
            payments = payments[:len(self.mortgage_month_series)]
            extra_principle_payments = extra_principle_payments[:len(self.mortgage_month_series)]
        
        amoritization_df = pd.DataFrame(payments, 
                                        columns=['Principal', 'Interest', 'ExtraPrinciple'],
                                        index=self.mortgage_month_series).astype(float)

        # correct so dont pay extra on last month
        amoritization_df['ExtraPrinciple'].iloc[-1] = 0.
        amoritization_df['TotalPrinciplePaid'] = amoritization_df['Principal'] + amoritization_df['ExtraPrinciple']
        amoritization_df['TotalPrinciplePaid'].iloc[0] += self.amount_down

        amoritization_df['TotalPaid'] = amoritization_df['TotalPrinciplePaid'] + amoritization_df['Interest']

        self.principal_paid = amoritization_df['TotalPrinciplePaid'].cumsum()

        payments = -amoritization_df['TotalPaid']

        if self.verbose > 2:
            print("Amoritization:")
            print(amoritization_df)

        payments_series = pd.Series(data=0, index=self.month_series)
        payments_series.loc[self.mortgage_month_series] = payments

        return payments_series
    
    @annot(scenario='mortgage')
    def pmi(self):
        if not hasattr(self, 'principal_paid'):
            self.mortgage_payments()
        
        pmi_series = pd.Series(data=0, index=self.mortgage_month_series)
        pct_principal_paid = self.principal_paid / self.house_cost
        pmi_series[pct_principal_paid < 0.2] = -self.pmi_monthly
        pmi_series[pct_principal_paid >= 0.2] = 0.

        return pmi_series

    @annot(scenario='mortgage')
    def property_fees(self):
        val  = -self.property_tax_monthly + \
               -self.hoa_fee_monthly + \
               -self.home_insurance_monthly
        return pd.Series(data=val, index=self.mortgage_month_series)
    
    @annot(scenario='mortgage')
    def house_sale_profit(self):
        house_price = self.house_cost
        sales_price = house_price

        vals = []
        for month in self.month_series:
            if month in self.mortgage_month_series:
                sales_price = sales_price * (1 + self.house_appreciation_annual_rate/12.)
                agent_sales_cost = (self.agent_sales_cost/100.) * house_price
                docs_stamp_cost = (self.docs_stamp_cost/100.) * sales_price
                title_ins_cost = (self.title_ins_cost/100.) * sales_price
                vals.append(sales_price - house_price - agent_sales_cost - docs_stamp_cost - title_ins_cost)
            elif month < self.mortgage_month_series[0]:
                vals.append(0)
            elif month > self.mortgage_month_series[-1]:
                vals.append(vals[-1])

        house_profit = pd.Series(data=vals, index=self.month_series)

        # embedding result in dictionary because the `run` code expects a Series
        # for each cost method that is cumulative, but this one should only be conducted once
        # (when selling the house)
        return {'profit': house_profit}

    @annot(scenario='mortgage')
    def renting_out_place(self):
        return pd.Series(data=self.mortgage_renting_income_monthly, index=self.mortgage_month_series)

    @annot(scenario='all')
    def posttax_income(self):

        income = pd.Series(data=self.base_salary/12., index=self.month_series)

        income.iloc[0] += self.signon_bonus / 2.
        income.iloc[12-1] += self.signon_bonus / 2.

        annual_rsu_vest = [self.total_rsus/4.]*4
        cumulative_annual_rsu_vest = np.cumsum(annual_rsu_vest)
        
        years = np.unique(self.month_series.year)

        year_idx = 0
        rsus_series = []
        rsus_cumulative_series = []
        for val, cumulative_val in zip( annual_rsu_vest, cumulative_annual_rsu_vest ):
            for idx in self.month_series[self.month_series.year == years[year_idx]]:
                if (idx.month==self.start_month_investigate):
                    rsus_series.append(val)
                else:
                    rsus_series.append(0)
                rsus_cumulative_series.append(cumulative_val)
            year_idx += 1
        last_cumulative_val = rsus_cumulative_series[-1]
        num_months = len(income)
        for _ in range(num_months-len(rsus_series)):
            rsus_series.append(0)
            rsus_cumulative_series.append(last_cumulative_val)

        rsus_series = pd.Series(data=rsus_series, index=self.month_series)

        self.rsus_cumulative_series = pd.Series(data=rsus_cumulative_series,
                                                index=self.month_series)
        self.rsus_cumulative_series = pd.Series(
            data=[ val * ( 1. + self.annual_investment_appreciation )**(i/12) if val > 0 else val
                for i,(ind,val) in enumerate(
                        self.rsus_cumulative_series.items()
            ) ], 
            index=self.month_series)

        taxable_income = copy.copy(income)
        taxable_income += rsus_series

        # subtracting 401k from income here because it is not taxed until withdrawal
        # addition used here because method returns negative values (as it is decreasing
        # the savings balance)
        taxable_income = taxable_income + self.retirement_401k()["value"]

        if self.verbose > 3:
            print("Salary & Bonus\n", income.groupby(self.month_series.year).sum())
            print("RSUs\n", rsus_series.groupby(self.month_series.year).sum())
            print("Retirement 401k discount\n", self.retirement_401k()["value"].groupby(self.month_series.year).sum())

        def income_tax_calc(untaxed_income):
            brackets = [
                (0, 0), # null case
                (11_000, 0.1),
                (44_725, 0.12),
                (95_375, 0.22),
                (182_100, 0.24),
                (231_250, 0.32),
                (578_125, 0.35),
                (np.inf, 0.37),
            ]
            income_tax = 0
            for i, bracket in enumerate(brackets[1:]):
                bracket_top_dollars, bracket_tax_rate = bracket
                previous_bracket_top_dollars, _ = brackets[i]
                if untaxed_income > previous_bracket_top_dollars:
                    income_tax += (min(bracket_top_dollars,untaxed_income)-previous_bracket_top_dollars) * bracket_tax_rate
            return income_tax

        income_tax_series = []
        for year, taxable_annual_salary in taxable_income.groupby(taxable_income.index.year).sum().items():
            if self.verbose > 4:
                print(year, taxable_annual_salary, income_tax_calc(taxable_annual_salary))
            income_tax_series.append( income_tax_calc(taxable_annual_salary) )

        self.income_tax_series = pd.Series(data=income_tax_series, index=self.month_series.year.unique())
        
        # remove income tax payments in April of each year (tax day)
        for idx, val in income.items():
            # required because you can start on different month of year so some years are partial
            # num_months_this_year = sum( self.month_series.year == idx.year ) 
            incomes_this_year = income[income.index.year == idx.year]
            pct_income_this_year = val / sum(incomes_this_year)
            income.loc[idx] -= ( self.income_tax_series.loc[idx.year] * pct_income_this_year)

        return income
    
    @annot(scenario='all')
    def retirement_401k(self):
        val = self.k401 / 12.

        # amount of money invested
        self.k401_cumulative_series = pd.Series(data=np.cumsum([val]*len(self.month_series)), 
                                     index=self.month_series)
        self.k401_cumulative_series = pd.Series(
            data=[ val * ( 1. + self.annual_investment_appreciation )**(i/12) if val > 0 else val
                for i,(ind,val) in enumerate(
                        self.k401_cumulative_series.items()
            ) ], 
            index=self.month_series)
        
        # amount of money coming out of your paycheck (this is smaller because 
        # part of it is matched by the company)
        payment = self.k401 - self.k401_company_coverage
        val = -payment / 12
        return pd.Series(data=val, index=self.month_series)

    @annot(scenario='all')
    def retirement_roth(self):
        val = self.roth / 12.
        self.roth_cumulative_series = pd.Series(data=np.cumsum([val]*len(self.month_series)), 
                                     index=self.month_series)
        self.roth_cumulative_series = pd.Series(
            data=[ val * ( 1. + self.annual_investment_appreciation )**(i/12) if val > 0 else val
                for i,(ind,val) in enumerate(
                        self.roth_cumulative_series.items()
            ) ], 
            index=self.month_series)

        val = -val
        return pd.Series(data=val, index=self.month_series)

    @annot(scenario='all')
    def food_entertainment(self):
        val = -self.foodandentertainment_monthly
        return pd.Series(data=val, index=self.month_series)

    @annot(scenario='rent')
    def rent(self):
        val = -self.rent_monthly
        return pd.Series(data=val, index=self.month_series)
    
    @annot(scenario='rent')
    def renter_insurance(self):
        val = -self.rental_insurance_monthly
        return pd.Series(data=val, index=self.month_series)

    def run(self):
        self.df_mortgage = pd.DataFrame()
        self.df_rent = pd.DataFrame()

        for attr in dir(self):
            if attr.startswith('__'):
                continue
            if attr == 'run':
                continue
            if callable(getattr(self, attr)):
                res = getattr(self, attr)()
                if isinstance(res['value'], pd.Series):
                    if res['scenario'] == 'mortgage':
                        if res['value'].index.equals(self.month_series):
                            self.df_mortgage[attr] = res['value']
                        elif res['value'].index.equals(self.pre_mortgage_month_series) or \
                             res['value'].index.equals(self.mortgage_month_series) :
                            series = pd.Series(data=0, index=self.month_series)
                            series.loc[res['value'].index] = res['value']
                            self.df_mortgage[attr] = series
                    elif res['scenario'] == 'rent':
                        self.df_rent[attr] = res['value']
                    elif res['scenario'] == 'all':
                        self.df_mortgage[attr] = res['value']
                        self.df_rent[attr] = res['value']

        if self.verbose > 1:
            print("Mortgage Scenario:")
            print(self.df_mortgage.astype(float).round(2))

            print("Rent Scenario:")
            print(self.df_rent.astype(float).round(2))
        
        savings_mortgage = self.df_mortgage.sum(axis=1).cumsum() + self.current_savings
        savings_rent = self.df_rent.sum(axis=1).cumsum() + self.current_savings
        investments = self.rsus_cumulative_series + self.current_investments
        roth_savings = self.roth_cumulative_series + self.current_roth
        k401_savings = self.k401_cumulative_series + self.current_k401

        def bank_interest(series, savings_interest_rate):
            savings_plus_interest = [ val * ( 1. + savings_interest_rate )**(i/12) if val > 0 else val
                for i,(ind,val) in enumerate(
                        series.items()
            ) ]
            savings_plus_interest = pd.Series(data=savings_plus_interest, index=series.index)
            return savings_plus_interest

        savings_mortgage = bank_interest(savings_mortgage, self.savings_interest_rate)
        savings_rent = bank_interest(savings_rent, self.savings_interest_rate)

        results_df = pd.DataFrame(index=self.month_series)
        results_df['savings_mortgage'] = savings_mortgage
        results_df['house_profit'] = self.house_sale_profit()['value']['profit']
        results_df['savings_rent'] = savings_rent
        results_df['investments'] = investments
        results_df['roth'] = roth_savings
        results_df['401k'] = k401_savings
        results_df['net_worth_mortgage'] = savings_mortgage + results_df['house_profit'] + investments + roth_savings + k401_savings
        results_df['net_worth_rent'] = savings_rent + investments + roth_savings + k401_savings

        if self.verbose > 2:
            print("Amount paid in taxes:")
            print(self.income_tax_series.astype(float).round(2))
            print("Annual Income post Taxes")
            print(self.df_mortgage['posttax_income'].astype(float).round(2).groupby(self.df_mortgage.index.year).sum())

        if self.verbose > 0:
            print("Annual results:")
            print( results_df.astype(float).round(2).groupby(results_df.index.year).last() )
            print()
            print('Monthly results:')
            print(results_df.astype(float).round(2))

        results_df = results_df.astype(float).round(2)        
        summary_dict = results_df[['net_worth_mortgage', 'net_worth_rent']].iloc[-1].to_dict()

        if (savings_mortgage<0).any():
            summary_dict['net_worth_mortgage'] = np.nan #'Went Broke (cash-wise)!'
            warnings.warn("Went broke during mortgage!")

        if (savings_rent<0).any():
            summary_dict['net_worth_rent'] = np.nan #'Went Broke (cash-wise)!'
            warnings.warn("Went broke during renting!")

        return summary_dict, results_df


def estimate(kwargs):
    return Estimator(kwargs).run()
