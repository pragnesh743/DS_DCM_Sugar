
# DS_DCM_Sugar Sock-PH Prediction

# Problem Statement
The problem statement is to predict a set points such way,so we get sock-ph value 9.1.

## Roadmap
Data collection   
Data cleaning and processing  
Data EDA- slecting Hyper parameter for VAR model  
Training-Testing  
Infer with live data  
Create a executable file  

### Data collection
We have collected data from Osisoft Pi in text formate.collected data stored in `./values/values.txt`.  
### Data cleaning and processing 
Path required in data cleaning and processing are confgured in `app.cfg` as below.  
`[Raw_data]`  
`value_txt=./values/values.txt`  
`data_path_p1=./Data/S_data1/`  
`data_path_p2=./Data/S_data_processed1/`  
`interpolate_data=./Data/Interpolate1.csv`  

## Run Locally
EDA - Data resampling,outlier removeal 
```python DCS_sugar_EDA.py
```
### Crete web-id to factch data from Osipisoft
 Using ```pi_server_connection.py```

### Data EDA- slecting Hyper parameter for VAR model -Training-Testing
Before Starting modeling read this document about VAR model  
Now using this-
```bash
  DCM_sugar_EDA_training.ipynb 
```
or You can use ``` DCM_training.py ```

### main application
now run ```app.py```
** app.py ** is final app code.

To bundle app.py use pyinstaller 
you can install py installer using ``` pip install pyinstaller```
using ```pyinstaller --onefile app.py --icon=logo.ico --noconsole```
you can make app.exe which is lacated in ./build

