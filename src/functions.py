
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import re

def get_holdings_overlap_percentage(etf1, etf2, key="Ticker"):
    """
    Returns the percentage of etf1's holdings that are also present in etf2's holdings.
    
    Parameters:
        etf1, etf2: ETF objects with a holdings attribute (a DataFrame).
        key (str): The column name that identifies each holding (default is "Ticker").
        
    Returns:
        float: The percentage of etf1's holdings overlapping with etf2.
    """
    # Determine the identifier set for etf1
    if key in etf1.holdings.columns:
        holdings1 = set(etf1.holdings[key])
    else:
        holdings1 = set(etf1.holdings.index)
        
    # Determine the identifier set for etf2
    if key in etf2.holdings.columns:
        holdings2 = set(etf2.holdings[key])
    else:
        holdings2 = set(etf2.holdings.index)
    
    # Calculate the intersection and compute the percentage overlap relative to etf1
    overlap = holdings1.intersection(holdings2)
    if len(holdings1) == 0:
        return 0.0
    return (len(overlap) / len(holdings1)) * 100

def visualize_overlap_pie(etf1, etf2, key="Ticker"):
    """
    Visualizes the holdings overlap between two ETFs using two pie charts.
    
    For each ETF, the pie chart shows:
      - The percentage of holdings that overlap with the other ETF (exploded).
      - The percentage of holdings that are unique to that ETF.
    
    We explicitly ensure the Overlap slice is first in the data list,
    and we explode only that slice (explode=(0.1, 0)).
    """
    # Calculate overlap percentages for each ETF perspective
    overlap_pct1 = get_holdings_overlap_percentage(etf1, etf2, key=key)
    unique_pct1 = 100 - overlap_pct1
    
    overlap_pct2 = get_holdings_overlap_percentage(etf2, etf1, key=key)
    unique_pct2 = 100 - overlap_pct2

    # Retrieve ETF names from metadata for labeling
    name1 = etf1.metadata.get("fund_name", "ETF 1")
    name2 = etf2.metadata.get("fund_name", "ETF 2")

    # Set seaborn theme for styling
    sns.set_theme(style="whitegrid")
    
    # Create subplots: two pie charts side by side
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    
    # In each pie chart, Overlap is the first slice => exploded
    slices1 = [overlap_pct1, unique_pct1]
    labels1 = [f"Overlap ({overlap_pct1:.1f}%)", f"Unique ({unique_pct1:.1f}%)"]
    explode1 = (0.1, 0)  # explode first slice (Overlap)

    slices2 = [overlap_pct2, unique_pct2]
    labels2 = [f"Overlap ({overlap_pct2:.1f}%)", f"Unique ({unique_pct2:.1f}%)"]
    explode2 = (0.1, 0)  # explode first slice (Overlap)

    # First pie chart (ETF1)
    axes[0].pie(
        slices1,
        labels=labels1,
        autopct="%1.1f%%",
        explode=explode1,
        colors=["#66b3ff", "#ff9999"],
        startangle=140  # rotate to highlight the exploded slice
    )
    axes[0].set_title(f"{name1} Holdings Overlap\nwith {name2}")
    
    # Second pie chart (ETF2)
    axes[1].pie(
        slices2,
        labels=labels2,
        autopct="%1.1f%%",
        explode=explode2,
        colors=["#66b3ff", "#ff9999"],
        startangle=140
    )
    axes[1].set_title(f"{name2} Holdings Overlap\nwith {name1}")
    
    plt.tight_layout()
    plt.show()


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def get_weighted_holdings_overlap(etf1, etf2, key="Ticker", weight_col="Weight"):
    """
    Computes the weighted overlap between two ETFs from each ETF's perspective.
    
    Parameters:
    -----------
    etf1, etf2 : objects
        Each should have a `holdings` attribute containing a DataFrame of holdings.
        The DataFrame must include:
          - A key column (e.g., "Ticker") to identify each holding.
          - A weight column (e.g., "Weight") indicating the holding's weight in the portfolio.
    key : str
        Column name used to identify each holding (default is "Ticker").
    weight_col : str
        Column name that contains the weight of each holding (default is "Weight").

    Returns:
    --------
    overlap_pct1 : float
        The percentage of ETF1's total weight that also appears in ETF2 (capped at 100%).
    overlap_pct2 : float
        The percentage of ETF2's total weight that also appears in ETF1 (capped at 100%).
    """
    # Select and rename columns for a clear merge
    df1 = etf1.holdings[[key, weight_col]].rename(columns={key: "Key", weight_col: "Weight1"})
    df2 = etf2.holdings[[key, weight_col]].rename(columns={key: "Key", weight_col: "Weight2"})
    
    # Calculate total weights in each ETF
    total_weight1 = df1["Weight1"].sum()
    total_weight2 = df2["Weight2"].sum()
    
    # Merge on the key to get only intersecting holdings
    merged = pd.merge(df1, df2, on="Key", how="inner")
    
    # Sum intersection weights from each ETF's perspective
    intersect_weight1 = merged["Weight1"].sum()
    intersect_weight2 = merged["Weight2"].sum()
    
    # Compute overlap percentages (handle case of zero total weight)
    overlap_pct1 = (intersect_weight1 / total_weight1) * 100 if total_weight1 else 0.0
    overlap_pct2 = (intersect_weight2 / total_weight2) * 100 if total_weight2 else 0.0
    
    # Cap the percentages at 100%
    overlap_pct1 = min(overlap_pct1, 100)
    overlap_pct2 = min(overlap_pct2, 100)
    
    return overlap_pct1, overlap_pct2

