"""
Bundesliga Database Project
CS2500A: Intro to Database Systems
Fall 2024
Ian Cox & Owen Donohoe
"""

from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import numpy as np

app = Flask(__name__)

app.config.from_object('config.Config')

# Function to connect to the database
def get_db():
    conn = sqlite3.connect('Bundesliga.db', timeout=20)
    conn.row_factory = sqlite3.Row
    return conn

# Helper function to calculate median
def calculate_median(data):
    return np.median(data)

def generate_plot(stats_dict, selected_stat):
    """
    Generate a plot for the selected statistic (mean, min, max, etc.) for either player stats or team stats.
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Create the plot for the selected statistic
    for stat, values in stats_dict.items():
        if selected_stat == 'mean':
            stat_value = np.mean(values)
        elif selected_stat == 'min':
            stat_value = np.min(values)
        elif selected_stat == 'max':
            stat_value = np.max(values)
        elif selected_stat == 'median':
            stat_value = np.median(values)
        elif selected_stat == 'std_dev':
            stat_value = np.std(values)
        
        ax.bar(stat, stat_value, label=f"{stat} ({selected_stat})")

    ax.set_title(f'Visualization - {selected_stat.capitalize()} Values')
    ax.set_ylabel(f'{selected_stat.capitalize()} Value')
    ax.legend()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    
    return f"data:image/png;base64,{plot_url}"

def generate_scatter_plot(minutes, goals):
    """
    Generate a scatter plot for Minutes Played vs Goals Scored.
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.scatter(minutes, goals, color='blue', label='Minutes vs Goals', alpha=0.7)
    ax.set_title('Minutes Played vs Goals Scored')
    ax.set_xlabel('Minutes Played')
    ax.set_ylabel('Goals Scored')
    ax.legend()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return f"data:image/png;base64,{plot_url}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/players_data', methods=['GET', 'POST'])
def players_data():
    """ Display all data from the selected player table. """
    selected_table = None
    result = None
    rows = None
    columns = None

    # List of player-related tables
    player_tables = ['player_expected_goals', 'player_ratings', 'player_tackles_won', 'player_top_scorers']

    if request.method == 'POST':
        selected_table = request.form['table']

        if selected_table not in player_tables:
            result = {"error": "Invalid table selected."}
            return render_template('players_data.html', result=result, rows=rows, columns=columns, selected_table=selected_table, player_tables=player_tables)

        # SQL query to fetch all data from the selected table
        query = f"SELECT * FROM {selected_table}"

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()  # Fetch all rows

            # Fetch column names
            columns = [description[0] for description in cursor.description]

            conn.close()

            if not rows:
                result = {"error": "No data found in the selected table."}
                return render_template('players_data.html', result=result, rows=rows, columns=columns, selected_table=selected_table, player_tables=player_tables)

            return render_template('players_data.html', rows=rows, columns=columns, selected_table=selected_table, player_tables=player_tables)

        except sqlite3.Error as e:
            result = {"error": f"An error occurred: {e}"}
            return render_template('players_data.html', result=result, rows=rows, columns=columns, selected_table=selected_table, player_tables=player_tables)

    return render_template('players_data.html', player_tables=player_tables, rows=rows, columns=columns, selected_table=selected_table)


@app.route('/teams_data', methods=['GET', 'POST'])
def teams_data():
    """ Display all data from the selected team table. """
    selected_table = None
    result = None
    rows = None
    columns = None

    # List of team-related tables
    team_tables = ['possession_percentage_team', 'team_goals_per_match', 'team_ratings', 'total_red_card_team']

    if request.method == 'POST':
        selected_table = request.form['table']

        if selected_table not in team_tables:
            result = {"error": "Invalid table selected."}
            return render_template('teams_data.html', result=result, rows=rows, columns=columns, selected_table=selected_table, team_tables=team_tables)

        query = f"SELECT * FROM {selected_table}"

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            columns = [description[0] for description in cursor.description]

            conn.close()

            if not rows:
                result = {"error": "No data found in the selected table."}
                return render_template('teams_data.html', result=result, rows=rows, columns=columns, selected_table=selected_table, team_tables=team_tables)

            return render_template('teams_data.html', rows=rows, columns=columns, selected_table=selected_table, team_tables=team_tables)

        except sqlite3.Error as e:
            result = {"error": f"An error occurred: {e}"}
            return render_template('teams_data.html', result=result, rows=rows, columns=columns, selected_table=selected_table, team_tables=team_tables)

    return render_template('teams_data.html', team_tables=team_tables, rows=rows, columns=columns, selected_table=selected_table)

