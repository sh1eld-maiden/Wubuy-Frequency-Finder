# coding= utf-8

"""
	File name: Frequency_finder.py
	Author: Chloe Turner
	Date Created: 07/12/2021
	Date Modified: 16/12/2021
	Python version: 3.10

	Version: 1.2
"""

import sys
import re 		#regex
import logging
import datetime


#define Regex paterns
# sgs: imo it's generally best to avoid single letter names
C = re.compile(u'[bɖwŋrɲgmyj]')	#Consonants
V = re.compile(u'[aiuoe]')			#Vowels
pause = re.compile(u'[.,!]')		#pauses

# sgs: would be good to give a brief comment describing what this class does and how to use it
class PhonologicalValues:
	def __init__(self, rawString):
		# sgs: consider doing some input validation here: what if rawString does not match either C or V?
		# convert the letter to lower case for the phonological information
		self.letter = rawString.lower()
		self.value = bool(V.match(rawString)) # V = true; C = false
		#logging.debug(self)

	def __repr__ (self):
		return (self.letter + ', ' + str(self.value))

# sgs: would be good to give a brief comment describing what this class does and how to use it
class Word:
	# keeps track of weather invalid string end has ended
	invalClosed = True

	#at initilisation, convert raw word string into array of marked charicters
	def __init__(self, rawWordString):
		logging.debug(rawWordString)
		#Initilise variables
		self.wordAsValues = []
		self.pausedBoundry = False
		#store raw string
		self.rawString = rawWordString

		# check for validity of word
		self.valid = True
		"""
			Invalid words include:
				> 'xxx' - uninteligable
				> underlined words - non native words
				> (...) - annotations
		"""
		if re.search('xxx|<\/*und>|[()]', rawWordString):
			# word is invalid
			self.valid = False
			if re.search('<und>|\(', rawWordString):
				# make words invalid untill anitation or fouren string ends
				Word.invalClosed = False
			if re.search('<\/und>[.,]*$|\)[,.]*$', rawWordString):
				# end of invalid string, only at word end
				Word.invalClosed = True

		# only handle data if a valid word; prevents words in the middle of brackets from being counted
		elif Word.invalClosed:
			#strip charicters to egnore
			self.wordString = re.sub('["*øØ\'><]|(<\/*zigzag>)', '', rawWordString)
			#check for pause at word boundry
			if pause.search(rawWordString):
				self.pausedBoundry = True
				# Strip the pause charicter from string
				self.wordString = re.sub(pause, '', self.wordString)
			#split word into morphemes
			self.morphemes = re.split('[-=]', self.wordString)

			#loop over morphemes
			for morpheme in self.morphemes:
				# loop over charicters
				for char in morpheme:
					if char == ":" or char == '\u032a':
						self.wordAsValues[-1].letter += char
					else:
						self.wordAsValues.append(PhonologicalValues(char))
		# if word has no values set valid to false
		if len(self.wordAsValues) == 0:
			self.valid = False
		logging.debug(self)
				

	#format data to print
	def __str__(self):
		firstLine = '\t'
		secondLine = '\t'
		for sound in self.wordAsValues:
			if sound.value:
				firstLine += 'V\t'
			else:
				firstLine += 'C\t'
			secondLine += sound.letter + '\t'

		formattedString = ('Word: ' + self.rawString + '\nPaused Boundry: ' + str(self.pausedBoundry) + '\nStructure:\n' +firstLine +'\n' + secondLine)
		return formattedString
	
	def __repr__ (self):
		if self.valid:
			letterValues = '('
			for sound in self.wordAsValues:
				letterValues += '[' + sound.letter + ', ' + str(sound.value) + '],'
			letterValues += ')'
			return ('word: ', self.rawString, ', paused: ',self.pausedBoundry, 'values: ', letterValues)
		else:
			return 'Invalid Word'
