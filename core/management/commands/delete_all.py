from core.models import Dato

for dato in Dato.objects.all():
    dato.delete()