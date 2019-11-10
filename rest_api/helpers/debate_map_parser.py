from django.contrib.auth.models import User
from rest_api.models import *
from .constants import *
from datetime import datetime, timedelta
from string import punctuation
from github import Github
import os
from urllib.request import urlopen
import sys
from pprint import pprint

# Run in shell:
# from rest_api.helpers.debate_map_parser import parse_debate_file; parse_debate_file(); exit();

# Constants

key_key = "key"
root_key = "root"
object_key = "object"
pro_value = "pro"
con_value = "con"
context_value = "context"
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
    return title_key in debate_info_dict and short_title_key in debate_info_dict and tags_key in debate_info_dict and last_updated_key in debate_info_dict and total_points_key in debate_info_dict

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
                handle_parse_error("Cannot have closed bracket ] without matching open bracket.")
            current_hyperlink[substring_key] = substring
            if any(char in substring for char in special_format_characters):
                handle_parse_error("Cannot have special formatting characters inside hyperlink string:", substring)
            substring = ""
        if is_parsing_substring:
            substring += char
        if char == '[':
            if is_parsing_substring:
                handle_parse_error("Cannot have open bracket [ after another open bracket.")
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
                handle_parse_error("Cannot have open parentheses ( after another open parentheses.")
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

# Updates

def delete_existing_debate(title):
    try:
        Debate.objects.get(title=title).delete()
    except Debate.DoesNotExist:
        handle_parse_error("No existing debate with that title.")

def update_debate(old_title, new_title="", new_short_title="", new_tags="", should_update_date=False):
    try:
        debate = Debate.objects.get(title=old_title)
    except Debate.DoesNotExist:
        handle_parse_error("No existing debate with that title.")

    if new_title:
        debate.title = new_title
    if new_short_title:
        debate.short_title = new_short_title
    if new_tags:
        debate.tags = new_tags
    if should_update_date:
        debate.last_updated = datetime.today()
    debate.save()
    print("Debate updated!")

def update_or_create_point(create=False, root=False, debate_title="", parent_point = (), old_short_description="", old_description="", new_short_description="", new_description="", new_side="", new_rebuttals=[]):
    if create and not (new_short_description or new_description or new_side or (debate_title or parent_point)):
        handle_parse_error("Did not provide a short description, description, side, or parent point/debate for your new point")
    if not create and (not old_short_description or not old_description):
        handle_parse_error("Did not provide the old short description and description for your updated point")

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
    if new_side and check_side_is_valid(new_side):
        side = new_side

    debate = None
    if create and root:
        if not debate_title:
            handle_parse_error("Did not provide a debate title")
        try:
            debate = Debate.objects.get(title=debate_title)
        except Debate.DoesNotExist:
            handle_parse_error("No existing debate with the title: ", debate_title)
    else:
        debate = old_point.debate

    if debate:
        if new_side == context_value:
            new_point = Point.objects.create(debate=debate, description=description, side=new_side)
        else:
            new_point = Point.objects.create(debate=debate, description=description, short_description=short_description, side=new_side)
    else:
        new_point = Point.objects.create(description=description, short_description=short_description, side=new_side)

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

    if create:
        try:
            cleaned_parent_short_description, _ = parse_hyperlinks(parent_point[0])
            cleaned_parent_description, _ = parse_hyperlinks(parent_point[1])
            parent_point = Point.objects.get(short_description=cleaned_parent_short_description, description=cleaned_parent_description)
            parent_point.rebuttals.add(new_point)
        except Point.DoesNotExist:
            handle_parse_error("No existing point with the description: ", cleaned_rebuttal_description)
    else:
        # Replace with new point in other manytomany fields
        old_parent_points = Points.filter(rebuttals=old_point)
        for old_parent_point in Points.filter(rebuttals=old_point):
            old_parent_point.rebuttals.add(new_point)
            old_parent_point.save()

    if not create:
        old_point.delete()

# Parser

def parse_debate_file(local=False, delete_existing=False):

    # Properties

    debate_info_dict = {}
    point_count = 0
    debate_info_dict[last_updated_key] = datetime.today()
    debate_info_dict[total_points_key] = point_count

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
                debate_info_dict[title_key] = title
            elif check_for_key(short_title_key, line):
                debate_info_dict[short_title_key] = get_value_for_key(short_title_key, line)
            elif check_for_key(tags_key, line):
                debate_info_dict[tags_key] = get_value_for_key(tags_key, line)
            elif check_for_key("Points", line):
                is_parsing_points = True
                continue

            if basic_debate_info_complete(debate_info_dict):
                new_debate = Debate.objects.create(title=debate_info_dict[title_key], short_title=debate_info_dict[short_title_key], tags=debate_info_dict[tags_key], last_updated=debate_info_dict[last_updated_key], total_points=debate_info_dict[total_points_key])

        if is_parsing_points: # points section
            if check_for_key(root_key, line):
                point_info_dict[root_key] = True
            elif check_for_key(key_key, line):
                if key_key in point_info_dict:
                    handle_parse_error("The following point does not have all the required fields:", point_info_dict)
                point_info_dict[key_key] = int(get_value_for_key(key_key, line))
            elif check_for_key(description_key, line):
                description = get_value_for_key(description_key, line)
                description, point_info_dict[hyperlinks_key] = parse_hyperlinks(description)
                point_info_dict[description_key] = description
            elif check_for_key(short_description_key, line):
                point_info_dict[short_description_key] = get_value_for_key(short_description_key, line)
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
                        new_point = Point.objects.create(debate=new_debate, description=point_info_dict[description_key], short_description=point_info_dict[short_description_key],  side=point_info_dict[side_key])
                else:
                    new_point = Point.objects.create(description=point_info_dict[description_key], short_description=point_info_dict[short_description_key],  side=point_info_dict[side_key])

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

    debate_info_dict[total_points_key] = point_count
    new_debate.total_points = point_count
    new_debate.save()
    print("Debate created!")
