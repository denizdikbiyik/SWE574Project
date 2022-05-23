from django.core.management.base import BaseCommand
from faker import Faker
from datetime import datetime
from django.contrib.auth.models import User
from social.models import UserProfile, Interest, Service, Event
import random
from openpyxl import load_workbook


class Command(BaseCommand):
    help = "Command Information"

    def handle(self, *args, **kwargs):
        fake = Faker(["tr_TR"])
        fake_en = Faker(["en_US"])
        fakedata_count = 1

        def load_interest_example():
            wb = load_workbook(filename='social\management\commands\interest_example.xlsx')
            ws = wb.active
            interest_dict = {}
            for row in list(ws.rows)[1:]:
                interest_dict[row[0].value] = [str(c.value) for c in row[1:]]
            return interest_dict

        # This function creates random users and updates the user_profiles randomly and adds an interest to that user
        def create_fake_user_data():
            interest_dict = load_interest_example()
            name = fake.name()
            if len(name) > 30:
                name = name[0:30]
            bio = fake_en.paragraph(nb_sentences=5, variable_nb_sentences=False)
            birth_date = datetime.combine(fake.date_of_birth(minimum_age=18, maximum_age=75), datetime.min.time())
            loc = fake.local_latlng(country_code="TR")
            location = str(loc[0]) + ',' + str(loc[1])
            password = 'admin123+'
            last_login = fake.date_time_between_dates(datetime_start=datetime(2022, 5, 20),
                                                      datetime_end=datetime(2022, 5, 22))
            username = fake.user_name()
            while len(User.objects.filter(username=username)) > 0:
                username = fake.user_name()
            email = fake.email()
            date_joined = fake.date_time_between_dates(datetime_start=datetime(2022, 1, 1),
                                                       datetime_end=datetime(2022, 5, 20))

            user = User.objects.create_user(username=username, email=email, password=password, is_superuser=False,
                                            is_staff=False, is_active=True, date_joined=date_joined,
                                            last_login=last_login)
            profile = UserProfile(user.id)
            profile.name = name
            profile.location = location
            profile.bio = bio
            profile.birth_date = birth_date
            profile.save()

            interest_no = random.randint(1, 31)
            new_interest = Interest.objects.create(user=user, name=interest_dict[interest_no][0],
                                                   wiki_description=interest_dict[interest_no][1], implicit=False,
                                                   origin='profile')
            new_interest.save()

        # This function makes random users follow other users
        def create_fake_following_data():
            last_user = User.objects.latest('id')
            arr = random.sample(range(1, last_user.id-1), 2)
            user1_id = arr[0]
            user2_id = arr[1]

            user1 = UserProfile.objects.get(pk=user1_id)
            user1.followers.add(user2_id)

        # This function creates random services
        def create_fake_service_data():
            interest_dict = load_interest_example()
            name = fake_en.sentence()
            sentence_count = random.randint(1, 7)
            desc = fake_en.paragraph(nb_sentences=sentence_count, variable_nb_sentences=False)
            loc = fake.local_latlng(country_code="TR")
            location = str(loc[0]) + ',' + str(loc[1])
            city = loc[2]
            create_date = fake.date_time_between_dates(datetime_start=datetime(2022, 1, 1),
                                                       datetime_end=datetime(2022, 5, 20))
            last_user = User.objects.latest('id')
            user_id = random.randint(1, last_user.id)
            capacity = random.randint(1, 5)
            duration = random.randint(1, 3)
            service_date = fake.future_datetime(end_date="+60d")
            wiki_no = random.randint(1, 31)
            wiki_desc = interest_dict[wiki_no][0] + ' as a(n) ' + interest_dict[wiki_no][1]

            new_service = Service.objects.create(createddate=create_date, description=desc, creater_id=user_id,
                                                 capacity=capacity, duration=duration, location=location, name=name,
                                                 servicedate=service_date, wiki_description=wiki_desc, city=city)
            new_service.save()

        # This function creates random events
        def create_fake_event_data():
            interest_dict = load_interest_example()
            name = fake_en.sentence()
            sentence_count = random.randint(1, 7)
            desc = fake_en.paragraph(nb_sentences=sentence_count, variable_nb_sentences=False)
            loc = fake.local_latlng(country_code="TR")
            location = str(loc[0]) + ',' + str(loc[1])
            city = loc[2]
            create_date = fake.date_time_between_dates(datetime_start=datetime(2022, 1, 1),
                                                       datetime_end=datetime(2022, 5, 20))
            last_user = User.objects.latest('id')
            user_id = random.randint(1, last_user.id)
            capacity = random.randint(5, 20)
            duration = random.randint(2, 6)
            event_date = fake.future_datetime(end_date="+60d")
            wiki_no = random.randint(1, 31)
            wiki_desc = interest_dict[wiki_no][0] + ' as a(n) ' + interest_dict[wiki_no][1]

            new_event = Event.objects.create(eventcreateddate=create_date, eventname=name, eventdescription=desc,
                                             event_wiki_description=wiki_desc, eventlocation=location,
                                             eventdate=event_date, eventcapacity=capacity, eventduration=duration,
                                             eventcreater_id=user_id, city=city)
            new_event.save()       

        for _ in range(fakedata_count):
            create_fake_user_data()

        for _ in range(fakedata_count):
            create_fake_following_data()

        for _ in range(fakedata_count):
            create_fake_service_data()

        for _ in range(fakedata_count):
            create_fake_event_data()
