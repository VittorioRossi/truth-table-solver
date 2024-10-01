from pprint import pprint
class Token:
    def __init__(self, type, value, line=None, column=None):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f'Token({self.type}, {self.value}, {self.line}, {self.column})'
    

class Tokenizer:
    def __init__(self):
        self.keywords = {'var', 'show', 'show_ones', 'not', 'and', 'or', 'True', 'False'}
        self.special_chars = {'(', ')', '=', ';'}

    def tokenize(self, text):
        tokens = []
        lines = text.strip().split('\n')
        for line_num, line in enumerate(lines, 1):
            i = 0  # Index of the current character
            while i < len(line):
                char = line[i]
                
                # Skip whitespace
                if char.isspace():
                    i += 1
                    continue
                
                # Handle comments
                if char == '#':
                    break  # Skip the rest of the line
                
                # Handle special characters
                if char in self.special_chars:
                    tokens.append(Token('SPECIAL', char, line_num, i + 1))
                    i += 1
                    continue
                
                # Handle vars, identifiers and keywords
                if char.isalpha() or char == '_':
                    start = i
                    while i < len(line) and (line[i].isalnum() or line[i] == '_'):
                        i += 1
                    word = line[start:i]
                    if word in self.keywords:
                        tokens.append(Token('KEYWORD', word, line_num, start + 1))
                    else:
                        tokens.append(Token('IDENTIFIER', word, line_num, start + 1))
                    continue
                
                # Handle unexpected characters
                raise ValueError(f"Unexpected character: {char} at line {line_num}, character {i + 1}")

        # Check for the final semicolon
        if len(tokens) == 0 or tokens[-1].value != ';':
            raise ValueError("Expected ';' at the end of the line")

        return tokens

if __name__=="__main__":
    #text_1 = "var x; var y; var z; show x; show_ones y; x = not y; y = x and z; z = x or y;"
    #text_2 = "var x y z; show x; show_ones y; x = not y; y = x and z; z = x or y"
    tokenizer = Tokenizer()
    #tokens = tokenizer.tokenize(text_1)
    #pprint(tokens)
    #tokens = tokenizer.tokenize(text_2)
    #pprint(tokens)

    text = """var Z_g cTY S_T;
    vYA = (not cTY) or (not ((cTY or Z_g or Z_g or S_T) or Z_g or S_T or cTY)) or 
    S_T or (Z_g or cTY);
    Rgw = cTY and ((not Z_g) or (not (not S_T)) or (not vYA)) and S_T and (Z_g and 
    S_T);
    Cjq = (((not S_T) and vYA and (Rgw or cTY or Z_g) and (Rgw or cTY)) and vYA) or 
    cTY or S_T;
    iPm = (not True) or ((Cjq and Z_g) and cTY and (S_T and (not Rgw)));
    show iPm Cjq Rgw;
    var HId sJl WxR;
    wdE = (not ((S_T and vYA) or Rgw or sJl or (HId or S_T))) and (not ((S_T and 
    Rgw and sJl) and vYA and (S_T or sJl or vYA or S_T) and Z_g));
    ERH = (not (not wdE)) and iPm;
    Tlb = ((iPm or cTY or cTY) or sJl or WxR or WxR) or wdE or vYA or (S_T or ((not 
    Rgw) and HId and WxR and (not wdE)));
    FGk = Rgw and (((Cjq and WxR and vYA) and (not Z_g) and S_T) and cTY and sJl 
    and (WxR and (not WxR) and (not S_T)));
    show Tlb FGk;
    """

    tokens = tokenizer.tokenize(text)
    pprint(tokens)

