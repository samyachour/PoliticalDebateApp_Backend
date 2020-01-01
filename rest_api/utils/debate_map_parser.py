from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_api.models import *
from rest_api.serializers import *
from .constants import *
from django.utils import timezone
from string import punctuation
from github import Github
import os
from urlpro.request import urlopen
import sys
from pprint import pprint

# Run in shell:
# from rest_api.utils.debate_map_parser import parse_debate_file; parse_debate_file(); exit();
# from rest_api.utils.debate_map_parser import update_debate_input; update_debate_input(); exit();
# from rest_api.utils.debate_map_parser import update_or_create_point_input; update_or_create_point_input(); exit();
# from rest_api.utils.debate_map_parser import parse_debate_file; delete_existing_debate("title"); exit();

# Constants

key_key = "key"
root_key = "root"
object_key = "object"
pro_value = "pro"
con_value = "con"
context_value = "context"
yes_value = "y"
no_value = "n"
special_format_characters = ["*"]

# Helpers:

def handle_parse_error(message="Parsing error.", line="", dictionary={}):
    print(message)
    if line:
        print(line)
    if dictionary:
        pprint(dictionary)
    sys.exit()

def check_for_key(key, source_string):
    key_length = len(key)
    formatted_key = key.replace("_", " ")
    return source_string.lower()[:key_length] == formatted_key.lower()

def get_value_for_key(key, source_string):
    key_length = len(key)
    value_string = source_string[key_length:]
    return value_string.replace(":","",1).lstrip().rstrip()

def basic_debate_info_complete(debate_info_dict):
    return title_key in debate_info_dict and short_title_key in debate_info_dict and tags_key in debate_info_dict

def basic_point_info_complete(point_info_dict):
    if side_key not in point_info_dict:
        return False
    if point_info_dict[side_key] == context_value:
        if not point_info_dict[root_key]:
            handle_parse_error("Context points must be root points.", point_info_dict)
        return key_key in point_info_dict and description_key in point_info_dict
    else:
        return key_key in point_info_dict and description_key in point_info_dict and short_description_key in point_info_dict

def get_formatted_rebuttals(rebuttals):
    formatted_rebuttals = []
    if rebuttals:
        rebuttals = rebuttals.split(", ")
        for rebuttal_pk in rebuttals:
            try:
                formatted_rebuttals.append(int(rebuttal_pk))
            except ValueError:
                handle_parse_error("Invalid formatting around rebuttal key: ", rebuttal_pk)
        return formatted_rebuttals
    else:
        handle_parse_error("Parsing empty rebuttals")

def parse_hyperlinks(description):
    cleaned_description = description
    hyperlinks = []
    substring = ""
    is_parsing_substring = False
    hyperlink = ""
    is_parsing_hyperlink = False
    current_hyperlink = {}
    for char in description:
        if char == ']':
            if is_parsing_substring:
                is_parsing_substring = False
            else:
                handle_parse_error("Cannot have closed bracket ] without matching open bracket.", description)
            current_hyperlink[substring_key] = substring
            if any(char in substring for char in special_format_characters):
                handle_parse_error("Cannot have special formatting characters inside hyperlink string.", description)
            substring = ""
        if is_parsing_substring:
            substring += char
        if char == '[':
            if is_parsing_substring:
                handle_parse_error("Cannot have open bracket [ after another open bracket.", description)
            else:
                is_parsing_substring = True

        if char == ')' and is_parsing_hyperlink:
            is_parsing_hyperlink = False
            current_hyperlink[url_key] = hyperlink
            hyperlinks.append(current_hyperlink)
            cleaned_description = cleaned_description.replace("[" + current_hyperlink[substring_key] + "]" + "(" + current_hyperlink[url_key] + ")", current_hyperlink[substring_key])
            hyperlink = ""
            current_hyperlink = {}
        if is_parsing_hyperlink:
            hyperlink += char
        if char == '(' and substring_key in current_hyperlink:
            if is_parsing_hyperlink:
                handle_parse_error("Cannot have open parentheses ( after another open parentheses.", description)
            else:
                is_parsing_hyperlink = True

    return cleaned_description, hyperlinks

