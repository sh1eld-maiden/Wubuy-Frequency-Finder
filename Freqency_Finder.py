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
import configparser


#define Regex paterns
reC = re.compile(u'[bɖwŋrɲgmyj]')	#Constonetns
reV = re.compile(u'[aiuoe]')		#Vowels
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
class PhonoPattern:
	def __init__ (self, rawString: str, pattern: list = ['nil']):
		if pattern[0] == 'nil':
			# base constructer
			self.pattern = []
			self.lable = rawString.strip('\n')
			# for each charicter in raw string
			for i in self.lable:
				if i == 'V':
					self.pattern.append(True)
				elif i == 'C':
					self.pattern.append(False)
				else:
					#control charicter
					self.pattern.append(i)
		else:
			# externally defined pattern constructor
			self.lable = rawString
			self.pattern = pattern

	def __str__ (self):
		return self.lable
	
	# returns a new pattern that is a reversed version of the pattern
	def reverse(self):
		temp =[]
		#loop through pattern, adding each element to start
		previous = 'nil'
		for sub in self.pattern:
			if type(sub) == bool:
				previous = sub
				temp.insert(0, sub)
			else:
				#controll element
				i = 0
				#loop over already flipped elements to find where to put the element
				for element in temp:
					if element == previous:
						i += 1
					else:
						# change in value, position found
						break
				# add in control element
				temp.insert(i, sub)

		logging.debug('flipped: ' + str(temp))
		#return new pattern
		return PhonoPattern(self.lable, temp)

	def matchEdge (self, values: list, edge: str = 'l'):
		logging.debug('edge matching; pattern: ' + str(self.pattern) + '; edge: ' + edge + '; values: ' + str(values))
		# control variables
		control = 'nil'
		environmentFound = []
		temp = ''
		# catch any list overflows, returning nil if one occurs
		try:
			# right edge of values search
			if edge == 'r':
				values.reverse()
				returnVal = self.reverse().matchEdge(values, 'l')
				
				#reverse array
				returnVal.reverse()

				return returnVal

				'''j = -1
				for i in range(-1, -1 * (len(self.pattern) +1 ), -1):
					logging.debug(str(i) + '; ' +  str(j))
					# look for control variable
					if self.pattern[i] == '*':
						logging.debug('control: *')
						control = '*'
					# values 
					if type(self.pattern[i]) == bool:
						#handle control
						if control == '*':
							# one or more of charicter
							temp = ''
							while values[j].value == self.pattern[i]:
								# add next charicter to enviroment if it matches pattern
								temp = values[j].letter + temp
								j -= 1
							# find minimum number of occurences
							minOccurence = 0
							logging.debug(range(i, -(len(self.pattern))))
							logging.debug(str(self.pattern))
							for sub in range(i, -(len(self.pattern))):
								if self.pattern[sub] == self.pattern[i]:
									# add to minimum number of occurences
									minOccurence += 1
								else:
									# if not a match, break and move index to last match
									i = sub + 1
									break
								# if the end of the pattern is reached as a match, move index to end
								if sub == -(len(self.pattern)):
									i = sub
							# check to see if match
							if len(temp) < minOccurence:
								# not enough occurences to match pattern
								logging.debug('no match')
								return 'nil'
							else:
								# match found; add to frount of found enviroment. reset control
								for val in temp:
									environmentFound = temp + environmentFound
								control = 'nil'
						#not control
						else:
							logging.debug(values[j])
							# check match
							if values[j].value == self.pattern[i]:
								environmentFound = values[j].letter + environmentFound
								j -= 1
							else:
								logging.debug('no match')
								return 'nil' '''

			else:
				# left edge search
				j = 0
				for i in range(len(self.pattern)):
				# look for control variable
					if self.pattern[i] == '*':
						# look back and match multibles of previous value
						while values[j].value == self.pattern[i-1]:
								# add next charicter to enviroment if it matches pattern
								environmentFound.append(values[j].letter)
								j += 1
					# values 
					if type(self.pattern[i]) == bool:
						# check match
						if values[j].value == self.pattern[i]:
							environmentFound.append(values[j].letter)
							j += 1
						else:
							logging.debug('no match')
							return ['nil']
			logging.debug('match found: ' + str(environmentFound))
			return environmentFound
		except (IndexError):
			# if overflowed a list; cannot be a match
			logging.debug('no match')
			return ['nil']

	def match (self, values: list):
		_matches = []
		for i in range(len(values)):
			if values[i].value == self.pattern[0]:
				# if a charicter matches the first part of the pattern, treat it as the start of an matchEdge
				temp = self.matchEdge(values[i:], 'l')
				if temp[0] != 'nil':
					# match found
					#convert to string
					strTemp = ''
					for str in temp:
						strTemp += str
					_matches.append(strTemp)
					i += len(temp) # skip over charicters already in match
		
		# if no matches found, return the empty array
		return _matches



