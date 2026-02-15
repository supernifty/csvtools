[![Build](https://github.com/supernifty/csvtools/actions/workflows/python-package.yml/badge.svg)](https://github.com/supernifty/csvtools/actions/workflows/python-package.yml)

# csvtools
Tools to manipulate CSV files

Summary of available tools:

## [add_count](csvtools/add_count.py)
Add a new column which incrementally increases in value, optionally grouped by values in other (specified) columns

```
add_count.py --cols key --dest count < test/3.csv
```
## [csvadd.py](csvtools/csvadd.py)
Add a new column with a value determined by using rules based on other columns

```
csvadd.py --name greet --value no --rule key=hello:yes < test/3.csv
```
## [csvcalc.py](csvtools/csvcalc.py)
Calculate a new column based on mapping existing column values.
Reads a CSV from stdin and uses provided source and destination value lists to append a new computed column.

## [csvcols.py](csvtools/csvcols.py)
Filter on columns and perform other operations on columns

```
csvcols.py --cols key < test/3.csv
csvcols.py --starts_with v < test/3.csv
```

## [csvdiff.py](csvtools/csvdiff.py)
Compare two files on a cell level

```
csvtools/csvdiff.py --key Y --f1 test/join1.csv --f2 test/diff.csv
```
## [csvdrophead.py](csvtools/csvdrophead.py)
Drops header lines beginning with '##' 

```
csvtools/csvdrophead.py < test/1.vcf
```

## [csvempty.py](csvtools/csvempty.py)
Counts missing data for each column

```
csvempty.py < test/missing.csv
```

## [csvfilter.py](csvtools/csvfilter.py)
Filter rows using rules

```
csvfilter.py --filter 'x>0' < test/missing.csv
```

## [csvfilter_cols.py](csvtools/csvfilter_cols.py)
Remove columns not matching a rule

```
python csvtools/csvfilter_cols.py --min 5 --keep Class < test/iris.tsv
```

## [csvfilter_boring.py](csvtools/csvfilter_boring.py)
Drop columns containing numeric data with a small range or low mean. Columns containing non-numeric data are always retained.

```
python csvtools/csvfilter_boring.py --min_range 5 < test/iris.tsv
```
## [csvfilter_file.py](csvtools/csvfilter_file.py)
Filter one file based on another
```
python csvtools/csvfilter_file.py --col sample --file test/todo.csv < test/iris.csv
```

## [csvflatten](csvtools/csvflatten.py)
Converts a table into two columns by making a "key" which includes each column name

```
csvflatten.py --key Key < test/3.csv
```

## [csvgroup](csvtools/csvgroup.py)
Combine rows by grouping columns following a specified rule

```
csvgroup.py --op state=join pop=sum < test/5.csv
```
## [csvhist.py](csvtools/csvhist.py)
Generate counts of each value in a specified column (or combination of columns)

```
csvhist.py --cols Col1 < test/join1.csv
csvhist.py --cols 'Sepal Length' --bins 5 --numeric < test/iris.tsv
```

## [csvjoin.py](csvtools/csvjoin.py)
Joins two tables based on a key column from each

```
python csvjoin.py --keys col1 col2 --files file1 file2.csv > file3.csv
```

```
csvtools/csvjoin.py --keys key key2 --files test/3.csv test/4.csv
```

## [csvmap](csvtools/csvmap.py)
Update values of specified columns.

```
python csvmap.py --map colname,oldvalue,newvalue [colname,oldvalue,newvalue...] < old.csv > new.csv
```

## [csvmapfile](csvtools/csvmapfile.py)
Map values in a specified column using a mapping file.
The tool reads the mapping and applies it to update or append the target column.

```
python csvmapfile.py --mapfile fn --source_col --map_col_from --map_col_to < old.csv > new.csv
```

## [csvmatrix](csvtools/csvmatrix.py)
Convert CSV data by pivoting values in a specified column into new columns.
Each unique value becomes a new column, with corresponding data populated from the input.

```
csvmatrix.py --x  key --y v1 --z v2 < test/3.csv
```

## [csvmd](csvtools/csvmd.py)
Converts to a md compatible table

```
csvmd.py < test/1.csv
```


## [csvmerge](csvtools/csvmerge.py)
Merge CSV files horizontally with different column names

By default any column name that does not appear in all CSV files is dropped from the final output.

```
python csvmerge.py file1.csv [file2.csv...]
```

```
python csvmerge.py test/1.csv test/2.csv > 3.csv
```


## [csvmin](csvtools/csvmin.py)
Filters a column numerically on range.

```
csvmin.py --col x --min 0 < test/missing.csv
```

## [csvnorm](csvtools/csvnorm.py)
Adds a total column and updates specified columns to be a proportion of this total by row

```
csvnorm.py --cols Shared1 Shared2 Only1 < test/1.csv
```

## [csvnormalise_mean](csvtools/csvnormalise_mean.py)
Normalises each specified column individually to the mean

```
csvtools/csvnormalise_mean.py --cols Shared1 Shared2 Only1 < test/1.csv
```

## [csvnormalise_range](csvtools/csvnormalise_range.py)
Normalises each specified column individually as a proportion of the (maximum-minimum) observed value

```
csvtools/csvnormalise.py --cols Shared1 Shared2 Only1 < test/1.csv
```

## [csvop](csvtools/csvop.py)
Apply an operation on column or columns to generate a new column.

```
csvop.py --op sum --cols Shared1 Shared2 --dests Total < test/1.csv
```

## [csvpivot](csvtools/csvpivot.py)
Pivot CSV data based on a specified column.
Transforms the input so that values in the pivot column become new headers.

```
csvpivot.py --pivot key2 < test/4.csv
```
## [csvsort](csvtools/csvsort.py)
Sort rows on a selected column or columns

```
csvsort.py --cols x --numeric < test/missing.csv
```
## [csvsplit](csvtools/csvsplit.py)
split into multiple files based on a column value

```
csvsplit.py --col key --target out.value.csv < test/3.csv # generates out.hello.csv out.goodbye.csv

``` 

## [csvsplit_horizontal.py](csvtools/csvsplit_horizontal.py)
Split a CSV file horizontally into multiple files, each with a fixed number of data lines, while preserving the header.

```
csvsplit_horizontal.py --lines 2 --target out.value.csv < test/3.csv # generates out.0.csv out.1.csv
```

## [csvstratify](csvtools/csvstratify.py)
make a stratified (categorical) variable from a continuous variable

```
csvstratify.py --col x --dest xcat --names Low High --separators 0 < test/missing.csv
```
## [csvsubsample](csvtools/csvsubsample.py)
writes each row with a provided probability

```
csvsubsample.py --probability 0.5 < test/5.csv
```

## [csvshrink](csvtools/csvshrink.py)
reduce column values using Dirichlet shrinkage to prior

```
csvshrink.py --cols S18 --k 4 --n_col S36 < test/pivot.csv
```

## [csvsummary](csvtools/csvsummary.py)
summarise columns. numeric are summarised with mean stdev etc, categorical with counts

```
csvsummary.py --cols pop < test/5.csv
```

## [csvungroup](csvtools/csvungroup.py)
removes columns and replaces each column removed with a row containing colname/value. useful for where you want two columns of the form key/value, such as supernifty/plotme/heatmap.

```
csvungroup.py --cols country state --targetname n --targetvalue v < test/5.csv
```

## [csvunique](csvtools/csvunique.py)
filter out duplicate rows

```
csvunique.py --cols key < test/3.csv
```

## [csvunique_simple](csvtools/csvunique_simple.py)
Filter out duplicate rows, considering all columns, preserving only the first occurrence.

```
csvunique_simple.py < test/3.csv
```

## [csvview](csvtools/csvview.py)
Format rows with fixed width (vertical) or as individual lines (horizontal)

```
csvview.py --mode vertical < test/3.csv
```
## [reorder](csvtools/reorder.py)
Write rows in order specified on command line - note that this doesn't treat the header differently, it counts as line 0

```
reorder.py 0 3 2 1 < test/3.csv

