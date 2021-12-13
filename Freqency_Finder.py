# coding= utf-8
import sys
import re 		#regex
import logging
import datetime


#define Regex paterns
C = re.compile(u'[bɖwŋrɲgmyj]')	#Constonetns
V = re.compile(u'[aiuoe]')			#Vowels
pause = re.compile(u'[.,!]')		#pauses

class PhonologicalValues:
	def __init__(self, rawString):
		self.letter = rawString
		self.value = bool(V.match(rawString)) # V = true; C = false
		logging.debug(self)

	def __repr__ (self):
		return (self.letter + ', ' + str(self.value))

class Word:
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
		if re.search('^xxx|<und>|[()]', rawWordString):
			self.valid = False

		# only handle data if a valid word
		else:
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

	def __str__(self):
		output = self.lable + '\nUnpaused Boundries:\n'
		for target in self.unpaused:
			output += '\t' + target + ': ' + str(self.unpaused[target]) + '\n'
		output += '\tTotal Unpaused: ' + str(self.unpausedTotal) + '\nPaused Boundries:\n'
		for target in self.paused:
			output += '\t' + target + ': ' + str(self.paused[target]) + '\n'
		output += '\tTotal Paused: ' + str(self.pausedTotal) + '\n'
		output += 'Total for ' + self.lable + ': ' + str(self.pausedTotal + self.unpausedTotal)

		return output
		

	def add(self, value, paused):
		if paused:
			if value in self.paused:
				# if enviroment has been found previously, incriment value
				self.paused[value] += 1
			else:
				#otherwise add new enviroment to the list
				self.paused.update({value:1})
			#incriment the count for target
			self.pausedTotal += 1
		else:
			if value in self.unpaused:
				# if enviroment has been found previously, incriment value
				self.unpaused[value] += 1
			else:
				#otherwise add new enviroment to the list
				self.unpaused.update({value:1})
			#incriment the count for target
			self.unpausedTotal += 1


def findWords():
	#loop through words to find phonotactical rules
	for i in range(len(convertedWords)):
		try:
			lableString = ''
			keyString = ''
			# ensure there is a word following to prevent overflow
			if (i+1) < len(convertedWords):
				
				#ensure words are valid for analysis
				if convertedWords[i].valid and convertedWords[i+1].valid:
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
						targets[keyString].add(lableString, convertedWords[i].pausedBoundry)
		except IndexError:
			logging.error("Error on word %d in paragraph %d, %s"%(i, currentParagraph, convertedWords[i].rawString))
			logging.error('words: ' + str(len(convertedWords)) + ', i: ' + str(i) + ', keystring = ' + keyString)


# initilise variables at run
# create dictionary of phonotactic enviroments
lables = ['CC#C','VC#C','V#C','V#V']
targets = {}
for lable in lables:
	targets.update({lable : PhonotacticTargets(lable)})

# set up file logging - will create a new log fine for each exicution of file
logging.basicConfig(filename = 'logs/' + str(datetime.datetime.now())+ '.log', encoding='utf-8', level=logging.DEBUG)

# control variables
currentParagraph = 0

# converted word buffer
convertedWords = []

#open source file (sys.argv[1]; defined at run) in read mode
file = open(sys.argv[1], 'r', encoding="utf-8")

#loop over lines in file
for line in file:

	# if the new line is a new paragraph, handle all words in buffer and update paragraph before continuing
	linePara = int(line[:(line.find('.'))])
	if linePara != currentParagraph:
		findWords()
		# empty buffer of words
		convertedWords.clear()
		currentParagraph = linePara
		print(linePara)

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
findWords()
	
# output data
output = open('output_long.txt', 'w', encoding="utf-8")
summery = open('output.txt','w', encoding="utf-8")
for target in targets:
	output.write(str(targets[target]) + '\n')
	# write a summoriesed output lacking enviroments
	summery.write(targets[target].lable + ':\n\tPaused: ' + str(targets[target].pausedTotal) + '\n\tUnpaused: ' + str(targets[target].unpausedTotal) + '\n\tTotal: ' + str(targets[target].pausedTotal + targets[target].unpausedTotal) + '\n')
output.close()
summery.close()