import json
import pandas as pd
import matplotlib.pyplot as plt
import os

# --- Load JSON File ---
json_file = "experiments_out/results.json"  # change this to your file path
if not os.path.exists(json_file):
    raise FileNotFoundError(f"❌ File not found: {json_file}")

with open(json_file, "r") as f:
    data = json.load(f)

# --- Convert to DataFrame ---
if "tests" not in data:
    raise KeyError("⚠️ Expected key 'tests' not found in JSON file.")

df = pd.json_normalize(data["tests"])

# --- Add index labels for display ---
df["test_label"] = [f"Test {i+1}" for i in range(len(df))]

# --- Columns to show ---
cols_to_show = [
    "endpoint", "elapsed", "top_k", "status_code",
    "keyword_matches", "expected_keyword_count", "file_hits", "expected_file_count"
]

# --- Display Test Measurements ---
print("\n=== 📋 Test Measurements Summary ===")
print(df[cols_to_show].to_string(index=True))

# --- Compute Averages ---
numeric_cols = ["elapsed", "top_k", "keyword_matches", "expected_keyword_count", "file_hits", "expected_file_count"]
averages = df[numeric_cols].mean(numeric_only=True).to_dict()

# --- Display Averages in Table Form ---
print("\n=== 📊 Average Metrics Across All Tests ===")
avg_df = pd.DataFrame([averages])
print(avg_df.to_string(index=False))

# --- Visualization 1: Query Response Time ---
plt.figure(figsize=(10, 5))
plt.barh(df["test_label"], df["elapsed"], color="steelblue")
plt.xlabel("Elapsed Time (seconds)")
plt.ylabel("Test")
plt.title("⏱ Query Response Time Comparison")
plt.gca().invert_yaxis()
plt.grid(axis="x", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig("elapsed_time.png", dpi=300)
plt.close()
print("✅ Saved plot: elapsed_time.png")

# --- Visualization 2: Status Code Distribution ---
plt.figure(figsize=(5, 4))
df["status_code"].value_counts().plot(kind="bar", color="lightgreen")
plt.title("📊 API Status Code Distribution")
plt.xlabel("Status Code")
plt.ylabel("Count")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig("status_codes.png", dpi=300)
plt.close()
print("✅ Saved plot: status_codes.png")

# --- Visualization 3: Keyword Match Accuracy (optional) ---
if "keyword_matches" in df.columns and "expected_keyword_count" in df.columns:
    df["keyword_accuracy"] = df["keyword_matches"] / df["expected_keyword_count"].replace(0, 1)
    plt.figure(figsize=(10, 5))
    plt.barh(df["test_label"], df["keyword_accuracy"], color="orange")
    plt.xlabel("Keyword Match Accuracy")
    plt.ylabel("Test")
    plt.title("🎯 Keyword Match Accuracy per Test")
    plt.gca().invert_yaxis()
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig("keyword_accuracy.png", dpi=300)
    plt.close()
    print("✅ Saved plot: keyword_accuracy.png")

print("\n✅ All visualizations and tables generated successfully!")
