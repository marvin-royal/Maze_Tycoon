# metrics/plotting.py
import pandas as pd
import matplotlib.pyplot as plt


def plot_solver_performance(csv_path: str):
    """
    Plots average runtime and steps per solver.
    """
    df = pd.read_csv(csv_path)

    agg = df.groupby("solver").agg(
        avg_steps=("steps", "mean"),
        avg_runtime=("runtime_ms", "mean"),
    )

    fig, ax = plt.subplots()
    agg["avg_steps"].plot(kind="bar", ax=ax)
    ax.set_title("Average Steps per Solver")
    ax.set_ylabel("Steps")
    plt.show()

    fig, ax = plt.subplots()
    agg["avg_runtime"].plot(kind="bar", ax=ax)
    ax.set_title("Average Runtime per Solver")
    ax.set_ylabel("Runtime (ms)")
    plt.show()


def plot_difficulty_curve(csv_path: str):
    """
    Shows success rate vs maze size.
    """
    df = pd.read_csv(csv_path)
    df["area"] = df["width"] * df["height"]

    agg = df.groupby("area").agg(
        success_rate=("success", "mean")
    )

    fig, ax = plt.subplots()
    agg["success_rate"].plot(kind="line", marker="o", ax=ax)
    ax.set_title("Success Rate vs Maze Size")
    ax.set_xlabel("Maze Area (width*height)")
    ax.set_ylabel("Success Rate")
    plt.show()