class PhonotacticTargets:
	def __init__(self, lable):
		#initilise variables
		self.lable = lable
		self.unpaused = {}
		self.paused = {}
		self.unpausedTotal = 0
		self.pausedTotal = 0
		self.unpausedWords = {}
		self.pausedWords = {}
	def __str__(self):
		output = self.lable + '\nUnpaused Boundries:\n'
		for target in self.unpaused:
			output += '\t' + target + ': ' + str(self.unpaused[target]) + '\n'
		output += '\tTotal Unpaused: ' + str(self.unpausedTotal) + '\nPaused Boundries:\n'
		for target in self.paused:
			output += '\t' + target + ': ' + str(self.paused[target]) + '\n'
		output += '\tTotal Paused: ' + str(self.pausedTotal) + '\n'
		output += 'Total for ' + self.lable + ': ' + str(self.pausedTotal + self.unpausedTotal)

		return output + '\n'
		
	def wordEnviroments(self):
		output = self.lable + '\nUnpaused Boundries:\n'
		for target in self.unpaused:
			output += '\t' + target + ': ' + str(self.unpaused[target]) + '\n'
			for wordEnv in self.unpausedWords[target]:
				output += '\t\t' + wordEnv + '\n'
		output += '\tTotal Unpaused: ' + str(self.unpausedTotal) + '\nPaused Boundries:\n'
		for target in self.paused:
			output += '\t' + target + ': ' + str(self.paused[target]) + '\n'
			for wordEnv in self.pausedWords[target]:
				output += '\t\t' + wordEnv + '\n'
		output += '\tTotal Paused: ' + str(self.pausedTotal) + '\n'
		output += 'Total for ' + self.lable + ': ' + str(self.pausedTotal + self.unpausedTotal)

		return output + '\n'


	def add(self, value, paused, word1, word2):
		if paused:
			if value in self.paused:
				# if enviroment has been found previously, incriment value
				self.paused[value] += 1
				self.pausedWords[value].append(word1+'#'+word2)
			else:
				#otherwise add new enviroment to the list
				self.paused.update({value:1})
				self.pausedWords.update({value:[(word1+'#'+word2)]})
			#incriment the count for target
			self.pausedTotal += 1
		else:
			if value in self.unpaused:
				# if enviroment has been found previously, incriment value
				self.unpaused[value] += 1
				self.unpausedWords[value].append(word1+'#'+word2)
			else:
				#otherwise add new enviroment to the list
				self.unpaused.update({value:1})
				self.unpausedWords.update({value:[(word1+'#'+word2)]})
			#incriment the count for target
			self.unpausedTotal += 1

# sgs: i think it's generally a bad idea to write functions which opeerate on global variables. it's hard to know what they depend on and what they will mutate.
#  also it would make it harder to use the functions in this file as a module to be imported into other scripts.
#  consider passing the global variables in as arguments instead.
# sgs: and yeah it's generally unclear to me what this function does. what are the inputs and outputs? 
def findWords():
	boundriesFound = 0
	#loop through words to find phonotactical rules
	for i in range(len(convertedWords)):
		try:
			lableString = ''
			keyString = ''
			# ensure there is a word following to prevent overflow
			if (i+1) < len(convertedWords):
				#ensure words are valid for analysis
				if convertedWords[i].valid and convertedWords[i+1].valid:
					# add to total word
					boundriesFound += 1
					# word final vowel
					if convertedWords[i].wordAsValues[-1].value:
						keyString += 'V#'
						lableString += (convertedWords[i].wordAsValues[-1].letter + '#')
						logging.debug('final vowel')
						# find word initial value
						if convertedWords[i+1].wordAsValues[0].value:
							logging.debug('initial vowel')
							keyString += 'V'
							lableString += (convertedWords[i+1].wordAsValues[0].letter)
						else:
							logging.debug('initial constonent')
							keyString += 'C'
							lableString += (convertedWords[i+1].wordAsValues[0].letter)
					else:
						logging.debug('final constonent')
						#word final constonent
						if convertedWords[i].wordAsValues[-2].value:
							logging.debug('VC end')
							#VC ending
							keyString += 'VC#'
						else:
							logging.debug('CC end')
							# CC ending
							keyString += 'CC#'
						# read final two letters as enviroment
						lableString += (convertedWords[i].wordAsValues[-2].letter + convertedWords[i].wordAsValues[-1].letter + '#')
						#word initial value
						if convertedWords[i+1].wordAsValues[0].value:
							logging.debug('initial vowel')
							keyString += 'V'
							lableString += (convertedWords[i+1].wordAsValues[0].letter)
						else:
							logging.debug('initial constonent')
							keyString += 'C'
							lableString += (convertedWords[i+1].wordAsValues[0].letter)
					# add entry to dictionary; key string is present
					if keyString in targets:
						logging.debug(keyString + ' Found: ' + lableString + ' with words ' + str(convertedWords[i]) + str(convertedWords[i+1]))
						targets[keyString].add(lableString, convertedWords[i].pausedBoundry, convertedWords[i].rawString, convertedWords[i+1].rawString)
		except IndexError:
			# sgs: is it ok to just log the error and ignore it? what if the user never looks at the log? maybe print a warning, or return an error code, or something.
			logging.error("Error on word %d in paragraph %d, %s"%(i, currentParagraph, convertedWords[i].rawString))
			logging.error('words: ' + str(len(convertedWords)) + ', i: ' + str(i) + ', keystring = ' + keyString)
	
	#return found boundries for data
	return boundriesFound


