# Libraries
import re

# TODO: eliminate 'helping' as in 'helping hand' from being counted in object occurrences. Also check verb properties for this
## Could do by checking if next work after helping is hand and eliminating if so

# TODO: intervening_words counter is counting 's as in "one's thoughts" as a seperate token and incrementing
## maybe have if loop in the verb sections saying if the found_object flag is on and next word is "'s", then decrement
## intervening words by 1?
## Alt maybe have an apostrophe 's counter and minus that value from intervening words at the end??

parsed_file = r"C:\Users\helen\Downloads\help_all_files_parsed.txt"

# Initialise results string (ONLY OBJ AND HELP PROPERTIES!!)
# HelpPosition = location of help word in whole KWIC file (not the hit counter!!) <-- just for my reference
results = "HelpPosition\tDepVar\tHelpClass\tHelpInflection\tVerbLemma\tInterveningWords\tObjPresent\tObjPronoun\tObjLength\tObjHead\n"

# ---------------------------------------------------------
# Getting variables in right context window
# ---------------------------------------------------------
# Check .txt file has been supplied
if not parsed_file.endswith(".txt"):
    print(f"The file {parsed_file} is not in the correct form")
else:
    with open(parsed_file, "r", encoding="utf8") as textfile:
        string = textfile.read()

        # Getting individual tokens
        tagged_words = string.split()

        # -------------------------------------------
        # Getting help positions
        # -------------------------------------------
        # Finding all instances of help in tagged KWICs
        help_pattern = r'\w+_help\w*_\d+_\w+_\d+_\w+_\w+'
        help_positions = []

        for i, word in enumerate(tagged_words):
            if re.search(help_pattern, word, re.IGNORECASE):
                help_positions.append(i)

        help_count = len(help_positions)  # Variable to count instances of help

        # -------------------------------------------
        # Star loop for right checks
        # -------------------------------------------
        # Going through each occurrence of help
        for pos in help_positions:
            # Getting help parts
            tagged_help_word = tagged_words[pos]  # Ex: VB_help_35_ROOT_35_help_noNE
            help_parts = tagged_help_word.split('_')
            help_tag = help_parts[0]  # Ex: VB, VBN
            help_word = help_parts[1]  # Ex: helping, helps
            help_index = help_parts[2]  # Ex: 11 (if 11th word in whole file)
            # Above tags are all we need???? <-----------------------------------------------------------------------

            # -------------------------------------------
            # Variables
            # -------------------------------------------
            help_class = "" # VERB, NOUN, ADJ, ADV, OTHER
            intervening_words = 0 # Intervening words between help and infinitive
            obj_present = ""  # Is there a dobj argument for 'help'?
            obj_pronoun = ""
            obj_length = ""
            obj_head = "TODO!!!"  # TODO
            words_to_review = 30  # how many words after "help" are we going to consider?
            verb_after_help = ""
            help_dv = ""

            # -------------------------------------------
            # Flags and counters
            # -------------------------------------------
            obj_length_counter = 0  # How long is the object?
            found_to = False
            found_bare = False
            found_ing = False
            found_in = False
            found_verb = False
            found_object = False

            # -------------------------------------------
            # Looping through 30 word after help
            # -------------------------------------------
            for i in range(1, words_to_review + 1):
                if pos + i >= len(tagged_words):
                    break

                next_tagged_word = tagged_words[pos + i] # PRP_them_550_dobj_549_they_noNE
                parts = next_tagged_word.split('_')
                next_tag = parts[0] # Ex: PRP, TO, IN, VB
                next_word = parts[1] # token text
                next_index = parts[2] # index within whole file
                next_depend = parts[3] # dependency relation (eg, dobj, aux, xcomp)
                next_head_index = parts[4] # index of next word's head
                next_lemma = parts[5] # lemma

                # -------------------------------------------------------------------
                # Break if encounter items likely to be irrelevant
                # -------------------------------------------------------------------
                # Break if the help_tag does not start with VB: expect VB, VBN, VBP, VBP, etc
                if not help_tag.startswith('VB'):
                    break
                # Break if hit terminating punctuation
                if next_tag in ['.', ',', '``', 'HYPH', ':', ")"]:
                    break
                # Break if get something like help sits
                if next_tag in ["VBP", "VBD", "VBZ"]:
                    break
                # Break if get something like helps that
                if next_tag.startswith('MD') or (next_word == 'that') or next_tag.startswith('WP'):
                    break
                # Break if encounter these words
                if next_word.lower() in ['and', 'or', 'are', 'if']:
                    break

                # -------------------------------------------------------------------
                # Object-related properties
                # -------------------------------------------------------------------
                # If haven't found a verb yet, potentially have an object
                if not found_verb:
                    # TODO: Need to add pronoun that: The event in the white building. She helps that run smoothly.
                    # TODO: Need to add pronoun this: She helps this run smoothly.
                    # If next word id a pronoun
                    if (next_tag == 'PRP' or
                            next_word.lower() in ['someone', 'anyone', 'who', 'myself', 'yourself',
                                                  'herself', 'himself', 'themself', 'themselves']):
                        obj_pronoun = "PRO"
                        found_object = True
                    # If not a pronoun, check other potential object types
                    else:
                        if next_tag in ['NN', 'NP', 'NNS', 'NNP', 'NNPS', 'DT', 'CD', 'WP','PRP$']:
                            found_object = True

                # if found an object
                if found_object:
                    # Don't want to increment if one of the items in list holds (ie, if hit the end of the obj clause)
                    if not (next_word.lower() in ['to'] or next_tag in ['RB', 'TO', 'POS'] or next_tag.startswith('VB')):
                        obj_length_counter += 1

                # -------------------------------------------------------------------
                # Finding verb in complement
                # -------------------------------------------------------------------
                # TODO: Use dependency to exclude verbs where end up at dobj where that dobj's dependency is help, or a word like 'who'
                ## maybe put the above in a function so can recur as follow dependency relations

                # Check for '"to": helps to supply
                if not found_bare and not found_in and not found_ing and next_tag == 'TO' or next_word.lower() == 'to':
                    # Look over next few words from position i
                    for j in range(1, 3):
                        # Only proceed if next few words won't exceed remaining words in text
                        if pos + i + j < len(tagged_words):
                            potential_verb = tagged_words[pos + i + j]
                            verb_parts = potential_verb.split('_')
                            verb_tag = verb_parts[0]
                            verb_word = verb_parts[1]
                            verb_lemma = verb_parts[5]
                            # Getting verb lemma of the complement verb (supplies --> supply)
                            if verb_tag in ['VB', 'HV', 'BE']:
                                found_to = True
                                verb_after_help = verb_lemma
                                found_verb = True
                                intervening_words = i + j - 2
                                break

                # Check for -ing form verbs: help doing
                # Exclude according: help according to
                elif not found_to and not found_in and not found_bare and next_tag in ['VBG',
                                                                                       'HVG','BEG'] and next_word not in [
                         "according"]:
                    found_ing = True
                    verb_after_help = next_lemma
                    found_verb = True
                    intervening_words = i - 1
                    break

                # Check for bare infinitive
                elif not found_to and not found_in and not found_ing and next_tag in ['VB', 'HV', 'BE']:
                    found_bare = True
                    verb_after_help = next_lemma
                    found_verb = True
                    intervening_words = i - 1
                    break

                # Break loop looking at words after help if verb found
                if found_verb:
                    break

            # -------------------------------------------------------------------
            # Recording variables
            # -------------------------------------------------------------------
            # Record variables once finished looking over items after help at position tagged_words[pos]

            # Recording dependent variable
            if found_to:
                help_dv = "TO"
            elif found_bare:
                help_dv = "BARE"
            elif found_in:
                help_dv = "INING"
            elif found_ing:
                help_dv = "ING"
            else:
                help_dv = "NA"

            # Recording object properties
            if found_verb:
                if found_object:
                    obj_present = "Yes" # dobj present
                    obj_length = obj_length_counter
                    # Obj NP if length is more than 1
                    if obj_length_counter > 1:
                        obj_pronoun = "NP"
                    # If obj length 1 and haven't yet recorded the obj_pronoun variable
                    elif obj_pronoun == "" and obj_length_counter == 1:
                        obj_pronoun = "PRO"
                # If have no object before the complement
                else:
                    obj_present = "No" # complement after help but no dobj
                    obj_pronoun = "NA"
                    obj_length = "NA"
                    obj_head = "NA"
            # no complement after help
            else:
                obj_present = "NA"
                obj_pronoun = "NA"
                obj_length = "NA"
                obj_head = "NA"

            # Recording the part of speech of help
            if help_tag.startswith('VB'):
                help_class = "VERB"
            elif help_tag.startswith('NN'):
                help_class = "NOUN"
            elif help_tag.startswith('JJ'):
                help_class = "ADJ"
            elif help_tag.startswith('RB'):
                help_class = "ADV"
            else:
                help_class = "OTHER"

            # Printing the KWIC for help occurrence at tagged_words[pos]
            # HelpPosition\tDepVar\tHelpClass\tHelpInflection\tVerbLemma\tInterveningWords\tObjPresent\tObjPronoun\tObjLength\tObjHead
            results += f"{pos}\t{help_dv}\t{help_class}\t{help_tag}\t{verb_after_help}\t{intervening_words}\t{obj_present}\t{obj_pronoun}\t{obj_length}\t{obj_head}\n"

#--------------------------------------------------------------------------------------
# END
#--------------------------------------------------------------------------------------
print(results)

# Write results to txt file
with open("results.txt", "w", encoding="utf-8") as f:
  f.write(results)







