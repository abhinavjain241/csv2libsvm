import csv
import subprocess
import argparse

TOTAL = 0
CATEGORICAL = 0
IGNORE = 0
CONVERTED = 0
IGR = 0

categorical_dict = {}
categorical_val = set()
ignore_val = set()
default_val = {}
# total_features = NUMERICAL

parser = argparse.ArgumentParser(description='Convert your CSV files to LIBSVM format. Works with categorical attributes too.')
parser.add_argument('csv_file', help='csv filename')
parser.add_argument('header_file', help='header filename')
parser.add_argument('libsvm_file', help='libsvm filename')
parser.add_argument('key_file', help='ID filename')

args = parser.parse_args()


# This part parses the header file and stores necessary information like default values and unique counts of each categorical attribute
with open(args.header_file) as header:
	i = 1
	for line in header:
		 a = line.split()
		 if a[1] == 'I' or a[1] == 'K' or a[1] == 'L': # Ignore I, Key, or Label Attributes
		 	IGNORE += 1
		 	ignore_val.add(i - IGR)
		 	i = i + 1
		 	continue
		 # if a[1] != 'I' or a[1] != 'K':
		 default_val[i - IGR] = a[3] # store default values of all attributes except the label
		 
		 if a[1] == 'C':
		 	 CATEGORICAL += 1
		 	 categorical_val.add(i - IGR) # add i to the set of categorical values
			 bashCommand = "cat %s | cut -d , -f %d | sort | uniq" % (args.csv_file, i - IGR) # return unique values of an attribute in the given column, here (i - IGR) because skipping first IGR attributes
			 cmd = subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE)
			 j = 0
			 cdict = {}
			 for line in cmd.stdout: # Parse output of the unix command
			 	if line.strip() == '':
			 		cdict[a[3]] = j
			 	else:
			 		cdict[line.strip()] = j  # Store correspondence of categorical value and increment
			 	j = j + 1
			 CONVERTED += j
			 # cdict[a[3]] = j # Finally add a correspondence for the default value as well
		 	 categorical_dict[i - IGR]  = cdict # Add this dictionary to the master dictionary where the keys are row numbers
		 i = i + 1 # Increment row number
	TOTAL = i - 1

NUMERICAL = TOTAL - CATEGORICAL - IGNORE
OFFSET = 1	
LABEL = TOTAL - OFFSET

print "Total Attributes:" + str(TOTAL)
print "Categorical:" + str(CATEGORICAL)
print "Numerical:" + str(NUMERICAL)
print "Converted Features:" + str(CONVERTED + NUMERICAL)
# print categorical_dict
# print total_features

key_file = open(args.key_file, 'w')

# This is the main part of the code which actually performs the conversion of the CSV data to LIBSVM format
with open(args.libsvm_file, 'w') as target:
	with open(args.csv_file) as data:
		csv_reader = csv.reader(data)
		for row in csv_reader:
			line = ""
			line += str(row[LABEL])
			line += " "
			i = 1
			l = 1
			# Store keys/ID in a separate file
			key_file.write(row[i - 1])
			key_file.write("\n")
			while i <= LABEL: # Loop through columns
				if i not in ignore_val:	
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
					line += new_item
					line += " "
				i = i + 1
			line += "\n"
			target.write(line)

# Close the key file
key_file.close()