class PhonologicalValue:
	def __init__(self, rawString):
		# convert the letter to lower case for the phonological information
		self.letter = rawString.lower()
		self.value = bool(reV.match(rawString)) # V = true; C = false
		#logging.debug(self)

	def __repr__ (self):
		return (self.letter + ', ' + str(self.value))

class Morpheme:
	def __init__ (self, boundry: str, values: list[PhonologicalValue]):
		self.boundry = boundry
		self.values = values

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
			if re.search('(<\/und>)|\)[,.]*$', rawWordString):
				# [.,!\'"]*$|[-=]	
				# end of invalid string, only at word or morpheme end
				Word.invalClosed = True

		# only handle data if a valid word; prevents words in the middle of brackets from being counted
		elif Word.invalClosed:
			#strip charicters to egnore
			self.wordString = re.sub('["*øØ\']|(<\/*zigzag>)|(<\/*sub>)', '', rawWordString)
			#check for pause at word boundry
			if rePause.search(rawWordString):
				self.pausedBoundry = True
				# Strip the pause charicter from string
				self.wordString = re.sub(rePause, '', self.wordString)
			#split word into morphemes
			self.morphemes = []
			_morphemeString = re.split('[-=]', self.wordString)

			_morphemeBounds = []

			for char in self.wordString:
				if re.search('[-=]', char):
					_morphemeBounds.append(char)

			# add word boundry to end to prevent overflow
			_morphemeBounds.append('#')

			#loop over morphemes
			for morpheme in _morphemeString:
				_morphemeVal = []
				# loop over charicters
				for char in morpheme:
					if char == ":" or char == '\u032a': # vowel lengthening and dental diacritic (\u032a)
						# ensure _morphemeVal is not empty
						if _morphemeVal:
							_morphemeVal[-1].letter += char
					else:
						_morphemeVal.append(PhonologicalValue(char))
				# add found values
				self.wordAsValues = self.wordAsValues + _morphemeVal
				# create new morpheme with next bound
				self.morphemes.append(Morpheme(_morphemeBounds[0],_morphemeVal))
				# remove bound from list
				_morphemeBounds.pop(0)
			
		# if word has no values set valid to false
		if len(self.wordAsValues) == 0:
			self.valid = False
		logging.debug(self)
				

	#format data to print
	def __str__(self):
		if self.valid:
			firstLine = '\t'
			secondLine = '\t'
			for sound in self.wordAsValues:
				if sound.value:
					firstLine += 'V\t'
				else:
					firstLine += 'C\t'
				secondLine += sound.letter + '\t'

			formattedString = ('Word: ' + self.rawString + '\nPaused Boundry: ' + str(self.pausedBoundry) + '\nStructure:\n' +firstLine +'\n' + secondLine)
		else:
			formattedString = ('Word: ' + self.rawString + '\nInvalid Word For Analysis')
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

