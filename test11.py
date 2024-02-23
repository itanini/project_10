# Open a Jack file for reading
from JackTokenizer import JackTokenizer

with open("C:/Users/itani/BioInformatics/3-A/NAND/nand2tetris/projects/10/check_11.txt", "r") as input_file:
    # Create an instance of JackTokenizer
    tokenizer = JackTokenizer(input_file)

# Open the output file for reading
with open("output_file.txt", "r") as output_file:
    # Print the contents of the output file
    print(output_file.read())
