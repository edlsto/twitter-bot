def get_first_sentence(string):
    m = re.search('^.*?[\.!;](?:\s|$)(?<=[^ ]{4,4}[\.!;]\s)', string + ' ')
    if m is not None:
        result = m.group(0).strip()
        return result
    else:
        return ""

def get_sentences(string, max_length):
    last_character = list(string)[-1]
    if last_character not in (';', '.', '!'):
      string = string + '.';
      
    result = ""
    char_count = 0

    while char_count <= max_length:
        string = string.strip()
        sentence = get_first_sentence(string)
        sentence_length = len(sentence)

        if char_count + sentence_length <= max_length and len(string) > 0:
            result += sentence + ' '
            char_count += sentence_length
            string = string.replace(sentence, '', 1)
        else:
            break

    result = result.strip()

    result = s = list(result)
    if s[-1] == ';':
        s[-1] = '.'
    return "".join(s)

def extract_date(input_string):
    if input_string is None:
        return ''
    # Split the input string at the first semicolon
    parts = input_string.split(';', 1)
    
    # If there is a semicolon, return the part before it
    if len(parts) > 1:
        return f"({parts[0]})"
    else:
        # If there is no semicolon, return the original string
        return f"({input_string})"
