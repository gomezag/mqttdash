import environ
import csv
from core.models import Dato
import datetime

env = environ.Env()

i = 0
j = 0
k = 0
fecha_fin = Dato.objects.all().order_by('-fecha')[1000].fecha
fecha_fin = fecha_fin.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=2)))
# for dato in Dato.objects.all():
#     dato.delete()
#
# print('deleted all data')
with open('./mqtt.log', 'r') as f:
    rows = csv.reader(f, delimiter=',')
    total = sum(1 for _ in rows)

with open('./mqtt.log', 'r') as f:
    rows = csv.reader(f, delimiter=',')
    next(rows)
    procesando = 0
    for row in rows:
        procesando = procesando +1
        print('processing '+str(procesando)+'/'+str(total))
        fecha = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')
        fecha = fecha.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=2)))
        if fecha<fecha_fin:
            print('skip')
            k = k+1
            continue
        else:
            print(fecha)
            try:
                dato = Dato()
                dato.fecha = fecha
                dato.location = row[1]
                dato.valor = row[2]
                dato.save()
                i = i+1
            except Exception as e:
                print(repr(e))
                j = j+1
                continue

print('done '+str(i)+' entries.')
print('skipped '+str(k)+' entries.')
print('error in '+str(j)+' entries.')
