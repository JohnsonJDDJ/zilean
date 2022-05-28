CSV_FILES=$(wildcard data/*.csv)

.PHONY : clean
clean :
	rm -rf $(CSV_FILES)