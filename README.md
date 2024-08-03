# csvtools
Tools to manipulate CSV files

Summary of available tools:

## add_count
Add a new column which incrementally increases in value, optionally grouped by values in other (specified) columns

```
add_count.py --cols key --dest count < test/3.csv
```
## csvadd.py
Add a new column with a value determined by using rules based on other columns

```
csvadd.py --name greet --value no --rule key=hello:yes < test/3.csv
```
## csvcalc.py
TODO

## csvcols.py
Filter on columns and perform other operations on columns

```
csvcols.py --cols greet < test/3.csv
```

## csvempty.py
Counts missing data for each column

```
csvempty.py < test/missing.csv
```

## csvfilter.py
Filter rows using rules

```
csvfilter.py --filter 'x>0' < test/missing.csv
```

## csvflatten
Converts a table into two columns by making a "key" which includes each column name

```
csvflatten.py --key Key < test/3.csv
```

## csvgroup
TODO Combine rows by grouping columns following a specified rule

```
csvgroup.py --delimiter '       ' --op Count=max
```

## csvjoin.py
Joins two tables based on a key column from each

```
python csvjoin.py --keys col1 col2 --files file1 file2.csv > file3.csv
```

```
csvtools/csvjoin.py --keys key key2 --files test/3.csv test/4.csv
```

## csvmap
Update values of specified columns.

```
python csvmap.py --map colname,oldvalue,newvalue [colname,oldvalue,newvalue...] < old.csv > new.csv
```

## csvmapfile
Update values of a specified column (source_col) using mappings from another file

```
python csvmapfile.py --mapfile fn --source_col --map_col_from --map_col_to < old.csv > new.csv
```

## csvmatrix
Converts values into columns: convert columns x y z to x [values of y] - and each new column of y contains the value of z

```
csvmatrix.py --x  key --y v1 --z v2 < test/3.csv
```

## csvmd
Converts to a md compatible table

```
csvmd.py < test/1.csv
```


## csvmerge
Merge CSV files horizontally with different column names

By default any column name that does not appear in all CSV files is dropped from the final output.

```
python csvmerge.py file1.csv [file2.csv...]
```

```
python csvmerge.py test/1.csv test/2.csv > 3.csv
```


## csvmin
Filters a column numerically on range.

```
csvmin.py --col x --min 0 < test/missing.csv
```

## csvnorm
Adds a total column and updates specified columns to be a proportion of this total by row

```
csvnorm.py --cols Shared1 Shared2 Only1 < test/1.csv
```
## csvnormalise
Normalises each specified column individually as a proportion of the maximum observed value

```
csvtools/csvnormalise.py --cols Shared1 Shared2 Only1 < test/1.csv
```

## csvop
Apply an operation on column or columns to generate a new column.

```
csvop.py --op sum --cols Shared1 Shared2 --dests Total < test/1.csv
```
```

## csvpivot
The values of a column become the column names, and the values of each row are then the values of those columns.

```
csvpivot.py --pivot key2 < test/4.csv
```
## csvsort
Sort rows on a selected column or columns

```
csvsort.py --cols x --numeric < test/missing.csv
```
## csvsplit
split into multiple files based on a column value

```
csvsplit.py --col key --target out.value.csv < test/3.csv # generates out.hello.csv out.goodbye.csv
``` 

## csvstratify
make a stratified (categorical) variable from a continuous variable

```
csvstratify.py --col x --dest xcat --names Low High --separators 0 < test/missing.csv
```

