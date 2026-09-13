# Agent instructions

This repo is the source of truth for Rajdeep's daily schedule, two medications, and nightly habit counts.

## When sending a morning reminder

1. Read `config.toml`.
2. Run `python3 -m daily remind morning`.
3. Email that text to the address in `config.toml`.
4. Do not invent schedule items or medication names.

## When sending a night reminder

1. Run `python3 -m daily remind night`.
2. Email that text.
3. Ask for calories, steps, and pages read today.

## When the user replies with numbers

Save them with:

```bash
python3 -m daily log --calories N --steps N --pages N --book "TITLE"
```

Mark meds only if they said they took them:

```bash
python3 -m daily log --med morning
python3 -m daily log --med night
```

## On the first of the month

```bash
python3 -m daily summary --previous --send
```

Commit `summaries/YYYY-MM.md` if it changed.

## Rules

- Use timezone `Asia/Kolkata` for "today".
- Never overwrite an existing day's calories/steps/pages unless the user is correcting that day.
- Keep medication names and times exactly as `config.toml` has them.
