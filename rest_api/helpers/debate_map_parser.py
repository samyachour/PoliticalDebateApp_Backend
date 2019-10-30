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

# Helpers

key_key = "key"
root_key = "root"
object_key = "object"
pro_value = "pro"
con_value = "con"
context_value = "context"
special_format_characters = ["*"]

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
    side = point_info_dict[side_key]

    if side == context_value:
        if not point_info_dict[root_key]:
            print("Context points must be root points.")
            pprint(point_info_dict)
            sys.exit()
        return key_key in point_info_dict and description_key in point_info_dict
    else:
        return key_key in point_info_dict and description_key in point_info_dict and short_description_key in point_info_dict

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
                print("Cannot have closed bracket ] without matching open bracket.")
                sys.exit()
            current_hyperlink[substring_key] = substring
            if any(char in substring for char in special_format_characters):
                print("Cannot have special formatting characters inside hyperlink string:")
                print(substring)
                sys.exit()
            substring = ""
        if is_parsing_substring:
            substring += char
        if char == '[':
            if is_parsing_substring:
                print("Cannot have open bracket [ after another open bracket.")
                sys.exit()
            else:
                is_parsing_substring = True

        if char == ')' and is_parsing_hyperlink:
            if is_parsing_hyperlink:
                is_parsing_hyperlink = False
            else:
                print("Cannot have closed parentheses ) without matching open parentheses.")
                sys.exit()
            current_hyperlink[url_key] = hyperlink
            hyperlinks.append(current_hyperlink)
            cleaned_description = cleaned_description.replace("[" + current_hyperlink[substring_key] + "]" + "(" + current_hyperlink[url_key] + ")", current_hyperlink[substring_key])
            hyperlink = ""
            current_hyperlink = {}
        if is_parsing_hyperlink:
            hyperlink += char
        if char == '(' and substring_key in current_hyperlink:
            if is_parsing_hyperlink:
                print("Cannot have open parentheses ( after another open parentheses.")
                sys.exit()
            else:
                is_parsing_hyperlink = True

    return cleaned_description, hyperlinks

# Parser

def parse_debate_file(title_to_delete = "", local = False):

    if title_to_delete != "":
        Debate.objects.get(title=title_to_delete).delete()

    # Properties

    debate_info_dict = {}
    point_count = 0
    debate_info_dict[last_updated_key] = datetime.today()
    debate_info_dict[total_points_key] = point_count

    point_info_dict = {}
    all_points_dict = {}
    is_parsing_points = False

    # Parsing

    if local:
        with open("/Users/samy/Documents/PoliticalDebateApp/PoliticalDebateApp_DebateMaps/Upload.txt") as debate_map:
            debate_map_lines = debate_map.readlines()
    else:
        github_auth = Github(os.environ['GITHUB_ACCESS_TOKEN'])
        for repo in github_auth.get_user().get_repos():
            if repo.name == "PoliticalDebateApp_DebateMaps":
                debate_maps_repo = repo
        debate_map_file = debate_maps_repo.get_contents("Upload.txt")

        with urlopen(debate_map_file.download_url) as debate_map:
            debate_map_lines = [line.decode('utf-8') for line in debate_map.readlines()]

    for line in debate_map_lines:
        if line in ['\n', '\r\n']: # empty line
            continue
        # Trim all leading non-alphanumeric characters
        line = line.lstrip().lstrip(punctuation).lstrip()

        if not is_parsing_points: # basic info section
            if check_for_key(title_key, line):
                debate_info_dict[title_key] = get_value_for_key(title_key, line)
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
                    print("The following point does not have all the required fields:")
                    pprint(point_info_dict)
                    return
                point_info_dict[key_key] = int(get_value_for_key(key_key, line))
            elif check_for_key(description_key, line):
                description = get_value_for_key(description_key, line)
                description, point_info_dict[hyperlinks_key] = parse_hyperlinks(description)
                point_info_dict[description_key] = description
            elif check_for_key(short_description_key, line):
                point_info_dict[short_description_key] = get_value_for_key(short_description_key, line)
            elif check_for_key(side_key, line):
                side = get_value_for_key(side_key, line)
                if side.lower() not in [pro_value, con_value, context_value]:
                    print("Invalid side: " + side)
                    return
                else:
                    point_info_dict[side_key] = side.lower()
            elif check_for_key(rebuttals_key, line):
                rebuttals = get_value_for_key(rebuttals_key, line)
                if key_key not in point_info_dict:
                    print("Rebuttals must always be before the side key:")
                    print(rebuttals)
                    return
                formatted_rebuttals = []
                if rebuttals:
                    rebuttals = rebuttals.split(", ")
                    for rebuttal_pk in rebuttals:
                        formatted_rebuttals.append(int(rebuttal_pk))
                point_info_dict[rebuttals_key] = formatted_rebuttals

            if basic_point_info_complete(point_info_dict):
                if not check_for_key(side_key, line):
                    print("The side must always come last.")
                    pprint(point_info_dict)
                    sys.exit()
                if point_info_dict[root_key]:
                    if point_info_dict[side_key] == context_value:
                        new_point = Point.objects.create(debate=new_debate, description=point_info_dict[description_key], side=point_info_dict[side_key])
                    else:
                        new_point = Point.objects.create(debate=new_debate, description=point_info_dict[description_key], short_description=point_info_dict[short_description_key],  side=point_info_dict[side_key])
                else:
                    new_point = Point.objects.create(description=point_info_dict[description_key], short_description=point_info_dict[short_description_key],  side=point_info_dict[side_key])

                for hyperlink in point_info_dict[hyperlinks_key]:
                    PointHyperlink.objects.create(point=new_point, substring=hyperlink[substring_key], url=hyperlink[url_key])

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
    print("NEW DEBATE PK:")
    print(new_debate.pk)