class PhonotacticTarget:
	def __init__ (self, lable):
		#initilise variables
		self.lable = lable
		self.pattern = PhonoPattern(lable)
		self.environment = {} # enviroment : count
		self.tally = 0
		self.words = {} #key = enviroment

	def add (self, value: str, word: str):
		logging.debug("MATCH FOUND: " + value + '; word: ' + word)
		# check to see if enviroent previously encountered
		if value in self.environment:
			# increase counts and save word
			self.environment[value] += 1
			self.words[value].append(word)
			self.tally += 1
		else:
			#add new enviroenment
			self.environment.update({value:1})
			self.words.update({value:[word]})
			# increase tally
			self.tally += 1

	def search(self, word: Word):
		# find all matches for the pattern
		_environments = self.pattern.match(word.wordAsValues)
		# ensure matches found
		if _environments:
			# add each match found
			for environ in _environments:
				self.add(environ, word.wordString)
			
			#return True to indicate matches were found
			return True
		else:
			# no matches found, return False
			return False
	
	def __str__(self):
		output = self.lable + '\n'
		for key in self.environment:
			output += '\t' + key + ': ' + str(self.environment[key]) + '\n'
		output += 'total: ' + str(self.tally) + '\n'
		return output

	def summery(self):
		return self.lable + ': ' + str(self.tally)

	def wordEnvironments(self):
		output = self.lable + '\n'
		for key in self.environment:
			output += '\t' + key + ': ' + str(self.environment[key]) + '\n'
			for word in self.words[key]:
				output += '\t\t' + word + '\n'
		output += 'total: ' + str(self.tally) + '\n'
		return output

class WordboundTarget (PhonotacticTarget):
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
			self.patterns.append(PhonoPattern(pattern))

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
		
	def wordEnvironments(self):
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

	def summery(self):
		return self.lable + '\nUnpaused Boundries: ' + str(self.unpausedTotal) + '\nPaused Boundries: ' + str(self.pausedTotal) + '\nTotal: ' + str(self.pausedTotal + self.unpausedTotal) + '\n'

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
		environmentFound = ''
		# search first word end
		temp = self.patterns[0].matchEdge(word1.wordAsValues, 'r')
		if temp[0] == 'nil':
			return False
		# convert array into string
		for str in temp:
			environmentFound += str
		# word boundry
		environmentFound += '#'
		# search second word
		temp = self.patterns[1].matchEdge(word2.wordAsValues, 'l')
		if temp[0] == 'nil':
			return False
		# convert array into string
		for str in temp:
			environmentFound += str
		logging.debug('Word Edge Match: ' + environmentFound)
		# add found enviroment
		self.add(environmentFound, word1.pausedBoundry, word1.wordString, word2.wordString)
		return True

class MorphemeBoundTarget (PhonotacticTarget):
	def __init__ (self, lable):
		self.lable = lable
		self.verbRoot = {}
		self.verbRootWords = {}
		self.verbRootTotal = 0
		self.enviroment = {}
		self.tally = 0
		self.words = {}
		self.patterns = [] # 0 is before boundry, 1 is after
		#split lable into enviroments
		patternString = re.split('[-=]', lable)
		for string in patternString:
			self.patterns.append(PhonoPattern(string))
			# pattern array format: [Patern, Patern] where each element is an edge of the morpheme
		logging.debug(str(self.patterns[0]) + '; ' + str(self.patterns[1]))

	def __str__ (self):
		output = self.lable + ':\n\tVerb Roots:\n'
		for target in self.verbRoot:
			output += '\t\t' + target + ": " + str(self.verbRoot[target]) + '\n'
		output += '\tTotal: ' + str(self.verbRootTotal) + '\nReguler morpheme boundries: \n'
		for target in self.enviroment:
			output += '\t' + target + ': ' + str(self.enviroment[target]) + '\n'
		output += "Total: " + str(self.tally) + '(including verb root boundries: ' + str(self.tally + self.verbRootTotal) + ')\n'
		return output

	def wordEnvironments(self):
		# print verb root boundries
		output = self.lable + ':\n\tVerb Roots:\n'
		for target in self.verbRoot:
			output += '\t\t' + target + ": " + str(self.verbRoot[target]) + '\n'
			for word in self.verbRootWords[target]:
				output += '\t\t\t' + word + '\n'
		output += '\tTotal: ' + str(self.verbRootTotal) + '\nReguler morpheme boundries: \n'
		# print regular morpheme boundries
		for target in self.enviroment:
			output += '\t' + target + ': ' + str(self.enviroment[target]) + '\n'
			for word in self.words[target]:
				output += '\t\t' + word + '\n'
		output += "total: " + str(self.tally) + '(including verb root boundries: ' + str(self.tally + self.verbRootTotal) + ')\n'
		return output
	
	def summery(self):
		return self.lable + '\n\tVerb Root morpheme boundry: ' + str(self.verbRootTotal) + "\ntotal: " + str(self.tally) + '(including verb root boundries: ' + str(self.tally + self.verbRootTotal) + ')\n'
	
	def add (self, value: str, word: str):
		logging.debug("MATCH FOUND: " + value + "; word: " + word)
		# check to see if special case
		if re.search('=', value):
			if value in self.verbRoot:
				# pattern already encountered
				self.verbRoot[value] += 1
				self.verbRootTotal += 1
				self.verbRootWords[value].append(word)
			else:
				# add new enviroment
				self.verbRoot.update({value:1})
				self.verbRootTotal += 1
				self.verbRootWords.update({value:[word]})
			logging.debug("environment: " + value + '; tally: ' + str(self.verbRoot[value]))
		else:
			# non verb root enviroment
			if value in self.enviroment:
				# already exsissts in data
				self.enviroment[value] += 1
				self.tally += 1
				self.words[value].append(word)
			else:
				# add new enviroment
				self.enviroment.update({value:1})
				self.tally += 1
				self.words.update({value:[word]})
			logging.debug("environment: " + value + '; tally: ' + str(self.enviroment[value]))

	def search (self, word: Word):
		for i in range(len(word.morphemes)):
			#ensure there is a non empty morpheme to follow
			if i+1 < len(word.morphemes) and word.morphemes[i+1].values:
				# search right edge of first morpheme
				environmentFound = ''
				temp = self.patterns[0].matchEdge(word.morphemes[i].values, 'r')
				if temp[0] == 'nil':
					return False

				#convert array into string
				for str in temp:
					environmentFound += str
				# add in boundry
				environmentFound += word.morphemes[i].boundry
				# read left edge of second morpheme
				temp = self.patterns[1].matchEdge(word.morphemes[i+1].values, 'l')
				if temp[0] == 'nil':
					return False
				#convert array into string
				for strs in temp:
					environmentFound += strs
				self.add(environmentFound, word.rawString)
				return True
	
