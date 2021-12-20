# Read me

## Program overview

The Wubuy Frequency Finder is a simple program which reads in formatted Wubuy texts and produces an output describing the phonotactic environments found at word boundaries. This output is split into 3 different files of increasing complexity. The first, *output.txt*, provides a summery of the different target environments, tallying paused and unpaused word boundaries separately. The second file, *output_long.txt*, provides the same information as the summary, with the addition of each exact phonological environments that were found. The final file, *word_environments.txt*, takes this a step further and provides a list of the words that created the environments in order of appearance.

The program ignores both morphological boundaries present in the input for the purposes of looking for sound environments, though these boundaries are preserved in the provided word-list. For further information on how the program handles input see the section on Formatting below.

### Running the program

In order to run the program you must first open a terminal (or command prompt) and run the following command:

> python3 <path_to_file>/Frequency_Finder.py <input_file>

If no input file is specified, the file *test data.txt* will be used.

NOTE: This program requires at least python 3.9, if unsure of which version you currently have run:

> python3 --version


## Input Formatting

The program assumes that the input file has no headings and each line starts with marking for paragraph and line as well as a page number of the source in the following format:

>	\<paragraph>.\<line> \<page_number>
	
Additionally the program only currently supports text files that only contains the Wubuy language examples. sgs: found this sentence confusing and don't understand it.

### Special characters

The program automatically ignores the following characters when finding phonetic environments:

+ \* 				- notes in original text
+ Ø					- zero morpheme
+ "					- quotation
+ '					- obscured phoneme(s)
+ \>					-"completion of word" (from Heath 1980 pg. 13)

These characters will still be present in the outputted word-list.

Words surrounded by \<zigzag>...\</zigzag>, representing uncertain transcriptions, are counted by the program.

### Pauses

The following characters will create a paused environment between words.

+ .
+ ,
+ !

### 'Illegal' words

The following markings will mark a word as invalid for analysis, preventing any targets being found involving them

+ \<und>...\</und> 	- non native words
+ xxx 				- unintelligible
+ (...)				- annotations
+ --					\- interruption in text

## Log files

Each time the program is run it will produce a log file, named for the time of program execution. This provides a breakdown of each word found by the program, as well as the matches found. However they are primarily for the purposes of finding errors, and can safely be ignored.
