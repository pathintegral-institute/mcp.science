from mcp.server.fastmcp import FastMCP, Image
from mcp.types import TextContent, ImageContent
from netket_schemas import LatticeSchema, HilbertSpaceSchema, HamiltonianSchema
from netket_jsons import NetKetJSONManager, QuantumSystemState
from typing import Literal, Optional, Dict, Any, List, Union
import numpy as np
import netket as nk
from netket.experimental.operator.fermion import destroy as c
from netket.experimental.operator.fermion import create as cdag
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt
import io
import base64
import shutil

# Create the MCP server object
mcp = FastMCP('NetKet Quantum Many-Body Physics Server')

# Create a JSON manager
json_manager = NetKetJSONManager()

# @mcp.tool() # This is a test tool
# def add(a: int, b: int) -> int:
#     return a + b

@mcp.tool()
def create_quantum_system(description: Optional[str] = None) -> Dict[str, Any]:
    '''Create a new quantum system for analysis.
    
    This tool creates a new quantum system with a unique ID that can be used
    to build up a complete quantum many-body system step by step.
    
    Args:
        description: Optional description of the system to create
        
    Returns:
        Dictionary containing the system ID and status
        
    Example:
        - Input: {"description": "SSH model on 24-site chain"}
        - Output: {
            "system_id": "system_a1b2c3d4",
            "status": "empty",
            "message": "New quantum system created successfully"
        }
    '''
    system_id = json_manager.create_system(description)
    system = json_manager.systems[system_id]
    return {
        "system_id": system_id,
        "status": system.status,
        "message": "New quantum system created successfully"
    }

@mcp.tool()
def set_lattice(system_id: str, lattice_spec: str) -> Dict[str, Any]:
    '''Set the lattice geometry for a quantum system.
    
    This tool sets the lattice component of a quantum system using text-based specification.
    
    Args:
        system_id: The ID of the quantum system
        lattice_spec: Text description of the lattice (e.g., "chain of 24 sites", "4x4 square lattice")
        
    Returns:
        Dictionary containing the updated system status and lattice information
        
    Examples:
        - Input: {"system_id": "system_a1b2c3d4", "lattice_spec": "chain of 24 sites"}
        - Output: {
            "system_id": "system_a1b2c3d4",
            "lattice": "chain of 24 sites",
            "lattice_type": "chain",
            "extent": [24],
            "status": "partial"
        }
    '''
    json_manager.update_component("lattice", lattice_spec, system_id)
    system = json_manager.systems[system_id]
    return {
        "system_id": system_id,
        "lattice": system.lattice.text,
        "lattice_type": system.lattice.lattice_type,
        "extent": system.lattice.extent,
        "status": system.status,
        "warnings": system.warnings
    }

@mcp.tool()
def set_hilbert_space(system_id: str, hilbert_spec: str) -> Dict[str, Any]:
    '''Set the Hilbert space for a quantum system.
    
    This tool sets the Hilbert space component of a quantum system using text-based specification.
    
    Args:
        system_id: The ID of the quantum system
        hilbert_spec: Text description of the Hilbert space (e.g., "1 fermion", "spin-1/2 on each site")
        
    Returns:
        Dictionary containing the updated system status and Hilbert space information
        
    Examples:
        - Input: {"system_id": "system_a1b2c3d4", "hilbert_spec": "1 fermion"}
        - Output: {
            "system_id": "system_a1b2c3d4",
            "hilbert": "1 fermion",
            "space_type": "fermion",
            "n_particles": 1,
            "status": "partial"
        }
    '''
    json_manager.update_component("hilbert", hilbert_spec, system_id)
    system = json_manager.systems[system_id]
    return {
        "system_id": system_id,
        "hilbert": system.hilbert.text,
        "space_type": system.hilbert.space_type,
        "n_particles": system.hilbert.n_particles,
        "status": system.status,
        "warnings": system.warnings
    }