def findWords(_words: list[Word], _targets: list[PhonotacticTarget]):
	# loop through each word, passing to each pattern to search
	for i in range(len(_words)):
		# ensure word is valid for parsing
		if _words[i].valid:
			for target in _targets:
				# if wordboundry, pass two words
				if type(target) == WordboundTarget:
					# ensure there is a valid word following
					if i + 1 < len(_words) and _words[i+1].valid:
						target.search(_words[i], _words[i+1])
				else:
					#only requires one word
					target.search(_words[i])

# open config.ini and read elements
config = configparser.ConfigParser()
config.read('config.ini')

# set up file logging - will create a new log fine for each exicution of file
logging.basicConfig(filename = 'logs/' + str(datetime.datetime.now())+ '.log', encoding='utf-8', level=logging.DEBUG)

# initilise variables at run
targets = []
# create list of targets; split into two and one word targets
with open(config['targets']['target_list'], 'r') as file:
	for line in file:
		if re.search('#', line):
			# word bound environment
			targets.append(WordboundTarget(line))
		elif re.search('[-=]', line):
			# morpheme boundry environment
			targets.append(MorphemeBoundTarget(line))
		else:
			# whole word environment
			targets.append(PhonotacticTarget(line))

# control variables
currentParagraph = 0
totalBoundries = 0

# converted word buffer
convertedWords = []

#open source file (sys.argv[1]; defined at run) in read mode
file = open(config['system']['input'], 'r', encoding="utf-8")

#loop over lines in file
for line in file:

	# if the new line is a new paragraph, handle all words in buffer and update paragraph before continuing
	linePara = int(line[:(line.find('.'))])
	if linePara != currentParagraph:
		findWords(convertedWords, targets)
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
findWords(convertedWords, targets)
	
# output data
output = open(config['system']['output_folder'] + 'output_long.txt', 'w', encoding="utf-8")
summery = open(config['system']['output_folder'] +'output.txt','w', encoding="utf-8")
wordList = open(config['system']['output_folder'] +'word_environments.txt', 'w', encoding="utf-8")

for target in targets:
	output.write(str(target) + '\n')
	# write a summoriesed output lacking enviroments
	summery.write(target.summery() + '\n')
	wordList.write(target.wordEnvironments() +'\n')

output.close()
summery.close()
wordList.close()
