import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from netket_schemas import LatticeSchema, HilbertSpaceSchema, HamiltonianSchema

class QuantumSystemState:
    def __init__(self, system_id: Optional[str] = None):
        self.system_id = system_id or f"system_{uuid.uuid4().hex[:8]}"
        self.created_at = datetime.now().isoformat()
        self.last_modified = self.created_at
        self.status = "incomplete"
        self.warnings = []
        self.history = []
        self.lattice: Optional[LatticeSchema] = None
        self.hilbert: Optional[HilbertSpaceSchema] = None
        self.hamiltonian: Optional[HamiltonianSchema] = None
        self.results: Dict[str, Any] = {}

    def to_dict(self):
        return {
            "system_id": self.system_id,
            "created_at": self.created_at,
            "last_modified": self.last_modified,
            "status": self.status,
            "warnings": self.warnings,
            "history": self.history,
            "lattice": self.lattice.model_dump() if self.lattice else None,
            "hilbert": self.hilbert.model_dump() if self.hilbert else None,
            "hamiltonian": self.hamiltonian.model_dump() if self.hamiltonian else None,
            "results": self.results,
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(system_id=data.get("system_id"))
        obj.created_at = data.get("created_at", obj.created_at)
        obj.last_modified = data.get("last_modified", obj.last_modified)
        obj.status = data.get("status", "incomplete")
        obj.warnings = data.get("warnings", [])
        obj.history = data.get("history", [])
        if data.get("lattice"):
            obj.lattice = LatticeSchema(**data["lattice"])
        if data.get("hilbert"):
            obj.hilbert = HilbertSpaceSchema(**data["hilbert"])
        if data.get("hamiltonian"):
            obj.hamiltonian = HamiltonianSchema(**data["hamiltonian"])
        obj.results = data.get("results", {})
        return obj

class NetKetJSONManager:
    def __init__(self, storage_dir: str = "/tmp/quantum_systems"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.systems: Dict[str, QuantumSystemState] = {}
        self.current_system_id: Optional[str] = None
        self._load_existing_systems()

    def _get_system_dir(self, system_id: str) -> Path:
        system_dir = self.storage_dir / system_id
        system_dir.mkdir(exist_ok=True)
        return system_dir

    def _system_file(self, system_id: str) -> Path:
        return self._get_system_dir(system_id) / f"{system_id}.json"

    def create_system(self, description: Optional[str] = None) -> str:
        system = QuantumSystemState()
        if description:
            # Optionally parse description to fill in components
            pass
        
        # Create the directory for the new system
        self._get_system_dir(system.system_id)
        
        self.systems[system.system_id] = system
        self.current_system_id = system.system_id
        self.save_system(system.system_id)
        return system.system_id

    def update_component(self, component_type: str, specification: Any, system_id: Optional[str] = None):
        system_id = system_id or self.current_system_id
        if not system_id or system_id not in self.systems:
            raise ValueError("No such system to update.")
        system = self.systems[system_id]
        
        if component_type == "lattice":
            system.lattice = LatticeSchema(text=specification) if isinstance(specification, str) else LatticeSchema(**specification)
            action = "set_lattice"
        elif component_type == "hilbert":
            system.hilbert = HilbertSpaceSchema(text=specification) if isinstance(specification, str) else HilbertSpaceSchema(**specification)
            action = "set_hilbert"
        elif component_type == "hamiltonian":
            system.hamiltonian = HamiltonianSchema(text=specification) if isinstance(specification, str) else HamiltonianSchema(**specification)
            action = "set_hamiltonian"
        else:
            raise ValueError(f"Unknown component type: {component_type}")
        
        system.last_modified = datetime.now().isoformat()
        system.history.append({
            "timestamp": system.last_modified,
            "action": action,
            "data": specification
        })
        self._validate_system(system)
        self.save_system(system_id)

    def save_system(self, system_id: Optional[str] = None):
        system_id = system_id or self.current_system_id
        if not system_id or system_id not in self.systems:
            raise ValueError("No such system to save.")
        system = self.systems[system_id]
        
        # Ensure the directory exists
        self._get_system_dir(system_id)
        
        file_path = self._system_file(system_id)
        with open(file_path, 'w') as f:
            json.dump(system.to_dict(), f, indent=2)

    def load_system(self, system_id: str):
        file_path = self._system_file(system_id)
        if not file_path.exists():
            raise FileNotFoundError(f"System file {file_path} does not exist.")
        with open(file_path, 'r') as f:
            data = json.load(f)
        system = QuantumSystemState.from_dict(data)
        self.systems[system_id] = system
        self.current_system_id = system_id
        return system

    def list_systems(self):
        return [
            {
                "system_id": sys_id,
                "status": sys.status,
                "last_modified": sys.last_modified,
                "lattice": sys.lattice.text if sys.lattice else None,
                "hilbert": sys.hilbert.text if sys.hilbert else None,
                "hamiltonian": sys.hamiltonian.text if sys.hamiltonian else None
            }
            for sys_id, sys in self.systems.items()
        ]

    def _load_existing_systems(self):
        for file_path in self.storage_dir.glob("system_*/system_*.json"):
            with open(file_path, 'r') as f:
                data = json.load(f)
            system = QuantumSystemState.from_dict(data)
            self.systems[system.system_id] = system

    def _validate_system(self, system: QuantumSystemState):
        warnings = []
        
        # Check for Hilbert space compatibility with lattice
        if system.lattice and system.hilbert:
            try:
                # Get total lattice sites
                if hasattr(system.lattice, 'extent') and system.lattice.extent:
                    total_sites = 1
                    for x in system.lattice.extent:
                        total_sites *= x
                    
                    # Check if number of particles exceeds sites for fermions
                    if (system.hilbert.space_type == "fermion" and 
                        system.hilbert.n_particles is not None and 
                        system.hilbert.n_particles > total_sites):
                        warnings.append(f"Invalid: {system.hilbert.n_particles} fermions cannot fit on {total_sites} sites")
                    
                    # Check if number of particles equals sites (half filling)
                    elif (system.hilbert.space_type == "fermion" and 
                          system.hilbert.n_particles == total_sites):
                        warnings.append(f"Note: System at maximum filling ({total_sites} fermions on {total_sites} sites)")
                    
            except Exception as e:
                warnings.append(f"Validation error: {str(e)}")
        
        # Update status
        if system.lattice and system.hilbert and system.hamiltonian:
            system.status = "complete"
        elif system.lattice or system.hilbert or system.hamiltonian:
            system.status = "partial"
        else:
            system.status = "empty"
        
        system.warnings = warnings 