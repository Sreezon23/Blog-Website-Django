import urllib.request
import json
import ssl
from django.core.cache import cache

def get_la_liga_standings():
    """
    Fetches La Liga standings from FotMob unofficial API and caches them for 15 minutes.
    La Liga ID on FotMob is 87.
    """
    cache_key = 'fotmob_la_liga_standings_v2'
    standings = cache.get(cache_key)

    if standings is not None:
        return standings

    url = 'https://www.fotmob.com/api/leagues?id=87'
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )

    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode())
            if 'table' in data and len(data['table']) > 0:
                # The top-level table is an array and usually index 0 is the main table
                # data['table'][0]['data']['table']['all'] contains the standings list
                table_data = data['table'][0]['data']['table']['all']
                
                # Parse to extract what we need
                parsed_standings = []
                for idx, team in enumerate(table_data):
                    parsed_standings.append({
                        'position': idx + 1,
                        'name': team.get('name', ''),
                        'pts': team.get('pts', 0),
                        'played': team.get('played', 0),
                        'wins': team.get('wins', 0),
                        'draws': team.get('draws', 0),
                        'losses': team.get('losses', 0),
                        'goalDifference': team.get('goalConDiff', 0),
                    })
                
                # Cache for 15 minutes (900 seconds)
                cache.set(cache_key, parsed_standings, 900)
                return parsed_standings
    except Exception as e:
        print(f"Error fetching FotMob standings: {e}")
        return []
    
    return []

def get_barca_upcoming_matches():
    """
    Fetches the next 5 upcoming matches for FC Barcelona from FotMob team API
    and caches them for 15 minutes.
    FC Barcelona ID on FotMob is 8634.
    """
    cache_key = 'fotmob_barca_upcoming_matches'
    matches = cache.get(cache_key)

    if matches is not None:
        return matches

    url = 'https://www.fotmob.com/api/teams?id=8634'
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )

    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode())
            
            if 'fixtures' in data and 'allFixtures' in data['fixtures'] and 'fixtures' in data['fixtures']['allFixtures']:
                upcoming = data['fixtures']['allFixtures']['fixtures']
                
                parsed_matches = []
                for match in upcoming:
                    status_info = match.get('status', {})
                    # A match is truly upcoming if it's not finished, not started, and not cancelled
                    if not status_info.get('finished', False) and not status_info.get('cancelled', False):
                        
                        comp_name = match['tournament']['name']
                        
                        # FotMob returns 'Champions League Final Stage' generically for the knockouts in the team API. 
                        # We can attempt to pull the specific round if it's there, but default to the current active round
                        round_name = match.get('round', '')
                        if 'Final Stage' in comp_name and round_name:
                            comp_name = f"Champions League {round_name}"
                        elif comp_name == 'Champions League Final Stage':
                            comp_name = 'Champions League Round of 16'
                            
                        parsed_matches.append({
                            'competition': comp_name,
                            'home_team': match['home']['name'],
                            'away_team': match['away']['name'],
                            'status': status_info.get('reason', {}).get('long', 'Scheduled'),
                            'utc_time': status_info.get('utcTime', ''),
                        })
                    
                    if len(parsed_matches) >= 5:
                        break
                
                cache.set(cache_key, parsed_matches, 900)
                return parsed_matches
    except Exception as e:
        print(f"Error fetching FotMob team matches: {e}")
        return []
    return []

def get_knockout_bracket(league_id):
    """
    Fetches the knockout bracket for a specific FotMob league ID
    and caches it for 30 minutes.
    """
    cache_key = f'fotmob_knockout_bracket_{league_id}'
    bracket = cache.get(cache_key)

    if bracket is not None:
        return bracket

    url = f'https://www.fotmob.com/api/leagues?id={league_id}'
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )

    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode())
            if 'playoff' in data and data['playoff']:
                rounds = data['playoff'].get('rounds', [])
                parsed_rounds = []
                for round_data in rounds:
                    stage = round_data.get('stage', '')
                    matchups = []
                    for match in round_data.get('matchups', []):
                        match_info = {
                            'home_team': match.get('homeTeam', ''),
                            'away_team': match.get('awayTeam', ''),
                            'home_score': match.get('homeScore', 0),
                            'away_score': match.get('awayScore', 0),
                            'winner_id': match.get('winner', None),
                            'home_team_id': match.get('homeTeamId', None),
                            'away_team_id': match.get('awayTeamId', None),
                        }
                        
                        # Add winner true/false for styling
                        match_info['home_winner'] = match_info['winner_id'] == match_info['home_team_id']
                        match_info['away_winner'] = match_info['winner_id'] == match_info['away_team_id']
                        
                        matchups.append(match_info)
                    
                    parsed_rounds.append({
                        'stage': stage,
                        'stage_name': str(stage).capitalize().replace('_', ' '),
                        'matchups': matchups
                    })
                
                # Filter to only the main knockouts
                if league_id == 42: # Champions League
                    allowed_stages = ['1/8', '1/4', '1/2', 'final']
                    parsed_rounds = [r for r in parsed_rounds if r['stage'] in allowed_stages]
                    # Rename 1/8 to Round of 16
                    for r in parsed_rounds:
                        if r['stage'] == '1/8':
                            r['stage_name'] = 'Round of 16'
                        elif r['stage'] == '1/4':
                            r['stage_name'] = 'Quarter-Finals'
                        elif r['stage'] == '1/2':
                            r['stage_name'] = 'Semi-Finals'
                elif league_id == 138: # Copa del Rey
                    allowed_stages = ['1/16', '1/8', '1/4', '1/2', 'final']
                    parsed_rounds = [r for r in parsed_rounds if r['stage'] in allowed_stages]
                    for r in parsed_rounds:
                        if r['stage'] == '1/16':
                            r['stage_name'] = 'Round of 32'
                        elif r['stage'] == '1/8':
                            r['stage_name'] = 'Round of 16'
                        elif r['stage'] == '1/4':
                            r['stage_name'] = 'Quarter-Finals'
                        elif r['stage'] == '1/2':
                            r['stage_name'] = 'Semi-Finals'
                            
                cache.set(cache_key, parsed_rounds, 1800) # 30 minutes
                return parsed_rounds
    except Exception as e:
        print(f"Error fetching FotMob bracket: {e}")
        return []
        
    return []
