#!/usr/bin/env python3
"""
Analysis of the Hubbard model metal-insulator transition (Mott gap).
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from mcp_server import create_quantum_system, set_lattice, set_hilbert_space, set_hamiltonian, compute_energy_spectrum
from mcp_server import json_manager

def analyze_hubbard_transition():
    print("Analyzing Hubbard Model Metal-Insulator Transition (Mott gap)")
    print("=" * 50)
    L = 10
    t = 1.0
    U_values = np.linspace(0, 8, 17)
    N = L  # half-filling for spin-1/2 fermions
    gs_energies = []
    gap_mott = []
    
    # Create a single system for the entire analysis
    sys_id = create_quantum_system("Hubbard Mott Gap Analysis")['system_id']
    set_lattice(sys_id, f"chain of {L} sites")
    
    for U in U_values:
        # Update system for N particles
        set_hilbert_space(sys_id, f"{N} fermions with spin-1/2")
        set_hamiltonian(sys_id, f"Hubbard model with t={t}, U={U}")
        e0_N = compute_energy_spectrum(sys_id, num_eigenvalues=1)["ground_state_energy"]
        
        # Update system for N+1 particles
        set_hilbert_space(sys_id, f"{N+1} fermions with spin-1/2")
        set_hamiltonian(sys_id, f"Hubbard model with t={t}, U={U}")
        e0_Np1 = compute_energy_spectrum(sys_id, num_eigenvalues=1)["ground_state_energy"]
        
        # Update system for N-1 particles
        set_hilbert_space(sys_id, f"{N-1} fermions with spin-1/2")
        set_hamiltonian(sys_id, f"Hubbard model with t={t}, U={U}")
        e0_Nm1 = compute_energy_spectrum(sys_id, num_eigenvalues=1)["ground_state_energy"]
        
        gs_energies.append(e0_N)
        gap_mott.append(e0_Np1 + e0_Nm1 - 2 * e0_N)
        print(f"U={U:.2f}: E0(N)={e0_N:.3f}, gap={gap_mott[-1]:.3f}")
    
    # Plot only the Mott gap
    plt.figure(figsize=(7, 5))
    plt.plot(U_values, gap_mott, 'o-', color='red')
    plt.xlabel('U')
    plt.ylabel('Mott Gap')
    plt.title('Hubbard Model: Mott Gap vs. U')
    plt.grid(True)
    plt.tight_layout()
    
    # Save plot in the system directory using the json_manager's path
    system_dir = json_manager.storage_dir / sys_id
    system_dir.mkdir(exist_ok=True)
    plot_path = system_dir / "hubbard_phase_transition.png"
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"Plot saved to: {plot_path}")
    print("\n✅ Hubbard Mott gap analysis complete!")

if __name__ == "__main__":
    analyze_hubbard_transition() 