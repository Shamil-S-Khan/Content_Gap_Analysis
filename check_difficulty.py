import json

data = json.load(open('content_gap_analysis_package.json', encoding='utf-8'))
diffs = [r['difficulty'] for r in data['recommendations']]

print('Difficulty Distribution:')
print(f'  Low: {diffs.count("low")} ({diffs.count("low")/len(diffs)*100:.0f}%)')
print(f'  Medium: {diffs.count("medium")} ({diffs.count("medium")/len(diffs)*100:.0f}%)')
print(f'  High: {diffs.count("high")} ({diffs.count("high")/len(diffs)*100:.0f}%)')
print()
print('All recommendations with difficulty:')
for i, r in enumerate(data['recommendations'], 1):
    print(f'{i:2}. Impact:{r["impact_score"]:3}/100, Difficulty:{r["difficulty"]:6} - {r["title"][:60]}')
