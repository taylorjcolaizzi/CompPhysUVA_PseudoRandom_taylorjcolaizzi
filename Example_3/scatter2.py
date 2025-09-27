import numpy as np
import matplotlib.pyplot as plt

def make_uniform_scatter(
    N=8000,
    seed=42,
    theme="light",            # "light" or "dark"
    point_size=6,
    alpha=0.55,
    color_light="#2979ff",
    color_dark="#66d9ef",
    title="Uniform(0, 1) Random Pairs"
):
    np.random.seed(seed)
    x = np.random.uniform(0, 1, N)
    y = np.random.uniform(0, 1, N)

    if theme == "dark":
        bg, fg, pc, grid = "#0f0f0f", "#eaeaea", color_dark, "#444444"
    else:
        bg, fg, pc, grid = "white", "#1f1f1f", color_light, "#d0d0d0"

    fig, ax = plt.subplots(figsize=(6, 6), dpi=160)
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)

    ax.scatter(x, y, s=point_size, c=pc, alpha=alpha, edgecolors="none")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(title, color=fg, fontsize=12, pad=10)
    ax.set_xlabel("Uniform X", color=fg)
    ax.set_ylabel("Uniform Y", color=fg)

    for spine in ax.spines.values():
        spine.set_color(fg)
    ax.tick_params(colors=fg)
    ax.grid(True, color=grid, linestyle="-", linewidth=0.6, alpha=0.5)

    plt.tight_layout()
    plt.show()

# Example usages:
make_uniform_scatter(N=8000, theme="light")  # Light style
# make_uniform_scatter(N=10000, theme="dark", point_size=5, alpha=0.6)  # Dark style
