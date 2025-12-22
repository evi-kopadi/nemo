# NEMO Brain Simulation Library

## Overview

`brain.py` is a Python library that implements the NEMO (Neural Model) computational brain model. It provides classes and functions for simulating neural assemblies, brain areas, and various network architectures inspired by biological neural systems.

The library is based on research by Christos Papadimitriou, Santosh Vempala, Max Dabagia, and Dan Mitropolsky, exploring how complex cognition can arise from neuronal activity.

## Core Concepts

### Assemblies of Neurons
The fundamental unit of computation in NEMO is the **assembly** - a set of neurons that fire together. When neurons fire together repeatedly, their synaptic connections strengthen through Hebbian plasticity, forming stable patterns of activity.

### Brain Areas
Brain areas are collections of neurons with specific connectivity patterns. Different types of areas implement different computational primitives.

## Dependencies

```python
import numpy as np
```

The library uses NumPy for efficient numerical computations.

## Utility Functions

### `k_cap(input, cap_size)`
Implements k-winners-take-all activation. Returns the indices of the top `cap_size` neurons based on their input values.

**Parameters:**
- `input`: Array of neuron activation values
- `cap_size`: Number of top neurons to select

**Returns:**
- Array of indices of the top-k neurons, or empty array if all inputs are zero

**Example:**
```python
activations = np.array([0.1, 0.5, 0.3, 0.8, 0.2])
winners = k_cap(activations, cap_size=2)  # Returns indices [3, 1] (neurons with values 0.8 and 0.5)
```

### `idx_to_vec(idx, shape)`
Converts indices to a one-hot encoded vector representation.

**Parameters:**
- `idx`: Array of neuron indices
- `shape`: Total number of neurons

**Returns:**
- Dense binary vector with 1s at specified indices

## Classes

### FFArea (Feed-Forward Area)

The base class for a brain area with feed-forward connectivity.

**Constructor Parameters:**
- `n_inputs`: Number of input neurons (int) or list of input sizes for multiple input areas
- `n_neurons`: Number of neurons in this area
- `cap_size`: Number of neurons that fire (k in k-winners-take-all)
- `density`: Probability of synaptic connection between neurons (0 to 1)
- `plasticity`: Hebbian plasticity rate (weight increase factor)
- `norm_init`: Whether to normalize weights during initialization (default: False)

**Key Methods:**

- `reset()`: Reinitialize the area's synaptic weights randomly
- `inhibit()`: Clear all activations and inputs
- `fire(activations, update=True)`: Directly set which neurons are firing
- `set_input(inputs, input_area=0)`: Set input to the area
- `clear_input(input_area=-1)`: Clear inputs
- `step(update=True)`: Execute one timestep: compute activations, apply k-winners-take-all, optionally update weights
- `forward(inputs, input_area=0, update=True)`: Convenience method combining set_input, step, and clear_input
- `update(new_activations)`: Apply Hebbian plasticity to strengthen connections
- `normalize()`: Normalize synaptic weights
- `read(dense=False)`: Get current activations (as indices or dense vector)
- `set_input_weights(pre_idx, post_idx, w, area=0)`: Manually set weights between specific neurons

**Example:**
```python
# Create a simple feed-forward area
area = FFArea(n_inputs=100, n_neurons=1000, cap_size=50, density=0.05, plasticity=0.1)

# Present input and let neurons fire
input_neurons = np.array([0, 5, 10, 15, 20])
area.forward(input_neurons)

# Get which neurons fired
active_neurons = area.read()
```

### RecurrentArea

Extends FFArea with recurrent (self) connections, allowing the area to maintain and process temporal patterns.

**Additional Features:**
- `recurrent_weights`: Weight matrix for connections within the area
- Recurrent connections are also updated via Hebbian plasticity
- Total input includes both external input and recurrent feedback

**Key Methods (in addition to FFArea):**
- `set_recurrent_weights(pre_idx, post_idx, w)`: Manually set recurrent weights

**Example:**
```python
# Area with recurrent connections for temporal sequences
recurrent_area = RecurrentArea(n_inputs=100, n_neurons=1000, cap_size=50, 
                               density=0.05, plasticity=0.1)

# Present a sequence of inputs
for input_pattern in sequence:
    recurrent_area.forward(input_pattern)
```

### RefractedArea

Extends FFArea with a bias term that increases when neurons fire, implementing a form of refractoriness or adaptation.

