import csv
import subprocess

HEADER_FILE = "header.2016v3.txt"
TOTAL = 345
CATEGORICAL = 56
NUMERICAL = TOTAL - CATEGORICAL
IGR = 9

# CSV_FILE = 'segmentaa'
CSV_FILE = 'dev_mix_v6_11-01-2016_17-01-2016.csv'

categorical_dict = {}
categorical_val = set()
default_val = {}
# total_features = NUMERICAL

# This part parses the header file and stores necessary information like default values and unique counts of each categorical attribute
with open(HEADER_FILE) as header:
	i = 1
	for line in header:
		 a = line.split()
		 if a[1] != 'I' or a[1] != 'K':
		 	default_val[i - IGR] = a[3] # store default values of all attributes except those which are Ignore or Key
		 if a[1] == 'C':
		 	 categorical_val.add(i - IGR) # add i to the set of categorical values
			 bashCommand = "cat %s | cut -d , -f %d | sort | uniq" % (CSV_FILE, i - IGR) # return unique values of an attribute in the given column, here (i - IGR) because skipping first IGR attributes
			 cmd = subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE)
			 j = 0
			 cdict = {}
			 for line in cmd.stdout: # Parse output of the unix command
			 	if line.strip() == '':
			 		cdict[a[3]] = j
			 	else:
			 		cdict[line.strip()] = j  # Store correspondence of categorical value and increment
			 	j = j + 1
			 #total_features += j
			 # cdict[a[3]] = j # Finally add a correspondence for the default value as well
		 	 categorical_dict[i - IGR]  = cdict # Add this dictionary to the master dictionary where the keys are row numbers
		 i = i + 1 # Increment row number
			 		
# print categorical_dict
# print total_features

# This is the main part of the code which actually performs the conversion of the CSV data to LIBSVM format
with open(CSV_FILE) as data:
	csv_reader = csv.reader(data)
	for row in csv_reader:
		line = ""
		line += str(row[TOTAL - 4])
		line += " "
		# line.append(row[TOTAL - 4])
		i = 1
		l = 1
		while i < TOTAL - 4: # Loop through columns
			if row[i - 1] == '':
				val = default_val[i]
			else:
				val = row[i - 1]
			new_list = [] # List for LIBSVM
			if i in categorical_val: # Check if field is categorical
				j = categorical_dict[i][val] # Get additional increment from i for the given value
				for k in range(0, len(categorical_dict[i])): # For x distinct values of the attribute 
					if k == j: # if the loop variable mat
						temp = "%d:1.000000" % (l + k)
					else:
						temp = "%d:0.000000" % (l + k)
					new_list.append(temp)
					new_item = " ".join(str(e) for e in new_list)
				l = l + len(categorical_dict[i])
			else:
				new_item = "%s:%.6f" % (l, float(val))
				l = l + 1
			i = i + 1
			line += new_item
			line += " "
		print line