@app.route('/team_stats', methods=['GET', 'POST'])
def team_stats():
    selected_table = None
    selected_stat = None
    result = None
    plot_url = None

    table_columns = {
        'possession_percentage_team': ['Team', 'Possession_Percentage', 'Matches'],
        'team_goals_per_match': ['Team', 'Goals_Per_Match', 'Total_Goals_Scored', 'Matches'],
        'team_ratings': ['Team', 'FotMob_Team_Rating', 'Matches'],
        'total_red_card_team': ['Team', 'Red_Cards', 'Yellow_Cards', 'Matches']
    }

    if request.method == 'POST':
        selected_table = request.form['table']
        selected_stat = request.form['stat']

        if selected_table not in table_columns:
            result = {"error": "Invalid table selected."}
            return render_template('team_stats.html', result=result, selected_stat=selected_stat, selected_table=selected_table)

        columns = table_columns[selected_table]
        table_name = selected_table

        query = f"SELECT {', '.join(columns)} FROM {table_name}"

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(query)
            teams = cursor.fetchall()
            conn.close()

            if not teams:
                result = {"error": "No data found for the selected table."}
                return render_template('team_stats.html', result=result, selected_stat=selected_stat, selected_table=selected_table)

            stats_dict = {col: [team[col] for team in teams] for col in columns[1:]}

            # Calculate required stat based on the selected option
            if selected_stat == 'mean':
                result = {key: np.mean(values) for key, values in stats_dict.items()}
            elif selected_stat == 'min':
                result = {key: np.min(values) for key, values in stats_dict.items()}
            elif selected_stat == 'max':
                result = {key: np.max(values) for key, values in stats_dict.items()}
            elif selected_stat == 'median':
                result = {key: np.median(values) for key, values in stats_dict.items()}
            elif selected_stat == 'std_dev':
                result = {key: np.std(values) for key, values in stats_dict.items()}

            plot_url = generate_plot(stats_dict, selected_stat)

        except sqlite3.OperationalError as e:
            print(f"SQL Error: {e}")
            print(f"Query attempted: {query}")
            result = {"error": f"An error occurred while querying the database: {e}"}

    return render_template('team_stats.html', result=result, selected_stat=selected_stat, selected_table=selected_table, plot_url=plot_url)

@app.route('/player_stats', methods=['GET', 'POST'])
def player_stats():
    """ Route for calculating player stats. """
    selected_table = None
    selected_stat = None
    result = None
    plot_urls = {'stat_plot': None, 'scatter_plot': None}
    scatter_plot_url = None

    table_columns = {
        'player_expected_goals': ['Player', 'Team', 'Expected_Goals', 'Goals', 'Minutes', 'Matches', 'Country'],
        'player_ratings': ['Player', 'Team', 'FotMob_Rating', 'Player_Match_Awards', 'Minutes', 'Matches', 'Country'],
        'player_tackles_won': ['Player', 'Team', 'Tackles_per_90', 'Tackle_Success_Rate', 'Minutes', 'Matches', 'Country'],
        'player_top_scorers': ['Player', 'Team', 'Goals', 'Penalties', 'Minutes', 'Matches', 'Country']
    }

    if request.method == 'POST':
        selected_table = request.form['table']
        selected_stat = request.form['stat']

        if selected_table not in table_columns:
            result = {"error": "Invalid table selected."}
            return render_template('player_stats.html', result=result, selected_stat=selected_stat, selected_table=selected_table)

        columns = table_columns[selected_table]
        table_name = selected_table

        query = f"SELECT {', '.join(columns)} FROM {table_name}"
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(query)
            players = cursor.fetchall()
            conn.close()

            if not players:
                result = {"error": "No data found for the selected table."}
                return render_template('player_stats.html', result=result, selected_stat=selected_stat, selected_table=selected_table)

            stats_dict = {}

            numeric_columns = columns[2:-1]  # Exclude first ('Player', 'Team') and last ('Country') columns

            for col in numeric_columns:
                values = []
                for player in players:
                    value = player[columns.index(col)]  # Get the value for this column
                    if isinstance(value, (int, float)):  # Check if the value is already numeric
                        values.append(value)
                    else:
                        try:
                            # Convert to float
                            values.append(float(value))
                        except (ValueError, TypeError):
                            values.append(0)
                stats_dict[col] = values

            if selected_stat == 'mean':
                result = {key: np.mean(values) for key, values in stats_dict.items()}
            elif selected_stat == 'min':
                result = {key: np.min(values) for key, values in stats_dict.items()}
            elif selected_stat == 'max':
                result = {key: np.max(values) for key, values in stats_dict.items()}
            elif selected_stat == 'median':
                result = {key: np.median(values) for key, values in stats_dict.items()}
            elif selected_stat == 'std_dev':
                result = {key: np.std(values) for key, values in stats_dict.items()}

            plot_urls['stat_plot'] = generate_plot(stats_dict, selected_stat)

            # Generate the scatter plot
            if 'Minutes' in stats_dict and 'Goals' in stats_dict:
                scatter_plot_url = generate_scatter_plot(stats_dict['Minutes'], stats_dict['Goals'])
                plot_urls['scatter_plot'] = scatter_plot_url

        except sqlite3.OperationalError as e:
            result = {"error": f"An error occurred while querying the database: {e}"}

    return render_template('player_stats.html', result=result, selected_stat=selected_stat, selected_table=selected_table, plot_urls=plot_urls)

