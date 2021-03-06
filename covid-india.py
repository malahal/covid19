#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
from cycler import cycler
import argparse
import os

# Work in Indian Time zone
os.environ['TZ'] = 'Asia/Kolkata'

parser = argparse.ArgumentParser(description="India Covid-19 plotter")
parser.add_argument('-s', '--savefig', action="store_true",
                    default=False, help="save plot figures")
parser.add_argument('datafile', metavar='FILE', help='file to use for data')
args = parser.parse_args()

# Modify the file with the given data atomically
def modify_file(fname, data):
    from tempfile import NamedTemporaryFile
    import os
    f = NamedTemporaryFile(mode='wt', dir=os.path.dirname(fname), delete=False)
    f.write(data)
    f.flush()
    os.fsync(f.fileno())

    # If the file exists, get its stats and apply them to the temp file
    try:
        stat = os.stat(fname)
        os.chown(f.name, stat.st_uid, stat.st_gid)
        os.chmod(f.name, stat.st_mode)
    except:
        pass
    os.rename(f.name, fname)

url = 'https://www.mohfw.gov.in'
dfs = pd.read_html(url)
for df in dfs:
    columns = df.columns
    if not 'Name of State' in df.columns:
        continue
    if not 'Total Confirmed cases' in df.columns:
        continue
    break # got the right table

# West Bengal is the last state, get entries upto it
df = df.iloc[:(df["Name of State / UT"] == 'West Bengal').idxmax()+1]
cols = [x for x in list(df.columns) if ("State" in x or "Confirmed" in x)]
df = df[cols] # two columns data frame
df.columns = ['State', 'Confirmed'] # rename columns
df['State'] = df['State'].str.rstrip('*')   # remove asterisks.

# Add date column
df['Date'] = pd.Timestamp.now().normalize()
df = df[['Date', 'State', 'Confirmed']] # reorder/reindex as Date first
df['Confirmed'] = df['Confirmed'].astype('int64')

all_df = pd.read_csv(args.datafile, index_col=0) # match defunct from_cvs
all_df['Date'] = pd.to_datetime(all_df['Date']).dt.normalize()
all_df['Confirmed'] = all_df['Confirmed'].astype('int64')

# Telengana was changed to Telanagana on June 11, 2020!
all_df['State'] = all_df['State'].replace('Telengana', 'Telangana')

# Remove asterisk's, happened to Telangana on July 26, 2020.
all_df['State'] = all_df['State'].str.rstrip('*')   # remove asterisks.

all_df = all_df.drop_duplicates(keep='last') # June 11's data for both is same!

all_df = pd.concat([all_df, df]).drop_duplicates(subset=['Date', 'State'],
                                            keep='last').reset_index(drop=True)

modify_file(args.datafile, all_df.to_csv())
start_date = pd.Timestamp.now() - pd.to_timedelta(15, unit='d')
df = all_df[all_df['Date'] > start_date]
df = df.pivot(index='Date', columns='State', values='Confirmed').fillna(0)

# Styles for line plots!
colors = list('rgbyk')
styles = ['-', ':', '--']
def_cycler = cycler('linestyle', styles) * cycler('color', colors)
plt.rc('axes', prop_cycle=def_cycler)
plt.rcParams["figure.figsize"] = (14,11)

# Last day values might be just a copy of the previous day. Remove
# it from graphs if so.
if len(df.index) > 1 and df.iloc[-1].equals(df.iloc[-2]):
    df = df.head(-1)

# Plot all india total cases
fig, ax = plt.subplots()
df.sum(axis=1).plot.line(ax=ax, marker='o')
ax.grid()
plt.title("Total cases, all of India  (generated at %s IST)" %
        pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'))
plt.ylabel("Total number of confirmed cases")
if args.savefig:
    fig.savefig("covid19-india-total.png")
else:
    plt.show()

# Sort states and plot total cases of top 10 states
df = df.reindex(df.iloc[-1].sort_values(ascending=False).index, axis=1)
fig, ax = plt.subplots()
# Include only top 10
df.iloc[:,0:10].plot.line(ax=ax, marker='o')
ax.grid()
plt.title("Total cases, top 10 states  (generated at %s IST)" %
        pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'))
plt.ylabel("Total number of confirmed cases")
if args.savefig:
    fig.savefig("covid19-states-total.png")
else:
    plt.show()

# Plot new cases of all india
fig, ax = plt.subplots()
df.sum(axis=1).diff().plot.line(ax=ax, marker='o')
ax.grid()
plt.title("New cases, all of India  (generated at %s IST)" %
        pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'))
plt.ylabel("Number of new cases")
if args.savefig:
    fig.savefig("covid19-india-new.png")
else:
    plt.show()

# Sort and plot new cases of top 10 states
df = df.diff() # computes daily new cases
df = df.reindex(df.iloc[-1].sort_values(ascending=False).index, axis=1)
fig, ax = plt.subplots()
# Include only top 10
df.iloc[:,0:10].plot.line(ax=ax, marker='o')
ax.grid()
plt.title("New cases, top 10 states  (generated at %s IST)" %
        pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'))
plt.ylabel("Number of new cases")
if args.savefig:
    fig.savefig("covid19-states-new.png")
else:
    plt.show()
