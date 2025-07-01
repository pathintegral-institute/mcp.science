from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Literal, Any, Optional, Union, Dict, List
import re
import numpy as np

# Import NetKet components
import netket.graph as nkgraph
import netket.hilbert as nkh
import netket.experimental as nkx
import netket.operator as nko
from netket.experimental.operator.fermion import destroy as c
from netket.experimental.operator.fermion import create as cdag

class LatticeSchema(BaseModel):
    """
    Represents a quantum lattice with text-based specification.
    
    Converts text descriptions like "4x4 square lattice" to NetKet graph objects.
    Supports various lattice types: chain, square, triangular, kagome, honeycomb, etc.
    """
    
    lattice_type: str = Field(
        description="Lattice type: 'chain', 'square', 'triangular', 'kagome', 'honeycomb', 'fcc', 'bcc', 'pyrochlore', 'cube', 'hypercube'"
    )
    
    extent: list[int] = Field(
        description="Lattice dimensions, e.g., [4] for 1D chain, [4,4] for 2D square, [2,2,2] for 3D cube"
    )
    
    text: str | None = Field(
        default=None,
        description="Text description like '4x4 square lattice' or 'chain of 8 sites'"
    )
    
    @model_validator(mode='before')
    @classmethod
    def parse_from_text(cls, data: dict) -> dict:
        """Parse text description to populate lattice_type and extent."""
        if 'text' in data and data['text']:
            text = data.pop('text').strip()
            
            # Parse various lattice descriptions
            parsed = cls._parse_lattice_text(text)
            data['lattice_type'] = parsed['lattice_type']
            data['extent'] = parsed['extent']
            
        return data
    
    @classmethod
    def _parse_lattice_text(cls, text: str) -> dict:
        """Parse lattice text descriptions."""
        text_lower = text.lower()
        
        # 1D patterns
        if "chain" in text_lower:
            # "chain of 8 sites", "8-site chain", "chain 8", "1D chain with 2 sites"
            match = re.search(r'(?:(\d+)(?:\s*sites?)?\s*chain)|(?:chain\s*(?:of|with)?\s*(\d+)(?:\s*sites?)?)', text_lower)
            if match:
                size = int(match.group(1) or match.group(2))
                return {"lattice_type": "chain", "extent": [size]}
        
        # 2D patterns
        elif "square" in text_lower:
            # "4x4 square lattice", "square lattice 4x4", "4x4 square"
            match = re.search(r'(\d+)\s*x\s*(\d+)\s*square|square\s*(?:lattice\s*)?(\d+)\s*x\s*(\d+)', text_lower)
            if match:
                dims = [int(match.group(1) or match.group(3)), int(match.group(2) or match.group(4))]
                return {"lattice_type": "square", "extent": dims}
        
        elif "triangular" in text_lower:
            # "3x3 triangular lattice", "triangular lattice 3x3"
            match = re.search(r'(\d+)\s*x\s*(\d+)\s*triangular|triangular\s*(?:lattice\s*)?(\d+)\s*x\s*(\d+)', text_lower)
            if match:
                dims = [int(match.group(1) or match.group(3)), int(match.group(2) or match.group(4))]
                return {"lattice_type": "triangular", "extent": dims}
        
        elif "kagome" in text_lower:
            # "3x3 kagome lattice", "kagome lattice 3x3"
            match = re.search(r'(\d+)\s*x\s*(\d+)\s*kagome|kagome\s*(?:lattice\s*)?(\d+)\s*x\s*(\d+)', text_lower)
            if match:
                dims = [int(match.group(1) or match.group(3)), int(match.group(2) or match.group(4))]
                return {"lattice_type": "kagome", "extent": dims}
        
        elif "honeycomb" in text_lower:
            # "3x3 honeycomb lattice", "honeycomb lattice 3x3"
            match = re.search(r'(\d+)\s*x\s*(\d+)\s*honeycomb|honeycomb\s*(?:lattice\s*)?(\d+)\s*x\s*(\d+)', text_lower)
            if match:
                dims = [int(match.group(1) or match.group(3)), int(match.group(2) or match.group(4))]
                return {"lattice_type": "honeycomb", "extent": dims}
        
        # 3D patterns
        elif "cube" in text_lower or "cubic" in text_lower:
            # "2x2x2 cubic lattice", "cube 2x2x2", "2x2x2 cube"
            match = re.search(r'(\d+)\s*x\s*(\d+)\s*x\s*(\d+)\s*(?:cubic?|cube)|(?:cubic?|cube)\s*(\d+)\s*x\s*(\d+)\s*x\s*(\d+)', text_lower)
            if match:
                dims = [int(match.group(1) or match.group(4)), 
                       int(match.group(2) or match.group(5)), 
                       int(match.group(3) or match.group(6))]
                return {"lattice_type": "cube", "extent": dims}
        
        elif "fcc" in text_lower:
            # "2x2x2 fcc lattice", "fcc 2x2x2"
            match = re.search(r'(\d+)\s*x\s*(\d+)\s*x\s*(\d+)\s*fcc|fcc\s*(\d+)\s*x\s*(\d+)\s*x\s*(\d+)', text_lower)
            if match:
                dims = [int(match.group(1) or match.group(4)), 
                       int(match.group(2) or match.group(5)), 
                       int(match.group(3) or match.group(6))]
                return {"lattice_type": "fcc", "extent": dims}
        
        elif "bcc" in text_lower:
            # "2x2x2 bcc lattice", "bcc 2x2x2"
            match = re.search(r'(\d+)\s*x\s*(\d+)\s*x\s*(\d+)\s*bcc|bcc\s*(\d+)\s*x\s*(\d+)\s*x\s*(\d+)', text_lower)
            if match:
                dims = [int(match.group(1) or match.group(4)), 
                       int(match.group(2) or match.group(5)), 
                       int(match.group(3) or match.group(6))]
                return {"lattice_type": "bcc", "extent": dims}
        
        # Higher dimensional
        elif "hypercube" in text_lower:
            # "hypercube 4", "4D hypercube"
            match = re.search(r'hypercube\s*(\d+)|(\d+)d?\s*hypercube', text_lower)
            if match:
                dim = int(match.group(1) or match.group(2))
                return {"lattice_type": "hypercube", "extent": [dim]}
        
        # Fallback: try to extract dimensions
        match = re.search(r'(\d+)(?:\s*x\s*(\d+))?(?:\s*x\s*(\d+))?', text)
        if match:
            dims = [int(x) for x in match.groups() if x is not None]
            if len(dims) == 1:
                return {"lattice_type": "chain", "extent": dims}
            elif len(dims) == 2:
                return {"lattice_type": "square", "extent": dims}
            elif len(dims) == 3:
                return {"lattice_type": "cube", "extent": dims}
        
        raise ValueError(f"Could not parse lattice description: '{text}'. Supported formats: '4x4 square lattice', 'chain of 8 sites', '2x2x2 cubic lattice', etc.")
    
    @field_validator('lattice_type')
    @classmethod
    def validate_lattice_type(cls, v: str) -> str:
        """Validate lattice type."""
        valid_types = ['chain', 'square', 'triangular', 'kagome', 'honeycomb', 
                      'fcc', 'bcc', 'pyrochlore', 'cube', 'hypercube']
        if v.lower() not in valid_types:
            raise ValueError(f"Invalid lattice type: {v}. Valid types: {valid_types}")
        return v.lower()
    
    @field_validator('extent')
    @classmethod
    def validate_extent(cls, v: list[int]) -> list[int]:
        """Validate extent dimensions."""
        if not v or len(v) == 0:
            raise ValueError("Extent must be a non-empty list of positive integers")
        if not all(isinstance(x, int) and x > 0 for x in v):
            raise ValueError("All extent values must be positive integers")
        return v
    
    def to_netket_graph(self) -> Any:
        """Convert to NetKet graph object."""
        lattice_map = {
            'chain': ('length', nkgraph.Chain),
            'square': ('length', nkgraph.Square),
            'cube': ('length', nkgraph.Cube),
            'hypercube': ('length', nkgraph.Hypercube),
            'triangular': ('extent', nkgraph.Triangular),
            'kagome': ('extent', nkgraph.Kagome),
            'honeycomb': ('extent', nkgraph.Honeycomb),
            'fcc': ('extent', nkgraph.FCC),
            'bcc': ('extent', nkgraph.BCC),
            'pyrochlore': ('extent', nkgraph.Pyrochlore),
        }
        arg_name, graph_class = lattice_map.get(self.lattice_type, (None, None))
        if not graph_class:
            raise ValueError(f"Unsupported lattice type: {self.lattice_type}")

        # Chain: length=int
        if self.lattice_type == "chain":
            return graph_class(length=self.extent[0])
        # Square: length=int (only n x n)
        elif self.lattice_type == "square":
            if len(self.extent) == 2 and self.extent[0] == self.extent[1]:
                return graph_class(length=self.extent[0])
            else:
                raise ValueError("NetKet Square only supports n x n lattices. Use e.g. [4, 4].")
        # Cube: length=int (only n x n x n)
        elif self.lattice_type == "cube":
            if len(self.extent) == 3 and self.extent[0] == self.extent[1] == self.extent[2]:
                return graph_class(length=self.extent[0])
            else:
                raise ValueError("NetKet Cube only supports n x n x n lattices. Use e.g. [2, 2, 2].")
        # Hypercube: length=int (only n)
        elif self.lattice_type == "hypercube":
            if len(self.extent) == 1:
                return graph_class(length=self.extent[0])
            else:
                raise ValueError("NetKet Hypercube only supports a single dimension. Use e.g. [4].")
        # All others: extent=[...]
        else:
            return graph_class(extent=self.extent)
    
    @model_validator(mode='after')
    def render_to_text(self):
        """Generate canonical text representation."""
        if self.lattice_type == 'chain':
            self.text = f"chain of {self.extent[0]} sites"
        elif len(self.extent) == 2:
            self.text = f"{self.extent[0]}x{self.extent[1]} {self.lattice_type} lattice"
        elif len(self.extent) == 3:
            self.text = f"{self.extent[0]}x{self.extent[1]}x{self.extent[2]} {self.lattice_type} lattice"
        else:
            self.text = f"{self.lattice_type} lattice with extent {self.extent}"
        return self

