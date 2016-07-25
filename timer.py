from datetime import timedelta

song = timedelta(minutes=5, seconds=26)
buffer_time = timedelta(seconds=30)
minutes = timedelta(minutes=input('enter your minutes: '))
seconds = timedelta(seconds=input('enter  your seconds: '))

monologue = minutes + seconds

start_secs = (song - monologue - buffer_time).seconds

final_minutes = ((start_secs % 3600) // 60)

final_secs = start_secs % 60

print("start at {}:{}").format(final_minutes, final_secs)



