# epidemicsio

Epidemics.io, a web app simulating the spread of disease with agent-based models built on [Mesa](https://mesa.readthedocs.io/).

Two models are included:

- **Traditional (Grid)** ([MoneyModel.py](MoneyModel.py)) — agents move on a grid, spreading infection on contact, with configurable age/genetic/lifestyle risk factors, a death risk after a sustained infection, and a fixed recovery/infectious zone.
- **Network** ([NetworkModel.py](NetworkModel.py)) — agents sit on a generated graph (Barabasi-Albert, Watts-Strogatz, Erdos-Renyi, or Power-Law Cluster), with the same risk factors plus vaccination.

## Setup

```
pipenv install
```

## Running

**Streamlit app** (both models, switchable from the sidebar — this is the one to deploy):

```
pipenv run streamlit run streamlit_app.py
```

**Solara apps** (one process per model, richer interactive controls):

```
pipenv run solara run main.py         # Traditional (Grid)
pipenv run solara run NetworkMain.py  # Network
```
