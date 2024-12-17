# Bundesliga Soccer App

### By Ian Cox and Owen Donohoe

### CS2500A: Intro to Database Systems

## Description

This project is a web-based application interface for Bundesliga league statistics for the years 2023-2024. It allows users to manage and visualize team and player data, including team ratings, goals per match, possession percentages, red cards, yellow cards, goals, penalties, expected goals, and tackles. Users can add and remove teams and players, modify team entries, calculate stats, and view detailed information about team/player performance. In addition, users can also query against columns of data and do specific searches based on rankings. There are plots for visualization of select statistics.

The application is built using Flask as the web framework, SQLite for the database, html for the web pages, and python for functionality.

## Tables

There are 4 tables for players data including:

- `player_expected_goals`
- `player_ratings`
- `player_tackles_won`
- `player_top_scorers`

There are 4 tables for teams data including:

- `possession_percentage_team`
- `team_goals_per_match`
- `team_ratings`
- `total_red_card_team`

![ER Diagram](./static/images/ER.png)

E-R Diagram (Made with LucidChart)

## Relational Model

`player_expected_goals (Player, Team, Expected_Goals, Goals, Minutes, Matches, Country);`

`player_ratings (Player, Team, FotMob_Rating, Player_Match_Awards, Minutes, Matches, Country);`

`player_tackles_won (Player, Team, Tackles_per_90, Tackle_success_rate, Minutes, Matches, Country);`

`player_top_scorers (Player, Team, Goals, Penalties, Minutes, Matches, Country);`

`possession_percentage_team (Team, possession_percentage, Matches);`

`team_ratings (Team, FotMob_team_rating, Matches);`

`team_goals_per_match (Team, Goals_per_match, Total_goals_scored, Matches);`

`total_red_card_team (Team, Red_cards, Yellow_cards, Matches);`
