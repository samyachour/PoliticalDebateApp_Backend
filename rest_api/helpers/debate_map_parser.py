from django.contrib.auth.models import User
from rest_api.models import *
from .constants import *
from datetime import datetime, timedelta

# Run in shell:
# from rest_api.helpers.debate_map_parser import parse_debate_file
# parse_debate_file("path/to/map.txt", 300); exit();

# Helpers

def count_indentation(source_string, tabsize=4):
    stripped_source_string = source_string.lstrip()
    return (stripped_source_string, len(source_string) - len(stripped_source_string))

def check_for_key(key, source_string):
    key_length = len(key)
    formatted_key = key.replace("_", " ")
    return source_string.lower()[:key_length] == formatted_key.lower()

def get_value_for_key(key, source_string):
    key_length = len(key)
    value_string = source_string[key_length:]
    return value_string.replace(": ","",1).rstrip()

def basic_debate_info_complete(debate_info_dict):
    return title_key in debate_info_dict and short_title_key in debate_info_dict and tags_key in debate_info_dict and last_updated_key in debate_info_dict and total_points_key in debate_info_dict

def basic_point_info_complete(point_info_dict):
    return description_key in point_info_dict and short_description_key in point_info_dict and side_key in point_info_dict

def parse_hyperlinks(description):
    hyperlinks = []
    substring = ""
    is_parsing_substring = False
    hyperlink = ""
    is_parsing_hyperlink = False
    current_hyperlink = {}
    for char in description:
        if char == ']':
            is_parsing_substring = False
            current_hyperlink[substring_key] = substring
            substring = ""
        if is_parsing_substring:
            substring += char
        if char == '[':
            is_parsing_substring = True

        if char == ')':
            is_parsing_hyperlink = False
            current_hyperlink[url_key] = hyperlink
            hyperlinks.append(current_hyperlink)
            hyperlink = ""
            current_hyperlink = {}
        if is_parsing_hyperlink:
            hyperlink += char
        if char == '(' and current_hyperlink[substring_key]:
            is_parsing_hyperlink = True

    return hyperlinks

def parse_images(point, images):
    images_list = images.split(", ")
    for image in images_list:
        image_parts = image.split("/")
        image_dict = {}
        for index, image_part in enumerate(image_parts):
            if index == 0:
                if len(image_parts) == 2:
                    image_dict[source_key] = image_part
                if len(image_parts) == 3:
                    image_dict[name_key] = image_part
            if index == 1:
                if len(image_parts) == 2:
                    image_dict[url_key] = image_part
                if len(image_parts) == 3:
                    image_dict[source_key] = image_part
            if index == 2:
                image_dict[url_key] = image_part

        if image_dict:
            if name_key in image_dict:
                PointImage.objects.create(point=point, name=image_dict[name_key], source=image_dict[source_key], url=image_dict[url_key])
            else:
                PointImage.objects.create(point=point, source=image_dict[source_key], url=image_dict[url_key])
            image_dict = {}

# Parser

def parse_debate_file(filename, old_version_pk = -1):

    if old_version_pk != -1:
        Debate.objects.filter(pk=old_version_pk).delete()

    # Properties

    debate_info_dict = {}
    point_count = 0
    debate_info_dict[last_updated_key] = datetime.today()
    debate_info_dict[total_points_key] = point_count

    point_info_dict = {}
    indented_points_dict = {}
    is_parsing_points = False
    whitespace_count = 0
    typical_whitespace = 0

    # Parsing

    with open(filename) as debate_map:

        for line in debate_map:
            line = line.replace("- ","",1)
            if line in ['\n', '\r\n']: # empty line
                continue

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
                previous_whitespace_count = whitespace_count
                line, whitespace_count = count_indentation(line)
                if whitespace_count != previous_whitespace_count:
                    typical_whitespace = whitespace_count - previous_whitespace_count

                if check_for_key(description_key, line):
                    description = get_value_for_key(description_key, line)
                    point_info_dict[hyperlinks_key] = parse_hyperlinks(description)
                    point_info_dict[description_key] = get_value_for_key(description_key, line)
                elif check_for_key(short_description_key, line):
                    point_info_dict[short_description_key] = get_value_for_key(short_description_key, line)
                elif check_for_key(side_key, line):
                    point_info_dict[side_key] = get_value_for_key(side_key, line)
                elif check_for_key(images_key, line):
                    current_point = indented_points_dict[whitespace_count]
                    images = get_value_for_key(images_key, line)
                    parse_images(current_point, images)

                if basic_point_info_complete(point_info_dict):
                    if whitespace_count == 0:
                        new_point = Point.objects.create(debate=new_debate, description=point_info_dict[description_key], short_description=point_info_dict[short_description_key],  side=point_info_dict[side_key])
                    else:
                        parent_point = indented_points_dict[whitespace_count - typical_whitespace]
                        new_point = Point.objects.create(description=point_info_dict[description_key], short_description=point_info_dict[short_description_key],  side=point_info_dict[side_key])
                        parent_point.rebuttals.add(new_point)
                        parent_point.save()

                    for hyperlink in point_info_dict[hyperlinks_key]:
                        PointHyperlink.objects.create(point=new_point, substring=hyperlink[substring_key], url=hyperlink[url_key])

                    indented_points_dict[whitespace_count] = new_point
                    point_count += 1
                    point_info_dict = {}

    debate_info_dict[total_points_key] = point_count
    new_debate.total_points = point_count
    new_debate.save()
    print("DEBATE INFO: ")
    print(debate_info_dict) # TODO: Remove
    print("NEW DEBATE PK:")
    print(new_debate.pk)
