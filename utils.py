import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime as dt, timedelta as td
from fitter import Fitter

# Parse times variables from String to Datetime type
def parse_times(df):
    df = df.apply(lambda x: dt.strptime(x, '%H:%M:%S').time())        
    return df
        
# Convert all Datetime types to second 
def dateToSecond(df):
    df = df.apply(lambda time: time.hour*3600 + time.minute*60 + time.second)
    return df

def select_cols(df, cols=[]):
    return df[cols]

def select_type(df, call_type, time_column_name):
    return df[df['type'] == call_type][time_column_name]

def plot_distribution(data, title="Distribution", kde=True, hist=True):
    sns.displot(data, kind='hist', hist=hist, kde=kde, 
                 edgecolor='black', bins=300)
    plt.title(title)
    plt.show()
    
def int2Date(date_integer):
    date_string = str(date_integer)
    year = int(f'19{date_string[0:2]}')
    month = int(date_string[2:4])    
    day = int(date_string[4:6])
    return dt(year, month, day)

def describe(data):
    print(f"mean:\t\t\t{np.mean(data)}")
    print(f"standard deviation:\t{np.std(data)}")
    print(f"max:\t\t\t{np.max(data)}")
    print(f"min:\t\t\t{np.min(data)}\n")

def plot_arrivals_in_ascending_order(arrivals, time_column_name="vru_entry"):
    arrivals_reseted_index = arrivals.reset_index()[time_column_name]
    plt.plot(arrivals_reseted_index, 'g.', markersize=0.5)
    plt.title("Arrivals in ascending order")
    plt.xlabel("Arrival order")
    plt.ylabel("Arrival time in seconds")

def get_arrivals(month_name="January", call_type="PS", time_column_name="vru_entry", date=990104):
    month = pd.read_csv(f"AnonymousBANK/data/{month_name}1999.txt", delim_whitespace=True)
    day = month[month['date']==date]
    arrivals_with_types = select_cols(day, ['type', time_column_name])
    arrivals = select_type(arrivals_with_types, call_type, time_column_name)
#     if(isinstance(arrivals[time_column_name].dtype, object)): 
    arrivals_parsed = parse_times(arrivals)
    arrivals_in_seconds = dateToSecond(arrivals_parsed)
    return arrivals_in_seconds.sort_values()
#     return arrivals

def get_inter_arrivals(arrivals_in_seconds):#, bank_start_time=td(hours=7).seconds):
#     return arrivals_in_seconds - arrivals_in_seconds.shift(fill_value=bank_start_time)
    return arrivals_in_seconds.drop(arrivals_in_seconds.index[0]).values - arrivals_in_seconds.drop(arrivals_in_seconds.index[-1]).values

def find_best_distribution_between(data, distributions = None, Nbest=3, bins=300, xmin=None, xmax=None, progress=True, data_name="arrivals"):    
    print(f"Searching {Nbest} best distributions for {data_name}...")
    if(distributions != None):
        fitter = Fitter(data, bins=bins, distributions=distributions, xmin=xmin, xmax=xmax)
    else:
        fitter = Fitter(data, bins=bins, xmin=xmin, xmax=xmax)
        
    fitter.fit(progress=progress)
    print(f"Summary...")
    fitter.summary(Nbest=Nbest)
    plt.show()
    return fitter

def pipeline(month_name="January", call_type="PS", time_column_name="vru_entry", date=990104, arrivals_distributions = None, inter_arrivals_distributions= None):
    true_date = int2Date(990104) 
    print(f"""
    **********************************************************************
    * Call Type: {call_type}\n
    * Column: {time_column_name}\n
    * Date: {true_date.strftime("%B %d %A %Y")}
    **********************************************************************
    """)
    arrivals = get_arrivals(month_name, call_type, time_column_name, date)
    print("Description of arrivals")
    describe(arrivals)
    plot_arrivals_in_ascending_order(arrivals, time_column_name)
    plot_distribution(arrivals, 'Distribution of Customer Arrivals')

    inter_arrivals = get_inter_arrivals(arrivals)
    print("Description of inter arrivals")
    describe(inter_arrivals)
    plot_distribution(inter_arrivals, 'Distribution of Customer Inter Arrivals')
    
    plot_distribution(inter_arrivals[inter_arrivals <= 450], 'Distribution of Customer Inter Arrivals for time less than 450')

    fitter_arrivals = find_best_distribution_between(arrivals_distributions, arrivals)
    fitter_inter_arrivals = find_best_distribution_between(inter_arrivals_distributions, inter_arrivals, xmax=1000, data_name="inter-arrivals")

    def get_best(fitter):
        return list(fitter.get_best().keys())

    fitter_inter_arrivals.plot_pdf(names=get_best(fitter_inter_arrivals))
    fitter_inter_arrivals.hist()
    
    print(f"Best distribution for inter arrivals: {fitter_inter_arrivals.get_best()}")
    
    return arrivals, inter_arrivals, fitter_arrivals, fitter_inter_arrivals

