"""This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re

END_COMMENT = ['//']
COMMENT = ['/', '/']
DOCUMENTATION = ['/', '*/']
CLOSED_COMMENT_REGEX = r'\/\/?\*.*\*\/'
OPEN_COMMENT_REGEX = r'\/\/.*'
ALL_COMMENTS = set(END_COMMENT+COMMENT+DOCUMENTATION)


ARITHMETIC_GROUPING =['(', ')']
ARRAY_INDEXING= ['[' ,']']
STATEMENT_GROUPING=['{','}']
LIST_SEPARATOR=[',']
STATEMENT_TERMINATOR = [';']
COMPARISON_OPERATOR = ['=']
CLASS_MEMBERSHIP = ['.']
OPERATORS = ['+','-','*','/','&','|','~', '<','>','^','#']
SYMBOLS = set(ARITHMETIC_GROUPING+ARRAY_INDEXING+STATEMENT_GROUPING+LIST_SEPARATOR+STATEMENT_TERMINATOR+
              COMPARISON_OPERATOR+CLASS_MEMBERSHIP+OPERATORS)

PROGRAM_COMPONENTS = ['class', 'constructor', 'method', 'function']
PRIMITIVE_TYPES = ['int', 'boolean', 'char', 'void']
VARIABLE_DECLARATIONS = ['var', 'static', 'field']
STATEMENTS = ['let', 'do', 'if', 'else', 'while', 'return']
CONSTANT_VALUES = ['true', 'false', 'null']
OBJECTIVE_REFERENCE = ['this']

KEYWORD = set(PROGRAM_COMPONENTS+PRIMITIVE_TYPES+VARIABLE_DECLARATIONS+STATEMENTS+CONSTANT_VALUES+OBJECTIVE_REFERENCE)

CLASS_NAMES = []
FUNCTION_NAMES = []
REGEX = r'"?\w+"?|\/\/|\\/|\/\+|-|\\/|&|\||~|<|>|\(|\)|\[|\]|\{|}|,|;|=|\.|\+|-|\|\/|&|\||~|<|>|\^|#'




def regex_maker(cur_line: str):
    return re.findall(REGEX, cur_line)



class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.

    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters,
    and comments, which are ignored. There are three possible comment formats:
    /* comment until closing / , /* API comment until closing */ , and
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' |
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' |
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' |
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate
    file. A compilation unit is a single class. A class is a sequence of tokens
    structured according to the following context free syntax:

    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type)
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement |
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{'
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions

    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName |
            varName '['expression']' | subroutineCall | '(' expression ')' |
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className |
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'

    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        #
        self.cur_token = None
        self.cur_line = None
        file = input_stream.read()
        comment_clean_input = self.comment_cleaner(file)
        self.input_lines = [line for line in comment_clean_input.splitlines() if line != '']
        pass

    def comment_cleaner(self, input_stream):
        comment_clean_input = re.sub(CLOSED_COMMENT_REGEX, '', input_stream, flags=re.DOTALL)
        comment_clean_input = re.sub(OPEN_COMMENT_REGEX, '', comment_clean_input)
        return comment_clean_input

    def token_generator(self):
        for cur_line in self.input_lines:
            self.cur_line = regex_maker(cur_line)
            while self.has_more_tokens():
                yield self.advance()
        yield None

    def process_token(self, cur_token_text, token_type):
        if token_type == "SYMBOL":
            return self.symbol(cur_token_text)
        elif token_type == "KEYWORD":
            return self.keyword(cur_token_text)
        elif token_type == "STRING_CONST":
            return self.string_val(cur_token_text)
        elif token_type == "INT_CONST":
            return self.int_val(cur_token_text)
        elif token_type == "IDENTIFIER":
            return self.identifier(cur_token_text)

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        if not self.cur_line:
            return False
        return True

    def advance(self):
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        cur_token_text = ""
        while cur_token_text == "" and self.cur_line:
            cur_token_text = self.cur_line.pop(0)
        if cur_token_text != "":
            token_type = self.token_type(cur_token_text)
            cur_token_text = self.process_token(cur_token_text, token_type)
            return Token(cur_token_text, token_type)

    def token_type(self, token_text) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if token_text in SYMBOLS:
            return "SYMBOL"
        elif token_text in KEYWORD:
            return "KEYWORD"
        elif token_text == '"' and token_text == '"':
            return "STRING_CONST"
        else:
            try:
                int(token_text)
                return "INT_CONST"
            except ValueError:
                return "IDENTIFIER"

    def keyword(self,cur_token_text) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return cur_token_text.upper()

    def symbol(self, cur_token_text) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        if cur_token_text == "<":
            return "&lt"
        elif cur_token_text == ">":
            return "&gt"
        elif cur_token_text == "&":
            return "&amp"
        else:
            return cur_token_text

    def identifier(self,cur_token_text) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        assert not cur_token_text.isdigit()
        return cur_token_text

    def int_val(self, cur_token_text) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        return int(cur_token_text)

    def string_val(self, cur_token_text) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        return cur_token_text[1:-1]


class Token:
    def __init__(self, text: str, token_type: str) -> None:
        self.text = text
        self.type = token_type

    def set_type(self, token_type):
        self.type = token_type

    def set_text(self, text):
        self.text = text

    def token_string(self) -> str:
        return f'<{self.type}> {self.text} </{self.type}>\n'