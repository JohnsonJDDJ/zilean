CSV_FILES=$(wildcard data/*.csv)

.PHONY : test
test :
	pip install .
	coverage run -m pytest .
	coverage report -m 

.PHONY : clean
clean :
	rm -rf $(CSV_FILES)