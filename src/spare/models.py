from django.db import models


class Parts(models.Model):
    name = models.CharField(max_length=64, unique=True)
    count = models.PositiveIntegerField(default=0)
    mustbe = models.PositiveIntegerField(default=0)
    arrive = models.PositiveIntegerField(default=0)
    alternatives = models.ForeignKey('Alternatives', related_name='parts',
                                     blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Part {}>: {} of {}'.format(self.name, self.count+self.arrive, self.mustbe)


class Alternatives(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    @property
    def alt_parts(self):
        result = {'name': self.name, 'count': 0, 'mustbe': 0, 'arrive': 0}
        for part in self.parts.all():
            result['count'] += part.count
            result['arrive'] += part.arrive
            if part.mustbe > result['count']:
                result['mustbe'] = part.mustbe
        return result