def get_debate_map_lines(local):
    if local:
        with open("/Users/samy/Documents/PoliticalDebateApp/PoliticalDebateApp_DebateMaps/Upload.txt") as debate_map:
            return debate_map.readlines()
    else:
        github_auth = Github(os.environ['GITHUB_ACCESS_TOKEN'])
        for repo in github_auth.get_user().get_repos():
            if repo.name == "PoliticalDebateApp_DebateMaps":
                debate_maps_repo = repo
        debate_map_file = debate_maps_repo.get_contents("Upload.txt")

        with urlopen(debate_map_file.download_url) as debate_map:
            return [line.decode('utf-8') for line in debate_map.readlines()]

def check_side_is_valid(side):
    if side.lower() not in [pro_value, con_value, context_value]:
        handle_parse_error("Invalid side: ", side)

def create_hyperlink_objects(point, hyperlinks):
    for hyperlink in hyperlinks:
        PointHyperlink.objects.create(point=point, substring=hyperlink[substring_key], url=hyperlink[url_key])

def add_hyperlinks(point_info_dict, hyperlinks):
    if hyperlinks_key in point_info_dict:
        point_info_dict[hyperlinks_key] = hyperlinks + point_info_dict[hyperlinks_key]
    else:
        point_info_dict[hyperlinks_key] = hyperlinks
    return point_info_dict

def get_boolean_input(message, boolean=True, default=False):
    if not boolean:
        return default
    user_input = str(input(message + "({0}/{1}) ".format(yes_value, no_value))).lower()
    if user_input == yes_value:
        return True
    elif user_input == no_value or not user_input:
        return False
    else:
        handle_parse_error("Input must be {0} or {1}".format(yes_value, no_value))

def get_string_input(message, boolean=True, default=""):
    return str(input(message)) if boolean else default

# Updates

def delete_existing_debate(title):
    try:
        Debate.objects.get(title=title).delete()
    except Debate.DoesNotExist:
        handle_parse_error("No existing debate with the title: ", title)
    for point in Point.objects.all().filter(debate=None):
        # If child point doesn't exist in any rebuttals
        if not point.point_set.exists():
            point.delete()

def check_if_debate_exists(title):
    try:
        Debate.objects.get(title=title)
        # We found a debate w/ that title
        handle_parse_error("Debate exists with the title: ", title)
    except:
        return

def update_debate_input():
    old_title = get_string_input("Current debate title: ")
    new_title = get_string_input("New debate title: ")
    new_short_title = get_string_input("New debate short title: ")
    new_tags = get_string_input("New debate tags: ")
    should_update_date = get_boolean_input("Update debate date to today: ")
    update_debate(old_title, new_title, new_short_title, new_tags, should_update_date)

def update_debate(old_title, new_title="", new_short_title="", new_tags="", should_update_date=False):
    if not old_title or not (new_title or new_short_title or new_tags or should_update_date):
        handle_parse_error("Missing old title or new debate info")
    try:
        debate = Debate.objects.get(title=old_title)
    except Debate.DoesNotExist:
        handle_parse_error("No existing debate with the title: ", old_title)

    if new_title:
        debate.title = new_title
    if new_short_title:
        debate.short_title = new_short_title
    if new_tags:
        debate.tags = new_tags.lower()
    if should_update_date:
        debate.last_updated = timezone.now()
    debate.save()
    print("Debate updated!")

def update_or_create_point_input():
    create = get_boolean_input("Create new point: ")
    root = get_boolean_input("Is it a root point: ", create, False)
    debate_title = get_string_input("For what debate title: ", create, "")
    parent_point_short_description = get_string_input("Parent point short description: ", create and not root, "")
    parent_point_description = get_string_input("Parent point description: ", create and not root, "")
    old_short_description = get_string_input("Old short point description: ", not create, "")
    old_description = get_string_input("Old point description: ", not create, "")
    update_old_point = get_boolean_input("Update old point directly: ", not create, "")
    new_short_description = get_string_input("Short point description: ")
    new_description = get_string_input("Point description: ")
    new_side = get_string_input("Point side: ")

    new_rebuttals = []
    while get_boolean_input("Add rebuttal: "):
        rebuttal_short_description = get_string_input("Rebuttal short description: ")
        rebuttal_description = get_string_input("Rebuttal description: ")
        new_rebuttals.append((rebuttal_short_description, rebuttal_description))

    update_or_create_point(create=create, update_old_point=update_old_point, root=root, debate_title=debate_title, parent_point=(parent_point_short_description, parent_point_description), old_short_description=old_short_description, old_description=old_description, new_short_description=new_short_description, new_description=new_description, new_side=new_side, new_rebuttals=new_rebuttals)

