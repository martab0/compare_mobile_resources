import xml.etree.ElementTree as ET
import os

# SCENARIO
# Android resources are in XML file, iOS resources are in XLIFF file. 
# The Android and iOS files differ by list of strings, by sorting, and string keys.
# English strings can be identical between Android and iOS files.
# We need to check if translations are also identical for the strings that are identical in English.
# The code is written with ChatGPT 4.0 in 8 prompts.

# DEFINITIONS
# Please update definitions to your use case:

SUPPORTED_LANGUAGES = ["de", "es", "fr", "it-IT", "ja-JP", "ko-KR", "pt-BR", "ru-RU", "zh-CN", "zh-TW"]  # Languages list
# Translated file names are created by appending _ and language code to source file name

ENGLISH_ANDROID_PATH = "Android/strings V2.xml" # Android source path and file
# Put Android translated files in the same folder as Android source file
ENGLISH_IOS_PATH = "iOS/en V1.xliff" # iOS source path and file
# Put iOS translated files in the same folder as iOS source file

IGNORED_CHARACTERS = ["\\"]  # Characters to ignore because they are only added in one type of file
# For example: In Android files, apostrophe ' is escaped - in iOS files it is not. 
# Italian translations are identical in this case, so we don't want a false positive.
# English: A temporary error has occurred.
# Android: Une erreur temporaire s\'est produite.
# iOS: Une erreur temporaire s'est produite.

# END OF DEFINITIONS

def parse_android(xml_path):
    """Parse Android XML."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    strings = {}

    for child in root:
        if child.tag == "string" and child.attrib.get("translatable", "true") != "false":
            strings[child.attrib["name"]] = child.text

    return strings


def parse_ios_xliff(xliff_path):
    """Parse iOS XLIFF."""
    tree = ET.parse(xliff_path)
    root = tree.getroot()

    ns = {'xliff': 'urn:oasis:names:tc:xliff:document:1.2'}
    strings = {}

    for file in root.findall('xliff:file', ns):
        for body in file.findall('xliff:body', ns):
            for trans_unit in body.findall('xliff:trans-unit', ns):
                source = trans_unit.find('xliff:source', ns).text
                target = trans_unit.find('xliff:target', ns).text
                strings[source] = target

    return strings


def create_english_lookup(strings):
    """Given a dictionary of strings, create a reverse lookup based on the English value."""
    return {v: k for k, v in strings.items()}


def find_common_english_strings(android_lookup, ios_lookup):
    """Find English strings that are common between Android and iOS."""
    return set(android_lookup.keys()) & set(ios_lookup.keys())


def get_strings(file_path, parser):
    """Parse the file and return strings."""
    return parser(file_path)


def main_comparison(english_android_path, english_ios_path, translated_android_path, translated_ios_path):
    """Parse English and translated files."""
    english_android_strings = get_strings(english_android_path, parse_android)
    english_ios_strings = get_strings(english_ios_path, parse_ios_xliff)
    
    translated_android_strings = get_strings(translated_android_path, parse_android)
    translated_ios_strings = get_strings(translated_ios_path, parse_ios_xliff)

    # Create lookups for English strings
    android_english_lookup = create_english_lookup(english_android_strings)
    ios_english_lookup = create_english_lookup(english_ios_strings)

    # Identify common English strings
    common_english = find_common_english_strings(android_english_lookup, ios_english_lookup)

    # Find discrepancies between translated strings for common English strings
    discrepancies = []
    for eng in common_english:
        android_key = android_english_lookup[eng]
        ios_key = ios_english_lookup[eng]
        
        # Read translated strings from Android and iOS for a common English string
        android_translated_value_raw = translated_android_strings.get(android_key)
        ios_translated_value_raw = translated_ios_strings.get(ios_key)
        
        # Clean the translations from characters that cause false positives
        android_translated_value = clean_string(android_translated_value_raw, IGNORED_CHARACTERS) if android_translated_value_raw else None
        ios_translated_value = clean_string(ios_translated_value_raw, IGNORED_CHARACTERS) if ios_translated_value_raw else None

        # If Android and iOS translations are not empty, then check if they are identical
        if android_translated_value and ios_translated_value and android_translated_value != ios_translated_value:
            discrepancies.append((eng, android_translated_value_raw, ios_translated_value_raw))

    for eng, android_value, ios_value in discrepancies:
        print(f'English: {eng}')
        print(f'Android: {android_value}')
        print(f'iOS: {ios_value}')
        print('---')


def construct_translated_file_path(base_path, language_code):
    """Construct the file path for translated files based on language code."""
    file_name, file_extension = os.path.splitext(base_path)
    return f"{file_name}_{language_code}{file_extension}"

def clean_string(s, ignored_chars):
    """Remove ignored characters from the string."""
    for char in ignored_chars:
        s = s.replace(char, '')
    return s


if __name__ == "__main__":
    for language in SUPPORTED_LANGUAGES:
        print(f"Comparing translations for {language}...")

        translated_android_path = construct_translated_file_path(ENGLISH_ANDROID_PATH, language)
        translated_ios_path = construct_translated_file_path(ENGLISH_IOS_PATH, language)
        
        main_comparison(ENGLISH_ANDROID_PATH, ENGLISH_IOS_PATH, translated_android_path, translated_ios_path)
        print("---" * 15)  # Separator between languages for better clarity

