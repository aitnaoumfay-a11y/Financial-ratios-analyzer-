"""
Financial Ratio Analyzer
=========================
Author : Fadoua Ait Naoum — FSJES Marrakech, Centre d'Excellence
Master of Excellence in Applied Finance (Sustainable Finance)

A reusable Python module for computing, benchmarking, and visualising
financial ratios from balance sheet and income statement data.

Validated on Moroccan listed companies (Label Vie, CIH Bank, Cosumar).

Usage
-----
    from financial_ratio_analyzer import FinancialAnalyzer
    fa = FinancialAnalyzer(company_data)
    fa.compute_all()
    fa.radar_chart()
    fa.report()
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings("ignore")

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 150,
})

# ── Moroccan sector benchmarks (approximate industry medians) ──────────────────
BENCHMARKS = {
    "Distribution": {
        "current_ratio":      1.2,
        "quick_ratio":        0.7,
        "debt_to_equity":     1.5,
        "interest_coverage":  3.0,
        "gross_margin_pct":   22.0,
        "net_margin_pct":     3.5,
        "roe_pct":            10.0,
        "roa_pct":            4.0,
    },
    "Banques": {
        "current_ratio":      None,
        "quick_ratio":        None,
        "debt_to_equity":     8.0,
        "interest_coverage":  None,
        "gross_margin_pct":   None,
        "net_margin_pct":     18.0,
        "roe_pct":            12.0,
        "roa_pct":            1.2,
    },
    "Agroalimentaire": {
        "current_ratio":      1.4,
        "quick_ratio":        0.9,
        "debt_to_equity":     0.8,
        "interest_coverage":  5.0,
        "gross_margin_pct":   35.0,
        "net_margin_pct":     8.0,
        "roe_pct":            15.0,
        "roa_pct":            7.0,
    },
    "BTP": {
        "current_ratio":      1.3,
        "quick_ratio":        0.8,
        "debt_to_equity":     1.2,
        "interest_coverage":  4.0,
        "gross_margin_pct":   18.0,
        "net_margin_pct":     6.0,
        "roe_pct":            13.0,
        "roa_pct":            5.0,
    },
}

# ── Color palette ─────────────────────────────────────────────────────────────
def _ratio_color(value, benchmark, higher_is_better=True):
    """Return green/orange/red based on distance from benchmark."""
    if benchmark is None or value is None:
        return "#888780"
    ratio = value / benchmark if benchmark != 0 else 1
    if higher_is_better:
        if ratio >= 0.9:  return "#1D9E75"
        if ratio >= 0.6:  return "#EF9F27"
        return "#E24B4A"
    else:
        if ratio <= 1.1:  return "#1D9E75"
        if ratio <= 1.5:  return "#EF9F27"
        return "#E24B4A"


# ── Core analyzer class ────────────────────────────────────────────────────────
class FinancialAnalyzer:
    """
    Compute and visualise key financial ratios for a single company.

    Parameters
    ----------
    data : dict
        Financial data with keys matching the expected input fields.
    company_name : str
        Display name of the company.
    sector : str
        Sector for benchmark comparison (must be in BENCHMARKS).
    year : int or str
        Fiscal year label.
    """

    REQUIRED = [
        "current_assets", "current_liabilities",
        "inventory", "cash",
        "total_debt", "total_equity",
        "ebit", "interest_expense",
        "revenue", "gross_profit", "net_income",
        "total_assets",
    ]

    def __init__(self, data: dict, company_name: str = "Company",
                 sector: str = "Distribution", year: int = 2023):
        self.raw = data
        self.name = company_name
        self.sector = sector
        self.year = year
        self.ratios: dict = {}
        self._validate()

    def _validate(self):
        missing = [k for k in self.REQUIRED if k not in self.raw]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

    def _safe_div(self, num, den):
        if den == 0 or den is None:
            return None
        return round(num / den, 4)

    # ── Ratio computation ────────────────────────────────────────────────────
    def compute_liquidity(self):
        d = self.raw
        self.ratios["current_ratio"]    = self._safe_div(d["current_assets"], d["current_liabilities"])
        self.ratios["quick_ratio"]      = self._safe_div(d["current_assets"] - d["inventory"], d["current_liabilities"])
        self.ratios["cash_ratio"]       = self._safe_div(d["cash"], d["current_liabilities"])

    def compute_leverage(self):
        d = self.raw
        self.ratios["debt_to_equity"]   = self._safe_div(d["total_debt"], d["total_equity"])
        self.ratios["debt_ratio"]       = self._safe_div(d["total_debt"], d["total_assets"])
        self.ratios["equity_ratio"]     = self._safe_div(d["total_equity"], d["total_assets"])
        self.ratios["interest_coverage"] = self._safe_div(d["ebit"], d["interest_expense"])

    def compute_profitability(self):
        d = self.raw
        self.ratios["gross_margin_pct"] = round(self._safe_div(d["gross_profit"], d["revenue"]) * 100, 2)
        self.ratios["net_margin_pct"]   = round(self._safe_div(d["net_income"], d["revenue"]) * 100, 2)
        self.ratios["roe_pct"]          = round(self._safe_div(d["net_income"], d["total_equity"]) * 100, 2)
        self.ratios["roa_pct"]          = round(self._safe_div(d["net_income"], d["total_assets"]) * 100, 2)

    def compute_all(self):
        self.compute_liquidity()
        self.compute_leverage()
        self.compute_profitability()
        return self

    # ── Scoring ──────────────────────────────────────────────────────────────
    def score(self) -> float:
        """
        Compute a simple weighted financial health score (0–100).
        Weights reflect typical credit analysis emphasis.
        """
        bench = BENCHMARKS.get(self.sector, BENCHMARKS["Distribution"])
        weights = {
            "current_ratio":      0.15,
            "quick_ratio":        0.10,
            "debt_to_equity":     0.15,
            "interest_coverage":  0.15,
            "net_margin_pct":     0.20,
            "roe_pct":            0.15,
            "roa_pct":            0.10,
        }
        higher_is_better = {
            "current_ratio": True, "quick_ratio": True,
            "debt_to_equity": False, "interest_coverage": True,
            "net_margin_pct": True, "roe_pct": True, "roa_pct": True,
        }
        total, w_sum = 0.0, 0.0
        for ratio, w in weights.items():
            v = self.ratios.get(ratio)
            b = bench.get(ratio)
            if v is None or b is None:
                continue
            if higher_is_better[ratio]:
                score_r = min(v / b, 1.5) / 1.5
            else:
                score_r = max(0, 1 - (v / b - 1)) if v > b else 1.0
            total += score_r * w
            w_sum += w
        return round((total / w_sum) * 100, 1) if w_sum > 0 else 0.0

    # ── Visualisations ────────────────────────────────────────────────────────
    def bar_chart(self, save: bool = True) -> None:
        """Horizontal bar chart — ratios vs sector benchmarks."""
        bench = BENCHMARKS.get(self.sector, BENCHMARKS["Distribution"])
        display = {
            "current_ratio":      ("Ratio de liquidité générale",  True),
            "quick_ratio":        ("Ratio de liquidité rapide",    True),
            "debt_to_equity":     ("Levier D/E",                   False),
            "interest_coverage":  ("Couverture des charges fin.",  True),
            "gross_margin_pct":   ("Marge brute (%)",              True),
            "net_margin_pct":     ("Marge nette (%)",              True),
            "roe_pct":            ("ROE (%)",                      True),
            "roa_pct":            ("ROA (%)",                      True),
        }

        labels, company_vals, bench_vals, colors = [], [], [], []
        for key, (label, hib) in display.items():
            v = self.ratios.get(key)
            b = bench.get(key)
            if v is None:
                continue
            labels.append(label)
            company_vals.append(v)
            bench_vals.append(b if b else 0)
            colors.append(_ratio_color(v, b, hib))

        fig, ax = plt.subplots(figsize=(10, 6))
        y = np.arange(len(labels))
        ax.barh(y - 0.2, company_vals, height=0.35,
                color=colors, alpha=0.85, label=self.name)
        ax.barh(y + 0.2, bench_vals, height=0.35,
                color="#D3D1C7", alpha=0.7, label=f"Benchmark ({self.sector})")

        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=10)
        ax.set_xlabel("Valeur")
        ax.set_title(f"{self.name} — Ratios financiers vs benchmark\nExercice {self.year}",
                     fontweight="bold", pad=12)
        ax.legend(frameon=False)

        score_val = self.score()
        score_color = "#1D9E75" if score_val >= 70 else "#EF9F27" if score_val >= 50 else "#E24B4A"
        ax.text(0.98, 0.02, f"Score santé financière : {score_val}/100",
                transform=ax.transAxes, ha="right", va="bottom",
                fontsize=11, fontweight="bold", color=score_color)

        plt.tight_layout()
        fname = f"ratios_{self.name.lower().replace(' ', '_')}_{self.year}.png"
        if save:
            plt.savefig(fname, bbox_inches="tight")
            plt.close()
            print(f"✓ {fname} saved")
        else:
            plt.show()

    def radar_chart(self, save: bool = True) -> None:
        """Radar chart — normalised ratio scores (0–1 vs benchmark)."""
        bench = BENCHMARKS.get(self.sector, BENCHMARKS["Distribution"])
        keys = ["current_ratio", "quick_ratio", "interest_coverage",
                "net_margin_pct", "roe_pct", "roa_pct"]
        hib  = [True, True, True, True, True, True]
        labels_r = ["Liquidité\ngénérale", "Liquidité\nrapide",
                    "Couverture\ncharges fin.", "Marge\nnette", "ROE", "ROA"]

        vals, bench_n = [], []
        for k, h in zip(keys, hib):
            v = self.ratios.get(k)
            b = bench.get(k)
            if v is None or b is None:
                vals.append(0.5)
            elif h:
                vals.append(min(v / b, 1.5) / 1.5)
            else:
                vals.append(max(0, 1 - (v / b - 1)) if v > b else 1.0)
            bench_n.append(1.0)   # benchmark is always 1 by definition

        N = len(labels_r)
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        vals   = vals + [vals[0]]
        bench_n = bench_n + [bench_n[0]]
        angles  = angles  + [angles[0]]

        fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
        ax.plot(angles, bench_n, color="#D3D1C7", linewidth=1.5, linestyle="--",
                label=f"Benchmark ({self.sector})")
        ax.fill(angles, bench_n, color="#D3D1C7", alpha=0.15)
        ax.plot(angles, vals, color="#378ADD", linewidth=2, label=self.name)
        ax.fill(angles, vals, color="#378ADD", alpha=0.2)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels_r, fontsize=10)
        ax.set_yticklabels([])
        ax.set_ylim(0, 1.3)
        ax.set_title(f"{self.name} — Profil financier normalisé\nExercice {self.year}",
                     fontweight="bold", y=1.08)
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.12),
                  frameon=False, fontsize=9)

        plt.tight_layout()
        fname = f"radar_{self.name.lower().replace(' ', '_')}_{self.year}.png"
        if save:
            plt.savefig(fname, bbox_inches="tight")
            plt.close()
            print(f"✓ {fname} saved")
        else:
            plt.show()

    def report(self) -> None:
        """Print a structured ratio report to the console."""
        bench = BENCHMARKS.get(self.sector, BENCHMARKS["Distribution"])
        print(f"\n{'='*60}")
        print(f"  FINANCIAL RATIO REPORT — {self.name.upper()}")
        print(f"  Sector : {self.sector}  |  Year : {self.year}")
        print(f"{'='*60}")
        sections = {
            "LIQUIDITY": ["current_ratio", "quick_ratio", "cash_ratio"],
            "LEVERAGE":  ["debt_to_equity", "debt_ratio", "equity_ratio", "interest_coverage"],
            "PROFITABILITY": ["gross_margin_pct", "net_margin_pct", "roe_pct", "roa_pct"],
        }
        for section, keys in sections.items():
            print(f"\n  {section}")
            print(f"  {'Ratio':<30} {'Value':>10} {'Benchmark':>12}  {'Signal':>8}")
            print(f"  {'-'*64}")
            for k in keys:
                v = self.ratios.get(k)
                b = bench.get(k)
                v_str = f"{v:.2f}" if v is not None else "N/A"
                b_str = f"{b:.2f}" if b is not None else "—"
                if v is None or b is None:
                    signal = "—"
                elif k == "debt_to_equity":
                    signal = "✓" if v <= b * 1.1 else "✗"
                else:
                    signal = "✓" if v >= b * 0.9 else ("~" if v >= b * 0.6 else "✗")
                print(f"  {k:<30} {v_str:>10} {b_str:>12}  {signal:>8}")

        print(f"\n  HEALTH SCORE : {self.score()}/100")
        print(f"{'='*60}\n")


# ── Multi-company comparison ───────────────────────────────────────────────────
def compare_companies(analysts: list, save: bool = True) -> None:
    """
    Side-by-side bar chart comparing multiple FinancialAnalyzer instances.
    """
    metrics = ["gross_margin_pct", "net_margin_pct", "roe_pct", "roa_pct",
               "current_ratio", "debt_to_equity"]
    labels_m = ["Marge brute (%)", "Marge nette (%)", "ROE (%)", "ROA (%)",
                "Ratio liquidité", "Levier D/E"]

    colors = ["#378ADD", "#1D9E75", "#EF9F27", "#D4537E", "#7F77DD", "#E24B4A"]
    x = np.arange(len(metrics))
    width = 0.8 / len(analysts)

    fig, ax = plt.subplots(figsize=(13, 6))
    for i, fa in enumerate(analysts):
        vals = [fa.ratios.get(m) for m in metrics]
        offsets = x + (i - len(analysts) / 2 + 0.5) * width
        ax.bar(offsets, vals, width=width * 0.9, color=colors[i % len(colors)],
               alpha=0.85, label=fa.name)

    ax.set_xticks(x)
    ax.set_xticklabels(labels_m, fontsize=9)
    ax.set_title("Comparaison financière — sociétés cotées MASI", fontweight="bold")
    ax.set_ylabel("Valeur du ratio")
    ax.legend(frameon=False, fontsize=9)
    plt.tight_layout()

    if save:
        plt.savefig("comparison_companies.png", bbox_inches="tight")
        plt.close()
        print("✓ comparison_companies.png saved")
    else:
        plt.show()


# ── Demo — Label Vie, CIH Bank, Cosumar ───────────────────────────────────────
if __name__ == "__main__":

    label_vie = FinancialAnalyzer(
        data={
            "current_assets":      3_850_000,
            "current_liabilities": 3_100_000,
            "inventory":           1_200_000,
            "cash":                  420_000,
            "total_debt":          2_800_000,
            "total_equity":        2_100_000,
            "ebit":                  310_000,
            "interest_expense":       90_000,
            "revenue":            14_200_000,
            "gross_profit":        2_980_000,
            "net_income":            580_000,
            "total_assets":        7_100_000,
        },
        company_name="Label Vie",
        sector="Distribution",
        year=2023,
    )

    cosumar = FinancialAnalyzer(
        data={
            "current_assets":      4_200_000,
            "current_liabilities": 2_800_000,
            "inventory":             980_000,
            "cash":                  650_000,
            "total_debt":          1_400_000,
            "total_equity":        4_800_000,
            "ebit":                  980_000,
            "interest_expense":       85_000,
            "revenue":             8_100_000,
            "gross_profit":        3_240_000,
            "net_income":            850_000,
            "total_assets":        9_200_000,
        },
        company_name="Cosumar",
        sector="Agroalimentaire",
        year=2023,
    )

    cih_bank = FinancialAnalyzer(
        data={
            "current_assets":      18_000_000,
            "current_liabilities": 16_500_000,
            "inventory":                    0,
            "cash":                 2_100_000,
            "total_debt":          14_800_000,
            "total_equity":         2_800_000,
            "ebit":                   420_000,
            "interest_expense":       180_000,
            "revenue":              1_950_000,
            "gross_profit":         1_950_000,
            "net_income":             350_000,
            "total_assets":        19_800_000,
        },
        company_name="CIH Bank",
        sector="Banques",
        year=2023,
    )

    for fa in [label_vie, cosumar, cih_bank]:
        fa.compute_all()
        fa.report()
        fa.bar_chart()
        fa.radar_chart()

    compare_companies([label_vie, cosumar, cih_bank])
    print("All done. Charts generated for Label Vie, Cosumar, CIH Bank.")

    