**Key Features:**
- Neurons that fire frequently develop negative bias, reducing their likelihood of firing again
- Useful for ensuring diversity in representations

**Example:**
```python
# Area that discourages repeated firing of the same neurons
refracted_area = RefractedArea(n_inputs=100, n_neurons=1000, cap_size=50,
                               density=0.05, plasticity=0.1)
```

### RandomChoiceArea

A specialized recurrent area that can be trained on specific assemblies and then randomly select between them.

**Constructor Parameters:**
- `n_neurons`: Number of neurons
- `cap_size`: Size of assemblies
- `density`: Connection density
- `plasticity`: Fixed at 3.0 internally
- `norm_init`: Whether to normalize (default: False)

**Key Methods:**
- `train(assemblies)`: Train on a list of assemblies (each represented as neuron indices)
- `flip(n_rounds=10)`: Randomly select one of the trained assemblies

**Example:**
```python
# Create random choice area and train on two assemblies
choice_area = RandomChoiceArea(n_neurons=1000, cap_size=50, density=0.05, plasticity=0.1)
assemblies = [np.arange(50), np.arange(50, 100)]  # Two assemblies
choice_area.train(assemblies)

# Randomly select one assembly
chosen = choice_area.flip()
```

### ScaffoldNetwork

A two-area recurrent network where areas mutually excite each other, useful for sequence learning and generation.

**Constructor Parameters:**
- `n_inputs`: Number of input neurons
- `n_neurons`: Number of neurons in each of the two areas
- `cap_size`: k for k-winners-take-all
- `density`: Connection density
- `plasticity`: Hebbian plasticity rate
- `norm_init`: Whether to normalize weights

**Architecture:**
- Area 0: Receives external input and feedback from Area 1
- Area 1: Receives feedback from Area 0
- Both areas are recurrent

**Key Methods:**
- `reset()`: Reset both areas
- `inhibit()`: Inhibit both areas
- `set_input(inputs)`: Set input to Area 0
- `step(update=True)`: Execute one timestep with bidirectional feedback
- `forward(inputs, update=True)`: Present input and execute one step
- `normalize()`: Normalize all weights
- `read(dense=False)`: Read output from Area 0

**Example:**
```python
# Create scaffold network for sequence learning
scaffold = ScaffoldNetwork(n_inputs=100, n_neurons=1000, cap_size=50,
                          density=0.05, plasticity=0.1)

# Learn a sequence
for item in sequence:
    scaffold.forward(item)
```

### FSMNetwork (Finite State Machine Network)

Implements a learnable finite state machine using two brain areas: one for states and one for state transitions (arcs).

**Constructor Parameters:**
- `n_symbol_neurons`: Number of neurons for input symbols
- `n_state_neurons`: Number of neurons for states
- `n_arc_neurons`: Number of neurons for state transitions
- `cap_size`: k for k-winners-take-all
- `density`: Connection density
- `plasticity`: Hebbian plasticity rate
- `norm_init`: Whether to normalize weights

**Architecture:**
- `state_area`: FFArea that represents current state
- `arc_area`: RefractedArea that computes state transitions based on current symbol and state

**Key Methods:**
- `reset()`: Reset both areas
- `inhibit()`: Inhibit both areas
- `forward(inputs, update=True)`: Process one symbol and transition to next state
- `read(dense=False)`: Read current state
- `train(symbol, state, new_state)`: Teach a specific transition: symbol + state → new_state

**Example:**
```python
# Create FSM that recognizes patterns
fsm = FSMNetwork(n_symbol_neurons=100, n_state_neurons=500, n_arc_neurons=1000,
                cap_size=50, density=0.05, plasticity=0.1)

# Train FSM on transitions
fsm.train(symbol_a, state_0, state_1)  # a: state_0 → state_1
fsm.train(symbol_b, state_1, state_2)  # b: state_1 → state_2

# Process symbols
fsm.forward(symbol_a)
current_state = fsm.read()
```

### PFANetwork (Probabilistic Finite Automaton Network)

A network that can generate stochastic sequences by incorporating randomness into state transitions.

**Constructor Parameters:**
- `n_symbol_neurons`: Neurons for output symbols
- `n_state_neurons`: Neurons for states
- `n_arc_neurons`: Neurons for transitions
- `n_random_neurons`: Neurons for randomness source
- `cap_size`: k for k-winners-take-all
- `density`: Connection density
- `plasticity`: Hebbian plasticity rate
- `norm_init`: Whether to normalize weights

