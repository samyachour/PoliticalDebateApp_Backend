from django.contrib.auth.models import User
from rest_api.models import *
from django.utils import timezone
import random
from .shell_utils import delete_existing_debate

# Run in shell:
# from rest_api.utils.generate_database import generate_accounts, generate_debates; generate_accounts(); generate_debates(); exit();

def boolean_probability(percent=50):
    return random.randrange(100) < percent

# Generate X test accounts
def generate_accounts(count = 50):

    newUser = User.objects.create_user(
        username="reservedstubgenerationacct@mail.com",
        email="reservedstubgenerationacct@mail.com",
        password="testing"
    )

    for i in range(count):

        newUser = User.objects.create_user(
            username="test{0}@mail.com".format(i),
            email="test{0}@mail.com".format(i),
            password="testing"
        )

# Generate X test debbates
def generate_debates(count = 300):

    now = timezone.now()

    stub_generation_user = User.objects.get(username="reservedstubgenerationacct@mail.com")
    first_test_user = User.objects.get(username="test0@mail.com")

    test_users = [stub_generation_user, first_test_user]

    for user in test_users:
        if not Starred.objects.filter(user=user).exists():
            Starred.objects.create(user=user)

    total_points = 2

    first_run = True

    for i in range(count):

        title = "Test debate number #{0}".format(i)
        delete_existing_debate(title, force=False)
        test_debate = Debate.objects.create(title=title, short_title="Debate #{0}".format(i), last_updated=now - timezone.timedelta(days=1), tags="Test tag")
        test_debate_point_2 = Point.objects.create(short_description="Test *point 2*", description="Test *point 2* description. (in debate {0})".format(i), side="con")
        test_debate_point_1 = Point.objects.create(debate=test_debate, short_description="Test **point 1**", description="This is a longer description of test **point 1**. (in debate {0})".format(i), side="pro")
        test_debate_point_1.rebuttals.add(test_debate_point_2)
        test_debate_point_1.save()

        PointHyperlink.objects.create(point=test_debate_point_2, substring="point", url="www.test.com/article")

        if boolean_probability(4) or first_run: # Just so we definitely add the first debate info
            # Star this debate for our test users
            for user in test_users:
                starred = Starred.objects.get(user=user)
                starred.starred_list.add(test_debate)
                starred.save()

        if boolean_probability(8) or first_run: # Just so we definitely add the first debate info
            # Add progress points for our test users
            for user in test_users:
                completed_points = random.randrange(1, total_points + 1)
                if completed_points > 0:
                    progress = Progress.objects.create(user=user, debate=test_debate)
                    progress.seen_points.add(test_debate_point_1)
                    if completed_points > 1:
                        progress.seen_points.add(test_debate_point_2)
                    progress.save()

        if first_run:
            first_run = False