@app.route('/add_team', methods=['GET', 'POST'])
def add_team():
    """ Route to add a new team. """
    if request.method == 'POST':
        team_name = request.form['team_name']
        fotmob_rating = request.form['fotmob_rating']
        matches = request.form['matches']
        goals_per_match = request.form['goals_per_match']
        total_goals_scored = request.form['total_goals_scored']
        possession = request.form['possession']
        red_cards = request.form['red_cards']
        yellow_cards = request.form['yellow_cards']

        with get_db() as conn:
            cursor = conn.cursor()

            # Insert into team_ratings table
            cursor.execute('''
                INSERT INTO team_ratings (Team, "FotMob_Team_Rating", Matches) 
                VALUES (?, ?, ?)
            ''', (team_name, fotmob_rating, matches))

            # Insert into team_goals_per_match table
            cursor.execute('''
                INSERT INTO team_goals_per_match (Team, "Goals_per_Match", "Total_Goals_Scored", Matches) 
                VALUES (?, ?, ?, ?)
            ''', (team_name, goals_per_match, total_goals_scored, matches))

            # Insert into possession_percentage_team table
            cursor.execute('''
                INSERT INTO possession_percentage_team (Team, Possession_Percentage, Matches) 
                VALUES (?, ?, ?)
            ''', (team_name, possession, matches))

            # Insert into total_red_card_team table
            cursor.execute('''
                INSERT INTO total_red_card_team (Team, Red_Cards, Yellow_Cards, Matches) 
                VALUES (?, ?, ?, ?)
            ''', (team_name, red_cards, yellow_cards, matches))

            conn.commit()

        return redirect(url_for('index'))

    return render_template('add_team.html')

@app.route('/remove_team', methods=['GET', 'POST'])
def remove_team():
    """ Route to remove a team. """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT Team, FotMob_Team_Rating, Matches FROM team_ratings")
    teams = cursor.fetchall()

    teams = [{'Team': team['Team'], 'FotMob_Team_Rating': team['FotMob_Team_Rating'], 'Matches': team['Matches']} for team in teams]

    print(f"Teams fetched: {teams}")

    if not teams:
        return "No teams available to remove."

    cursor.execute("SELECT Team, Possession_Percentage FROM possession_percentage_team")
    possession_data = cursor.fetchall()

    cursor.execute("SELECT Team, Goals_per_Match, Total_Goals_Scored FROM team_goals_per_match")
    goals_data = cursor.fetchall()

    cursor.execute("SELECT Team, Red_Cards, Yellow_Cards FROM total_red_card_team")
    red_cards_data = cursor.fetchall()

    conn.close()

    team_info = []
    for team in teams:
        team_name = team['Team']
        fotmob_rating = team['FotMob_Team_Rating']
        matches = team['Matches']

        # Get data from other tables for the same team
        possession = next((x[1] for x in possession_data if x[0] == team_name), None)
        goals_per_match, total_goals = next((x[1], x[2]) for x in goals_data if x[0] == team_name)
        
        # Handle the case where red cards and yellow cards data might be missing
        red_card_data = next((x[1:] for x in red_cards_data if x[0] == team_name), (None, None))
        red_cards, yellow_cards = red_card_data

        team_info.append({
            'Team': team_name,
            'FotMob_Team_Rating': fotmob_rating,
            'Matches': matches,
            'Possession_Percentage': possession,
            'Goals_per_Match': goals_per_match,
            'Total_Goals_Scored': total_goals,
            'Red_Cards': red_cards,
            'Yellow_Cards': yellow_cards
        })

    if request.method == 'POST':
        team_name = request.form['team_name']
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM team_ratings WHERE Team = ?", (team_name,))
        cursor.execute("DELETE FROM possession_percentage_team WHERE Team = ?", (team_name,))
        cursor.execute("DELETE FROM team_goals_per_match WHERE Team = ?", (team_name,))
        cursor.execute("DELETE FROM total_red_card_team WHERE Team = ?", (team_name,))

        conn.commit()
        conn.close()

        return redirect(url_for('remove_team'))

    return render_template('remove_team.html', team_info=team_info)

