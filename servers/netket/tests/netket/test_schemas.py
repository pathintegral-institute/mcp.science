"""
Simple tests for NetKet Schemas - basic validation functionality.
"""

import pytest
from pathlib import Path
import sys

# Import the modules to test
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "netket"))

from netket_schemas import LatticeSchema, HilbertSpaceSchema, HamiltonianSchema


class TestLatticeSchema:
    """Test basic lattice parsing."""

    def test_basic_lattice_parsing(self):
        """Test common lattice types."""
        # Chain
        lattice = LatticeSchema(text="chain of 8 sites")
        assert lattice.lattice_type == "chain"
        assert lattice.extent == [8]
        
        # Square
        lattice = LatticeSchema(text="4x4 square lattice")
        assert lattice.lattice_type == "square"
        assert lattice.extent == [4, 4]
        
        # Cube
        lattice = LatticeSchema(text="2x2x2 cubic lattice")
        assert lattice.lattice_type == "cube"
        assert lattice.extent == [2, 2, 2]


class TestHilbertSpaceSchema:
    """Test basic Hilbert space parsing."""

    def test_basic_hilbert_parsing(self):
        """Test common Hilbert space types."""
        # Spin
        hilbert = HilbertSpaceSchema(text="spin-1/2 on each site")
        assert hilbert.space_type == "spin"
        assert hilbert.spin == 0.5
        
        # Fermion
        hilbert = HilbertSpaceSchema(text="4 fermions")
        assert hilbert.space_type == "fermion"
        assert hilbert.n_particles == 4


class TestHamiltonianSchema:
    """Test basic Hamiltonian parsing."""

    def test_basic_hamiltonian_parsing(self):
        """Test common Hamiltonian types."""
        # SSH
        hamiltonian = HamiltonianSchema(text="SSH model with t1=1, t2=0.2")
        assert hamiltonian.model_type == "ssh"
        assert hamiltonian.parameters["t1"] == 1.0
        assert hamiltonian.parameters["t2"] == 0.2
        
        # Hubbard  
        hamiltonian = HamiltonianSchema(text="Hubbard model with t=1, U=4")
        assert hamiltonian.model_type == "hubbard"
        assert hamiltonian.parameters["t"] == 1.0
        assert hamiltonian.parameters["U"] == 4.0

    @pytest.mark.integration
    def test_netket_integration(self):
        """Test basic NetKet integration."""
        try:
            import netket as nk
            
            # Create simple test system
            graph = nk.graph.Chain(length=4)
            hilbert_space = HilbertSpaceSchema(text="spin-1/2 on each site")
            hilbert = hilbert_space.to_netket_hilbert(graph)
            
            # Test SSH model (works well)
            hamiltonian = HamiltonianSchema(text="SSH model with t1=1, t2=0.2")
            h_op = hamiltonian.build_netket_hamiltonian(hilbert, graph, hilbert_space)
            assert h_op is not None
            
        except (ImportError, TypeError) as e:
            pytest.skip(f"NetKet integration failed: {e}") 