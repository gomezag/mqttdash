from core.models import Dato
import datetime

i=0
j=0
queryset = Dato.objects.all().order_by('-fecha')
lens = len(queryset)
for dato in queryset:
    duplicates = queryset.filter(fecha__lte=dato.fecha+datetime.timedelta(seconds=10), fecha__gte=dato.fecha-datetime.timedelta(seconds=10), location=dato.location)
    j = j+1
    print('processed '+str(j)+'/'+str(lens)+' entries with '+str(i)+' deletions')
    if len(duplicates)>1:
        for dup in duplicates[1:]:
            i+=1
            dup.delete()

print('erased '+str(i)+' entries')