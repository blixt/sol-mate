# Sol Mate service

This service powers the [Sol Mate GPT](https://chat.openai.com/g/g-QIydQSFRm-sol-mate). It uses Modal because it's one of the easiest ways to run a simple service like this.

The output has been specifically formatted in a way that helps GPT visually describe the weather to Dall·E. This output can probably be used to describe the weather for any other LLM-related purpose.

## Running it

Make sure you have Modal installed:

```
pip install modal
```

Then, install the dependencies:

```
pip install ephem pytz requests
```

(You may use a virtual environment for this, up to you.)

For now you'll need to update `blixt` in the code to your own username.

And finally you can run it to see that it works:

```
$ modal run sol_mate.py
✓ Initialized. View run at https://modal.com/blixt/apps/ap-NbqYUrhnWHuqB8itLCIcGE
✓ Created objects.
├── 🔨 Created mount /Users/blixt/src/sol-mate/sol_mate.py
└── 🔨 Created weather_api => https://blixt--sol-mate-weather-api-dev.modal.run
The weather for {'latitude': 40.7128, 'longitude': -74.006, 'timezone': 'America/New_York', 'temperature_unit': 'fahrenheit'}:
Temperature: 46°F
Weather condition: overcast
The local time is 13:06 on a Thursday in April.
The sun is hidden behind clouds.
The sky is completely overcast.
A moderate breeze is blowing.
Stopping app - local entrypoint completed.
    GET /current -> 200 OK  (duration: 4.27 s, execution: 418.0 ms)
✓ App completed. View run at https://modal.com/blixt/apps/ap-NbqYUrhnWHuqB8itLCIcGE
```
