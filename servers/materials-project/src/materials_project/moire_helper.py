import numpy as np
from ase import Atom, Atoms
from ase.build import cut


def homobilayer_twist(
    structure: Atoms, interlayer_spacing: float, max_num_atoms=10, twist_angle=0.0, vacuum_thickness=15.0
) -> Atom | Atoms:
    """
    Generate a moire superstructure of a 2D homobilayer.
    Args:
        structure (ase.Atoms): The primitive structure of the monolayer 2D material. The z direction should be perpendicular to the 2D plane.
        interlayer_spacing (float): The interlayer spacing between the two layers, in angstrom.
        max_num_atoms (int): The maximum number of atoms in the moire superstructure.
        twist_angle (float): The twist angle of the moire superstructure, in degrees.
        vacuum_thickness (float): The vacuum thickness in the z direction, in angstrom.
    Returns:
        ase.Atoms: The moire superstructure.
    """
    cell_array = structure.get_cell().array.copy()  # unit cell vectors, in angstrom
    # Number of atoms in the primitive unit cell
    Natoms = len(structure.get_atomic_numbers())

    a1 = cell_array[0, :]
    a2 = cell_array[1, :]
    assert np.abs(np.linalg.norm(a1) / np.linalg.norm(a2) -
                  1) < 1e-3, "The lattice should be square or hexagonal"
    angle = np.arccos(np.clip(np.dot(a1, a2) / (np.linalg.norm(a1)
                      * np.linalg.norm(a2)), -1.0, 1.0)) * 180 / np.pi
    assert np.round(angle) == 90 or np.round(angle) == 120 or np.round(angle) == 60, (
        "The lattice should be square or hexagonal"
    )
    # in the hexagonal lattice, We use the convention that the angle between a1 and a2 is 60 degrees
    if np.round(angle) == 120:
        a2 = a2 + a1
        cell_array[1, :] = a2
        structure.set_cell(cell_array, scale_atoms=False)

    # Generate the table of twist angles
    iter_max = 50
    lst = np.zeros([iter_max * iter_max + 1, 4])
    cnt = 0
    for n in range(1, iter_max - 1):
        for m in reversed(range(n, iter_max)):
            if m == n and n > 1:
                continue
            supercell_a1 = m * (a1 + a2) - n * a2
            supercell_a2 = m * (a1 + a2) - n * a1
            cos_theta = np.dot(supercell_a1, supercell_a2) / (
                np.linalg.norm(supercell_a1) * np.linalg.norm(supercell_a2)
            )
            twist_angle_degree = np.arccos(
                np.clip(cos_theta, -1.0, 1.0)) * 180 / np.pi
            Natoms_super = 2 * Natoms * \
                np.round((np.linalg.norm(supercell_a1) ** 2) /
                         (np.linalg.norm(a1) ** 2))
            lst[cnt, :] = np.array(
                [m, m - n, twist_angle_degree, Natoms_super])
            cnt += 1
    lst[cnt, :] = np.array([1, 0, 0, 2 * Natoms])
    lst = lst[: cnt + 1]

    # Find desired structures
    filtered_indices = np.where(lst[:, 3] < max_num_atoms)[0]
    filtered_data = lst[filtered_indices]
    differences = np.abs(filtered_data[:, 2] - twist_angle)
    closest_indices = np.argsort(differences)[:5]

    # Generate the moire structure
    interlayer_spacing = 3.5  # in angstrom
    interlayer_spacing += np.max(structure.positions[:, 2]) - np.min(
        structure.positions[:, 2])
    p, q = int(filtered_data[closest_indices[0], 0]), int(
        filtered_data[closest_indices[0], 1])
    twist_angle_rad = filtered_data[closest_indices[0], 2] * np.pi / 180

    super_struc_1 = cut(structure, a=(p, q, 0), b=(-q, p + q, 0),
                        c=(0, 0, 1))  # Supercell of layer 1
    super_struc_2 = cut(structure, a=(q, p, 0), b=(-p, q + p, 0),
                        c=(0, 0, 1))  # Supercell of layer 2

    # Rotate the second layer and shift in the z direction to form a moire superstructure
    rotmat = np.array(
        [
            [np.cos(twist_angle_rad), -np.sin(twist_angle_rad), 0],
            [np.sin(twist_angle_rad), np.cos(twist_angle_rad), 0],
            [0, 0, 1],
        ]
    )
    super_numbers_1 = super_struc_1.get_atomic_numbers()
    super_numbers_2 = super_struc_2.get_atomic_numbers()
    super_positions_1 = super_struc_1.positions
    super_positions_2 = super_struc_2.positions @ rotmat
    position_offset = np.zeros_like(super_positions_1)
    position_offset[:, 2] = interlayer_spacing / 2
    super_positions_1 += position_offset
    super_positions_2 -= position_offset

    # Generate the moire structure
    numbers_moire = np.concatenate((super_numbers_1, super_numbers_2))
    positions_moire = np.concatenate((super_positions_1, super_positions_2))
    positions_moire[:,
                    2] -= np.mean(positions_moire[:, 2]) + cell_array[2, 2] / 2
    positions_moire = np.mod(
        positions_moire, super_struc_1.get_cell().array[2][2])
    moire_cell = super_struc_1.get_cell().array.copy()
    moire_cell[2, 2] = np.max(positions_moire[:, 2]) - \
        np.min(positions_moire[:, 2]) + vacuum_thickness
    positions_moire[:, 2] += vacuum_thickness / 2

    struc_moire = Atoms(numbers=numbers_moire,
                        positions=positions_moire, cell=moire_cell, pbc=[1, 1, 0])
    atomic_numbers = struc_moire.get_atomic_numbers()  # [8, 6, 14, 14, 6, 8]
    sorted_indices = np.argsort(atomic_numbers)
    sorted_struc_moire = struc_moire[sorted_indices]

    return sorted_struc_moire
