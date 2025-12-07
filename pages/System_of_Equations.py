import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="System of Equations Solver & Graph", layout="wide")

st.title("System of Equations Solver & Graph")
st.write(
    "Use this tool to solve and visualize two linear equations in two variables. "
    "It’s useful for **break-even analysis**, **supply–demand equilibrium**, and "
    "**capacity planning**."
)

# ---------- Example selector ----------
example = st.selectbox(
    "Load a business scenario (optional):",
    ("None (manual input)", "Break-even: Revenue vs Cost",
     "Supply–Demand equilibrium", "Capacity: Machine A & B"),
)

use_case_text = ""

# Default coefficients
a1, b1, c1 = 1.0, 1.0, 10.0
a2, b2, c2 = 2.0, -1.0, 0.0

if example == "Break-even: Revenue vs Cost":
    # Revenue: y = 10x  -> 10x - y = 0
    # Cost:    y = 5x + 100 -> 5x - y = -100
    a1, b1, c1 = 10.0, -1.0, 0.0
    a2, b2, c2 = 5.0, -1.0, -100.0
    use_case_text = (
        "**Break-even analysis**  \n"
        "- Let `x` = quantity of units sold, `y` = revenue/cost.  \n"
        "- Equation 1: Revenue `y = 10x`  \n"
        "- Equation 2: Cost `y = 5x + 100`  \n"
        "The intersection gives the break-even quantity."
    )

elif example == "Supply–Demand equilibrium":
    # Demand: Q = 100 - 2P -> 2P + Q = 100  -> 2x + 1y = 100
    # Supply: Q = 20 + 3P  -> -3P + Q = 20 -> -3x + 1y = 20
    a1, b1, c1 = 2.0, 1.0, 100.0
    a2, b2, c2 = -3.0, 1.0, 20.0
    use_case_text = (
        "**Supply–Demand equilibrium**  \n"
        "- Let `x` = price (P), `y` = quantity (Q).  \n"
        "- Demand: `Q = 100 − 2P`  \n"
        "- Supply: `Q = 20 + 3P`  \n"
        "The intersection gives equilibrium price and quantity."
    )

elif example == "Capacity: Machine A & B":
    # Total: x + y = 1000
    # Speed: x = 2y -> x - 2y = 0
    a1, b1, c1 = 1.0, 1.0, 1000.0
    a2, b2, c2 = 1.0, -2.0, 0.0
    use_case_text = (
        "**Capacity planning**  \n"
        "- Let `x` = units from Machine A, `y` = units from Machine B.  \n"
        "- Equation 1: total output `x + y = 1000`  \n"
        "- Equation 2: Machine A twice as fast: `x = 2y`  \n"
        "The solution tells how much each machine should produce."
    )

if use_case_text:
    st.info(use_case_text)

st.markdown("---")

col1, col2 = st.columns(2)

# ---------- Inputs for Equation 1 ----------
with col1:
    st.subheader("Equation 1")

    # number_inputs FIRST
    a1 = st.number_input("a₁ (coefficient of x)", value=a1, step=1.0, format="%.4f")
    b1 = st.number_input("b₁ (coefficient of y)", value=b1, step=1.0, format="%.4f")
    c1 = st.number_input("c₁ (right-hand side)", value=c1, step=1.0, format="%.4f")

    # dynamic equation preview (uses *current* values)
    st.latex(rf"{a1:.2f}x + {b1:.2f}y = {c1:.2f}")

# ---------- Inputs for Equation 2 ----------
with col2:
    st.subheader("Equation 2")

    a2 = st.number_input("a₂ (coefficient of x)", value=a2, step=1.0, format="%.4f")
    b2 = st.number_input("b₂ (coefficient of y)", value=b2, step=1.0, format="%.4f")
    c2 = st.number_input("c₂ (right-hand side)", value=c2, step=1.0, format="%.4f")

    st.latex(rf"{a2:.2f}x + {b2:.2f}y = {c2:.2f}")


# ---------- Solve system ----------
eps = 1e-9
det = a1 * b2 - a2 * b1

has_unique = abs(det) > eps
x_sol, y_sol = None, None

if has_unique:
    x_sol = (c1 * b2 - c2 * b1) / det
    y_sol = (a1 * c2 - a2 * c1) / det
    st.success(
        f"**Solution (intersection point)**  \n"
        f"x ≈ `{x_sol:.4f}`, y ≈ `{y_sol:.4f}`"
    )
else:
    st.warning(
        "No **unique** solution: the lines are parallel or coincide "
        "(no intersection or infinitely many solutions)."
    )

# ---------- Build plot ----------
# choose x-range
x_min, x_max = -10.0, 10.0
if has_unique and np.isfinite(x_sol):
    margin = 5.0
    x_min = min(x_min, x_sol - margin)
    x_max = max(x_max, x_sol + margin)

x_vals = np.linspace(x_min, x_max, 400)

def line_points(a, b, c):
    """Return x and y arrays for the line a x + b y = c."""
    if abs(b) > eps:
        y_vals = (c - a * x_vals) / b
        return x_vals, y_vals, False, None
    elif abs(a) > eps:
        # vertical line x = c / a
        x_vert = c / a
        y_vals = np.linspace(-10, 10, 400)
        x_arr = np.full_like(y_vals, x_vert)
        return x_arr, y_vals, True, x_vert
    else:
        # degenerate
        return np.array([]), np.array([]), False, None

x1, y1, vertical1, _ = line_points(a1, b1, c1)
x2, y2, vertical2, _ = line_points(a2, b2, c2)

fig = go.Figure()

if x1.size > 0:
    fig.add_trace(
        go.Scatter(
            x=x1,
            y=y1,
            mode="lines",
            name="Equation 1",
        )
    )

if x2.size > 0:
    fig.add_trace(
        go.Scatter(
            x=x2,
            y=y2,
            mode="lines",
            name="Equation 2",
        )
    )

if has_unique and x_sol is not None and y_sol is not None and np.isfinite(x_sol) and np.isfinite(y_sol):
    fig.add_trace(
        go.Scatter(
            x=[x_sol],
            y=[y_sol],
            mode="markers",
            name="Intersection",
            marker=dict(size=10),
        )
    )

fig.update_layout(
    title="Graph of the Two Equations",
    xaxis_title="x",
    yaxis_title="y",
    legend=dict(x=0.02, y=0.98),
    height=500,
)

st.plotly_chart(fig, use_container_width=True)
