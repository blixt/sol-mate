# Sol Mate service

This service powers the [Sol Mate GPT](https://chat.openai.com/g/g-QIydQSFRm-sol-mate). It uses Modal because it's one of the easiest ways to run a simple service like this.

The output has been specifically formatted in a way that helps GPT visually describe the weather to Dall·E. This output can probably be used to describe the weather for any other LLM-related purpose.

## Running it

Make sure you have [uv](https://docs.astral.sh/uv/) installed, then:

```sh
uv sync
uv run modal run sol_mate.py
```

Example output:

```
✓ Initialized.
✓ Created objects.
├── 🔨 Created mount sol_mate.py
├── 🔨 Created mount PythonPackage:tz
└── 🔨 Created web function weather_api
The weather for {'latitude': 40.7128, 'longitude': -74.006, ...}:
Temperature: 34°F
Weather condition: mainly clear
The local time is 12:34 on a Sunday in January.
The sun is high in the sky.
The sky is partly cloudy.
There's a light breeze gently blowing.
✓ App completed.
```
