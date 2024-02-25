"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer
from JackTokenizer import Token


class CompilationError(BaseException):
    pass


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream, output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        output_stream.write("<token>\n")
        self.output_stream = output_stream
        self.tokenizer = JackTokenizer(input_stream)
        self.generator = input_stream.token_generator()
        self.cur_token: Token = next(self.generator)
        self.cur_indent = 0


    def eat(self, typ: list = None, text: list = None, check_type = False, check_text = False):  # eat function
        if self.cur_token:  # checking if reaches end of file
            if check_type and self.cur_token.type not in typ:
                raise Exception(f'Expected to get a token from type {typ} but got {self.cur_token.text} from type {self.cur_token.type} instead')
            elif check_text and self.cur_token.text not in text:
                raise Exception(f'Expected to get a token from {text} but got {self.cur_token.text} instead')
            self.output_stream.write(self.write_indent() + self.cur_token.token_string())
            self.cur_token = next(self.generator)
            return
        raise Exception("NO TOKEN TO WRITE")

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.output_stream.write("<class>\n")
        self.cur_indent += 1
        self.eat(text = ["CLASS"], check_text= True)
        class_name = self.cur_token.text
        self.eat(typ = ["IDENTIFIER"], check_type= True)
        self.eat(text = ["{"], check_text= True)

        self.compile_class_var_dec()

        self.eat(text = ["}"], check_text= True)
        if self.cur_token:  # not a function or a class field
            raise Exception("illegal format")
        self.output_stream.write("</class>\n")


    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        if not self.cur_token:
            return
        if self.cur_token.text not in ["STATIC", "FIELD"]:  # if there are no fields in the begin of class
            self.compile_subroutine()
            return

        self.output_stream.write("<classVarDec>\n")
        self.cur_indent += 1

        while self.cur_token.text in ["STATIC", "FIELD"]:  # compile all the fields of class
            self.eat(text = ["STATIC", "FIELD"], check_text= True)
            self.eat(text=["INT", "CHAR", "BOOLEAN", "CLASS_NAME"], check_text= True)
            self.eat(typ=["IDENTIFIER"], check_type=True)
            while self.cur_token.text == ",":
                self.eat(text=[","], check_text=True)
                self.eat(typ=["IDENTIFIER"], check_type=True)
            self.eat(text=[";"], check_text=True)

        self.output_stream.write("</classVarDec>\n")
        self.compile_subroutine()

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        if not self.cur_token or self.cur_token.text not in ["CONSTRUCTOR", "FUNCTION", "METHOD"]:
            return

        self.output_stream.write("<subroutineDec>\n")
        self.cur_indent += 1

        while self.cur_token.text in ["CONSTRUCTOR", "FUNCTION", "METHOD"]:  # compile all function in class
            self.eat(text=["CONSTRUCTOR", "FUNCTION", "METHOD"], check_text=True)
            if self.cur_token.type is "KEYWORD":
                self.eat(text=["INT", "CHAR", "BOOLEAN", "CLASS_NAME", "VOID"], check_text=True)
            elif self.cur_token.type == "IDENTIFIER":
                self.eat(typ=["IDENTIFIER"], check_type=True)
            else:
                raise Exception
            self.eat(typ=["IDENTIFIER"], check_type=True)
            self.eat(text=["("], check_text=True)
            self.compile_parameter_list()
            self.eat(text=[")"], check_text=True)
            # subroutine body
            self.eat(text=["{"], check_text=True)
            while self.cur_token.text != "RETURN":
                if self.cur_token.text == "VAR":
                    self.compile_var_dec()
                if self.cur_token.text == "LET":
                    self.compile_let()
                if self.cur_token.text == "DO":
                    self.compile_do()
                if self.cur_token.text == "IF":
                    self.compile_if()
                if self.cur_token.text == "WHILE":
                    self.compile_while()
            # subroutine return
            if self.cur_token.text == "RETURN":
                self.compile_return()
            else:  # every function in jack needs a return
                raise Exception("Function finished running without return")
            self.eat(text=["}"], check_text=True)
        self.output_stream.write("</subroutineDec>\n")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        if self.cur_token.text == ")":  # if no parameters in the list
            return
        self.output_stream.write("<parameterList>\n")
        self.eat(text=["INT", "CHAR", "BOOLEAN"], check_text=True)
        self.eat(typ=["IDENTIFIER"], check_type=True)
        while self.cur_token.text == ",":
            self.eat(text=[","], check_text=True)
            self.eat(text=["INT", "CHAR", "BOOLEAN", "VOID"], check_text= True)
            self.eat(typ=["IDENTIFIER"], check_type=True)
        self.output_stream.write("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.output_stream.write("<varDec>\n")
        self.eat(text=["VAR"], check_text=True)
        if self.cur_token and self.cur_token.type is "KEYWORD":
            self.eat(text= ["INT", "CHAR", "BOOLEAN"], check_text=True)
        elif self.cur_token and self.cur_token.type is "IDENTIFIER":
            self.eat(typ=["IDENTIFIER"], check_type= True)
        else:
            raise Exception(f'No Type declaration')
        self.eat(typ=["IDENTIFIER"], check_type=True)
        while self.cur_token.text == ",":
            self.eat(text=[","], check_type=True)
            self.eat(text=["IDENTIFIER"], check_text=True)
        self.eat(text=[";"], check_text=True)
        self.output_stream.write("</varDec>\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        # Your code goes here!
        pass

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.output_stream.write("<doStatement>\n")
        self.eat(text=["DO"], check_text=True)
        self.eat(typ=['IDENTIFIER'], check_type=True)
        if self.cur_token and self.cur_token.text:
            if self.cur_token and self.cur_token.text == "(":
                self.eat(text=['('], check_text=True)
                self.compile_expression_list()
                self.eat(text=[')'], check_text=True)
                self.eat(text=["."], check_text=True)
        self.eat(typ=['IDENTIFIER'], check_type=True)
        self.eat(text=['('], check_text=True)
        self.compile_expression_list()
        self.eat(text=[')'], check_text=True)
        self.eat(text=[";"], check_text=True)
        self.output_stream.write("</doStatement>\n")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.output_stream.write("<letStatement>\n")
        self.cur_indent += 1
        self.eat(text=["LET"], check_text=True)
        self.eat(typ=['IDENTIFIER'], check_type=True)
        if self.cur_token and self.cur_token.text == "[":
            self.compile_expression()
            self.eat(text=["]"], check_text=True)
        self.eat(text=["="], check_text=True)
        self.compile_expression()
        self.eat(text=[";"], check_text=True)
        self.output_stream.write("</letStatement>\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.output_stream.write("<whileStatement>\n")
        self.cur_indent += 1
        self.eat(text=["WHILE"], check_text=True)
        self.eat(text=["("], check_text=True)
        self.compile_expression()
        self.eat(text=[")"], check_text=True)
        self.eat(text=["{"], check_text=True)
        self.compile_statements()
        self.eat(text=["}"], check_text=True)
        self.output_stream.write("</whileStatement>\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.output_stream.write("<returnStatement>\n")
        self.eat(text=["RETURN"], check_text=True)
        if self.cur_token.text != ";":
            self.compile_expression()
        self.eat(text=[";"], check_text=True)
        self.output_stream.write("</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.output_stream.write("<ifStatement>\n")
        self.cur_indent += 1
        self.eat(text=["IF"], check_text=True)
        self.eat(text=["("], check_text=True)
        self.compile_expression()
        self.eat(text=[")"], check_text=True)
        self.eat(text= ["{"], check_text=True)
        self.compile_statements()
        self.eat(text=["}"], check_text=True)
        if self.cur_token and self.cur_token.text == "ELSE":
            self.eat(text=["ELSE"], check_text=True)
            self.eat(text=["{"], check_text=True)
            self.compile_statements()
            self.eat(text=["}"], check_text=True)
        self.output_stream.write("</ifStatement>\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.eat(typ=['IDENTIFIER'], check_type=True)

    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Your code goes here!
        pass

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        pass

    def write_indent(self):
        indent = ""
        for i in range(self.cur_indent):
            indent = indent + " "
        return indent