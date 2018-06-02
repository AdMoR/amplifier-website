# Webserver for Alliance_industrie_futur
Webserver for http://jeunes-industrie-du-futur.fr

# A little context
The Youth's Alliance Industrie du Futur (aka AIF) website add several goal :
- Present the AIF to younger generation
- Introduce them the goals of the organisation
- Motivate them to join and think during a 1 month challenge
- Organize the challenge through Slack and provide and easy access to it (Slack is less popular in on non tech communities)

This website allowed an good tradeoff between functionnalities and easiness of deployment

# Technical details
The server can simply be runned with `python run_debug.py`.
It uses Flask, a redis, and Bootstrap.

A very simple redis user database is used to register users and a hook to Slack allows the same time registration on a Slack forum.
Some unfinished admin functions were created to allow message broadcast on Slack via a UI and the Slack API.

A team membership function was also developped to allow users to form teams.

The system is deployed with ansible on https://github.com/AdMoR/ansible-aif-website