class HilbertSpaceSchema(BaseModel):
    """
    Represents the Hilbert space of a quantum system with text-based specification.
    
    Converts text descriptions like:
    - "spin-1/2 on each site"
    - "fermions at half filling"
    - "8 fermions with spin-1/2"
    - "2 bosons in 3 modes"
    to NetKet Hilbert space specifications.
    """
    
    space_type: Literal["spin", "fermion", "boson"] = Field(
        description="Type of Hilbert space"
    )
    
    spin: Optional[float] = Field(
        default=0.5, 
        description="Spin value (for spin/fermion spaces); None for spinless fermions"
    )
    
    n_particles: Optional[int] = Field(
        default=None, 
        description="Fixed particle number (for fermion/boson spaces)"
    )
    
    n_modes: int = Field(
        default=1, 
        description="Number of modes (for bosons)"
    )
    
    text: str | None = Field(
        default=None,
        description="Text description like 'spin-1/2 on each site' or '8 fermions with spin-1/2'"
    )
    
    @model_validator(mode='before')
    @classmethod
    def parse_from_text(cls, data: dict) -> dict:
        """Parse text description to populate Hilbert space properties."""
        if 'text' in data and data['text']:
            text = data.pop('text').strip()
            parsed = cls._parse_hilbert_text(text)
            data.update(parsed)
        return data
    
    @classmethod
    def _parse_hilbert_text(cls, text: str) -> dict:
        """Parse Hilbert space text descriptions."""
        text_lower = text.lower()
        
        # Get particle number if specified (allow for words like 'spinless' in between)
        number_match = re.search(r'(\d+)\s*(?:\w+\s+)?(particles?|fermions?|bosons?)', text_lower)
        n_particles = int(number_match.group(1)) if number_match else None
        
        # Get spin if specified
        spin_match = re.search(r'spin[-\s]?(\d+(?:/\d+)?)', text_lower)
        if spin_match:
            spin_str = spin_match.group(1)
            if '/' in spin_str:
                num, denom = spin_str.split('/')
                spin = float(int(num)) / float(int(denom))
            else:
                spin = float(int(spin_str))
        else:
            spin = 0.5  # Default spin-1/2
        
        # Spinless fermion
        if "spinless" in text_lower and "fermion" in text_lower:
            return {
                "space_type": "fermion",
                "spin": None,
                "n_particles": n_particles
            }
        # Fermionic space
        if "fermion" in text_lower:
            return {
                "space_type": "fermion",
                "spin": spin,
                "n_particles": n_particles
            }
        
        # Bosonic space
        elif "boson" in text_lower:
            modes_match = re.search(r'(\d+)\s*modes?', text_lower)
            n_modes = int(modes_match.group(1)) if modes_match else 1
            
            return {
                "space_type": "boson",
                "n_particles": n_particles,
                "n_modes": n_modes
            }
            
        # Spin space (default)
        else:
            return {
                "space_type": "spin",
                "spin": spin
            }
    
    @field_validator('n_particles')
    @classmethod
    def validate_n_particles(cls, v: Optional[int], info) -> Optional[int]:
        """Validate particle number."""
        if info.data.get('space_type') in ['fermion', 'boson'] and v is None:
            raise ValueError("Number of particles must be specified for fermion/boson spaces")
        if v is not None and v <= 0:
            raise ValueError("Number of particles must be positive")
        return v
    
    def to_netket_hilbert(self, graph: Any) -> Any:
        """Convert to NetKet Hilbert space."""
        if self.space_type == "spin":
            return nkh.Spin(s=self.spin, N=graph.n_nodes)
        
        elif self.space_type == "fermion":
            if self.n_particles is None:
                raise ValueError("Number of particles must be specified for fermion space")
            # Spinless fermion
            if self.spin is None:
                return nkx.hilbert.SpinOrbitalFermions(graph.n_nodes, n_fermions=self.n_particles, s=None)
            else:
                return nkx.hilbert.SpinOrbitalFermions(graph.n_nodes, s=self.spin, n_fermions=self.n_particles)
        
        elif self.space_type == "boson":
            if self.n_particles is None:
                raise ValueError("Number of particles must be specified for boson space")
            return nkh.Fock(
                n_particles=self.n_particles, 
                N=self.n_modes, 
                n_max=None
            )
        
        else:
            raise ValueError(f"Unsupported Hilbert space type: {self.space_type}")
    
    @model_validator(mode='after')
    def render_to_text(self):
        """Generate canonical text representation."""
        if self.space_type == "spin":
            if self.spin == 0.5:
                self.text = "spin-1/2 on each site"
            else:
                self.text = f"spin-{self.spin} on each site"
        
        elif self.space_type == "fermion":
            if self.n_particles:
                if self.spin == 0.5:
                    self.text = f"{self.n_particles} fermions with spin-1/2"
                else:
                    self.text = f"{self.n_particles} fermions with spin-{self.spin}"
            else:
                self.text = "fermions"
        
        elif self.space_type == "boson":
            if self.n_particles:
                if self.n_modes == 1:
                    self.text = f"{self.n_particles} bosons"
                else:
                    self.text = f"{self.n_particles} bosons in {self.n_modes} modes"
            else:
                self.text = "bosons"
        
        return self

