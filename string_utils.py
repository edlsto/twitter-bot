import re
import logging

logging.basicConfig(level=logging.INFO)

def get_first_sentence(string):
    m = re.search('^.*?[\.!;](?:\s|$)(?<=[^ ]{4,4}[\.!;]\s)', string + ' ')
    if m is not None:
        result = m.group(0).strip()
        return result
    else:
        return ""

def get_sentences(string, max_length):
    logging.info("Tweet too long... truncating tweet")
    result = ""
    char_count = 0
    first_sentence = True

    while char_count < max_length and string:
        string = string.strip()
        sentence = get_first_sentence(string)
        sentence_length = len(sentence)

        # If no sentence is found, exit the loop
        if not sentence:
            break

        # If the first sentence exceeds max_length, truncate it
        if first_sentence and sentence_length > max_length:
            result += sentence[:max_length].strip()  # Truncate and strip extra space
            char_count = max_length  # Exit after reaching max length
            break

        # If the sentence fits within max_length, add it to result
        if char_count + sentence_length <= max_length:
            if not first_sentence:
                result += ' '  # Add a space before subsequent sentences
            result += sentence
            char_count += sentence_length + (1 if not first_sentence else 0)  # Include space in count for subsequent sentences
            string = string.replace(sentence, '', 1)
        else:
            break

        first_sentence = False  # Only allow truncation for the first sentence

    logging.info(f"Truncated tweet: {result}")

    return result

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
