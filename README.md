# csvtools
Tools to manipulate CSV files

## csvmap
Update values of specified columns.

### Usage
```
python csvmap.py --map colname,oldvalue,newvalue [colname,oldvalue,newvalue...] < old.csv > new.csv
```

## csvmerge
Merge CSV files with different column names

By default any column name that does not appear in all CSV files is dropped from the final output.

### Usage
```
python csvmerge.py file1.csv [file2.csv...]
```

### Example
```
python csvmerge.py test/1.csv test/2.csv > 3.csv
```
