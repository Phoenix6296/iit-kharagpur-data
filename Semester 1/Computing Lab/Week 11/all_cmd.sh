#!/bin/bash

# Create or clear the output file
> output_all.txt

# #1: Calculator Commands
echo "#1 Calculator Commands" >> output_all.txt
bash calculator.sh 10 + 5 >> output_all.txt
bash calculator.sh 20 "*" 3 >> output_all.txt
bash calculator.sh 30 / 0 >> output_all.txt

# #2: LCM Commands
echo -e "\n#2 LCM Commands" >> output_all.txt
bash lcm.sh numbers_2_1.txt >> output_all.txt
bash lcm.sh numbers_2_2.txt >> output_all.txt

# #3: Password Generator Commands
echo -e "\n#3 Password Generator Commands" >> output_all.txt
bash password.sh 5 >> output_all.txt
bash password.sh 16 >> output_all.txt

# #4: Word Count Commands
echo -e "\n#4 Word Count Commands" >> output_all.txt
bash wordcount.sh file_4.txt fifa >> output_all.txt
bash wordcount.sh file_4.txt 2024 >> output_all.txt

# #5: API Fetch Commands
echo -e "\n#5 API Fetch Commands" >> output_all.txt
bash api-fetch.sh Enhancement >> output_all.txt
cat combined_issues.json >> output_all.txt

# #6: To-Do List Manager Commands
echo -e "\n#6 To-Do List Manager Commands" >> output_all.txt
bash todo.sh add "Walk the dog" medium >> output_all.txt
bash todo.sh add "Call mom" low >> output_all.txt
bash todo.sh add "Finish homework" high >> output_all.txt
bash todo.sh add "Submit project report" high >> output_all.txt
bash todo.sh add "Buy groceries" high >> output_all.txt
bash todo.sh complete 5 >> output_all.txt
bash todo.sh complete 3 >> output_all.txt
bash todo.sh add "Pay bills" high >> output_all.txt
bash todo.sh add "Watch a movie" urgent >> output_all.txt
bash todo.sh complete 10 >> output_all.txt
bash todo.sh show >> output_all.txt

# #7: Search Books Script Commands
echo -e "\n#7 Search Books Commands" >> output_all.txt
bash search_books.sh books_7.txt "dark night" -both 3 >> output_all.txt
bash search_books.sh books_7.txt "howling" -both 2 >> output_all.txt

# #8: Log File Analyzer Command
echo -e "\n#8 Log File Analyzer Command" >> output_all.txt
bash analyselog.sh access_8.log 15 >> output_all.txt

# #9: Alternating Case Text Processor Commands
echo -e "\n#9 Alternating Case Commands" >> output_all.txt
bash alternatecase.sh file_9_1.txt test >> output_all.txt
bash alternatecase.sh file_9_2.txt test >> output_all.txt

# #10: Lexicographic Text Processor Commands
echo -e "\n#10 Lexicographic Text Processor Commands" >> output_all.txt
bash lexiographic.sh input_dir output_dir >> output_all.txt
for file in output_dir/*.txt; do
  count=$(wc -l < "$file")
  if [ "$count" -gt 0 ]; then
    echo "$(basename "$file" .txt) -> $count" >> output_all.txt
  fi
done

# Indicate that the script has finished running
echo -e "\nAll commands have been executed. Results are saved in output_all.txt"