@mcp.tool()
def set_hamiltonian(system_id: str, hamiltonian_spec: str, 
                   parameter_ranges: Optional[Dict[str, List[float]]] = None) -> Dict[str, Any]:
    '''Set the Hamiltonian for a quantum system with optional parameter ranges for sweeps.
    
    This tool sets the Hamiltonian component of a quantum system using text-based specification.
    It can also include parameter ranges for automatic parameter sweeps.
    
    Args:
        system_id: The ID of the quantum system
        hamiltonian_spec: Text description of the Hamiltonian (e.g., "SSH model with t1=1, t2=0.2")
        parameter_ranges: Optional parameter ranges for sweeps (e.g., {"t2": [0.1, 0.5, 1.0, 1.5, 2.0]})
        
    Returns:
        Dictionary containing the updated system status and Hamiltonian information
        
    Examples:
        - Input: {
            "system_id": "system_a1b2c3d4", 
            "hamiltonian_spec": "SSH model with t1=1, t2=0.2",
            "parameter_ranges": {"t2": [0.1, 0.5, 1.0, 1.5, 2.0]}
          }
        - Output: {
            "system_id": "system_a1b2c3d4",
            "hamiltonian": "SSH model with t1=1, t2=0.2",
            "model_type": "SSH",
            "parameters": {"t1": 1.0, "t2": 0.2},
            "parameter_ranges": {"t2": [0.1, 0.5, 1.0, 1.5, 2.0]},
            "status": "complete"
          }
    '''
    # Create HamiltonianSchema with parameter ranges
    hamiltonian_data = {"text": hamiltonian_spec}
    if parameter_ranges:
        hamiltonian_data["parameter_ranges"] = parameter_ranges
    
    json_manager.update_component("hamiltonian", hamiltonian_data, system_id)
    system = json_manager.systems[system_id]
    
    # Extract parameters for display
    params = system.hamiltonian.get_parameters() if system.hamiltonian else {}
    
    return {
        "system_id": system_id,
        "hamiltonian": system.hamiltonian.text,
        "model_type": system.hamiltonian.model_type.upper() if system.hamiltonian else None,
        "parameters": params,
        "parameter_ranges": system.hamiltonian.parameter_ranges if system.hamiltonian else None,
        "status": system.status,
        "warnings": system.warnings
    }

@mcp.tool()
def compute_energy_spectrum(system_id: str, num_eigenvalues: int = 10, which: str = "SA") -> Dict[str, Any]:
    '''Compute the energy spectrum of a quantum system.
    
    This tool performs exact diagonalization to find the energy eigenvalues
    of the system's Hamiltonian. It automatically builds the Hamiltonian from
    the system specification if needed.
    
    Args:
        system_id: The ID of the quantum system
        num_eigenvalues: Number of eigenvalues to compute (default: 10)
        which: Which eigenvalues to compute ("SA" for smallest algebraic, "LA" for largest algebraic)
        
    Returns:
        Dictionary containing the energy spectrum
        
    Examples:
        - Input: {"system_id": "system_a1b2c3d4", "num_eigenvalues": 5}
        - Output: {
            "system_id": "system_a1b2c3d4",
            "eigenvalues": [-2.5, -1.8, -0.3, 0.3, 1.8],
            "ground_state_energy": -2.5,
            "energy_gap": 1.5,
            "num_eigenvalues": 5
          }
    '''
    try:
        # Validate system_id
        if system_id not in json_manager.systems:
            raise ValueError(f"System '{system_id}' not found. Use create_quantum_system() first.")
        
        system = json_manager.systems[system_id]
        
        # Validate input parameters
        if num_eigenvalues <= 0:
            raise ValueError(f"num_eigenvalues must be positive, got {num_eigenvalues}")
        
        if which not in ["SA", "LA", "SM", "LM"]:
            raise ValueError(f"Invalid 'which' parameter: {which}. Must be 'SA', 'LA', 'SM', or 'LM'")
        
        # Check if all required components are present
        if not system.lattice or not system.hilbert or not system.hamiltonian:
            missing = []
            if not system.lattice: missing.append("lattice")
            if not system.hilbert: missing.append("Hilbert space")
            if not system.hamiltonian: missing.append("Hamiltonian")
            raise ValueError(f"System missing required components: {', '.join(missing)}. "
                           "Use set_lattice(), set_hilbert_space(), and set_hamiltonian() first.")
        
        # Build Hamiltonian from specification
        try:
            H, hi, graph = _build_hamiltonian_from_spec(system)
        except Exception as e:
            raise ValueError(f"Failed to build quantum system: {str(e)}. "
                           "Check lattice, Hilbert space, and Hamiltonian compatibility.")
        
        # Check system size constraints
        if hi.n_states > 1e6:
            raise ValueError(f"System too large: {hi.n_states} states. "
                           "Consider reducing system size or using approximate methods.")
        

        
        # Function for exact diagonalization with error handling
        def ED(H, k=num_eigenvalues, which=which):
            try:
                if hi.n_states > 1e3:  # sparse matrix approach
                    try:
                        sp_h = H.to_sparse()
                        eig_vals, eig_vecs = eigsh(sp_h, k=k, which=which)
                        sort_idx = np.argsort(eig_vals)
                        eig_vals_sorted = eig_vals[sort_idx]
                        eig_vecs_sorted = eig_vecs[:, sort_idx]
                    except Exception as e:
                        raise RuntimeError(f"Sparse eigenvalue computation failed: {str(e)}. "
                                         "Try reducing system size or num_eigenvalues.")
                else:  # dense matrix approach
                    try:
                        dense_h = H.to_dense()
                        eig_vals_sorted, eig_vecs_sorted = np.linalg.eigh(dense_h)
                        if k < len(eig_vals_sorted):
                            eig_vals_sorted = eig_vals_sorted[:k]
                            eig_vecs_sorted = eig_vecs_sorted[:, :k]
                    except np.linalg.LinAlgError as e:
                        raise RuntimeError(f"Dense eigenvalue computation failed: {str(e)}. "
                                         "The Hamiltonian matrix may be ill-conditioned.")
                    except MemoryError:
                        raise RuntimeError("Not enough memory for dense matrix diagonalization. "
                                         "Try reducing system size.")
                
                return eig_vals_sorted, eig_vecs_sorted
                
            except Exception as e:
                raise RuntimeError(f"Eigenvalue computation failed: {str(e)}")
        
        # Perform eigenvalue computation
        eigvals, eigvecs = ED(H)
        
        # Validate results
        if len(eigvals) == 0:
            raise RuntimeError("No eigenvalues computed. Check system parameters.")
        
        # Store results with error handling
        try:
            system.results["energy_spectrum"] = {
                "eigenvalues": eigvals.tolist(),
                "eigenvectors": eigvecs.tolist(),
                "ground_state_energy": float(eigvals[0]),
                "energy_gap": float(eigvals[1] - eigvals[0]) if len(eigvals) > 1 else 0.0
            }
            system.results["model_type"] = system.hamiltonian.model_type
            system.results["parameters"] = system.hamiltonian.get_parameters()
            json_manager.save_system(system_id)
        except Exception as e:
            print(f"Warning: Failed to save results: {str(e)}")
        
        return {
            "system_id": system_id,
            "eigenvalues": eigvals.tolist(),
            "ground_state_energy": float(eigvals[0]),
            "energy_gap": float(eigvals[1] - eigvals[0]) if len(eigvals) > 1 else 0.0,
            "num_eigenvalues": len(eigvals),
            "model_type": system.hamiltonian.model_type.upper(),
            "parameters": system.hamiltonian.get_parameters()
        }
        
    except ValueError as e:
        # User input errors - clear error message
        raise ValueError(str(e))
    except RuntimeError as e:
        # Computation errors - clear error message 
        raise RuntimeError(str(e))
    except Exception as e:
        # Unexpected errors - provide debugging info
        raise RuntimeError(f"Unexpected error in compute_energy_spectrum: {str(e)}. "
                         f"System: {system_id}, Parameters: num_eigenvalues={num_eigenvalues}, which={which}")

