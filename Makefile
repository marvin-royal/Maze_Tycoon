.PHONY: venv install test run exp plots

venv:
	python -m venv .venv && . .venv/bin/activate && python -m pip install -U pip

install:
	. .venv/bin/activate && pip install -r requirements.txt

test:
	. .venv/bin/activate && pytest -q

run:
	. .venv/bin/activate && python -m src.maze_tycoon.game.app

exp:
	. .venv/bin/activate && python scripts/run_experiment.py --config config/experiments/heuristic_compare.yaml

plots:
	. .venv/bin/activate && python scripts/plot_results.py data/results/runs.csv --out data/results/figures