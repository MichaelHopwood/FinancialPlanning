import decimal
import numpy as np
import pandas as pd

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


def print_summary(m, extra_principle_payments=[]):
    print('{0:>25s}:  {1:>12.6f}'.format('Rate', m.rate()))
    print('{0:>25s}:  {1:>12.6f}'.format('Month Growth', m.month_growth()))
    print('{0:>25s}:  {1:>12.6f}'.format('APY', m.apy()))
    print('{0:>25s}:  {1:>12.0f}'.format('Payoff Years', m.loan_years()))
    print('{0:>25s}:  {1:>12.0f}'.format('Payoff Months', m.loan_months()))
    print('{0:>25s}:  {1:>12.2f}'.format('Amount', m.amount()))
    print('{0:>25s}:  {1:>12.2f}'.format('Monthly Payment', m.monthly_payment()))
    print('{0:>25s}:  {1:>12.2f}'.format('Annual Payment', m.annual_payment()))
    print('{0:>25s}:  {1:>12.2f}'.format('Total Payout', m.total_payout(extra_principle_payments)))


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


def estimate(kwargs):
    kwargs['monthly_extra_payment'] = [(k, v) for k, v in kwargs['monthly_extra_payment'].items()]
    kwargs['onetime_extra_payment'] = [(k, v) for k, v in kwargs['onetime_extra_payment'].items()]

    interest = kwargs['loan_interest_rate'][kwargs['loan_duration']]
    num_months = float(kwargs['loan_duration']) * 12

    extra_principle_payments, lump_payments = get_extra_principle_payments(
            num_months=num_months,
            extra_monthly_pay=kwargs['monthly_extra_payment'],
            lump_dumps=kwargs['onetime_extra_payment'],
            return_lump_separately=True
        )
    
    m = Mortgage(float(interest) / 100 , num_months, kwargs['house_cost'])

    monthly_loan_base_payment = m.monthly_payment()

    amoritization_df = pd.DataFrame(list(m.monthly_payment_schedule(extra_principle_payments)), columns=['Principal', 'Interest', 'ExtraPrinciple'])
    # correct so dont pay extra on last month
    amoritization_df['ExtraPrinciple'].iloc[-1] = dollar(0.0)

    if kwargs['print_amoritization']:
        pd.set_option('display.max_rows', len(amoritization_df)+1)
        print('\n\n')
        print("AMORITIZATION:")
        print(amoritization_df)

    amoritization_df['TotalPrinciplePaid'] = amoritization_df['Principal'] + amoritization_df['ExtraPrinciple']
    amount_paid_to_principal_for_yearsofinterest = {f"PrincipalPaid_Year{year}": amoritization_df.TotalPrinciplePaid.iloc[ : (year * 12)-1].sum() for year in range(1,kwargs['num_years_investigate']+1) }
    amount_lost_to_interest_for_yearsofinterest = {f"InterestPaid_Year{year}": amoritization_df.Interest.iloc[ : (year * 12)-1].sum() for year in range(1,kwargs['num_years_investigate']+1) }
    num_months_to_pay_full = len( amoritization_df )

    money_lost_to_interest = amoritization_df.Interest.sum()

    extra_principle_payments = np.array(extra_principle_payments)
    extra_principle_payments[ num_months_to_pay_full : ] = 0
    extra_principle_payments = list(extra_principle_payments)


    #########################################################################
    house_cost = kwargs['house_cost']

    def monthly_fees():
        property_tax_per_month = kwargs['property_tax_monthly']
        hoa_per_month = kwargs['hoa_fee_monthly']
        insurance_per_month = kwargs['home_insurance_monthly']
        return property_tax_per_month, hoa_per_month, insurance_per_month

    def house_sale_fees(sales_price):
        agent_sales_cost = - (kwargs['agent_sales_cost']/100.) * house_cost
        docs_stamp_cost = - (kwargs['docs_stamp_cost']/100.) * sales_price
        title_ins_cost = - (kwargs['title_ins_cost']/100.) * sales_price
        total_cost_to_sell = agent_sales_cost + docs_stamp_cost + title_ins_cost
        return agent_sales_cost, docs_stamp_cost, title_ins_cost, total_cost_to_sell

    def estimate_income_tax(untaxed_income):
        brackets = [
            (0, 0), # null case
            (11000, 0.1),
            (44725, 0.12),
            (95375, 0.22),
            (182100, 0.24),
            (231250, 0.32),
            (578125, 0.35),
            (np.inf, 0.37)
        ]
        income_tax = 0
        for i, bracket in enumerate(brackets[1:]):
            bracket_top_dollars, bracket_tax_rate = bracket
            previous_bracket_top_dollars, _ = brackets[i]
            if untaxed_income > previous_bracket_top_dollars:
                income_tax += (min(bracket_top_dollars,untaxed_income)-previous_bracket_top_dollars) * bracket_tax_rate
        return income_tax

    def retirement_payments():
        k401 = float(kwargs['k401'])
        roth = float(kwargs['roth'])
        print(f"Retirement 401k roth not traditional ({k401}) and RothIRA ({roth})")
        return k401 + roth

    def benefits_taxes():
        # https://www.quora.com/How-much-tax-does-an-average-software-engineer-working-at-the-big-4-companies-in-the-SF-Bay-Area-pay
        medicare_tax = kwargs['medicare_tax_annual']
        print(f"Medicare tax ({medicare_tax})")
        return medicare_tax

    # https://www.forbes.com/advisor/taxes/taxes-federal-income-tax-bracket/#:~:text=2023%20Tax%20Brackets%20(Taxes%20Due,the%20bracket%20you're%20in.
    base_salary = kwargs['base_salary']
    signon_bonus = kwargs['signon_bonus']
    total_rsus = kwargs['total_rsus']

    def estimate_everything(year, monthly_loan_base_payment):
        print('\n\n')
        print("###############################")
        print(f"Tallying income year {year+1}")
        print("###############################")

        if year in [0,1]:
            year_taxable_total = base_salary + signon_bonus/2 + total_rsus/4
            year_cash_pretax = base_salary + signon_bonus/2
        elif year in [2,3]:
            year_taxable_total = base_salary + total_rsus/4
            year_cash_pretax = base_salary
        else:
            year_taxable_total = base_salary
            year_cash_pretax = base_salary

        print(f"Full taxable income = {year_taxable_total}")
        # https://www.bankrate.com/taxes/how-bonuses-are-taxed/
        print(f"\t(also have annual bonus of {base_salary*0.1} on average, which has a tax of {base_salary*0.1*0.22}, but not assured so not including)")

        print(f"Cash made pretax = {year_cash_pretax}")

        year_income_tax = estimate_income_tax(year_taxable_total)
        print(f"Income tax calculated as {year_income_tax}")
        
        # This is earnings including RSUs: income_first_year_after_tax = year_taxable_total - year_income_tax

        year_cash_posttax = year_cash_pretax - year_income_tax - benefits_taxes() - retirement_payments()

        print(f"Cash available (after tax & payments) = {year_cash_posttax}" )

        month_st, month_ed = year*12, (year+1)*12
        extra_payments_monthly = extra_principle_payments[month_st:month_ed]
        monthly_loan_base_payment = float( monthly_loan_base_payment )
        normal_house_payments_monthly = [m+monthly_loan_base_payment for m, month_number in zip( extra_payments_monthly , list(range(month_st, month_ed)) ) if month_number <= num_months_to_pay_full ]
        normal_annual_house_payment = sum(normal_house_payments_monthly)
        normal_equivalent_monthly_house_payment = normal_annual_house_payment / 12
        print("Normal payments made per month = ", normal_house_payments_monthly, f" = {round(normal_annual_house_payment,2)} (or, {round(normal_equivalent_monthly_house_payment,2)} monthly)")
        print("Versus monthly rent: ", kwargs['rent_monthly'])

        lump_house_payments_monthly = lump_payments[month_st:month_ed]
        lump_annual_house_payment = sum(lump_house_payments_monthly)
        print("Lump payments made per month = ", lump_house_payments_monthly, f" = {round(lump_annual_house_payment,2)}")
        
        property_tax_per_month, hoa_per_month, insurance_per_month = monthly_fees()
        taxes_hoa_insurance = (property_tax_per_month+hoa_per_month+insurance_per_month)
        print(f"Monthly payments to property taxes ({property_tax_per_month}) + HOA ({hoa_per_month}) + insurance ({insurance_per_month}) = {taxes_hoa_insurance}")
        annual_fees = taxes_hoa_insurance * 12

        monthly_rent = kwargs['rent_monthly']
        utility_costs_monthly = kwargs['utilities_monthly']
        eat_and_fun_monthly = kwargs['foodandentertainment_monthly']

        utility_total_costs = 12 * utility_costs_monthly
        print(f"With utility costs of {utility_costs_monthly} monthly, equal to total of {utility_total_costs}")

        monthly_money_after_house_payments = round((year_cash_posttax - lump_annual_house_payment - annual_fees)/12 - normal_equivalent_monthly_house_payment - utility_costs_monthly - eat_and_fun_monthly, 2)

        print(f"Therefore, the available monthly income is {round(year_cash_posttax/12,2)}. \n\tRemoving the lump sum, we have on average {round((year_cash_posttax - lump_annual_house_payment)/12, 2)} monthly income. \n\tRemoving the property taxes, HOA, and property insurance (total monthly = {round(annual_fees/12, 2)}) \n\tand the avg monthly loan payments ({round(normal_equivalent_monthly_house_payment,2)}), \n\tand the monthly utility costs ({round(utility_costs_monthly,2)}) \n\tand the eat and fun costs monthly (manually set) = {eat_and_fun_monthly} \n\t==========================\n\tour remaining is {monthly_money_after_house_payments} for savings per month. ")

        rental_insurance_monthly = kwargs['rental_insurance_monthly']

        print("So renting house is like ", (  monthly_rent*12 + rental_insurance_monthly*12 + utility_costs_monthly*12 + eat_and_fun_monthly*12) / 12 )
        print(f"monthly_rent {monthly_rent} rental_insurance_monthly {rental_insurance_monthly} utility_costs_monthly {utility_costs_monthly} eat_and_fun_monthly {eat_and_fun_monthly}")
        print("And buying is like: ", (  lump_annual_house_payment + normal_annual_house_payment + annual_fees + utility_costs_monthly*12 + eat_and_fun_monthly*12) / 12 )
        print(f"lump_monthly_house_payment {lump_annual_house_payment/12} normal_monthly_house_payment {normal_annual_house_payment/12} annual_fees /12 {annual_fees/12} utility_costs_monthly {utility_costs_monthly} eat_and_fun_monthly {eat_and_fun_monthly}")
        return ( 
                # If renting
                year_cash_posttax - monthly_rent*12 - rental_insurance_monthly*12 - utility_costs_monthly*12 - eat_and_fun_monthly*12, 
                # If buying
                year_cash_posttax - lump_annual_house_payment - normal_annual_house_payment - annual_fees - utility_costs_monthly*12 - eat_and_fun_monthly*12
        )

    years_to_investigate = range(kwargs['num_years_investigate'])
    savings_annually = []
    savings_buying_house_annually = []
    for year in years_to_investigate:
        savings , savings_buying_house = estimate_everything(year, m.monthly_payment())
        if year == 0:
            # didn't pay the down payment
            savings = savings + kwargs['amount_down']
        savings_annually.append( savings  )
        savings_buying_house_annually.append( savings_buying_house )

    def savings_situation(savings):
        savings_df = pd.DataFrame()
        savings_df['Year'] = np.array(years_to_investigate) + 1
        savings_df['Avg Monthly Savings'] = (np.array(savings) / 12).round(2)
        savings_df['Annual Savings'] = savings
        # savings_with_interest = np.array(savings).astype(float)
        savings_df['Savings'] = np.array(savings).cumsum()
        savings_df = savings_df.set_index('Year')
        return savings_df

    print("\n\n##################################################")
    print("Savings if buying a house and selling even")
    print("##################################################")
    savings_df = savings_situation(savings_buying_house_annually)
    sales_price = house_cost
    agent_sales_cost, docs_stamp_cost, title_ins_cost, total_cost_to_sell = house_sale_fees(sales_price)
    print(f"Minus the fees of selling the house (Sales cost = {agent_sales_cost} (for agent) + {docs_stamp_cost} (doc stamp) + {title_ins_cost} (title ins) = {total_cost_to_sell}) ")
    # print(loan_plan[f"PrincipalPaid_Year"])
    savings_df['MoneyBackFromHouse'] = [ kwargs['amount_down'] + ( sales_price + float( amount_paid_to_principal_for_yearsofinterest[f"PrincipalPaid_Year{year}"] - house_cost ) + total_cost_to_sell ) for year in range(1, kwargs['num_years_investigate']+1) ]
    savingswithinterest = [float(row['Savings'] * (1.06 if row['MoneyBackFromHouse'] else 1.04 )**(i+1)) for i,(ind,row) in enumerate(savings_df[['Savings','MoneyBackFromHouse']].iterrows())]
    savings_df['Savings w/I'] = ["{:f}".format(a) for a in savingswithinterest]

    savings_df['NetWorth'] = ["{:f}".format(a) for a in (savingswithinterest + savings_df['MoneyBackFromHouse'] )]
    print(savings_df)
    savings_df_sellsameprice = savings_df.copy()

    #money_made_back_on_house = ( sales_price + float( loan_plan[f"PrincipalPaid_Year{NUM_YEARS_INVESTIGATING}"] - house_cost ) )
    #print(f"Plus a house sold at (say) {sales_price} plus the remaining principal back to bank {loan_plan[f'PrincipalPaid_Year{NUM_YEARS_INVESTIGATING}'] - house_cost} = {money_made_back_on_house}")
    #total_cash = round( savings_df.iloc[-1]['Savings'] + money_made_back_on_house + total_cost_to_sell , 2)
    #print(f"Total savings is cash savings ({round(savings_df.iloc[-1]['Savings'],2)}) + house money back ({money_made_back_on_house + total_cost_to_sell}) = {total_cash}. And {total_rsus} total RSUs (have to pay capital gain/loss when sell)")

    # print("\n\n##################################################")
    # print("Savings if buying a house and selling for a loss")
    # print("##################################################")
    # savings_df = savings_situation(savings_buying_house_annually)
    # sales_price = 0.8 * house_cost
    # agent_sales_cost, docs_stamp_cost, title_ins_cost, total_cost_to_sell = house_sale_fees(sales_price)
    # savings_df['MoneyBackFromHouse'] = [ amount_down + ( sales_price + float( loan_plan[f"PrincipalPaid_Year{year}"] - house_cost ) + total_cost_to_sell ) for year in range(1, NUM_YEARS_INVESTIGATING+1) ]
    # savings_df['NetWorth'] = savings_df['Savings'] + savings_df['MoneyBackFromHouse']
    # print(savings_df)


    print("\n\n##################################################")
    print("Savings if not buying a house")
    print("##################################################")
    savings_df = savings_situation(savings_annually)
    savingswithinterest = ["{:f}".format( float(P * (1.06)**(i+1)) ) for i,P in enumerate(savings_df['Savings'])]
    savings_df['Savings w/I'] = savingswithinterest
    savings_df['NetWorth'] = savings_df['Savings w/I']
    print(savings_df)
    print(f"Total savings is cash savings = {round(float(savings_df.iloc[-1]['Savings w/I']),2)}. And {total_rsus} total RSUs (have to pay capital gain/loss when sell)")
    print("Also likely doesn't come with parking spot (i.e. $200/mo extra) ")

    savings_df_renting = savings_df.copy()

    net_worth = float(savings_df_sellsameprice['NetWorth'].iloc[-1]) # Net worth at end
    net_worth = round(net_worth, 2)
    net_worth_rent = float(savings_df_renting['NetWorth'].iloc[-1])
    net_worth_rent = round(net_worth_rent, 2)

    target_monthly_savings_earlyon = 2000
    SumViolatedMonthlyLowEarnings = ( target_monthly_savings_earlyon - savings_df_sellsameprice[savings_df_sellsameprice['Avg Monthly Savings'] < target_monthly_savings_earlyon]['Avg Monthly Savings'] ).sum()
    SumViolatedMonthlyLowEarnings_rent = ( target_monthly_savings_earlyon - savings_df_renting[savings_df_renting['Avg Monthly Savings'] < target_monthly_savings_earlyon]['Avg Monthly Savings'] ).sum()

    return net_worth, net_worth_rent, SumViolatedMonthlyLowEarnings, SumViolatedMonthlyLowEarnings_rent