# initilise variables at run
# create dictionary of phonotactic enviroments
# sgs: label is spelled "label"
lables = ['CC#C','VC#C','V#C','V#V']
targets = {}
for lable in lables:
	targets.update({lable : PhonotacticTargets(lable)})

# set up file logging - will create a new log file for each execution of file
logging.basicConfig(filename = 'logs/' + str(datetime.datetime.now())+ '.log', encoding='utf-8', level=logging.DEBUG)

# control variables
currentParagraph = 0
totalBoundries = 0

# converted word buffer
convertedWords = []
try:
	#open source file (sys.argv[1]; defined at run) in read mode
	# sgs: the argparse library can handle getting the argument and providing a default value, see https://docs.python.org/3/library/argparse.html
	# sgs: see comment below about using `with open(...)`. file.close() is missing
	# also, if the user-provided file is corrupt or unable to be read, it would just happily use the default, which is confusing
	file = open(sys.argv[1], 'r', encoding="utf-8")
except:
	#open test data if no other file selected
	file = open('test data.txt', 'r', encoding="utf-8" )

#loop over lines in file
for line in file:

	# if the new line is a new paragraph, handle all words in buffer and update paragraph before continuing
	# sgs: this is confusing to me. maybe a little more explanation of how this tells you it's a new paragraph?
	# sgs: maybe i just need a better understanding of the input file structure.
	# sgs: ok yeah i get it now. 
	linePara = int(line[:(line.find('.'))])
	if linePara != currentParagraph:
		totalBoundries += findWords()
		# empty buffer of words
		convertedWords.clear()
		currentParagraph = linePara
		print(linePara)
		logging.debug('NEW PARAGRAPH: ' + str(linePara))

	#split line into list by whitespace, striping new line charicters
	new_line_list = re.split('\s+', line.strip('\n'))
	del new_line_list[1]	#delete page number from list
	del new_line_list[0]

	#convert raw string into parsed words
	for word in new_line_list:
		#ensure word has value
		if word != '':
			convertedWords.append(Word(word))

# handle the final paragraph's words
totalBoundries += findWords()

# sgs: consider whether the output from this tool will ever be fed into another tool. if so, think about
# 		making the format of the output more easily parsed by a computer, eg. a csv, or like a Pandas table or something. python has a csv package.
# 		that's not the only option just one i thought of. writing to files line by line manually is error prone

# sgs: if you use `with` to open files, it will automatically call close() when they go out of scope. for example
# with open('a', 'w') as a, open('b', 'w') as b:
# 		a.write("whatever")
# output data
output = open('output_long.txt', 'w', encoding="utf-8")
summery = open('output.txt','w', encoding="utf-8")
wordList = open('word_environments.txt', 'w', encoding="utf-8")

for target in targets:
	output.write(str(targets[target]) + '\n')
	# write a summorised output lacking enviroments
	summery.write(targets[target].lable + ':\n\tPaused: ' + str(targets[target].pausedTotal) + '\n\tUnpaused: ' + str(targets[target].unpausedTotal) + '\n\tTotal: ' + str(targets[target].pausedTotal + targets[target].unpausedTotal) + '\n')
	wordList.write(targets[target].wordEnviroments() +'\n')

output.write('Total Valid Boundries: ' + str(totalBoundries) + '\n')
summery.write('Total Valid Boundries: ' + str(totalBoundries) + '\n')
wordList.write('Total Valid Boundries: ' + str(totalBoundries) + '\n')


output.close()
summery.close()
wordList.close()
