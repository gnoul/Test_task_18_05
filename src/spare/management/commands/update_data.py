import requests
from requests.exceptions import RequestException

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from spare.models import Parts, Alternatives


class Command(BaseCommand):
    help = "Update sparse parts in database"

    def add_arguments(self, parser):
        parser.add_argument('--clean', action='store_true', help='Delete all records from database')

    def handle(self, *args, **options):
        parts = self.get_data('PARTS_URL')
        alternatives = self.get_data('PARTS_ALTERNATIVES')['alternatives']
        make_clean = options.get('clean')
        if make_clean:
            Parts.objects.all().delete()
            Alternatives.objects.all().delete()
        self.update_parts(parts)
        self.update_alternatives(alternatives)

    @staticmethod
    def update_parts(parts):
        for part_name, params in parts.items():
            part, created = Parts.objects.get_or_create(name=part_name)
            part.arrive = params.get('arrive', 0)
            part.count = params.get('count', 0)
            part.mustbe = params.get('mustbe', 0)
            part.save()

    @staticmethod
    def update_alternatives(alternatives):
        for alt_name, part_names in alternatives.items():
            alt, created = Alternatives.objects.get_or_create(name=alt_name)
            if not created:
                alt.parts.clear()
            for part_name in part_names:
                part, _ = Parts.objects.get_or_create(name=part_name)
                alt.parts.add(part)

    @staticmethod
    def get_data(param):
        url = getattr(settings, param, None)
        if not url:
            raise CommandError('URL for {} is missing in the settings '.format(param))
        try:
            res = requests.get(url)
            if res.status_code == requests.codes.ok:
                return res.json()
        except RequestException:
            pass
