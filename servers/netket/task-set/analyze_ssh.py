#!/usr/bin/env python3
"""
Analysis of the SSH model edge states and full spectrum.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from mcp_server import (
    create_quantum_system, set_lattice, set_hilbert_space,
    set_hamiltonian, compute_energy_spectrum, json_manager
)

def analyze_ssh_model():
    print("Analyzing SSH Model Edge States and Spectrum")
    print("=" * 45)
    
    # Create the main analysis system
    sys_id = create_quantum_system("SSH Model Analysis")['system_id']
    
    # SSH model parameters
    L = 24  # Number of sites
    t1 = 1.0  # Strong hopping
    t2 = 0.2  # Weak hopping (topological phase)
    
    # Set up the system for a SINGLE SPINLESS fermion
    set_lattice(sys_id, f"chain of {L} sites")
    set_hilbert_space(sys_id, "1 spinless fermion")  # Correctly specify spinless
    set_hamiltonian(sys_id, f"SSH model with t1={t1}, t2={t2}")
    
    # Compute full spectrum (ensure we get all eigenvalues for a small system)
    spectrum = compute_energy_spectrum(sys_id, num_eigenvalues=L)
    
    # Retrieve full results from the json_manager to get eigenvectors
    system = json_manager.systems[sys_id]
    eigvals = np.array(system.results["energy_spectrum"]["eigenvalues"])
    eigvecs = np.array(system.results["energy_spectrum"]["eigenvectors"])

    # Plot full spectrum
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(eigvals)), eigvals, 'o-', markersize=6, linewidth=2)
    plt.xlabel("Eigenvalue index", fontsize=12)
    plt.ylabel("Energy", fontsize=12)
    plt.title(f"SSH Model Full Spectrum (t1={t1}, t2={t2})", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='Zero Energy')
    plt.legend()
    plt.tight_layout()
    
    # Save full spectrum plot using the json_manager's path
    system_dir = json_manager.storage_dir / sys_id
    system_dir.mkdir(exist_ok=True)
    spectrum_plot_path = system_dir / "ssh_full_spectrum.png"
    plt.savefig(spectrum_plot_path, dpi=150)
    plt.close()
    print(f"Saved: {spectrum_plot_path}")
    
    # Find and analyze the zero-energy mode, not the ground state
    zero_mode_idx = np.argmin(np.abs(eigvals))
    psi_zero_mode = eigvecs[:, zero_mode_idx]
    spatial_profile = np.abs(psi_zero_mode)**2
    
    # Plot edge state profile
    plt.figure(figsize=(10, 5))
    plt.plot(range(len(spatial_profile)), spatial_profile, 'o-', markersize=4, linewidth=2)
    plt.xlabel("Site index", fontsize=12)
    plt.ylabel("|ψ(i)|²", fontsize=12)
    plt.title(f"SSH Model Edge State Profile (t1={t1}, t2={t2})", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save edge state plot using the json_manager's path
    edge_plot_path = system_dir / "ssh_edge_state_profile.png"
    plt.savefig(edge_plot_path, dpi=150)
    plt.close()
    print(f"Saved: {edge_plot_path} (zero mode, spinless)")

if __name__ == "__main__":
    analyze_ssh_model() 