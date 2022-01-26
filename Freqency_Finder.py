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
reC = re.compile(u'[bɖwŋrɲgmyj]')	#Constonetns
reV = re.compile(u'[aiuoe]')			#Vowels
rePause = re.compile(u'[.,!]')		#pauses

"""
	A phonotactic patern is a list of sound groups, boundries, and control values defined by a string.
	Charicters and their meanings:
		C 	- constonent
		V	- vowel
		-	- morpheme boundry
		=	- verb root morpheme boundry
		#	- word boundry
		*	- at least one of the proceding value
		.	- any target
"""
class Pattern:
	def __inti__ (self, rawString):
		self.pattern = []
		# for each charicter in raw string
		for i in rawString:
			if i == 'V':
				self.pattern.append(True)
			elif i == 'C':
				self.pattern.append(False)
			else:
				#control charicter
				self.pattern.append(i)
	
	@staticmethod
	def match (pattern, values: list, edge: str = 'l'):
		# control variables
		control = 'nil'
		enviromentFound = ''
		# right edge of values search
		if edge == 'r':
			j = -1
			for i in range(-1, -(len(pattern.pattern))):
				# look for control variable
				if pattern.pattern[i] == '*':
					control = '*'
				# values 
				if type(pattern.pattern[i]) == bool:
					#handle control
					if control == '*':
						# one or more of charicter
						temp = ''
						while values[j].value == pattern.pattern[i]:
							# add next charicter to enviroment if it matches pattern
							temp = values[j].letter + temp
							j -= 1
						#check to see if match
						if len(temp) == 0:
							# no match found
							return 'nil'
						else:
							#match found; add to frount of found enviroment. reset control
							enviromentFound = temp + enviromentFound
							control = 'nil'
					#no control
					else:
						# check match
						if values[j].value == pattern.pattern[i]:
							enviromentFound = values[j].letter + enviromentFound
							j -= 1
						else:
							return 'nil'
		else:
			# left edge search
			j = 0
			for i in range(len(pattern.pattern)):
			# look for control variable
				if pattern.pattern[i] == '*':
					control = '*'
				# values 
				if type(pattern.pattern[i]) == bool:
					#handle control
					if control == '*':
						# one or more of charicter
						temp = ''
						while values[j].value == pattern.pattern[i]:
							# add next charicter to enviroment if it matches pattern
							temp = values[j].letter + temp
							j += 1
						#check to see if match
						if len(temp) == 0:
							# no match found
							return 'nil'
						else:
							#match found; add to frount of found enviroment. reset control
							enviromentFound = temp + enviromentFound
							control = 'nil'
					#no control
					else:
						# check match
						if values[j].value == pattern.pattern[i]:
							enviromentFound = values[j].letter + enviromentFound
							j += 1
						else:
							return 'nil'
		
		return enviromentFound


class PhonologicalValues:
	def __init__(self, rawString):
		# convert the letter to lower case for the phonological information
		self.letter = rawString.lower()
		self.value = bool(reV.match(rawString)) # V = true; C = false
		#logging.debug(self)

	def __repr__ (self):
		return (self.letter + ', ' + str(self.value))

class Morpheme:
	def __init__ (self, boundry, charicters):
		self.boundry = boundry
		self.charicters = charicters

class Word:
	# keeps track of weather invalid string end has ended
	invalClosed = True

	#at initilisation, convert raw word string into array of marked charicters
	def __init__(self, rawWordString):
		logging.debug(rawWordString)
		#Initilise variables
		self.wordAsValues = []
		self.morphemes = []
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
			if rePause.search(rawWordString):
				self.pausedBoundry = True
				# Strip the pause charicter from string
				self.wordString = re.sub(rePause, '', self.wordString)
			#split word into morphemes
			self.morphemes = re.split('[-=]', self.wordString)

			_morphemeBounds = []

			for char in self.wordString:
				if re.search('[-=]', char):
					_morphemeBounds.append(char)

			#loop over morphemes
			for morpheme in self.morphemes:
				_morphemeVal = []
				# loop over charicters
				for char in morpheme:
					if char == ":" or char == '\u032a':
						_morphemeVal[-1].letter += char
					else:
						_morphemeVal.append(PhonologicalValues(char))
				# add found values
				self.wordAsValues = self.wordAsValues + _morphemeVal
				# add morpheme
				if len(_morphemeVal) > 0:
					# create new morpheme with next bound
					self.morphemes.append(Morpheme(_morphemeBounds[0],_morphemeVal))
					# remove bound from list
					_morphemeBounds.pop(0)
				else:
					# for final morpheme, add a word boundry
					self.morphemes.append(Morpheme('#', _morphemeVal))
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
	def __init__ (self, lable):
		#initilise variables
		self.lable = lable
		self.enviroment = {}
		self.tally = 0
		self.words = {} #key = enviroment

	def add (self, value, word):
		#check subpaterns
		if self.subordPattern[0] != 'nill':
			for _pattern in self.subordPattern:
				pass
	
	def search(self, word):
		pass
	

		
class WordboundTargets (PhonotacticTargets):
	def __init__(self, lable):
		#initilise variables
		self.lable = lable
		self.unpaused = {}
		self.paused = {}
		self.unpausedTotal = 0
		self.pausedTotal = 0
		self.unpausedWords = {}
		self.pausedWords = {}
		# split lable into two patterns
		self.patterns = []
		patternstring = re.split('#', lable) # patterns[0] = word1; patterns[1] = word2 start
		# create patern as an array of booleans (T = V, F = C) and control charicters
		for pattern in patternstring:
			self.patterns.append(Pattern(pattern))

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


	def add(self, value: str, paused: bool, word1: str, word2: str):
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

	def search (self, word1: Word, word2: Word):
		# search first word end
		environmentFound = Pattern.search(self.patterns[0], word1.wordAsValues, 'r')
		if environmentFound == 'nil':
			return False
		# enter word boundry
		environmentFound += '#'
		# search second word
		temp = Pattern.search(self.patterns[1],word2.wordAsValues, 'l')
		if temp == 'nil':
			return False
		environmentFound += temp
		# add found enviroment
		self.add(environmentFound, word1.pausedBoundry, word1.wordString, word2.wordString)
		return True

