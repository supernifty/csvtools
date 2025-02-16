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

## csvdiff.py
Compare two files on a cell level

```
csvtools/csvdiff.py --key Y --f1 test/join1.csv --f2 test/diff.csv
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
## csvhist.py
Generate counts of each value in a specified column (or combination of columns)

```
csvhist.py --cols Col1 < test/join1.csv
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

## csvsplit_horizontal.py
split into multiple files based on line number - similar to split command but keeps the header

```
csvsplit_horizontal.py --lines 2 --target out.value.csv < test/3.csv # generates out.0.csv out.1.csv
```

## csvstratify
make a stratified (categorical) variable from a continuous variable

```
csvstratify.py --col x --dest xcat --names Low High --separators 0 < test/missing.csv
```
## csvsubsample
writes each row with a provided probability

```
csvsubsample.py --probability 0.5 < test/5.csv
```

## csvsummary
summarise columns. numeric are summarised with mean stdev etc, categorical with counts

```
csvsummary.py --cols pop < test/5.csv
```

## csvungroup
removes columns and replaces each column removed with a row containing colname/value. useful for where you want two columns of the form key/value, such as supernifty/plotme/heatmap.

```
csvungroup.py --cols country state --targetname n --targetvalue v < test/5.csv
```

## csvunique
filter out duplicate rows

```
csvunique.py --cols key < test/3.csv
```

## csvunique_simple
filter out duplicate rows considering all columns

```
csvunique_simple.py < test/3.csv
```

## csvview
Format rows with fixed width (vertical) or as individual lines (horizontal)

```
csvview.py --mode vertical < test/3.csv
```
## reorder
Write rows in order specified on command line - note that this doesn't treat the header differently, it counts as line 0

```
reorder.py 0 3 2 1 < test/3.csv

