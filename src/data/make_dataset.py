import pandas as pd
from glob import glob

# --------------------------------------------------------------
# Read single CSV file
single_file_acc= pd.read_csv("../../Data/raw/MetaMotion/A-bench-heavy2-rpe8_MetaWear_2019-01-11T16.10.08.270_C42732BE255C_Accelerometer_12.500Hz_1.4.4.csv")

single_file_gyr= pd.read_csv("../../Data/raw/MetaMotion/A-bench-heavy2-rpe8_MetaWear_2019-01-11T16.10.08.270_C42732BE255C_Gyroscope_25.000Hz_1.4.4.csv")
# List all data in data/raw/MetaMotion
files= glob("../../Data/raw/MetaMotion/*.csv")
len(files)


# --------------------------------------------------------------
# Extract features from filename
# --------------------------------------------------------------
data_path=("../../Data/raw/MetaMotion/")
f=files[10]

participant= f.split("-")[0][-1]
label= f.split("-")[1]
category= f.split("-")[2].rstrip("123").rstrip("_MetaWear_2019")

df= pd.read_csv(f)
df["participant"]= participant
df["label"]= label
df["category"]= category
# --------------------------------------------------------------
# Read all files
# --------------------------------------------------------------
acc_df= pd.DataFrame()
gyr_df= pd.DataFrame()

acc_set= 1
gyr_set= 1

for f in files:
    
    participant= f.split("-")[0][-1]
    label= f.split("-")[1]
    category= f.split("-")[2].rstrip("123").rstrip("_MetaWear_2019")
    
    df= pd.read_csv(f)
    df["participant"]= participant
    df["label"]= label
    df["category"]= category
    
    if "Accelerometer" in f:
        df['set']= acc_set
        acc_set += 1
        acc_df= pd.concat([acc_df, df])        
        
    if "Gyroscope" in f:
        df['set']= gyr_set
        gyr_set += 1
        gyr_df= pd.concat([gyr_df, df])
# --------------------------------------------------------------
# Working with datetimes
# --------------------------------------------------------------
acc_df.info()

pd.to_datetime(df["epoch (ms)"], unit="ms")

pd.to_datetime(df["time (01:00)"]).dt.week

acc_df.index= pd.to_datetime(acc_df["epoch (ms)"], unit="ms")
gyr_df.index= pd.to_datetime(gyr_df["epoch (ms)"], unit="ms")

del acc_df["epoch (ms)"]
del acc_df["time (01:00)"]
del acc_df["elapsed (s)"]

del gyr_df["epoch (ms)"]
del gyr_df["time (01:00)"]
del gyr_df["elapsed (s)"]

# --------------------------------------------------------------
# Turn into function
# --------------------------------------------------------------
files = glob("../../Data/raw/MetaMotion/*.csv")

def read_data_from_files(files):
    acc_df= pd.DataFrame()
    gyr_df= pd.DataFrame()

    acc_set= 1
    gyr_set= 1

    for f in files:
    
        participant= f.split("-")[0][-1]
        label= f.split("-")[1]
        category= f.split("-")[2].rstrip("123").rstrip("_MetaWear_2019")
    
        df= pd.read_csv(f)
        df["participant"]= participant
        df["label"]= label
        df["category"]= category
    
        if "Accelerometer" in f:
            df['set']= acc_set
            acc_set += 1
            acc_df= pd.concat([acc_df, df])        
        
        if "Gyroscope" in f:
            df['set']= gyr_set
            gyr_set += 1
            gyr_df= pd.concat([gyr_df, df])
            
    acc_df.index= pd.to_datetime(acc_df["epoch (ms)"], unit="ms")
    gyr_df.index= pd.to_datetime(gyr_df["epoch (ms)"], unit="ms")

    del acc_df["epoch (ms)"]
    del acc_df["time (01:00)"]
    del acc_df["elapsed (s)"]

    del gyr_df["epoch (ms)"]
    del gyr_df["time (01:00)"]
    del gyr_df["elapsed (s)"]
    
    return acc_df,gyr_df

acc_df,gyr_df= read_data_from_files(files)

# --------------------------------------------------------------
# Merging datasets
# --------------------------------------------------------------
data_merge= pd.concat([acc_df.iloc[:,:3],gyr_df], axis=1)

#Rename columns
data_merge.columns= [
    "acc_x",
    "acc_y",
    "acc_z",
    "gyr_x",
    "gyr_y",
    "gyr_z",
    "participants",
    "label",
    "category",
    "sets",
]
# --------------------------------------------------------------
# Resample data (frequency conversion)
# --------------------------------------------------------------

# Accelerometer:    12.500HZ
# Gyroscope:        25.000Hz
sampling= {
    "acc_x": "mean",
    "acc_y": "mean",
    "acc_z": "mean",
    "gyr_x": "mean",
    "gyr_y": "mean",
    "gyr_z": "mean",
    "participants": "last",
    "label": "last",
    "category": "last",
    "sets": "last",
}

data_merge[:1000].resample(rule="200ms").apply(sampling)

#split by day
days = [g for n, g in data_merge.groupby(pd.Grouper(freq="D"))]
data_resampled = pd.concat([df.resample(rule="200ms").apply(sampling).dropna() for df in days])
data_resampled['sets'] = data_resampled['sets'].astype(int)
data_resampled.info()

# This code is creating a directory called "interim" inside the "../../Data" directory. If the
# directory already exists, it will not raise an error. Then, it saves the "data_resampled" DataFrame
# as a pickle file called "01_data_processing.pickle" inside the "interim" directory.
import os

output_directory = "../../Data/interim/"
os.makedirs(output_directory, exist_ok=True)

data_resampled.to_pickle(os.path.join(output_directory, "01_data_processing.pickle"))


# --------------------------------------------------------------
# Export dataset
# --------------------------------------------------------------

data_resampled.to_pickle("../../Data/interim/01_data_processing.pickle")

