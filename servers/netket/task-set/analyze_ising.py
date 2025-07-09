#!/usr/bin/env python3
"""
Analysis of the Ising model quantum phase transition (energy gap and degeneracy).
This script uses the `parameter_sweep` tool to efficiently analyze the system.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from mcp_server import create_quantum_system, set_lattice, set_hilbert_space, set_hamiltonian, parameter_sweep
from mcp_server import json_manager

def analyze_ising_transition():
    print("Analyzing Ising Model Quantum Phase Transition (Energy Gap and Degeneracy)")
    print("=" * 60)
    L = 16
    Jz = 1.0
    hx_values = np.linspace(0, 2, 21).tolist()
    
    # 1. Set up the quantum system
    sys_id = create_quantum_system("Ising Phase Transition Analysis")['system_id']
    set_lattice(sys_id, f"chain of {L} sites")
    set_hilbert_space(sys_id, "spin-1/2 on each site")
    # Set Hamiltonian with a base hx value and a parameter range for the sweep
    set_hamiltonian(
        sys_id, 
        f"Ising model with Jz={Jz}, hx=0.0",
        parameter_ranges={"hx": hx_values}
    )

    # 2. Perform the parameter sweep
    print("Performing parameter sweep over 'hx'...")
    sweep_results = parameter_sweep(sys_id, "hx")
    gaps = sweep_results["energy_gaps"]
    all_eigenvalues = sweep_results["all_eigenvalues"]
    
    # 3. Calculate degeneracy from the sweep results
    degeneracies = []
    for eigvals in all_eigenvalues:
        E0 = eigvals[0]
        degeneracy = sum(1 for e in eigvals if np.isclose(e, E0, atol=1e-6))
        degeneracies.append(degeneracy)
        
    print("Parameter sweep complete.")

    # 4. Create dual-axis plot
    fig, ax1 = plt.subplots(figsize=(8, 6))
    ax2 = ax1.twinx()
    
    # Plot energy gap on primary axis
    line1 = ax1.plot(hx_values, gaps, 'o-', color='blue', label='Energy Gap')
    ax1.set_xlabel('hx (Transverse Field)', fontsize=12)
    ax1.set_ylabel('Energy Gap', color='blue', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True, alpha=0.3)
    
    # Plot degeneracy on secondary axis
    line2 = ax2.plot(hx_values, degeneracies, 's-', color='red', label='Ground State Degeneracy')
    ax2.set_ylabel('Degeneracy', color='red', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.set_ylim(0, 3)
    ax2.set_yticks([0, 1, 2, 3])
    
    # Add legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')
    
    plt.title('Ising Model: Energy Gap and Degeneracy vs. Transverse Field', fontsize=14)
    plt.tight_layout()
    
    # Save plot in the system directory using the json_manager's path
    system_dir = json_manager.storage_dir / sys_id
    system_dir.mkdir(exist_ok=True)
    plot_path = system_dir / "ising_phase_transition_correct_gap.png"
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"\nPlot saved to: {plot_path}")
    print("\n✅ Ising gap and degeneracy analysis complete!")

if __name__ == "__main__":
    analyze_ising_transition() 