def update_or_create_point(create=False, update_old_point=False, root=False, debate_title="", parent_point = (), old_short_description="", old_description="", new_short_description="", new_description="", new_side="", new_rebuttals=[]):
    if create:
        if update_old_point:
            handle_parse_error("Cannot update old point and create a new one")
        if not (new_side or (new_side != context_value and new_short_description) or new_description or new_side or debate_title):
            handle_parse_error("Did not provide a short description, description, side, or parent point/debate for your new point")
    if not create:
        if not old_short_description or not old_description or not (new_short_description or new_description or new_side or new_rebuttals):
            handle_parse_error("Did not provide the old short description and description or any new attributes for your updated point")
        if old_short_description == new_short_description and old_description == new_description:
            handle_parse_error("Must change some aspect of the description or short description")

    if not create:
        cleaned_old_short_description, _ = parse_hyperlinks(old_short_description)
        cleaned_old_description, _ = parse_hyperlinks(old_description)
        try:
            old_point = Point.objects.get(short_description=cleaned_old_short_description, description=cleaned_old_description)
            short_description = old_point.short_description
            description = old_point.description
            side = old_point.side
        except Point.DoesNotExist:
            handle_parse_error("No existing point with the description: ", cleaned_old_description)

    new_short_description_hyperlinks = []
    if new_short_description:
        short_description, new_short_description_hyperlinks = parse_hyperlinks(new_short_description)
    new_description_hyperlinks = []
    if new_description:
        description, new_description_hyperlinks = parse_hyperlinks(new_description)
    if new_side:
        check_side_is_valid(new_side)
        side = new_side.lower()

    debate = None
    if create:
        try:
            parent_debate = Debate.objects.get(title=debate_title)
            parent_debate.save()
            if root:
                debate = parent_debate
        except Debate.DoesNotExist:
            handle_parse_error("No existing debate with the title: ", debate_title)
    else:
        debate = old_point.debate

    if update_old_point:
        new_point = old_point
        new_point.description = description
        new_point.short_description = short_description
        new_point.side = side
        new_point.save()
    elif debate:
        if side == context_value:
            new_point = Point.objects.create(debate=debate, description=description, side=side)
        else:
            new_point = Point.objects.create(debate=debate, description=description, short_description=short_description, side=side)
    else:
        new_point = Point.objects.create(description=description, short_description=short_description, side=side)

    if new_rebuttals:
        # Connect new rebuttals
        for new_rebuttal in new_rebuttals:
            cleaned_rebuttal_short_description, _ = parse_hyperlinks(new_rebuttal[0])
            cleaned_rebuttal_description, _ = parse_hyperlinks(new_rebuttal[1])
            try:
                new_rebuttal = Point.objects.get(short_description=cleaned_rebuttal_short_description, description=cleaned_rebuttal_description)
                new_point.rebuttals.add(new_rebuttal)
            except Point.DoesNotExist:
                handle_parse_error("No existing rebuttal point with the description: ", cleaned_rebuttal_description)
        new_point.save()

    create_hyperlink_objects(new_point, new_short_description_hyperlinks + new_description_hyperlinks)

    if create and not root:
        cleaned_parent_short_description, _ = parse_hyperlinks(parent_point[0])
        cleaned_parent_description, _ = parse_hyperlinks(parent_point[1])
        try:
            parent_point = Point.objects.get(short_description=cleaned_parent_short_description, description=cleaned_parent_description)
            parent_point.rebuttals.add(new_point)
        except Point.DoesNotExist:
            handle_parse_error("No existing point with the description: ", cleaned_parent_description)
    elif not create and not update_old_point:
        for old_parent_point in Point.objects.filter(rebuttals=old_point):
            old_parent_point.rebuttals.add(new_point)
            old_parent_point.save()

        for old_point_hyperlink in PointHyperlink.objects.filter(point=old_point):
            old_point_hyperlink.point = new_point
            old_point_hyperlink.save()

        old_point.delete()

    if create:
        print("Point created!")
    else:
        print("Point updated!")

