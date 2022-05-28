CSV_FILES=$(wildcard data/*.csv)

data/train.csv : split.py data/matches_cleaned.json
	python $<

.PHONY : data
data : data/train.csv

.PHONY : clean
clean :
	rm -rf $(CSV_FILES)