@mcp.tool()
def analyze_ground_state(system_id: str) -> Dict[str, Any]:
    '''Analyze the ground state properties of a quantum system.
    
    This is a convenience function that calls analyze_eigenstate with index 0.
    
    Args:
        system_id: The ID of the quantum system
        
    Returns:
        Dictionary containing ground state analysis
    '''
    return analyze_eigenstate(system_id, eigenstate_index=0)

@mcp.tool()
def parameter_sweep(system_id: str, parameter_name: str, 
                   parameter_range: Optional[List[float]] = None) -> Dict[str, Any]:
    '''Perform a parameter sweep for a quantum model.
    
    This tool varies one parameter while keeping others fixed, computing
    the energy spectrum at each point. It can use parameter ranges from
    the Hamiltonian specification if available.
    
    Args:
        system_id: The ID of the quantum system
        parameter_name: Name of parameter to sweep (e.g., "t2", "U", "J")
        parameter_range: List of parameter values to try (optional, uses Hamiltonian specification if not provided)
        
    Returns:
        Dictionary containing sweep results
        
    Examples:
        - Input: {
            "system_id": "system_a1b2c3d4",
            "parameter_name": "t2"
          }
        - Output: {
            "system_id": "system_a1b2c3d4",
            "parameter_name": "t2",
            "parameter_range": [0.1, 0.5, 1.0, 1.5, 2.0],
            "ground_state_energies": [-2.1, -1.8, -1.5, -1.8, -2.1],
            "energy_gaps": [0.5, 0.8, 0.0, 0.8, 0.5]
          }
    '''
    try:
        # Validate system_id
        if system_id not in json_manager.systems:
            raise ValueError(f"System '{system_id}' not found. Use create_quantum_system() first.")
        
        system = json_manager.systems[system_id]
        
        # Validate parameter_name
        if not parameter_name or not isinstance(parameter_name, str):
            raise ValueError("parameter_name must be a non-empty string")
        
        # Check if all required components are present
        if not system.lattice or not system.hilbert or not system.hamiltonian:
            missing = []
            if not system.lattice: missing.append("lattice")
            if not system.hilbert: missing.append("Hilbert space")
            if not system.hamiltonian: missing.append("Hamiltonian")
            raise ValueError(f"System missing required components: {', '.join(missing)}. "
                           "Use set_lattice(), set_hilbert_space(), and set_hamiltonian() first.")
        
        # Get parameter range from Hamiltonian specification if not provided
        if parameter_range is None:
            if system.hamiltonian.parameter_ranges and parameter_name in system.hamiltonian.parameter_ranges:
                parameter_range = system.hamiltonian.parameter_ranges[parameter_name]
            else:
                raise ValueError(f"No parameter range provided and no range found in Hamiltonian specification for '{parameter_name}'. "
                               "Either provide parameter_range or set it in set_hamiltonian() with parameter_ranges.")
        
        # Validate parameter_range
        if not parameter_range or not isinstance(parameter_range, list):
            raise ValueError("parameter_range must be a non-empty list")
        
        if len(parameter_range) < 2:
            raise ValueError("parameter_range must contain at least 2 values")
        
        # Check if parameter exists in Hamiltonian
        base_params = system.hamiltonian.get_parameters()
        if parameter_name not in base_params:
            available_params = list(base_params.keys())
            raise ValueError(f"Parameter '{parameter_name}' not found in Hamiltonian. "
                           f"Available parameters: {available_params}")
    
    except ValueError:
        raise
    except Exception as e:
        raise RuntimeError(f"Error validating parameter sweep inputs: {str(e)}")
    
    try:
        # Create NetKet objects
        graph = system.lattice.to_netket_graph()
        hi = system.hilbert.to_netket_hilbert(graph)
        
        # Check system size constraints
        if hi.n_states > 1e5:
            raise ValueError(f"System too large for parameter sweep: {hi.n_states} states. "
                           "Consider reducing system size.")
        
        # Function for exact diagonalization with error handling
        def ED(H, k=5, which="SA"):
            try:
                if hi.n_states > 1e3:  # sparse matrix
                    sp_h = H.to_sparse()
                    eig_vals, eig_vecs = eigsh(sp_h, k=k, which=which)
                    sort_idx = np.argsort(eig_vals)
                    eig_vals_sorted = eig_vals[sort_idx]
                    eig_vecs_sorted = eig_vecs[:, sort_idx]
                else:
                    eig_vals_sorted, eig_vecs_sorted = np.linalg.eigh(H.to_dense())
                return eig_vals_sorted, eig_vecs_sorted
            except Exception as e:
                raise RuntimeError(f"Eigenvalue computation failed: {str(e)}")
        
        ground_state_energies = []
        energy_gaps = []
        spectra_data = {}
        all_eigenvalues = []  # Store all eigenvalues for each parameter value
        
        # Get base parameters from Hamiltonian specification
        base_params = system.hamiltonian.get_parameters()
        model_type = system.hamiltonian.model_type
        
        # Main computation loop with error handling
        for i, param_value in enumerate(parameter_range):
            try:
                # Create a temporary Hamiltonian with the new parameter value
                temp_params = base_params.copy()
                temp_params[parameter_name] = param_value
                
                # Create a temporary HamiltonianSchema
                temp_hamiltonian = HamiltonianSchema(
                    model_type=model_type,
                    parameters=temp_params
                )
                
                # Build Hamiltonian using the schema's method
                H = temp_hamiltonian.build_netket_hamiltonian(hi, graph, system_hilbert=system.hilbert)
                
                # Compute spectrum
                eigvals, eigvecs = ED(H, k=hi.n_states if hi.n_states <= 100 else 10)
                
                if len(eigvals) == 0:
                    raise RuntimeError(f"No eigenvalues computed for {parameter_name}={param_value}")
                
                ground_state_energies.append(float(eigvals[0]))
                
                # Calculate the physical excitation gap, accounting for degeneracy
                if len(eigvals) > 1:
                    E0 = eigvals[0]
                    # Find the first eigenvalue that is not degenerate with the ground state
                    first_excited_val = E0
                    for e_val in eigvals[1:]:
                        if not np.isclose(e_val, E0, atol=1e-6): # Use tolerance for numerical degeneracy
                            first_excited_val = e_val
                            break
                    
                    # If all computed eigenvalues are degenerate, the gap is 0
                    if np.isclose(first_excited_val, E0, atol=1e-6):
                        gap = 0.0
                    else:
                        gap = first_excited_val - E0
                    energy_gaps.append(float(gap))
                else:
                    energy_gaps.append(0.0)

                spectra_data[f"{parameter_name}_{param_value}"] = eigvals.tolist()
                all_eigenvalues.append(eigvals.tolist())
                
            except Exception as e:
                raise RuntimeError(f"Error computing spectrum for {parameter_name}={param_value}: {str(e)}")
        
        # Validate results
        if not ground_state_energies:
            raise RuntimeError("No valid results computed in parameter sweep")
        
        # Store results with error handling
        try:
            system.results["parameter_sweep"] = {
                "parameter_name": parameter_name,
                "parameter_range": parameter_range,
                "ground_state_energies": ground_state_energies,
                "energy_gaps": energy_gaps,
                "spectra_data": spectra_data,
                "all_eigenvalues": all_eigenvalues,
                "model_type": model_type,
                "base_parameters": base_params
            }
            # Do NOT store any NetKet objects in results
            json_manager.save_system(system_id)
        except Exception as e:
            print(f"Warning: Failed to save parameter sweep results: {str(e)}")
        
        return {
            "system_id": system_id,
            "parameter_name": parameter_name,
            "parameter_range": parameter_range,
            "ground_state_energies": ground_state_energies,
            "energy_gaps": energy_gaps,
            "all_eigenvalues": all_eigenvalues,
            "model_type": model_type.upper(),
            "base_parameters": base_params
        }
        
    except ValueError as e:
        raise ValueError(str(e))
    except RuntimeError as e:
        raise RuntimeError(str(e))
    except Exception as e:
        raise RuntimeError(f"Unexpected error in parameter_sweep: {str(e)}. "
                         f"System: {system_id}, Parameter: {parameter_name}")

