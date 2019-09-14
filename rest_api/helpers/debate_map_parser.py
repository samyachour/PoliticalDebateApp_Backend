from django.contrib.auth.models import User
from rest_api.models import *
from .constants import *
from datetime import datetime, timedelta
from string import punctuation

# Run in shell:
# from rest_api.helpers.debate_map_parser import parse_debate_file; parse_debate_file("/Users/samy/Documents/PoliticalDebateApp/PoliticalDebateApp_Backend/DebateMap.txt"); exit();

# Helpers

key_key = "key"
main_key = "main"
object_key = "object"

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
    return main_key in point_info_dict and key_key in point_info_dict and description_key in point_info_dict and short_description_key in point_info_dict and side_key in point_info_dict and rebuttals_key in point_info_dict

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
            cleaned_description = cleaned_description.replace("[" + current_hyperlink[substring_key] + "]" + "(" + current_hyperlink[url_key] + ")", current_hyperlink[substring_key])
            hyperlink = ""
            current_hyperlink = {}
        if is_parsing_hyperlink:
            hyperlink += char
        if char == '(' and current_hyperlink[substring_key]:
            is_parsing_hyperlink = True

    return cleaned_description, hyperlinks

def parse_images(point, images):
    images_list = images.split(" || ")
    for image in images_list:
        image_parts = image.split("//")
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

def parse_debate_file(filename, title_for_deletion = ""):

    if title_for_deletion != "":
        Debate.objects.filter(title=title_for_deletion).delete()

    # Properties

    debate_info_dict = {}
    point_count = 0
    debate_info_dict[last_updated_key] = datetime.today()
    debate_info_dict[total_points_key] = point_count

    point_info_dict = {}
    all_points_dict = {}
    is_parsing_points = False

    # Parsing

    with open(filename) as debate_map:

        for line in debate_map:
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
                if check_for_key(main_key, line):
                    point_info_dict[main_key] = True
                elif check_for_key(key_key, line):
                    point_info_dict[key_key] = int(get_value_for_key(key_key, line))
                elif check_for_key(description_key, line):
                    description = get_value_for_key(description_key, line)
                    description, point_info_dict[hyperlinks_key] = parse_hyperlinks(description)
                    point_info_dict[description_key] = description
                elif check_for_key(short_description_key, line):
                    point_info_dict[short_description_key] = get_value_for_key(short_description_key, line)
                elif check_for_key(side_key, line):
                    point_info_dict[side_key] = get_value_for_key(side_key, line)
                elif check_for_key(rebuttals_key, line):
                    rebuttals = get_value_for_key(rebuttals_key, line)
                    formatted_rebuttals = []
                    if rebuttals:
                        rebuttals = rebuttals.split(", ")
                        for rebuttal_pk in rebuttals:
                            formatted_rebuttals.append(int(rebuttal_pk))
                    point_info_dict[rebuttals_key] = formatted_rebuttals
                elif check_for_key(images_key, line):
                    images = get_value_for_key(images_key, line)
                    parse_images(point_info_dict[object_key], images)

                if basic_point_info_complete(point_info_dict):
                    if point_info_dict[main_key]:
                        new_point = Point.objects.create(debate=new_debate, description=point_info_dict[description_key], short_description=point_info_dict[short_description_key],  side=point_info_dict[side_key])
                    else:
                        new_point = Point.objects.create(description=point_info_dict[description_key], short_description=point_info_dict[short_description_key],  side=point_info_dict[side_key])

                    for hyperlink in point_info_dict[hyperlinks_key]:
                        PointHyperlink.objects.create(point=new_point, substring=hyperlink[substring_key], url=hyperlink[url_key])

                    point_info_dict[object_key] = new_point
                    all_points_dict[point_info_dict[key_key]] = point_info_dict
                    point_count += 1
                    point_info_dict = { main_key: False, object_key: new_point }

    for _, point in all_points_dict.items():
        point_object = point[object_key]
        for rebuttal_pk in point[rebuttals_key]:
            rebuttal = all_points_dict[rebuttal_pk][object_key]
            point_object.rebuttals.add(rebuttal)
        point_object.save()

    debate_info_dict[total_points_key] = point_count
    new_debate.total_points = point_count
    new_debate.save()
    print("NEW DEBATE PK:")
    print(new_debate.pk)
