import streamlit as st
import pulp as pl
import pandas as pd


def build_model(var_names, obj_coeffs, constraints, sense, nonneg):
    """Build and solve a linear program using PuLP."""
    # Choose max or min
    sense_flag = pl.LpMaximize if sense == "Maximize" else pl.LpMinimize
    model = pl.LpProblem("User_Defined_LP", sense_flag)

    # Decision variables
    variables = {}
    for name in var_names:
        lb = 0 if nonneg else None  # non-negativity if checked
        variables[name] = pl.LpVariable(name, lowBound=lb)

    # Objective function: sum(c_i * x_i)
    model += pl.lpSum(
        coeff * variables[name] for coeff, name in zip(obj_coeffs, var_names)
    ), "Objective"

    # Constraints
    for idx, (row_coeffs, relation, rhs) in enumerate(constraints, start=1):
        expr = pl.lpSum(
            coeff * variables[name] for coeff, name in zip(row_coeffs, var_names)
        )
        cname = f"constr_{idx}"
        if relation == "<=":
            model += expr <= rhs, cname
        elif relation == ">=":
            model += expr >= rhs, cname
        else:
            model += expr == rhs, cname

    # Solve
    model.solve()
    return model, variables


def main():
    st.set_page_config(
        page_title="Linear Programming Solver",
        layout="wide",
    )

    st.title("Linear Programming Solver")
    st.caption("Define an LP by coefficients, and solve it using PuLP + CBC.")

    # Sidebar: high-level setup
    st.sidebar.header("Model setup")

    num_vars = st.sidebar.number_input(
        "Number of decision variables",
        min_value=1,
        max_value=10,
        value=2,
        step=1,
    )

    num_constraints = st.sidebar.number_input(
        "Number of constraints",
        min_value=0,
        max_value=30,
        value=2,
        step=1,
    )

    sense = st.sidebar.selectbox(
        "Objective sense",
        options=["Maximize", "Minimize"],
        index=0,
    )

    nonneg = st.sidebar.checkbox("All variables ≥ 0", value=True)

    st.markdown("### 1️⃣ Decision variables")

    # Variable names
    var_cols = st.columns(num_vars)
    var_names = []
    for i in range(num_vars):
        with var_cols[i]:
            name = st.text_input(
                f"Name of variable {i + 1}",
                value=f"x{i + 1}",
                key=f"var_name_{i}",
            )
        var_names.append(name if name.strip() else f"x{i + 1}")

    st.markdown("---")
    st.markdown("### 2️⃣ Objective function")

    st.write("Enter the coefficient of each variable in the objective:")
    obj_cols = st.columns(num_vars)
    obj_coeffs = []
    for i, name in enumerate(var_names):
        with obj_cols[i]:
            coeff = st.number_input(
                f"Coeff of {name}",
                value=0.0,
                key=f"obj_coeff_{i}",
            )
        obj_coeffs.append(coeff)

    st.info(
        f"Objective: {sense}  "
        + " + ".join(f"{obj_coeffs[i]}·{var_names[i]}" for i in range(num_vars))
    )

    st.markdown("---")
    st.markdown("### 3️⃣ Constraints")

    constraints = []

    if num_constraints > 0:
        for j in range(num_constraints):
            st.markdown(f"**Constraint {j + 1}**")
            # coefficients for each variable + relation + RHS
            row = st.columns(num_vars + 2)

            row_coeffs = []
            for i, name in enumerate(var_names):
                with row[i]:
                    c = st.number_input(
                        f"Coeff of {name}",
                        value=0.0,
                        key=f"con_{j}_var_{i}",
                    )
                row_coeffs.append(c)

            with row[-2]:
                relation = st.selectbox(
                    "Relation",
                    options=["<=", ">=", "="],
                    key=f"rel_{j}",
                )

            with row[-1]:
                rhs = st.number_input(
                    "RHS",
                    value=0.0,
                    key=f"rhs_{j}",
                )

            constraints.append((row_coeffs, relation, rhs))

            # Show constraint in human-readable form
            st.caption(
                "Constraint: "
                + " + ".join(f"{row_coeffs[i]}·{var_names[i]}" for i in range(num_vars))
                + f" {relation} {rhs}"
            )
            st.markdown("---")

    # Solve button
    if st.button("Solve model"):
        try:
            model, variables = build_model(
                var_names=var_names,
                obj_coeffs=obj_coeffs,
                constraints=constraints,
                sense=sense,
                nonneg=nonneg,
            )

            st.markdown("### 4️⃣ Results")

            status = pl.LpStatus[model.status]
            st.write("**Status:**", status)

            if status == "Optimal":
                # Variable values
                sol = {name: var.value() for name, var in variables.items()}
                df = pd.DataFrame.from_dict(sol, orient="index", columns=["Value"])
                df.index.name = "Variable"

                st.subheader("Decision variable values")
                st.table(df)

                st.subheader("Objective value")
                st.write(pl.value(model.objective))

            else:
                st.warning(
                    "Model status is not 'Optimal'. "
                    "Check your formulation and constraints."
                )

        except Exception as e:
            st.error(f"An error occurred while solving the model:\n\n{e}")


if __name__ == "__main__":
    main()