@mcp.tool()
def plot_xy(system_id: str, x_data: List[float], y_data: List[float], 
            x_label: str, y_label: str, title: str, 
            file_name: str) -> Dict[str, Any]:
    '''Generate a generic 2D plot and save it to a file.
    
    This tool creates a 2D plot from given x and y data and saves it
    to a file within the specified system's directory.
    
    Args:
        system_id: The ID of the quantum system to associate the plot with.
        x_data: Data for the x-axis.
        y_data: Data for the y-axis.
        x_label: Label for the x-axis.
        y_label: Label for the y-axis.
        title: Title of the plot.
        file_name: Name of the file to save the plot (e.g., 'custom_plot.png').
        
    Returns:
        Dictionary confirming the plot has been saved.
    '''
    system = json_manager.systems[system_id]
    system_dir = json_manager.storage_dir / system.system_id
    system_dir.mkdir(exist_ok=True)
    full_path = system_dir / file_name
    
    plt.figure(figsize=(8, 6))
    plt.plot(x_data, y_data, 'o-', markersize=6)
    plt.xlabel(x_label, fontsize=12)
    plt.ylabel(y_label, fontsize=12)
    plt.title(title, fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plt.savefig(full_path, dpi=150, bbox_inches='tight')
    plt.close()
        
    return {
        "system_id": system_id,
        "plot_type": "xy_plot",
        "file_path": str(full_path),
        "description": "XY plot saved to file"
    }

@mcp.tool()
def generate_plot(system_id: str, plot_type: str, file_path: Optional[str] = None) -> Dict[str, Any]:
    '''Generate plots for quantum system analysis.
    
    This tool creates various types of plots based on the system's analysis results.
    
    Args:
        system_id: The ID of the quantum system
        plot_type: Type of plot ("spectrum", "ground_state", "parameter_sweep")
        file_path: Optional path to save the plot image file (e.g., "ssh_transition.png")
        
    Returns:
        Dictionary containing plot data
        
    Examples:
        - Input: {"system_id": "system_a1b2c3d4", "plot_type": "parameter_sweep", "file_path": "ssh_transition.png"}
        - Output: {
            "system_id": "system_a1b2c3d4",
            "plot_type": "parameter_sweep",
            "file_path": "ssh_transition.png",
            "description": "Parameter sweep plot saved to file"
          }
    '''
    try:
        # Validate system_id
        if system_id not in json_manager.systems:
            raise ValueError(f"System '{system_id}' not found. Use create_quantum_system() first.")
        
        system = json_manager.systems[system_id]
        
        # Validate plot_type
        valid_plot_types = ["spectrum", "ground_state", "parameter_sweep"]
        if plot_type not in valid_plot_types:
            raise ValueError(f"Invalid plot_type '{plot_type}'. Must be one of: {valid_plot_types}")
        
        # Clear any existing plots to avoid conflicts
        plt.close('all')
        
        # Generate plots based on type with error handling
        if plot_type == "spectrum":
            if "energy_spectrum" not in system.results:
                raise ValueError("No energy spectrum data available. Run compute_energy_spectrum() first.")
            
            try:
                spectrum = system.results["energy_spectrum"]
                eigvals = spectrum["eigenvalues"]
                
                if not eigvals:
                    raise ValueError("Empty eigenvalue data")
                
                plt.figure(figsize=(8, 6))
                plt.plot(range(len(eigvals)), eigvals, 'o-', markersize=6)
                plt.xlabel("Eigenvalue index", fontsize=12)
                plt.ylabel("Energy", fontsize=12)
                plt.title(f"Energy Spectrum: {system.results.get('model_type', 'Unknown')} Model", fontsize=14)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
            except Exception as e:
                raise RuntimeError(f"Failed to create energy spectrum plot: {str(e)}")
                
        elif plot_type == "ground_state":
            if "ground_state_analysis" not in system.results:
                raise ValueError("No ground state data available. Run analyze_ground_state() first.")
            
            try:
                gs_analysis = system.results["ground_state_analysis"]
                spatial_profile = gs_analysis["spatial_profile"]
                
                if not spatial_profile:
                    raise ValueError("Empty spatial profile data")
                
                plt.figure(figsize=(8, 5))
                plt.plot(range(len(spatial_profile)), spatial_profile, 'o-', markersize=4)
                plt.xlabel("Site index", fontsize=12)
                plt.ylabel("|ψ(i)|²", fontsize=12)
                plt.title(f"Ground State Profile: {system.results.get('model_type', 'Unknown')} Model", fontsize=14)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
            except Exception as e:
                raise RuntimeError(f"Failed to create ground state plot: {str(e)}")
                
        elif plot_type == "parameter_sweep":
            if "parameter_sweep" not in system.results:
                raise ValueError("No parameter sweep data available. Run parameter_sweep() first.")
            
            try:
                sweep = system.results["parameter_sweep"]
                param_range = sweep["parameter_range"]
                gs_energies = sweep["ground_state_energies"]
                energy_gaps = sweep["energy_gaps"]
                
                if not param_range or not gs_energies or not energy_gaps:
                    raise ValueError("Incomplete parameter sweep data")
                
                if len(param_range) != len(gs_energies) or len(param_range) != len(energy_gaps):
                    raise ValueError("Inconsistent parameter sweep data lengths")
                
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                
                # Ground state energy
                ax1.plot(param_range, gs_energies, 'o-', markersize=6)
                ax1.set_xlabel(sweep["parameter_name"], fontsize=12)
                ax1.set_ylabel("Ground State Energy", fontsize=12)
                ax1.set_title("Ground State Energy", fontsize=14)
                ax1.grid(True, alpha=0.3)
                
                # Energy gap
                ax2.plot(param_range, energy_gaps, 'o-', markersize=6, color='red')
                ax2.set_xlabel(sweep["parameter_name"], fontsize=12)
                ax2.set_ylabel("Energy Gap", fontsize=12)
                ax2.set_title("Energy Gap", fontsize=14)
                ax2.grid(True, alpha=0.3)
                
                plt.tight_layout()
            except Exception as e:
                raise RuntimeError(f"Failed to create parameter sweep plot: {str(e)}")
        
        # Handle file saving or base64 encoding
        if file_path:
            try:
                # Validate file path
                if not file_path.endswith(('.png', '.jpg', '.jpeg', '.pdf', '.svg')):
                    file_path += '.png'  # Default to PNG
                
                # Save plot to file inside the system's directory
                system_dir = json_manager.storage_dir / system_id
                system_dir.mkdir(exist_ok=True)
                full_path = system_dir / file_path
                
                plt.savefig(full_path, dpi=150, bbox_inches='tight')
                
                # Verify file was created
                if not full_path.exists():
                    raise RuntimeError("Plot file was not created successfully")
                
                plt.close()
                
                return {
                    "system_id": system_id,
                    "plot_type": plot_type,
                    "file_path": str(full_path),
                    "description": f"{plot_type.replace('_', ' ').title()} plot saved to file"
                }
                
            except Exception as e:
                plt.close()  # Clean up
                raise RuntimeError(f"Failed to save plot to file: {str(e)}")
        else:
            try:
                # Return plot as base64
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                buf.seek(0)
                plot_data = base64.b64encode(buf.getvalue()).decode()
                plt.close()
                
                if not plot_data:
                    raise RuntimeError("Failed to generate plot data")
                
                return {
                    "system_id": system_id,
                    "plot_type": plot_type,
                    "plot_data": plot_data,
                    "description": f"{plot_type.replace('_', ' ').title()} plot as base64"
                }
                
            except Exception as e:
                plt.close()  # Clean up
                raise RuntimeError(f"Failed to encode plot as base64: {str(e)}")
                
    except ValueError as e:
        # Clean up matplotlib resources
        plt.close('all')
        raise ValueError(str(e))
    except RuntimeError as e:
        plt.close('all')
        raise RuntimeError(str(e))
    except Exception as e:
        plt.close('all')
        raise RuntimeError(f"Unexpected error in generate_plot: {str(e)}. "
                         f"System: {system_id}, Plot type: {plot_type}")

@mcp.tool()
def list_quantum_systems() -> List[Dict[str, Any]]:
    '''List all available quantum systems.
    
    Returns:
        List of dictionaries containing system information
        
    Example:
        - Output: [
            {
                "system_id": "system_a1b2c3d4",
                "status": "complete",
                "last_modified": "2024-01-15T10:30:00",
                "lattice": "chain of 24 sites",
                "hilbert": "1 fermion",
                "hamiltonian": "SSH model with t1=1, t2=0.2"
            }
        ]
    '''
    return json_manager.list_systems()

@mcp.tool()
def get_system_details(system_id: str) -> Dict[str, Any]:
    '''Get detailed information about a specific quantum system.
    
    Args:
        system_id: The ID of the quantum system
        
    Returns:
        Dictionary containing complete system details
        
    Example:
        - Input: {"system_id": "system_a1b2c3d4"}
        - Output: {
            "system_id": "system_a1b2c3d4",
            "status": "complete",
            "created_at": "2024-01-15T10:00:00",
            "last_modified": "2024-01-15T10:30:00",
            "lattice": {...},
            "hilbert": {...},
            "hamiltonian": {...},
            "results": {...},
            "warnings": []
        }
    '''
    if system_id not in json_manager.systems:
        raise ValueError(f"System {system_id} not found")
    
    system = json_manager.systems[system_id]
    return system.to_dict()

@mcp.tool()
def display_numerical_result(system_id: str, file_name: str) -> Union[ImageContent, TextContent]:
    """Displays a saved plot for a given quantum system analysis.

    Args:
        system_id: The ID of the system for which to display the plot.
        file_name: The name of the plot file, e.g., 'ssh_full_spectrum.png'.

    Returns:
        The plot as an image if found, otherwise a text error message.
    """
    try:
        # Get the system's directory from the json_manager
        system_dir = json_manager.storage_dir / system_id
        plot_path = system_dir / file_name

        if not plot_path.exists():
            return TextContent(type="text", text=f"Error: Plot file '{file_name}' not found for system '{system_id}' at '{plot_path}'.")

        # Read the image file in binary mode
        with open(plot_path, 'rb') as image_file:
            image_data = image_file.read()
        
        # Encode the binary data to a base64 string
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # Return the image content
        return ImageContent(data=image_base64, mimeType="image/png", type="image")

    except Exception as e:
        # Return an error message if anything goes wrong
        return TextContent(type="text", text=f"An error occurred: {e}")

@mcp.tool()
def delete_quantum_system(system_id: str) -> Dict[str, Any]:
    '''Delete a quantum system and its associated data.
    
    Args:
        system_id: The ID of the quantum system to delete
        
    Returns:
        Dictionary confirming deletion
        
    Example:
        - Input: {"system_id": "system_a1b2c3d4"}
        - Output: {
            "system_id": "system_a1b2c3d4",
            "status": "deleted",
            "message": "System deleted successfully"
        }
    '''
    if system_id not in json_manager.systems:
        raise ValueError(f"System {system_id} not found")
    
    # Remove from memory
    del json_manager.systems[system_id]

    # Delete the entire system directory
    system_dir = json_manager.storage_dir / system_id
    if system_dir.exists():
        shutil.rmtree(system_dir)
    
    return {
        "system_id": system_id,
        "status": "deleted",
        "message": "System and all associated files deleted successfully"
    }

def _build_hamiltonian_from_spec(system) -> Any:
    """Helper function to build NetKet Hamiltonian from system specification."""
    try:
        if not system.lattice or not system.hilbert or not system.hamiltonian:
            raise ValueError("System must have lattice, Hilbert space, and Hamiltonian defined")
        
        # Create NetKet objects with error handling
        try:
            graph = system.lattice.to_netket_graph()
        except Exception as e:
            raise ValueError(f"Failed to create lattice graph: {str(e)}. Check lattice specification.")
        
        try:
            hi = system.hilbert.to_netket_hilbert(graph)
        except Exception as e:
            raise ValueError(f"Failed to create Hilbert space: {str(e)}. Check Hilbert space compatibility with lattice.")
        
        # Validate Hilbert space size
        if hi.n_states <= 0:
            raise ValueError("Invalid Hilbert space: zero states")
        
        # Build Hamiltonian using the schema's method, passing the Hilbert space schema
        try:
            H = system.hamiltonian.build_netket_hamiltonian(hi, graph, system_hilbert=system.hilbert)
        except Exception as e:
            raise ValueError(f"Failed to build Hamiltonian: {str(e)}. Check Hamiltonian compatibility with lattice and Hilbert space.")
        
        return H, hi, graph
        
    except ValueError:
        # Re-raise ValueError with original message
        raise
    except Exception as e:
        # Wrap unexpected errors
        raise RuntimeError(f"Unexpected error building quantum system: {str(e)}")

@mcp.tool()
def analyze_eigenstate(system_id: str, eigenstate_index: int) -> Dict[str, Any]:
    '''Analyze a specific eigenstate of a quantum system.
    
    This tool computes various properties of a specified eigenstate, including
    energy and spatial profile for fermionic systems.
    It automatically computes the energy spectrum if not already available.
    
    Args:
        system_id: The ID of the quantum system
        eigenstate_index: The index of the eigenstate to analyze (0 for ground state, 1 for first excited, etc.)
        
    Returns:
        Dictionary containing eigenstate analysis
        
    Examples:
        - Input: {"system_id": "system_a1b2c3d4", "eigenstate_index": 1}
        - Output: {
            "system_id": "system_a1b2c3d4",
            "eigenstate_index": 1,
            "energy": -1.8,
            "spatial_profile": [0.3, 0.2, 0.1, ...],
            "localization": "extended"
          }
    '''
    system = json_manager.systems[system_id]
    
    # Check if all required components are present
    if not system.lattice or not system.hilbert or not system.hamiltonian:
        raise ValueError("System must have lattice, Hilbert space, and Hamiltonian defined. "
                        "Use set_lattice(), set_hilbert_space(), and set_hamiltonian() first.")
    
    # Check if we need to compute the spectrum
    spectrum = system.results.get("energy_spectrum")
    if not spectrum or eigenstate_index >= len(spectrum.get("eigenvalues", [])):
        num_to_compute = max(10, eigenstate_index + 1)
        
        # Build Hamiltonian and compute spectrum
        H, hi, graph = _build_hamiltonian_from_spec(system)
        
        # Function for exact diagonalization
        def ED(H, k=num_to_compute, which="SA"):
            if hi.n_states > 1e3:  # sparse matrix
                sp_h = H.to_sparse()
                eig_vals, eig_vecs = eigsh(sp_h, k=k, which=which)
                sort_idx = np.argsort(eig_vals)
                eig_vals_sorted = eig_vals[sort_idx]
                eig_vecs_sorted = eig_vecs[:, sort_idx]
            else:
                eig_vals_sorted, eig_vecs_sorted = np.linalg.eigh(H.to_dense())
                if k < len(eig_vals_sorted):
                    eig_vals_sorted = eig_vals_sorted[:k]
                    eig_vecs_sorted = eig_vecs_sorted[:, :k]
            return eig_vals_sorted, eig_vecs_sorted
        
        eigvals, eigvecs = ED(H)
        
        # Store spectrum results
        system.results["energy_spectrum"] = {
            "eigenvalues": eigvals.tolist(),
            "eigenvectors": eigvecs.tolist(),
            "ground_state_energy": float(eigvals[0]),
            "energy_gap": float(eigvals[1] - eigvals[0]) if len(eigvals) > 1 else 0.0
        }
        system.results["model_type"] = system.hamiltonian.model_type
        system.results["parameters"] = system.hamiltonian.get_parameters()

    spectrum = system.results["energy_spectrum"]
    eigvals = np.array(spectrum["eigenvalues"])
    eigvecs = np.array(spectrum["eigenvectors"])
    
    if eigenstate_index >= len(eigvals):
        raise ValueError(f"Eigenstate index {eigenstate_index} is out of bounds. "
                         f"Only {len(eigvals)} eigenvalues were computed. "
                         f"You might need to re-run compute_energy_spectrum with a larger num_eigenvalues.")

    # Get the requested eigenstate
    energy = eigvals[eigenstate_index]
    psi = eigvecs[:, eigenstate_index]
    prob_density = np.abs(psi)**2
    
    # Analyze localization
    if system.hilbert.space_type == "fermion":
        localization = "localized" if np.std(prob_density) > 0.1 else "extended"
    else:
        localization = "N/A"
    
    # Store results for this specific eigenstate
    analysis_key = f"eigenstate_{eigenstate_index}_analysis"
    system.results[analysis_key] = {
        "eigenstate_index": eigenstate_index,
        "energy": float(energy),
        "spatial_profile": prob_density.tolist(),
        "localization": localization
    }
    json_manager.save_system(system_id)
    
    return {
        "system_id": system_id,
        "eigenstate_index": eigenstate_index,
        "energy": float(energy),
        "spatial_profile": prob_density.tolist(),
        "localization": localization,
        "model_type": system.hamiltonian.model_type.upper(),
        "parameters": system.hamiltonian.get_parameters()
    }

def main():
    mcp.run('stdio')

if __name__ == "__main__":
    main() 