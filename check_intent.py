import json
from collections import Counter

data = json.load(open('content_gap_analysis_package.json', encoding='utf-8'))
intents = [r.get('search_intent', 'N/A') for r in data['recommendations']]

print('Search Intent Distribution:')
for intent, count in Counter(intents).items():
    print(f'  {intent}: {count} ({count/len(intents)*100:.0f}%)')

print()
print('All recommendations with search intent:')
for i, r in enumerate(data['recommendations'], 1):
    intent = r.get('search_intent', 'N/A')
    print(f'{i:2}. {intent:20} - {r["title"][:60]}')