class HamiltonianSchema(BaseModel):
    """
    Represents quantum Hamiltonians with predefined components.
    
    Supports common models like SSH, Hubbard, Heisenberg, etc. with simple parameter specification.
    """
    
    # Model type
    model_type: str = Field(description="Hamiltonian model type")
    
    # Parameters for different models
    parameters: Dict[str, float] = Field(default_factory=dict, description="Model parameters")
    
    # Parameter ranges for sweeps
    parameter_ranges: Optional[Dict[str, List[float]]] = Field(
        default=None, 
        description="Parameter ranges for sweeps, e.g., {'t2': [0.1, 0.5, 1.0, 1.5, 2.0]}"
    )
    
    text: str | None = Field(
        default=None,
        description="Text description like 'SSH model with t1=1, t2=0.2'"
    )
    
    @model_validator(mode='before')
    @classmethod
    def parse_from_text(cls, data: dict) -> dict:
        """Parse text description to populate model_type and parameters."""
        if 'text' in data and data['text']:
            text = data.pop('text').strip()
            
            # Parse various Hamiltonian descriptions
            parsed = cls._parse_hamiltonian_text(text)
            data['model_type'] = parsed['model_type']
            data['parameters'] = parsed['parameters']
            
        return data
    
    @classmethod
    def _parse_hamiltonian_text(cls, text: str) -> dict:
        """Parse Hamiltonian text descriptions."""
        text_lower = text.lower()
        
        # SSH Model
        if "ssh" in text_lower:
            t1 = cls._extract_parameter(text, "t1", 1.0)
            t2 = cls._extract_parameter(text, "t2", 0.2)
            return {
                "model_type": "ssh",
                "parameters": {"t1": t1, "t2": t2}
            }
        
        # Hubbard Model
        elif "hubbard" in text_lower:
            t = cls._extract_parameter(text, "t", 1.0)
            u = cls._extract_parameter(text, "u", 4.0)
            return {
                "model_type": "hubbard", 
                "parameters": {"t": t, "U": u}
            }
        
        # Fermion Hopping
        elif "fermion" in text_lower and "hopping" in text_lower:
            t = cls._extract_parameter(text, "t", 1.0)
            b = cls._extract_parameter(text, "b", 0.0)
            return {
                "model_type": "fermion_hopping",
                "parameters": {"t": t, "B": b}
            }
        
        # Heisenberg Model
        elif "heisenberg" in text_lower:
            j = cls._extract_parameter(text, "j", 1.0)
            return {
                "model_type": "heisenberg",
                "parameters": {"J": j}
            }
        
        # Ising Model
        elif "ising" in text_lower:
            jz = cls._extract_parameter(text, "jz", 1.0)
            hx = cls._extract_parameter(text, "hx", 0.0)
            hz = cls._extract_parameter(text, "hz", 0.0)
            return {
                "model_type": "ising",
                "parameters": {"Jz": jz, "hx": hx, "hz": hz}
            }
        
        # Kitaev Model
        elif "kitaev" in text_lower:
            jx = cls._extract_parameter(text, "jx", 1.0)
            jy = cls._extract_parameter(text, "jy", 1.0)
            jz = cls._extract_parameter(text, "jz", 1.0)
            return {
                "model_type": "kitaev",
                "parameters": {"Jx": jx, "Jy": jy, "Jz": jz}
            }
        
        else:
            raise ValueError(f"Could not parse Hamiltonian description: '{text}'. "
                           f"Supported models: SSH, Hubbard, Fermion Hopping, Heisenberg, Ising, Kitaev")
    
    @classmethod
    def _extract_parameter(cls, text: str, param_name: str, default: float) -> float:
        """Extract parameter value from text."""
        # Look for patterns like "t1=1.5", "t1 = 1.5", "t1: 1.5"
        patterns = [
            rf"{param_name}\s*=\s*([+-]?\d*\.?\d+)",
            rf"{param_name}\s*:\s*([+-]?\d*\.?\d+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return default
    
    def build_netket_hamiltonian(self, hilbert: Any, graph: Any, system_hilbert=None) -> Any:
        """Build NetKet Hamiltonian operator from specification."""
        L = graph.n_nodes
        H = 0
        
        # Check if we're dealing with spin-1/2 fermions using the schema
        is_spin_fermion = False
        if system_hilbert and system_hilbert.space_type == "fermion" and system_hilbert.spin == 0.5:
            is_spin_fermion = True
        
        if self.model_type == "ssh":
            t1 = self.parameters.get("t1", 1.0)
            t2 = self.parameters.get("t2", 0.2)
            for i in range(L - 1):
                t = t2 if i % 2 == 0 else t1
                if is_spin_fermion:
                    # For spin-1/2 fermions, use spin-up component (sz=1)
                    H += -t * (cdag(hilbert, i, sz=1) * c(hilbert, i+1, sz=1) + 
                              cdag(hilbert, i+1, sz=1) * c(hilbert, i, sz=1))
                else:
                    # For spinless fermions
                    H += -t * (cdag(hilbert, i) * c(hilbert, i+1) + 
                              cdag(hilbert, i+1) * c(hilbert, i))
        
        elif self.model_type == "hubbard":
            t = self.parameters.get("t", 1.0)
            U = self.parameters.get("U", 4.0)
            # Full spinful Hubbard model: sum hopping over both spins, and on-site U n_up n_down
            for i in range(L - 1):
                # Hopping for both spins
                H += -t * sum(
                    cdag(hilbert, i, sz) * c(hilbert, i+1, sz) + cdag(hilbert, i+1, sz) * c(hilbert, i, sz)
                    for sz in [1, -1]
                )
            # On-site interaction U n_up n_down
            for i in range(L):
                H += U * cdag(hilbert, i, sz=1) * c(hilbert, i, sz=1) * cdag(hilbert, i, sz=-1) * c(hilbert, i, sz=-1)
        
        elif self.model_type == "fermion_hopping":
            t = self.parameters.get("t", 1.0)
            B = self.parameters.get("B", 0.0)
            for i in range(L - 1):
                if is_spin_fermion:
                    # For spin-1/2 fermions, use spin-up component (sz=1)
                    H += -t * (cdag(hilbert, i, sz=1) * c(hilbert, i+1, sz=1) + 
                              cdag(hilbert, i+1, sz=1) * c(hilbert, i, sz=1))
                else:
                    # For spinless fermions
                    H += -t * (cdag(hilbert, i) * c(hilbert, i+1) + 
                              cdag(hilbert, i+1) * c(hilbert, i))
            if B != 0:
                for i in range(L):
                    if is_spin_fermion:
                        # For spin-1/2 fermions, use spin-up component (sz=1)
                        H += B * cdag(hilbert, i, sz=1) * c(hilbert, i, sz=1)
                    else:
                        # For spinless fermions
                        H += B * cdag(hilbert, i) * c(hilbert, i)
        
        elif self.model_type == "heisenberg":
            J = self.parameters.get("J", 1.0)
            # Heisenberg model for spins
            if system_hilbert and system_hilbert.space_type == "spin":
                H = J * nko.Heisenberg(hilbert)
            else:
                raise ValueError("Heisenberg model requires spin Hilbert space")
        
        elif self.model_type == "ising":
            Jz = self.parameters.get("Jz", 1.0)
            hx = self.parameters.get("hx", 0.0)
            hz = self.parameters.get("hz", 0.0)
            # Ising model for spins
            if system_hilbert and system_hilbert.space_type == "spin":
                H = Jz * nko.Ising(hilbert, graph, h=hx)
                if hz != 0:
                    H += hz * nko.LocalOperator(hilbert, nko.PauliZ, 0)
            else:
                raise ValueError("Ising model requires spin Hilbert space")
        
        elif self.model_type == "kitaev":
            Jx = self.parameters.get("Jx", 1.0)
            Jy = self.parameters.get("Jy", 1.0)
            Jz = self.parameters.get("Jz", 1.0)
            # Kitaev model (simplified implementation)
            if system_hilbert and system_hilbert.space_type == "spin":
                # This is a simplified Kitaev implementation
                # In practice, you'd need to implement the specific Kitaev interactions
                H = Jx * nko.LocalOperator(hilbert, nko.sigmax, 0) + \
                    Jy * nko.LocalOperator(hilbert, nko.sigmay, 0) + \
                    Jz * nko.LocalOperator(hilbert, nko.sigmaz, 0)
            else:
                raise ValueError("Kitaev model requires spin Hilbert space")
        
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
        
        return H
    
    def get_parameters(self) -> Dict[str, float]:
        """Get current parameters as a dictionary."""
        return self.parameters.copy()
    
    @model_validator(mode='after')
    def render_to_text(self):
        """Generate canonical text representation."""
        if not self.text:
            param_str = ", ".join([f"{k}={v}" for k, v in self.parameters.items()])
            self.text = f"{self.model_type.upper()} model with {param_str}"
        return self

# Utility function for creating schemas from text
def create_lattice_from_text(text: str) -> LatticeSchema:
    """Create LatticeSchema from text description."""
    return LatticeSchema(text=text)

def create_particles_from_text(text: str) -> HilbertSpaceSchema:
    """Create HilbertSpaceSchema from text description."""
    return HilbertSpaceSchema(text=text)

def create_hamiltonian_from_text(text: str) -> HamiltonianSchema:
    """Create HamiltonianSchema from text description."""
    return HamiltonianSchema(text=text) 