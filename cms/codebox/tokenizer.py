import html

KEYWORDS = {
    "if","else","for","while","switch","case",
    "break","continue","return","class","struct",
    "public","private","protected","virtual",
    "template","typename","namespace","using",
    "const","constexpr","static","inline","new","delete","this",
    "try","catch","throw"
}

BUILTIN_TYPES = {
    "int","float","double","char","bool",
    "short","long","unsigned","signed", "u_long",
    "size_t","void","wchar_t", "string","auto", "typedef",

    # Uints
    "uint8_t","uint16_t","uint32_t","uint64_t",
    "int8_t","int16_t","int32_t","int64_t",

    # C++20
    "char8_t","char16_t","char32_t"

}


class Token:
    def __init__(self, kind, text):
        self.kind = kind
        self.text = text


class Lexer:

    def __init__(self, source):
        self.src = source
        self.pos = 0
        self.length = len(source)

    def peek(self, offset=0):
        p = self.pos + offset
        if p >= self.length:
            return '\0'
        return self.src[p]

    def advance(self):
        ch = self.peek()
        self.pos += 1
        return ch

    def eof(self):
        return self.pos >= self.length

    def lex(self):
        tokens = []

        while not self.eof():

            ch = self.peek()

            if ch.isspace():
                tokens.append(
                    Token("text", self.advance())
                )
                continue

            if ch == '/' and self.peek(1) == '/':
                tokens.append(self.lex_line_comment())
                continue

            if ch == '/' and self.peek(1) == '*':
                tokens.append(self.lex_block_comment())
                continue

            if ch == '"':
                tokens.append(self.lex_string())
                continue

            if ch == '#':
                tokens.append(self.lex_preprocessor())
                continue

            if ch.isdigit():
                tokens.append(self.lex_number())
                continue

            if ch.isalpha() or ch == '_':
                tokens.append(self.lex_identifier())
                continue

            if ch in "{}[]();,.:":
                tokens.append(Token("punctuation", self.advance()))
                continue

            if ch in "+-*/=%<>!&|^~":
                tokens.append(self.lex_operator())
                continue

            tokens.append(Token("text", self.advance()))

        self.mark_functions(tokens)

        return tokens

    def lex_line_comment(self):
        text = ""

        while not self.eof() and self.peek() != '\n':
            text += self.advance()

        return Token("comment", text)

    def lex_block_comment(self):
        text = ""

        while not self.eof():
            text += self.advance()

            if text.endswith("*/"):
                break

        return Token("comment", text)

    def lex_string(self):
        text = self.advance()

        while not self.eof():
            c = self.advance()
            text += c

            if c == '"' and text[-2] != '\\':
                break

        return Token("string", text)

    def lex_number(self):
        text = ""

        while self.peek().isalnum() or self.peek() in ".xX":
            text += self.advance()

        return Token("number", text)

    def lex_preprocessor(self):
        text = ""

        while not self.eof() and self.peek() != '\n':
            text += self.advance()

        return Token("preprocessor", text)

    def lex_operator(self):
        text = self.advance()

        while self.peek() in "=<>|&":
            text += self.advance()

        return Token("operator", text)

    def lex_identifier(self):

        text = ""

        while self.peek().isalnum() or self.peek() == '_':
            text += self.advance()

        if text in KEYWORDS:
            return Token("keyword", text)

        if text in BUILTIN_TYPES:
            return Token("type", text)

        return Token("identifier", text)

    def mark_functions(self, tokens):

        for i in range(len(tokens)-1):

            a = tokens[i]
            b = tokens[i+1]

            if a.kind == "identifier":

                j = i + 1

                while j < len(tokens) and tokens[j].kind == "text":
                    j += 1

                if j < len(tokens):
                    if tokens[j].text == "(":
                        a.kind = "function"