def visualize_weighted_overlap_pie(etf1, etf2, key="Ticker", weight_col="Weight"):
    """
    Visualizes the weighted holdings overlap between two ETFs using two pie charts.
    
    For each ETF, the pie chart shows:
      - The percentage of that ETF's total weight that overlaps with the other ETF (exploded slice).
      - The percentage that is unique to that ETF.
    """
    # Get weighted overlap from each perspective
    overlap_pct1, overlap_pct2 = get_weighted_holdings_overlap(etf1, etf2, key, weight_col)
    
    # Compute the unique portions (i.e., 100% - overlap)
    unique_pct1 = 100 - overlap_pct1
    unique_pct2 = 100 - overlap_pct2
    
    # Retrieve ETF names from metadata for labeling
    name1 = etf1.metadata.get("fund_name", "ETF 1")
    name2 = etf2.metadata.get("fund_name", "ETF 2")
    
    # Set a seaborn style
    sns.set_theme(style="whitegrid")
    
    # Create subplots: two pie charts side by side
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    
    # Data for the first pie chart (ETF1)
    slices1 = [overlap_pct1, unique_pct1]
    labels1 = [f"Overlap ({overlap_pct1:.1f}%)", f"Unique ({unique_pct1:.1f}%)"]
    explode1 = (0.1, 0)  # explode the Overlap slice
    
    # Data for the second pie chart (ETF2)
    slices2 = [overlap_pct2, unique_pct2]
    labels2 = [f"Overlap ({overlap_pct2:.1f}%)", f"Unique ({unique_pct2:.1f}%)"]
    explode2 = (0.1, 0)  # explode the Overlap slice
    
    # First pie chart
    axes[0].pie(
        slices1,
        labels=labels1,
        autopct="%1.1f%%",
        explode=explode1,
        colors=["#66b3ff", "#ff9999"],
        startangle=140
    )
    axes[0].set_title(f"{name1}\nWeighted Overlap with {name2}")
    
    # Second pie chart
    axes[1].pie(
        slices2,
        labels=labels2,
        autopct="%1.1f%%",
        explode=explode2,
        colors=["#66b3ff", "#ff9999"],
        startangle=140
    )
    axes[1].set_title(f"{name2}\nWeighted Overlap with {name1}")
    
    plt.tight_layout()
    plt.show()

def parse_amundi_filename(filename):
    # Remove file extension
    name = os.path.splitext(os.path.basename(filename))[0]

    # Extract ISIN (usually 12 characters, starts with two letters)
    isin_match = re.search(r'[A-Z]{2}[A-Z0-9]{10}', name)
    isin = isin_match.group(0) if isin_match else None

    # Extract name between the prefix and the ISIN
    fund_match = re.search(r'_(.*?)_(' + isin + ')', name)
    fund_name = fund_match.group(1).strip() if fund_match else "Unknown Fund"

    return fund_name, isin