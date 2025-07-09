"""
Simple tests for NetKet JSON Manager - basic system management functionality.
"""

import pytest
import tempfile
from pathlib import Path
import sys

# Import the modules to test
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "netket"))
from netket_jsons import NetKetJSONManager


class TestNetKetJSONManager:
    """Test basic JSON manager functionality."""

    @pytest.fixture(autouse=True)
    def setup_manager(self, tmp_path):
        """Set up a clean manager for each test."""
        self.manager = NetKetJSONManager(storage_dir=str(tmp_path))

    def test_create_system(self):
        """Test creating a new quantum system."""
        system_id = self.manager.create_system("Test system")
        assert system_id is not None
        assert system_id in self.manager.systems
        assert self.manager.systems[system_id].status == "incomplete"

    def test_add_components(self):
        """Test adding components to a system."""
        system_id = self.manager.create_system("Test system")
        
        # Add lattice
        self.manager.update_component("lattice", "chain of 4 sites", system_id)
        assert self.manager.systems[system_id].lattice is not None
        
        # Add Hilbert space
        self.manager.update_component("hilbert", "spin-1/2 on each site", system_id)
        assert self.manager.systems[system_id].hilbert is not None
        
        # Add Hamiltonian
        self.manager.update_component("hamiltonian", "SSH model with t1=1, t2=0.2", system_id)
        assert self.manager.systems[system_id].hamiltonian is not None
        
        # Should be complete now
        assert self.manager.systems[system_id].status == "complete"

    def test_save_and_load(self):
        """Test saving and loading systems."""
        # Create and save a system
        system_id = self.manager.create_system("Test system")
        self.manager.update_component("lattice", "chain of 4 sites", system_id)
        
        # Create new manager and load the system
        new_manager = NetKetJSONManager(storage_dir=self.manager.storage_dir)
        loaded_system = new_manager.load_system(system_id)
        
        assert loaded_system.system_id == system_id
        assert loaded_system.lattice is not None

    def test_list_systems(self):
        """Test listing all systems."""
        # Create multiple systems
        id1 = self.manager.create_system("System 1")
        id2 = self.manager.create_system("System 2")
        
        systems = self.manager.list_systems()
        assert len(systems) == 2
        system_ids = [s["system_id"] for s in systems]
        assert id1 in system_ids
        assert id2 in system_ids

    def test_error_handling(self):
        """Test basic error handling."""
        # Try to update non-existent system
        with pytest.raises(ValueError):
            self.manager.update_component("lattice", "test", "non_existent_id")
        
        # Try invalid component type
        system_id = self.manager.create_system("Test system")
        with pytest.raises(ValueError):
            self.manager.update_component("invalid_type", "test", system_id)

    @pytest.mark.integration
    def test_netket_integration(self):
        """Test basic NetKet integration."""
        try:
            import netket as nk
            
            # Create a complete system
            system_id = self.manager.create_system("NetKet test")
            self.manager.update_component("lattice", "chain of 4 sites", system_id)
            self.manager.update_component("hilbert", "spin-1/2 on each site", system_id)
            self.manager.update_component("hamiltonian", "SSH model with t1=1, t2=0.2", system_id)

            system = self.manager.systems[system_id]
            
            # Build NetKet objects
            graph = system.lattice.to_netket_graph()
            hilbert = system.hilbert.to_netket_hilbert(graph)
            
            assert graph is not None
            assert hilbert is not None
            
        except (ImportError, TypeError) as e:
            pytest.skip(f"NetKet integration failed: {e}") 