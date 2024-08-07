__all__ = ["plot_hist", "print_summary_table"]

import random
import textwrap

import matplotlib.pyplot as plt
import numpy as np
from prettytable import PrettyTable

from .utils import generate_complementary_colors, reverse_dict


#     return adjacent_colors
def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb_color):
    """Convert RGB tuple to hex color."""
    return "#{:02x}{:02x}{:02x}".format(*rgb_color)


def generate_adjacent_colors(hex_color, k):
    """Generate a list of k adjacent hex colors near the given hex color. Generated by GPT-4 OMNI."""
    base_rgb = hex_to_rgb(hex_color)
    adjacent_colors = []

    for _ in range(k):
        # Generate small random changes to each RGB component
        new_rgb = tuple(
            max(0, min(255, base_rgb[i] + random.randint(-20, 20))) for i in range(3)
        )
        adjacent_colors.append(rgb_to_hex(new_rgb))

    return adjacent_colors


def plot_hist(summary, bin_count=30, legend=True, saveto=None):
    data_goi = summary["goi"]
    cluster_colors = generate_complementary_colors(len(summary["avg_clusters"]))
    _cluster_colors = {}
    for idx, cluster in enumerate(summary["avg_clusters"]):
        plt.axvline(
            np.mean(cluster),
            label=f"Group {idx + 1}",
            color=cluster_colors[idx],
        )
        adj_colors = generate_adjacent_colors(cluster_colors[idx], k=len(cluster))
        _cluster_colors[idx] = iter(adj_colors)

    bins = np.histogram(summary["rankings"], bins=bin_count)[1]
    for idx, key in enumerate(data_goi.keys()):
        data = data_goi[key]
        # kernel = gaussian_kde(data)
        # plt.plot(bins, kernel(bins), color=c18toMEANING[str(key)][1])
        c = next(_cluster_colors[summary["keyid2clusterid"][idx]])
        plt.hist(
            data,
            bins,
            alpha=0.7,
            edgecolor="white",
            linewidth=1.5,
            color=c,
            zorder=np.mean(data),
            density=False,
        )

    plt.rcParams["figure.figsize"] = [6, 4]  # or 7, 4 or 10,8
    plt.rcParams["lines.linewidth"] = 2
    plt.rcParams["lines.markersize"] = 4
    plt.rcParams["mathtext.fontset"] = "cm"
    plt.rcParams.update({"font.size": 14})
    plt.rcParams["font.family"] = "Helvetica"

    plt.tick_params(axis="y", direction="in", length=5, which="both")
    plt.tick_params(axis="x", direction="in", length=5, which="both")

    plt.ylabel("Frequency")
    plt.xlabel("Rankings")
    if legend:
        # plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
        plt.legend(
            loc="upper right",
        )
    if saveto is not None:
        plt.savefig(saveto, bbox_inches="tight")
    print("test")
    plt.show()


def print_summary_table(summary, max_width=40):
    rev_key_id2clsr_id = reverse_dict(summary["keyid2clusterid"])
    # Create a PrettyTable object
    table = PrettyTable()
    table.field_names = ["Group", "#Tags", "#Nodes", "Members", "Mean", "Std"]

    for idx, _s in enumerate(rev_key_id2clsr_id):
        members = ", ".join([summary[_][0] for _ in rev_key_id2clsr_id[_s]])
        counts = sum([summary[_][1] for _ in rev_key_id2clsr_id[_s]])
        sizes = len(rev_key_id2clsr_id[_s])
        m = np.mean(summary["avg_clusters"][idx])
        s = np.std(summary["avg_clusters"][idx])
        wrapped_members = textwrap.fill(members, width=max_width)
        table.add_row([_s + 1, sizes, counts, wrapped_members, f"{m:.3f}", f"{s:.1e}"])

    # Align columns to the left
    table.align["Group"] = "l"
    table.align["#Tags"] = "r"
    table.align["#Nodes"] = "r"
    table.align["Members"] = "l"
    table.align["Mean"] = "r"
    table.align["Std"] = "r"

    # Print the table
    print(table)
