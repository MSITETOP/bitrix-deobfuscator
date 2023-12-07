
import base64
import sys
import re

def read_input_file(file_path):
    """
    Read the content from the given file path.
    
    Args:
    file_path (str): The file path to read from.
    
    Returns:
    str: The content of the file.
    
    Raises:
    FileNotFoundError: If the file does not exist.
    """
    with open(file_path, 'r') as file:
        return file.read()


def write_output_file(file_path, content):
    """
    Write the content to the given file path.
    
    Args:
    file_path (str): The path to the file where the content should be written.
    content (str): The content to write to the file.
    """
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

        
def decode_base64(encoded_str):
    """
    Decode a base64 encoded string.
    
    Args:
    encoded_str (str): The base64 encoded string.
    
    Returns:
    str: The base64 decoded string.
    
    Raises:
    ValueError: If the base64 string cannot be decoded.
    """
    return base64.b64decode(encoded_str).decode('utf-8')


def extract_globals_object(php_code):
    """
    Extract the globals object from the PHP code.
    
    Args:
    php_code (str): The PHP code to extract from.
    
    Returns:
    str: The extracted globals object.
    """
    return re.findall(r"\$GLOBALS\['(.*?)'\]=", php_code)[0]


def decode_and_replace_globals(php_code, globals_object):
    """
    Decode and replace globally stored base64 encoded strings in the PHP code.
    
    Args:
    php_code (str): The PHP code to decode and replace in.
    globals_object (str): The globals object that refers to the encoded strings.
    
    Returns:
    str: The PHP code with decoded and replaced strings.
    """
    encoded_strings = php_code.split("base64_decode('")[1:] 
    for index, string in enumerate(encoded_strings):
        base64_str = string.split("')")[0]
        decoded_str = decode_base64(base64_str)
        php_code = php_code.replace(f"base64_decode('{base64_str}')", f"'{decoded_str}'")    
        php_code = php_code.replace(f"\$GLOBALS['{globals_object}'][{index}]", decoded_str)
    return php_code


def decode_and_replace_function(php_code, extracted_function_list, function_name):
    """
    Decode and replace base64 encoded function call indexes with literal values in the PHP code.
    
    Args:
    php_code (str): The PHP code to decode and replace in.
    extracted_function_list (list of str): List of base64 encoded strings representing function call indexes.
    function_name (str): The specific part of the function call to replace.
    
    Returns:
    str: The PHP code with decoded and replaced function call indexes.
    """
    for index, string in enumerate(extracted_function_list):  
        decoded_str = decode_base64(string)
        php_code = php_code.replace(f"___{function_name}({index})", f"'{decoded_str}'")
    return php_code


def deobfuscate_php(file_path):
    """
    Deobfuscate a PHP file by decoding encoded strings and replacing them in the code.
    
    Args:
    file_path (str): The path to the PHP file to deobfuscate.
    
    Returns:
    str: The path to the deobfuscated PHP file.
    """
    php_code = read_input_file(file_path)
    globals_object = extract_globals_object(php_code)
    php_code = decode_and_replace_globals(php_code, globals_object)
    extracted_function = re.findall(r"[0-9]+=array\((.+)\);return base64_decode", php_code)[0]
    extracted_function_list = extracted_function.split(",")
    function_name = re.findall(r'\\___(\d+)', php_code)[0]
    php_code = decode_and_replace_function(php_code, extracted_function_list, function_name)
    php_code = php_code.replace(";", ";\r").replace("',", "',\r")
    
    output_file_path = f"{file_path}.decode.php"
    write_output_file(output_file_path, php_code)
    
    return output_file_path

def main(file_path):
    try:
        output_file_path = deobfuscate_php(file_path)
        print(f"Deobfuscated file written to: {output_file_path}")
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
    except ValueError as e:
        print(f"Error during base64 decoding: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide file path as command-line argument.")
        sys.exit(1)
    main(sys.argv[1])