@app.route('/add_player', methods=['GET', 'POST'])
def add_player():
    """ Route to add a new player. """
    if request.method == 'POST':
        player = request.form['player']
        team = request.form['team']
        goals = request.form['goals']
        penalties = request.form['penalties']
        minutes = request.form['minutes']
        matches = request.form['matches']
        country = request.form['country']
        fotmob_rating = request.form['fotmob_rating']
        player_match_awards = request.form['player_match_awards']
        expected_goals = request.form['expected_goals']
        tackles_per_90 = request.form['tackles_per_90']
        tackle_success_rate = request.form['tackle_success_rate']
        
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute('BEGIN TRANSACTION;')

            cursor.execute('INSERT INTO player_top_scorers (Player, Team, Goals, Penalties, Minutes, Matches, Country) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                           (player, team, goals, penalties, minutes, matches, country))
            cursor.execute('INSERT INTO player_ratings (Player, Team, FotMob_Rating, Player_Match_Awards, Minutes, Matches, Country) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                           (player, team, fotmob_rating, player_match_awards, minutes, matches, country))
            cursor.execute('INSERT INTO player_expected_goals (Player, Team, Expected_Goals, Goals, Minutes, Matches, Country) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                           (player, team, expected_goals, goals, minutes, matches, country))
            cursor.execute('INSERT INTO player_tackles_won (Player, Team, Tackles_per_90, Tackle_Success_Rate, Minutes, Matches, Country) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                           (player, team, tackles_per_90, tackle_success_rate, minutes, matches, country))

            conn.commit()

        except Exception as e:
            conn.rollback()  # Rollback if there's an error
            print(f"Error occurred while adding player: {e}")

        finally:
            conn.close()

        return redirect(url_for('index'))
    
    return render_template('add_player.html')


@app.route('/remove_player', methods=['GET', 'POST'])
def remove_player():
    """ Route to remove a player. """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT Player, Team, Goals, Matches FROM player_top_scorers")
    players = cursor.fetchall()

    # Convert sqlite3.Row objects into dictionaries
    players = [{'Player': player['Player'], 'Team': player['Team'], 'Goals': player['Goals'], 'Matches': player['Matches']} for player in players]

    if not players:
        return "No players available to remove."

    cursor.execute("SELECT Player, Team, FotMob_Rating, Player_Match_Awards, Minutes, Matches, Country FROM player_ratings")
    ratings_data = cursor.fetchall()

    cursor.execute("SELECT Player, Expected_Goals, Goals FROM player_expected_goals")
    expected_goals_data = cursor.fetchall()

    cursor.execute("SELECT Player, Tackles_per_90, Tackle_Success_Rate FROM player_tackles_won")
    tackles_data = cursor.fetchall()

    cursor.execute("SELECT Player, Penalties FROM player_top_scorers")
    top_scorers_data = cursor.fetchall()

    conn.close()

    player_info = []
    for player in players:
        player_name = player['Player']
        team = player['Team']
        goals = player['Goals']
        matches = player['Matches']

        fotmob_rating = next((x[2] for x in ratings_data if x[0] == player_name), None)
        player_match_awards = next((x[3] for x in ratings_data if x[0] == player_name), None)
        minutes = next((x[4] for x in ratings_data if x[0] == player_name), None)
        country = next((x[6] for x in ratings_data if x[0] == player_name), None)

        expected_goals = next((x[1] for x in expected_goals_data if x[0] == player_name), None)
        actual_goals = next((x[2] for x in expected_goals_data if x[0] == player_name), None)

        tackles_per_90, tackle_success_rate = next(
            ((x[1], x[2]) for x in tackles_data if x[0] == player_name), 
            (None, None)
        )

        penalties = next((x[1] for x in top_scorers_data if x[0] == player_name), None)

        player_info.append({
            'Player': player_name,
            'Team': team,
            'Goals': goals,
            'Matches': matches,
            'FotMob_Rating': fotmob_rating,
            'Player_Match_Awards': player_match_awards,
            'Minutes': minutes,
            'Country': country,
            'Expected_Goals': expected_goals,
            'Actual_Goals': actual_goals,
            'Tackles_per_90': tackles_per_90,
            'Tackle_Success_Rate': tackle_success_rate,
            'Penalties': penalties
        })

    if request.method == 'POST':
        player_name = request.form['player_name']
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM player_top_scorers WHERE Player = ?", (player_name,))
        cursor.execute("DELETE FROM player_ratings WHERE Player = ?", (player_name,))
        cursor.execute("DELETE FROM player_expected_goals WHERE Player = ?", (player_name,))
        cursor.execute("DELETE FROM player_tackles_won WHERE Player = ?", (player_name,))

        conn.commit()
        conn.close()

        return redirect(url_for('remove_player'))

    return render_template('remove_player.html', player_info=player_info)

@app.route('/query', methods=['GET', 'POST'])
def query_database():
    """ Route to query the database. """
    results = None

    if request.method == 'POST':
        query_type = request.form.get('category')

        if query_type is None:
            column = request.form['column']
            value = request.form['value']

            allowed_columns = ['Player', 'Team', 'Goals', 'Penalties', 'Minutes', 'Matches', 'Country']
            if column not in allowed_columns:
                return "Invalid column selected."

            query = f"SELECT * FROM player_top_scorers WHERE {column} LIKE ?"
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(query, (f'%{value}%',))
            results = cursor.fetchall()
            conn.close()

        elif query_type in ['players', 'teams']:
            top_n = request.form['top_n']
            category = request.form['category']
            if category == 'players':
                query = f"""
                SELECT pt.Player AS Name, pt.Team, pr.FotMob_Rating AS Rating
                FROM player_top_scorers pt
                JOIN player_ratings pr ON pt.Player = pr.Player
                ORDER BY pr.FotMob_Rating DESC
                LIMIT ?
                """
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute(query, (top_n,))
                results = cursor.fetchall()
                conn.close()

            elif category == 'teams':
                query = f"""
                SELECT ts.Team AS Name, ts.Matches, tr.FotMob_Team_Rating AS Rating
                FROM team_goals_per_match ts
                JOIN team_ratings tr ON ts.Team = tr.Team
                ORDER BY tr.FotMob_Team_Rating DESC
                LIMIT ?
                """
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute(query, (top_n,))
                results = cursor.fetchall()
                conn.close()

    return render_template('query_form.html', results=results)

@app.route('/modify_teams', methods=['GET'])
def modify_teams():
    """ Route to modify teams. """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM team_ratings')
    teams = cursor.fetchall()
    conn.close()
    return render_template('modify_teams.html', teams=teams)

@app.route('/edit_team/<string:team_name>', methods=['GET', 'POST'])
def edit_team(team_name):
    """ Route to edit teams. """
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM team_ratings WHERE Team = ?", (team_name,))
        team = cursor.fetchone()

        if team is None:
            return "Team not found", 404  # No team is found

        if request.method == 'POST':
            updated_team_name = request.form['team_name']
            fotmob_rating = request.form['fotmob_team_rating']
            matches = request.form['matches']

            cursor.execute('BEGIN TRANSACTION;')

            cursor.execute("""
                UPDATE team_ratings
                SET Team = ?, FotMob_Team_Rating = ?, Matches = ?
                WHERE Team = ?
            """, (updated_team_name, fotmob_rating, matches, team_name))

            conn.commit()
            return redirect(url_for('modify_teams'))

    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error occurred: {e}")
        return "An error occurred while updating the team.", 500

    finally:
        cursor.close()
        conn.close()

    return render_template('edit_team.html', team=team)

if __name__ == '__main__':
    app.run(debug=True)