class MorphemeBoundTarget (PhonotacticTargets):
	def __init__ (self, lable):
		self.lable = lable
		self.verbRoot = {}
		self.verbRootWords = {}
		self.verbRootTotal = 0
		self.enviroment = {}
		self.tally = 0
		self.words = {}
		#split lable into enviroments
		self.patterns = re.split('[-=]', lable)

	def __str__ (self):
		output = self.lable + ':\n\tVerb Roots:\n'
		for target in self.verbRoot:
			output += '\t\t' + target + ": " + self.verbRoot[target] + '\n'
		output += '\tTotal: ' + str(self.verbRootTotal) + '\nReguler morpheme boundries: \n'
		for target in self.enviroment:
			output += '\t' + target + ': ' + self.enviroment[target] + '\n'
		output += "Total: " + str(self.tally) + '(including verb root boundries: ' + str(self.tally + self.verbRootTotal) + ')\n'
		return output

	def wordEnviroments(self):
		output = self.lable + ':\n\tVerb Roots:\n'
		for target in self.verbRoot:
			output += '\t\t' + target + ": " + self.verbRoot[target] + '\n'
			for word in self.verbRootWords[target]:
				output += '\t\t\t' + word + '\n'
		output += '\tTotal: ' + str(self.verbRootTotal) + '\nReguler morpheme boundries: \n'
		for target in self.enviroment:
			output += '\t' + target + ': ' + self.enviroment[target] + '\n'
			for word in self.words:
				output += '\t\t' + word + '\n'
		output += "total: " + str(self.tally) + '(including verb root boundries: ' + str(self.tally + self.verbRootTotal) + ')\n'
		return output
	def summery(self):
		return self.lable + '\n\tVerb Root morpheme boundry: ' + str(self.verbRootTotal) + "\ntotal: " + str(self.tally) + '(including verb root boundries: ' + str(self.tally + self.verbRootTotal) + ')\n'
	def add (self, value: str, word: str):
		# check to see if special case
		if re.search('=', value):
			if value in self.verbRoot:
				# already exsissts in data
				self.verbRoot[value] += 1
				self.verbRootTotal += 1
				self.verbRootWords[value].append(word)
			else:
				# add new enviroment
				self.verbRoot.update({value:1})
				self.verbRootTotal += 1
				self.verbRootWords.update({value:[word]})
		else:
			# non verb root enviroment
			if value in self.verbRoot:
				# already exsissts in data
				self.enviroment[value] += 1
				self.tally += 1
				self.words[value].append(word)
			else:
				# add new enviroment
				self.enviroment.update({value:1})
				self.tally += 1
				self.words[value].update({value:word})

	def search (self, word: Word):
		for i in range(len(word.morphemes)):
			#ensure there is a morpheme to follow
			if i+1 < len(word.morphemes):
				Pattern.search()
	
def findWords():
	boundriesFound = 0
	#loop through words to find phonotactical rules:
	# word boundry patterns
	
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
			logging.error("Error on word %d in paragraph %d, %s"%(i, currentParagraph, convertedWords[i].rawString))
			logging.error('words: ' + str(len(convertedWords)) + ', i: ' + str(i) + ', keystring = ' + keyString)
	
	#return found boundries for data
	return boundriesFound


# initilise variables at run
# create dictionary of phonotactic enviroments
lableFile = open('targets.txt', 'r')
soundClasses = []
lables = ['CC#C','VC#C','V#C','V#V']
targets = {}
for lable in lables:
	targets.update({lable : PhonotacticTargets(lable)})

# set up file logging - will create a new log fine for each exicution of file
logging.basicConfig(filename = 'logs/' + str(datetime.datetime.now())+ '.log', encoding='utf-8', level=logging.DEBUG)

# control variables
currentParagraph = 0
totalBoundries = 0

# converted word buffer
convertedWords = []
try:
	#open source file (sys.argv[1]; defined at run) in read mode
	file = open(sys.argv[1], 'r', encoding="utf-8")
except:
	#open test data if no other file selected
	file = open('test data.txt', 'r', encoding="utf-8" )

#loop over lines in file
for line in file:

	# if the new line is a new paragraph, handle all words in buffer and update paragraph before continuing
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
	
# output data
output = open('output_long.txt', 'w', encoding="utf-8")
summery = open('output.txt','w', encoding="utf-8")
wordList = open('word_environments.txt', 'w', encoding="utf-8")

for target in targets:
	output.write(str(targets[target]) + '\n')
	# write a summoriesed output lacking enviroments
	summery.write(targets[target].lable + ':\n\tPaused: ' + str(targets[target].pausedTotal) + '\n\tUnpaused: ' + str(targets[target].unpausedTotal) + '\n\tTotal: ' + str(targets[target].pausedTotal + targets[target].unpausedTotal) + '\n')
	wordList.write(targets[target].wordEnviroments() +'\n')

output.write('Total Valid Boundries: ' + str(totalBoundries) + '\n')
summery.write('Total Valid Boundries: ' + str(totalBoundries) + '\n')
wordList.write('Total Valid Boundries: ' + str(totalBoundries) + '\n')


output.close()
summery.close()
wordList.close()
