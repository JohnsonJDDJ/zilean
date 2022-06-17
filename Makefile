CSV_FILES=$(wildcard data/*.csv)

.PHONY : test
test :
	pip install .
	pytest .

.PHONY : clean
clean :
	rm -rf $(CSV_FILES)