# Parser

def parse_debate_file(local=False, delete_existing=False):

    # Properties

    debate_info_dict = {}
    point_count = 0

    point_info_dict = {}
    all_points_dict = {}
    is_parsing_points = False

    # Parsing

    for line in get_debate_map_lines(local):
        if line in ['\n', '\r\n']: # empty line
            continue
        # Trim all leading non-alphanumeric characters
        line = line.lstrip().lstrip(punctuation).lstrip()

        if not is_parsing_points: # basic info section
            if check_for_key(title_key, line):
                title = get_value_for_key(title_key, line)
                if delete_existing:
                    delete_existing_debate(title)
                else:
                    check_if_debate_exists(title)
                debate_info_dict[title_key] = title
            elif check_for_key(short_title_key, line):
                debate_info_dict[short_title_key] = get_value_for_key(short_title_key, line)
            elif check_for_key(tags_key, line):
                debate_info_dict[tags_key] = get_value_for_key(tags_key, line)
            elif check_for_key("Points", line):
                is_parsing_points = True
                continue

            if basic_debate_info_complete(debate_info_dict):
                new_debate = Debate.objects.create(title=debate_info_dict[title_key], short_title=debate_info_dict[short_title_key], tags=debate_info_dict[tags_key])

        if is_parsing_points: # points section
            if check_for_key(root_key, line):
                point_info_dict[root_key] = True
            elif check_for_key(key_key, line):
                if key_key in point_info_dict:
                    handle_parse_error("The following point does not have all the required fields:", point_info_dict)
                point_info_dict[key_key] = int(get_value_for_key(key_key, line))
            elif check_for_key(description_key, line):
                description = get_value_for_key(description_key, line)
                description, hyperlinks = parse_hyperlinks(description)
                point_info_dict = add_hyperlinks(point_info_dict, hyperlinks)
                point_info_dict[description_key] = description
            elif check_for_key(short_description_key, line):
                short_description = get_value_for_key(short_description_key, line)
                short_description, hyperlinks = parse_hyperlinks(short_description)
                point_info_dict = add_hyperlinks(point_info_dict, hyperlinks)
                point_info_dict[short_description_key] = short_description
            elif check_for_key(side_key, line):
                side = get_value_for_key(side_key, line)
                check_side_is_valid(side)
                point_info_dict[side_key] = side.lower()
            elif check_for_key(rebuttals_key, line):
                rebuttals = get_value_for_key(rebuttals_key, line)
                if key_key not in point_info_dict:
                    handle_parse_error("Rebuttals must always be before the side key:", rebuttals)
                point_info_dict[rebuttals_key] = get_formatted_rebuttals(rebuttals)

            if basic_point_info_complete(point_info_dict):
                if not check_for_key(side_key, line):
                    handle_parse_error("The side must always come last.", point_info_dict)
                if point_info_dict[root_key]:
                    if point_info_dict[side_key] == context_value:
                        new_point = Point.objects.create(debate=new_debate, description=point_info_dict[description_key], side=point_info_dict[side_key])
                    else:
                        new_point = Point.objects.create(debate=new_debate, description=point_info_dict[description_key], short_description=point_info_dict[short_description_key], side=point_info_dict[side_key])
                else:
                    new_point = Point.objects.create(description=point_info_dict[description_key], short_description=point_info_dict[short_description_key], side=point_info_dict[side_key])

                create_hyperlink_objects(new_point, point_info_dict[hyperlinks_key])

                point_info_dict[object_key] = new_point
                all_points_dict[point_info_dict[key_key]] = point_info_dict
                point_count += 1
                point_info_dict = { root_key: False, object_key: new_point }

    # Link rebuttals
    for _, point in all_points_dict.items():
        point_object = point[object_key]
        if rebuttals_key in point:
            for rebuttal_pk in point[rebuttals_key]:
                rebuttal = all_points_dict[rebuttal_pk][object_key]
                point_object.rebuttals.add(rebuttal)
            point_object.save()

    # Check for infinite recursion
    try:
        DebateSerializer(new_debate).data
    except Exception as e:
        handle_parse_error("Could not serialize debate.", e)

    print("Debate created!")
