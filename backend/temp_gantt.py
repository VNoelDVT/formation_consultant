import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

tasks = [
    ('Définition du projet', datetime(2025, 1, 1), datetime(2025, 1, 15)),
    ('Analyse des besoins', datetime(2025, 1, 16), datetime(2025, 2, 15)),
    ('Conception du projet', datetime(2025, 2, 16), datetime(2025, 3, 15)),
    ('Développement du projet', datetime(2025, 3, 16), datetime(2025, 5, 15)),
    ('Tests et validation', datetime(2025, 5, 16), datetime(2025, 6, 15)),
    ('Déploiement et maintenance', datetime(2025, 6, 16), datetime(2025, 7, 15))
]

fig, ax = plt.subplots(figsize=(10, 6))

for i, (task, start, end) in enumerate(tasks):
    ax.barh(i, (end - start).days, left=start, color='skyblue')

today = datetime.today()
ax.set_xlim(left=today)

ax.set_yticks(range(len(tasks)))
ax.set_yticklabels([task for task, _, _ in tasks])

ax.set_xlabel('Date')
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.title('Diagramme de Gantt du projet de gestion de projet R&D')

plt.savefig('gantt_diagram.png')
plt.close()