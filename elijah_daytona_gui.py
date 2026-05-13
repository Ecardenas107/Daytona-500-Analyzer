import tkinter as tk
from tkinter import messagebox, scrolledtext
import pandas as pd
import matplotlib.pyplot as plt
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = r"C:\Users\elija\PycharmProjects\PythonProject1\Project\daytona500_data.csv"

def load_data():
    print("Python file location:", os.path.abspath(__file__))
    print("Looking for CSV at:", CSV_FILE)
    print("File exists:", os.path.exists(CSV_FILE))

    if not os.path.exists(CSV_FILE):
        messagebox.showerror(
            "File Error",
            f"Could not find file:\n{CSV_FILE}\n\nMake sure the file really exists there."
        )
        return None

    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        messagebox.showerror("Read Error", f"Could not read CSV file.\n\n{e}")
        return None

    required_cols = {"year", "driver", "start_position", "finish_position"}
    if not required_cols.issubset(df.columns):
        messagebox.showerror(
            "Column Error",
            "CSV must contain these columns exactly:\n"
            "year, driver, start_position, finish_position"
        )
        return None

    try:
        df["year"] = pd.to_numeric(df["year"])
        df["start_position"] = pd.to_numeric(df["start_position"])
        df["finish_position"] = pd.to_numeric(df["finish_position"])
    except Exception as e:
        messagebox.showerror("Data Error", f"One or more numeric columns have bad values.\n\n{e}")
        return None

    df["position_change"] = df["start_position"] - df["finish_position"]
    df["winner"] = (df["finish_position"] == 1).astype(int)
    df["top5"] = (df["finish_position"] <= 5).astype(int)
    df["top10"] = (df["finish_position"] <= 10).astype(int)

    return df

def classify_start(pos):
    if pos <= 10:
        return "High"
    elif pos <= 20:
        return "Medium"
    else:
        return "Low"

def run_analysis():
    df = load_data()
    if df is None:
        return

    pearson_corr = df["start_position"].corr(df["finish_position"], method="pearson")
    spearman_corr = df["start_position"].corr(df["finish_position"], method="spearman")
    avg_winner_start = df[df["winner"] == 1]["start_position"].mean()
    avg_top5_start = df[df["top5"] == 1]["start_position"].mean()
    avg_top10_start = df[df["top10"] == 1]["start_position"].mean()
    avg_positions_gained = df["position_change"].mean()

    result_box.delete("1.0", tk.END)
    result_box.insert(tk.END, "DAYTONA 500 STARTING POSITION REPORT\n")
    result_box.insert(tk.END, "-" * 50 + "\n")
    result_box.insert(tk.END, f"CSV Path: {CSV_FILE}\n\n")
    result_box.insert(tk.END, f"Rows analyzed: {len(df)}\n")
    result_box.insert(tk.END, f"Years included: {int(df['year'].min())} to {int(df['year'].max())}\n\n")
    result_box.insert(tk.END, f"Pearson correlation: {pearson_corr:.3f}\n")
    result_box.insert(tk.END, f"Spearman correlation: {spearman_corr:.3f}\n")
    result_box.insert(tk.END, f"Average winner starting position: {avg_winner_start:.2f}\n")
    result_box.insert(tk.END, f"Average Top 5 starting position: {avg_top5_start:.2f}\n")
    result_box.insert(tk.END, f"Average Top 10 starting position: {avg_top10_start:.2f}\n")
    result_box.insert(tk.END, f"Average positions gained: {avg_positions_gained:.2f}\n\n")

    if spearman_corr > 0.30:
        result_box.insert(tk.END, "Interpretation: Starting closer to the front appears to help drivers finish better.\n")
    elif spearman_corr < -0.30:
        result_box.insert(tk.END, "Interpretation: Drivers starting deeper in the field still performed very well.\n")
    else:
        result_box.insert(tk.END, "Interpretation: Starting position has some impact, but it is not a strong predictor by itself.\n")

def lookup_driver():
    df = load_data()
    if df is None:
        return

    driver_name = driver_entry.get().strip()
    if not driver_name:
        messagebox.showwarning("Input Error", "Please type a driver name.")
        return

    matches = df[df["driver"].str.lower() == driver_name.lower()].copy()
    result_box.delete("1.0", tk.END)

    if matches.empty:
        result_box.insert(tk.END, f"No results found for {driver_name}.\n")
        result_box.insert(tk.END, f"\nCSV Path checked:\n{CSV_FILE}\n")
        return

    result_box.insert(tk.END, f"Results for {driver_name}\n")
    result_box.insert(tk.END, "-" * 40 + "\n")

    for _, row in matches.iterrows():
        probability = classify_start(row["start_position"])
        result_box.insert(
            tk.END,
            f"Year: {int(row['year'])} | "
            f"Start: {int(row['start_position'])} | "
            f"Finish: {int(row['finish_position'])} | "
            f"Positions Gained: {int(row['position_change'])} | "
            f"Start Advantage: {probability}\n"
        )

def show_scatter_plot():
    df = load_data()
    if df is None:
        return

    plt.figure(figsize=(8, 5))
    plt.scatter(df["start_position"], df["finish_position"])
    plt.xlabel("Starting Position")
    plt.ylabel("Finish Position")
    plt.title("Daytona 500: Starting Position vs Finish Position")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def show_winner_plot():
    df = load_data()
    if df is None:
        return

    winners = df[df["winner"] == 1].sort_values("year")

    plt.figure(figsize=(8, 5))
    plt.plot(winners["year"], winners["start_position"], marker="o")
    plt.xlabel("Year")
    plt.ylabel("Winner Starting Position")
    plt.title("Daytona 500 Winner Starting Position by Year")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

root = tk.Tk()
root.title("Daytona 500 Starting Position Analyzer")
root.geometry("900x650")

title_label = tk.Label(root, text="Daytona 500 Starting Position Analyzer", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

driver_frame = tk.Frame(root)
driver_frame.pack(pady=5)

driver_label = tk.Label(driver_frame, text="Enter Driver Name:")
driver_label.pack(side=tk.LEFT, padx=5)

driver_entry = tk.Entry(driver_frame, width=30)
driver_entry.pack(side=tk.LEFT, padx=5)

lookup_button = tk.Button(driver_frame, text="Lookup Driver", command=lookup_driver)
lookup_button.pack(side=tk.LEFT, padx=5)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

analyze_button = tk.Button(button_frame, text="Run Full Analysis", command=run_analysis, width=20)
analyze_button.grid(row=0, column=0, padx=10, pady=5)

scatter_button = tk.Button(button_frame, text="Show Scatter Plot", command=show_scatter_plot, width=20)
scatter_button.grid(row=0, column=1, padx=10, pady=5)

winner_button = tk.Button(button_frame, text="Show Winner Plot", command=show_winner_plot, width=20)
winner_button.grid(row=0, column=2, padx=10, pady=5)

result_box = scrolledtext.ScrolledText(root, width=110, height=28)
result_box.pack(pady=10)

root.mainloop()