**Architecture:**
- `symbol_area`: FFArea for output symbols
- `state_area`: FFArea for states
- `arc_area`: RefractedArea for transitions (takes state + random as input)
- `random_area`: RandomChoiceArea that provides stochasticity

**Key Methods:**
- `train(state, rand, new_state, symbol)`: Train a probabilistic transition
- `step()`: Execute one generation step (without updating weights)
- `read(dense=False)`: Read generated symbol

**Example:**
```python
# Create PFA for stochastic sequence generation
pfa = PFANetwork(n_symbol_neurons=100, n_state_neurons=500, n_arc_neurons=1000,
                n_random_neurons=200, cap_size=50, density=0.05, plasticity=0.1)

# Train probabilistic transitions
pfa.train(state_0, 0, state_1, symbol_a)  # With random choice 0
pfa.train(state_0, 1, state_2, symbol_b)  # With random choice 1

# Generate sequence
for _ in range(10):
    pfa.step()
    symbol = pfa.read()
```

### AttentionArea

A specialized recurrent area that implements attention-like mechanisms by tracking weight changes separately.

**Key Features:**
- Maintains `recurrent_change` matrix to track recent weight updates
- Can decay weights back to baseline

**Key Methods (in addition to RecurrentArea):**
- `decay_weights()`: Remove recent weight changes, returning to baseline connectivity
- `update(new_activations)`: Only updates recurrent weights (not input weights), with tracked changes

**Example:**
```python
# Area with attention mechanism
attention = AttentionArea(n_inputs=100, n_neurons=1000, cap_size=50,
                         density=0.05, plasticity=0.1)

# Process sequence with attention
for item in sequence:
    attention.forward(item)

# Later, decay attention
attention.decay_weights()
```

## Key Mechanisms

### Hebbian Plasticity
When neuron i fires at time t and neuron j fires at time t+1, the connection from i to j is strengthened:
```
w_ij ← w_ij × (1 + plasticity)
```

### K-Winners-Take-All
At each timestep, only the k neurons with the highest total input fire. This implements lateral inhibition and ensures sparse activity.

### Random Sparse Connectivity
Initial connections are created randomly with probability `density`, mimicking the sparse connectivity observed in biological neural networks.

## Usage Patterns

### Learning an Assembly
```python
# Create area
area = FFArea(n_inputs=100, n_neurons=1000, cap_size=50, density=0.05, plasticity=0.1)

# Present same input multiple times to form assembly
input_pattern = np.arange(20)  # First 20 neurons
for _ in range(10):
    area.forward(input_pattern)

# The same ~50 neurons will consistently fire in response to this input
```

### Sequence Learning with Recurrence
```python
# Create recurrent area
area = RecurrentArea(n_inputs=100, n_neurons=1000, cap_size=50, density=0.05, plasticity=0.1)

# Present sequence
sequence = [pattern_a, pattern_b, pattern_c]
for pattern in sequence:
    area.forward(pattern)

# Area learns temporal dependencies
```

### Pattern Completion
```python
# Train on full pattern
area = RecurrentArea(n_inputs=100, n_neurons=1000, cap_size=50, density=0.05, plasticity=0.1)
full_pattern = np.arange(50)
for _ in range(10):
    area.forward(full_pattern)

# Present partial pattern
partial_pattern = np.arange(25)  # Only half the pattern
area.forward(partial_pattern, update=False)

# Recurrent connections may complete the pattern
for _ in range(5):
    area.step(update=False)
```

## Biological Inspiration

The model abstracts key features of cortical computation:

1. **Sparse Activity**: Only a small fraction of neurons fire (k-winners-take-all)
2. **Hebbian Learning**: "Neurons that fire together, wire together"
3. **Random Connectivity**: Initial connections are random and sparse
4. **Recurrence**: Feedback connections enable temporal processing
5. **Modularity**: Different brain areas serve different functions

## References

This implementation is based on research including:
- Papadimitriou & Vempala (2019): "Random Projection in the Brain and Computation with Assemblies of Neurons"
- Papadimitriou et al. (2020): "Brain computation by assemblies of neurons" (PNAS)
- Dabagia et al. (2022): "Assemblies of neurons learn to classify well-separated distributions"
- And other papers listed in the documentation website

## See Also

- `nemo.py`: Additional sparse matrix implementations for efficiency
- `docs/`: Detailed documentation and examples
- `nemo-demo.ipynb`: Jupyter notebook with interactive demonstrations
