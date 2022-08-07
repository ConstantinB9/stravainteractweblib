# stravainteractweblib
Extends the Strava v3 API using web scraping and web browser interactions.
Extends [stravaweblib](https://github.com/pR0Ps/stravaweblib) and therefore [stravalib](https://github.com/hozn/stravalib) functionality.

## Requirements
This package uses a [selenium](https://pypi.org/project/selenium/) Firefox instance to interact with the strava website. Therefore, you need to install [geckodriver](https://github.com/mozilla/geckodriver/releases) and add it to the PATH variable.
However `stravainteractweblib` can handle this for you.

```
from stravainteractweblib import InteractiveWebClient

InteractiveWebClient.setup_geckodriver()
client = InteractiveWebClient(access_token=OAUTH_TOKEN, email=EMAIL, password=PASSWORD)
```

## Authentication
See [stravaweblib](https://github.com/pR0Ps/stravaweblib), on how to authenticate

## Added Functionality
### Changing Stats visibility
Stats cannot be set private by default using the strava API v3 and require the interaction with the edit page.

```
from stravainteractweblib import InteractiveWebClient

# Log in (requires API token and email/password for the site)
client = InteractiveWebClient(access_token=OAUTH_TOKEN, email=EMAIL, password=PASSWORD)

# Get the first activity id (uses the normal stravalib API)
activities = client.get_activities()
activity_id = activities[0].id

# set the heart rate data of the activity to private
client.change_stats_visibility(activity_id = activity_id, heart_rate = False)
```