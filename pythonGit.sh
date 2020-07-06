#! /bin/bash
# Helpful in bash basics
# https://www.thegeekstuff.com/2010/06/bash-array-tutorial/
# https://stackoverflow.com/questions/6723426/looping-over-arrays-printing-both-index-and-value

cd /Users/newjcc/Documents/Coding/Python/AutomateBoringStuff

# Declare array
declare -a fileList=()

# For file.py in current directory
for f in *.py
do
	# Add file name to the array
	fileList+=($f)
done

size=${#fileList[*]}
echo -e "\nNumber of files: ${size}"

for i in "${!fileList[@]}"
do
	echo -e "\t${i}: ${fileList[${i}]}"
done

# User enters number corresponding to file
read -p "Which file would you like to commit: " selection
selection=$(($selection*1)) # Making sure it is an integer
file="${fileList[selection]}"
echo -e "\nYou chose [${file}]."

# Get file name for selected file and add /commit it
git add "${file}"

echo 'Enter commit message'
read commitMessage

git commit -m "$commitMessage"

git push -u origin master

echo 'Commit pushed!'

exit